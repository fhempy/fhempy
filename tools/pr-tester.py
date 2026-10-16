#!/usr/bin/env python3
"""Test a fhempy pull request on the machine fhempy runs on (e.g. a Raspberry Pi).

The script
  1. lists the open pull requests of fhempy/fhempy and lets you pick one
     (or "master" for the latest unreleased code),
  2. installs that code into its own virtual environment (.fhempy/pr_test/venv),
     the normal fhempy installation stays untouched,
  3. stops the running fhempy (fhempyServer in FHEM or the fhempy systemd service),
  4. starts fhempy from the pull request in the foreground, its log is shown in the
     terminal and written to .fhempy/pr_test/,
  5. after Ctrl+C it stops the test fhempy, starts the normal fhempy again and
     prints a short summary (errors, tracebacks, event loop blocks).

Usage (as a user with sudo rights, the script switches to the fhempy user):
  curl -fsSLO https://raw.githubusercontent.com/fhempy/fhempy/master/tools/pr-tester.py
  python3 pr-tester.py              # choose a pull request from the list
  python3 pr-tester.py --pr 123     # test pull request 123
  python3 pr-tester.py --pr master  # test the master branch
  python3 pr-tester.py --restore    # start the normal fhempy again (e.g. after a crash)
  python3 pr-tester.py --clean      # remove the test installation

Run it within tmux or screen if you are connected via SSH. If the SSH connection
drops, the script still tries to start the normal fhempy again.

Only the Python standard library is used, any Python >= 3.9 works.
"""

import argparse
import base64
import configparser
import json
import os
import pwd
import re
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

REPO = "fhempy/fhempy"
API_URL = "https://api.github.com/repos/" + REPO
DEFAULT_PORT = 15733
DEFAULT_FHEM_DIRS = ["/opt/fhem"]
START_SCRIPT = "FHEM/bindings/python/bin/start_fhempy.py"
SERVICE = "fhempy"
# FHEM modules which belong to fhempy, they are not part of the Python package
FHEM_MODULE_RE = re.compile(r"^FHEM/(\d\d_[A-Za-z0-9_]+)\.pm$")
# starts fhempy with INFO logging like FHEM/bindings/python/bin/start_fhempy.py,
# the fhempy console script only logs warnings
RUN_FHEMPY = """
import logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s", level=logging.INFO
)
from fhempy.lib.fhem_pythonbinding import run
run()
"""
LOG_PATTERNS = {
    "errors": re.compile(r" - ERROR +- "),
    "tracebacks": re.compile(r"^Traceback \(most recent call last\)"),
    "event loop blocked": re.compile(r"Event loop blocked"),
}


class TestError(Exception):
    pass


def parse_json(text):
    """Parses the JSON output of an FHEM command, ignores telnet prompts around it."""
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON in FHEM output")
    return json.loads(text[start : end + 1])


def info(msg):
    print(f"\033[1m>>> {msg}\033[0m", flush=True)


def warn(msg):
    print(f"\033[1;33m>>> {msg}\033[0m", flush=True)


def ask(question, default=False):
    suffix = " [Y/n] " if default else " [y/N] "
    try:
        answer = input(question + suffix).strip().lower()
    except EOFError:
        return default
    if not answer:
        return default
    return answer in ("y", "yes", "j", "ja")


def run(cmd, check=True, **kwargs):
    """Runs cmd and returns the CompletedProcess, output is captured."""
    proc = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **kwargs
    )
    if check and proc.returncode != 0:
        raise TestError(f"{' '.join(cmd)} failed:\n{proc.stdout.strip()}")
    return proc


def port_open(port, host="127.0.0.1"):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def wait_for_port(port, is_open, timeout):
    end = time.time() + timeout
    while time.time() < end:
        if port_open(port) == is_open:
            return True
        time.sleep(0.5)
    return False


# --- GitHub ---------------------------------------------------------------


def github_get(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "fhempy-pr-tester",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(API_URL + path, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        if err.code == 403:
            raise TestError(
                "GitHub API rate limit reached, try again later or set GITHUB_TOKEN"
            ) from err
        raise TestError(f"GitHub API {path}: {err}") from err
    except urllib.error.URLError as err:
        raise TestError(f"GitHub not reachable: {err.reason}") from err


def choose_target(pr_arg):
    """Returns a dict describing what to test: name, sha, pr (number or None)."""
    if pr_arg is None:
        pulls = github_get("/pulls?state=open&per_page=50")
        print()
        if pulls:
            print("Open pull requests:")
            for pull in pulls:
                draft = " [draft]" if pull.get("draft") else ""
                print(
                    f"  #{pull['number']:<5} {pull['title'][:70]}{draft}"
                    f"  ({pull['user']['login']}, {pull['updated_at'][:10]})"
                )
        else:
            print("There are no open pull requests.")
        print("  master  latest code of the master branch (not released yet)")
        print()
        try:
            pr_arg = input("Pull request number to test (or master, q to quit): ")
        except EOFError:
            pr_arg = "q"
        pr_arg = pr_arg.strip().lstrip("#")
        if pr_arg in ("", "q", "quit"):
            sys.exit(0)

    if pr_arg == "master":
        branch = github_get("/branches/master")
        return {
            "name": "master",
            "sha": branch["commit"]["sha"],
            "pr": None,
        }
    if not pr_arg.isdigit():
        raise TestError(f"{pr_arg} is neither a pull request number nor master")
    pull = github_get(f"/pulls/{pr_arg}")
    if pull["state"] != "open":
        warn(
            f"Pull request #{pr_arg} is "
            + ("merged" if pull.get("merged_at") else "closed")
        )
    return {
        "name": f"PR #{pull['number']}: {pull['title']}",
        "sha": pull["head"]["sha"],
        "pr": pull["number"],
    }


def pr_fhem_modules(pr_number):
    """Returns the FHEM Perl modules (e.g. 10_BindingsIo) changed by the PR."""
    modules = []
    page = 1
    while True:
        files = github_get(f"/pulls/{pr_number}/files?per_page=100&page={page}")
        for entry in files:
            match = FHEM_MODULE_RE.match(entry["filename"])
            if match and entry["status"] != "removed":
                modules.append(match.group(1))
        if len(files) < 100:
            return modules
        page += 1


def download_source(target, src_dir):
    # commits of pull requests from forks are available in the fhempy repo too
    url = f"https://codeload.github.com/{REPO}/tar.gz/{target['sha']}"
    info(f"Downloading {target['sha'][:10]}")
    shutil.rmtree(src_dir, ignore_errors=True)
    os.makedirs(src_dir)
    with tempfile.TemporaryFile() as tmp:
        req = urllib.request.Request(url, headers={"User-Agent": "fhempy-pr-tester"})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                shutil.copyfileobj(resp, tmp)
        except urllib.error.URLError as err:
            raise TestError(f"Download of {url} failed: {err}") from err
        tmp.seek(0)
        with tarfile.open(fileobj=tmp, mode="r:gz") as tar:
            members = []
            for member in tar.getmembers():
                # strip the top level directory (fhempy-<sha>/)
                parts = member.name.split("/", 1)
                if len(parts) < 2 or not parts[1]:
                    continue
                member.name = parts[1]
                if member.name.startswith("/") or ".." in member.name.split("/"):
                    raise TestError(f"Unsafe path in archive: {member.name}")
                if member.issym() or member.islnk():
                    continue
                members.append(member)
            if hasattr(tarfile, "data_filter"):
                tar.extractall(src_dir, members=members, filter="data")
            else:
                tar.extractall(src_dir, members=members)


# --- FHEM connection (fhempy running locally on the FHEM machine) -----------


class Fhem:
    """Sends commands to FHEM via telnet or FHEMWEB, asks the user as fallback."""

    def __init__(self, fhem_dir, telnet_port=None, url=None):
        self.telnet_port = telnet_port
        self.url = url
        cfg = self._read_cfg(fhem_dir)
        if self.telnet_port is None:
            match = re.search(r"^define\s+\S+\s+telnet\s+(\d+)", cfg, re.M)
            self.telnet_port = int(match.group(1)) if match else 7072
        if self.url is None:
            match = re.search(r"^define\s+(\S+)\s+FHEMWEB\s+(\d+)", cfg, re.M)
            self.url = f"http://127.0.0.1:{match.group(2) if match else 8083}/fhem"
        self.method = None

    @staticmethod
    def _read_cfg(fhem_dir):
        try:
            with open(os.path.join(fhem_dir, "fhem.cfg"), encoding="utf-8") as f:
                return f.read()
        except OSError:
            return ""

    def _telnet(self, cmd):
        with socket.create_connection(("127.0.0.1", self.telnet_port), timeout=10) as s:
            s.sendall((cmd + "\nquit\n").encode("utf-8"))
            data = b""
            while True:
                chunk = s.recv(65536)
                if not chunk:
                    break
                data += chunk
        text = data.decode("utf-8", "replace")
        if text.lstrip().startswith("Password:"):
            raise TestError("telnet requires a password")
        return text

    def _http(self, cmd):
        parsed = urllib.parse.urlsplit(self.url)
        headers = {"User-Agent": "fhempy-pr-tester"}
        if parsed.username:
            creds = f"{urllib.parse.unquote(parsed.username)}:" + urllib.parse.unquote(
                parsed.password or ""
            )
            headers["Authorization"] = "Basic " + base64.b64encode(
                creds.encode("utf-8")
            ).decode("ascii")
            netloc = parsed.hostname + (f":{parsed.port}" if parsed.port else "")
            parsed = parsed._replace(netloc=netloc)
        base = urllib.parse.urlunsplit(parsed)
        req = urllib.request.Request(base + "?XHR=1", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            token = resp.headers.get("X-FHEM-csrfToken", "")
        query = urllib.parse.urlencode({"cmd": cmd, "XHR": "1", "fwcsrf": token})
        req = urllib.request.Request(base + "?" + query, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", "replace")

    def connect(self):
        """Finds a working connection, returns False if there is none."""
        for method in (self._telnet, self._http):
            try:
                parse_json(method("jsonlist2 TYPE=fhempyServer"))
            except (OSError, ValueError, TestError, urllib.error.URLError):
                continue
            self.method = method
            return True
        return False

    def cmd(self, cmd):
        if self.method is None:
            raise TestError("no connection to FHEM")
        return self.method(cmd)

    def cmd_or_ask(self, cmd):
        """Sends cmd to FHEM, asks the user to do it if there is no connection."""
        if self.method is not None:
            try:
                out = self.cmd(cmd).strip()
                if out:
                    print(out)
                return
            except (OSError, TestError, urllib.error.URLError) as err:
                warn(f"FHEM command failed: {err}")
        warn(f"Please run this command in FHEM: {cmd}")
        try:
            input("Press Enter when done...")
        except EOFError:
            pass

    def devices(self, devspec):
        try:
            return parse_json(self.cmd("jsonlist2 " + devspec)).get("Results", [])
        except (OSError, ValueError, TestError, urllib.error.URLError):
            return None


# --- installation detection -----------------------------------------------


def systemd_service():
    """Returns the properties of the fhempy systemd service or None."""
    if not shutil.which("systemctl"):
        return None
    proc = run(
        [
            "systemctl",
            "show",
            SERVICE,
            "-p",
            "LoadState,ActiveState,User,WorkingDirectory,ExecStart",
        ],
        check=False,
    )
    props = {}
    for line in proc.stdout.splitlines():
        key, _, value = line.partition("=")
        props[key] = value
    if props.get("LoadState") != "loaded":
        return None
    return props


def running_fhempy_dirs():
    """Returns the working directories of running fhempy processes (if readable)."""
    dirs = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                cmdline = f.read().split(b"\0")
            if not any(
                arg.endswith((b"start_fhempy.py", b"/bin/fhempy")) for arg in cmdline
            ):
                continue
            dirs.append(os.readlink(f"/proc/{pid}/cwd"))
        except OSError:
            continue
    return dirs


def detect(args):
    """Returns a dict with mode (local or peer), dir, user and service details."""
    service = systemd_service()
    if args.dir:
        work_dir = os.path.abspath(args.dir)
        mode = "local" if os.path.exists(os.path.join(work_dir, "fhem.pl")) else "peer"
    elif service and service.get("ActiveState") == "active":
        mode = "peer"
        work_dir = service.get("WorkingDirectory") or None
        if not work_dir:
            user = service.get("User") or "root"
            work_dir = pwd.getpwnam(user).pw_dir
    else:
        mode = "local"
        candidates = running_fhempy_dirs() + DEFAULT_FHEM_DIRS
        if os.environ.get("HOME"):
            candidates.append(os.environ["HOME"])
        work_dir = next(
            (d for d in candidates if os.path.exists(os.path.join(d, START_SCRIPT))),
            None,
        )
        if work_dir is None:
            if service:
                mode = "peer"
                work_dir = (
                    service.get("WorkingDirectory")
                    or pwd.getpwnam(service.get("User") or "root").pw_dir
                )
            else:
                raise TestError(
                    "No fhempy installation found, use --dir <FHEM or fhempy directory>"
                )
    if args.mode:
        mode = args.mode
    if not os.path.isdir(os.path.join(work_dir, ".fhempy")):
        raise TestError(f"{work_dir}/.fhempy not found, is fhempy installed there?")
    return {
        "mode": mode,
        "dir": work_dir,
        "user": pwd.getpwuid(os.stat(os.path.join(work_dir, ".fhempy")).st_uid).pw_name,
        "service": service,
    }


def switch_user(user):
    """Re-executes the script as the fhempy user, it owns the .fhempy directory."""
    if pwd.getpwnam(user).pw_uid == os.geteuid():
        return
    info(f"Switching to user {user}")
    # the user might not be allowed to read the script (e.g. in /home/pi)
    fd, copy = tempfile.mkstemp(prefix="fhempy-pr-tester-", suffix=".py")
    with os.fdopen(fd, "w") as f, open(os.path.abspath(__file__)) as src:
        f.write(src.read())
    os.chmod(copy, 0o644)
    cmd = ["sudo", "-u", user, "-H"]
    for var in ("GITHUB_TOKEN", "TERM"):
        if os.environ.get(var):
            cmd.append(f"{var}={os.environ[var]}")
    cmd += [sys.executable, copy] + sys.argv[1:]
    try:
        sys.exit(subprocess.call(cmd))
    finally:
        os.unlink(copy)


def sudo(cmd):
    return cmd if os.geteuid() == 0 else ["sudo"] + cmd


# --- test installation ------------------------------------------------------


class TestInstall:
    def __init__(self, work_dir):
        self.work_dir = work_dir
        self.base = os.path.join(work_dir, ".fhempy", "pr_test")
        self.venv = os.path.join(self.base, "venv")
        self.python = os.path.join(self.venv, "bin", "python")
        self.src = os.path.join(self.base, "src")
        self.prod_venv = os.path.join(work_dir, ".fhempy", "fhempy_venv")
        self.state_file = os.path.join(self.base, "state.json")
        self.installed_file = os.path.join(self.base, "installed.json")
        self.backup_dir = os.path.join(self.base, "fhem_backup")
        self.uv = self._find_uv()

    def _find_uv(self):
        if os.environ.get("FHEMPY_NO_UV"):
            return None
        uv = os.path.join(self.work_dir, ".fhempy", "bin", "uv")
        if os.access(uv, os.X_OK):
            return uv
        return shutil.which("uv")

    def index_env(self):
        """uv doesn't read pip.conf, pass extra indexes like bin/fhempy does."""
        env = {}
        if not self.uv:
            return env
        parser = configparser.ConfigParser()
        parser.read(
            ["/etc/pip.conf", os.path.expanduser("~/.config/pip/pip.conf")],
            encoding="utf-8",
        )
        urls = []
        for section in ("global", "install"):
            urls += parser.get(section, "extra-index-url", fallback="").split()
        if urls and python_version("/usr/bin/python3") != python_version(self.python):
            # piwheels builds wheels for the system Python of the OS release only
            urls = [u for u in urls if "piwheels" not in u]
            env["FHEMPY_NO_PIWHEELS"] = "1"
        if urls:
            env["UV_EXTRA_INDEX_URL"] = " ".join(urls)
            env["UV_INDEX_STRATEGY"] = "unsafe-best-match"
        return env

    def _pip(self, *args):
        env = dict(os.environ, **self.index_env())
        if self.uv:
            return run(
                [self.uv, "pip", "install", "--python", self.python] + list(args),
                env=env,
            )
        return run(
            [self.python, "-m", "pip", "install", "--quiet"] + list(args), env=env
        )

    def create_venv(self, fresh):
        if fresh:
            shutil.rmtree(self.venv, ignore_errors=True)
            remove(self.installed_file)
        if os.path.exists(self.python) and python_version(self.python):
            return
        prod_python = os.path.join(self.prod_venv, "bin", "python")
        if not python_version(prod_python):
            raise TestError(f"{prod_python} doesn't work, start the normal fhempy once")
        info(f"Creating test environment {self.venv}")
        shutil.rmtree(self.venv, ignore_errors=True)
        os.makedirs(self.base, exist_ok=True)
        # same Python as the normal fhempy
        if self.uv:
            run(
                [
                    self.uv,
                    "venv",
                    "--quiet",
                    "--seed",
                    "--python",
                    prod_python,
                    self.venv,
                ]
            )
        else:
            run([prod_python, "-m", "venv", self.venv])
        # same packages as the normal fhempy, modules don't need to install them again
        freeze = run(
            [prod_python, "-m", "pip", "freeze", "--exclude", "fhempy"], check=False
        ).stdout
        reqs = [
            line
            for line in freeze.splitlines()
            if re.match(r"^[A-Za-z0-9_.-]+==", line)
        ]
        if reqs:
            info(f"Copying {len(reqs)} packages of the normal fhempy installation")
            req_file = os.path.join(self.base, "requirements.txt")
            with open(req_file, "w") as f:
                f.write("\n".join(reqs) + "\n")
            try:
                self._pip("--no-deps", "-r", req_file)
            except TestError as err:
                warn(
                    "Not all packages could be copied, "
                    f"modules install them on demand\n{err}"
                )

    def install(self, target, fresh):
        self.create_venv(fresh)
        installed = read_json(self.installed_file)
        if installed.get("sha") == target["sha"] and not fresh:
            info(f"{target['name']} ({target['sha'][:10]}) is already installed")
            return
        download_source(target, self.src)
        info("Installing fhempy from the downloaded source")
        if self.uv:
            self._pip("--reinstall-package", "fhempy", self.src)
        else:
            self._pip(self.src)
            self._pip("--no-deps", "--force-reinstall", self.src)
        write_json(self.installed_file, {"sha": target["sha"], "name": target["name"]})

    def fhempy_version(self):
        proc = run([os.path.join(self.venv, "bin", "fhempy"), "--version"], check=False)
        return proc.stdout.strip()


def python_version(python):
    try:
        proc = run(
            [python, "-c", "import sys; print(sys.version_info[:2])"], check=False
        )
    except OSError:
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def remove(path):
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


# --- stop/start the normal fhempy -----------------------------------------


class Runner:
    def __init__(self, ctx, args):
        self.ctx = ctx
        self.args = args
        self.port = args.port
        self.inst = TestInstall(ctx["dir"])
        self.fhem = None
        if ctx["mode"] == "local":
            self.fhem = Fhem(ctx["dir"], args.telnet_port, args.fhem_url)
            if not self.fhem.connect():
                warn(
                    "No connection to FHEM via telnet or FHEMWEB, you'll be asked to "
                    "run FHEM commands yourself (see --telnet-port and --fhem-url)"
                )

    def server_device(self):
        if self.fhem and self.fhem.method:
            devices = self.fhem.devices("TYPE=fhempyServer") or []
            if devices:
                return devices[0]["Name"]
        return "fhempy_local"

    def stop_normal(self, state):
        if self.ctx["mode"] == "local":
            device = self.server_device()
            state["device"] = device
            write_json(self.inst.state_file, state)
            info(f"Stopping the normal fhempy (set {device} stop)")
            self.fhem.cmd_or_ask(f"set {device} stop")
        else:
            write_json(self.inst.state_file, state)
            info(f"Stopping the {SERVICE} service")
            run(sudo(["systemctl", "stop", SERVICE]))
        if not wait_for_port(self.port, False, 30):
            raise TestError(f"Port {self.port} is still in use, fhempy didn't stop")

    def start_normal(self, state):
        self.restore_fhem_modules(state)
        if state.get("mode") == "local":
            device = state.get("device", "fhempy_local")
            info(f"Starting the normal fhempy again (set {device} start)")
            fhem = self.fhem or Fhem(
                self.ctx["dir"], self.args.telnet_port, self.args.fhem_url
            )
            if fhem.method is None:
                fhem.connect()
            fhem.cmd_or_ask(f"set {device} start")
        else:
            info(f"Starting the {SERVICE} service again")
            run(sudo(["systemctl", "start", SERVICE]), check=False)
        if wait_for_port(self.port, True, 120):
            info("The normal fhempy is running again")
        else:
            warn(
                f"The normal fhempy doesn't listen on port {self.port} yet, "
                "please check"
            )
        remove(self.inst.state_file)

    # FHEM Perl modules of the pull request (only if FHEM runs on this machine)

    def select_fhem_modules(self, target):
        """Returns the changed FHEM modules the user wants to test as well."""
        if target["pr"] is None:
            # master: installed fhempy modules which differ from the master version
            modules = []
            for name in os.listdir(os.path.join(self.inst.src, "FHEM")):
                match = FHEM_MODULE_RE.match("FHEM/" + name)
                installed = os.path.join(self.ctx["dir"], "FHEM", name)
                if (
                    match
                    and os.path.exists(installed)
                    and not same_file(
                        os.path.join(self.inst.src, "FHEM", name), installed
                    )
                ):
                    modules.append(match.group(1))
        else:
            modules = pr_fhem_modules(target["pr"])
        if not modules:
            return []
        print()
        warn("These FHEM modules are changed too: " + ", ".join(modules))
        if self.ctx["mode"] != "local":
            warn("FHEM doesn't run on this machine, test them on the FHEM machine")
            return []
        if ask(
            "Copy them into FHEM and reload them? They are restored after the test."
        ):
            return modules
        return []

    def install_fhem_modules(self, modules, state):
        if not modules:
            return
        os.makedirs(self.inst.backup_dir, exist_ok=True)
        state["fhem_modules"] = []
        for module in modules:
            dst = os.path.join(self.ctx["dir"], "FHEM", module + ".pm")
            backup = os.path.join(self.inst.backup_dir, module + ".pm")
            if os.path.exists(dst) and not os.path.exists(backup):
                shutil.copy2(dst, backup)
            state["fhem_modules"].append(module)
            write_json(self.inst.state_file, state)
            shutil.copy(os.path.join(self.inst.src, "FHEM", module + ".pm"), dst)
            self.fhem.cmd_or_ask(f"reload {module}")

    def restore_fhem_modules(self, state):
        modules = state.get("fhem_modules") or []
        if not modules:
            return
        info("Restoring the FHEM modules: " + ", ".join(modules))
        fhem = self.fhem or Fhem(
            self.ctx["dir"], self.args.telnet_port, self.args.fhem_url
        )
        if fhem.method is None:
            fhem.connect()
        for module in modules:
            dst = os.path.join(self.ctx["dir"], "FHEM", module + ".pm")
            backup = os.path.join(self.inst.backup_dir, module + ".pm")
            if os.path.exists(backup):
                shutil.copy2(backup, dst)
                os.unlink(backup)
            else:
                # new module of the pull request
                remove(dst)
                warn(f"{module} is new, please run in FHEM: shutdown restart")
                continue
            fhem.cmd_or_ask(f"reload {module}")

    # the test fhempy

    def fhempy_args(self):
        if self.ctx["mode"] == "local":
            args = ["--local"]
        else:
            # same arguments as the service (e.g. --port)
            exec_start = (self.ctx["service"] or {}).get("ExecStart", "")
            match = re.search(r"argv\[\]=(.*?) ;", exec_start)
            args = match.group(1).split()[1:] if match else []
        if self.args.debug:
            args.append("--debug")
        return args

    def run_test_fhempy(self, target):
        log_name = f"pr-{target['pr']}" if target["pr"] else "master"
        log_path = os.path.join(
            self.inst.base, f"{log_name}-{time.strftime('%Y%m%d-%H%M%S')}.log"
        )
        env = dict(os.environ, **self.inst.index_env())
        env["VIRTUAL_ENV"] = self.inst.venv
        env["PATH"] = (
            os.path.join(self.inst.venv, "bin") + os.pathsep + env.get("PATH", "")
        )
        env["PYTHONUNBUFFERED"] = "1"
        if self.inst.uv:
            env["FHEMPY_UV"] = self.inst.uv
        cmd = [self.inst.python, "-c", RUN_FHEMPY] + self.fhempy_args()
        print()
        info(f"Starting {target['name']}")
        info(f"Log: {log_path}")
        info(
            "Check FHEM now. Press Ctrl+C to stop the test and start the normal fhempy."
        )
        print()
        counts = dict.fromkeys(LOG_PATTERNS, 0)
        proc = subprocess.Popen(
            cmd,
            cwd=self.ctx["dir"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            # Ctrl+C is for this script, fhempy gets SIGTERM afterwards
            start_new_session=True,
        )
        reader = threading.Thread(
            target=self._read_output, args=(proc, log_path, counts), daemon=True
        )
        reader.start()
        if self.fhem and self.fhem.method:
            threading.Thread(
                target=self._report_fhem_state, args=(proc,), daemon=True
            ).start()
        try:
            proc.wait()
            warn(f"fhempy exited with code {proc.returncode}")
        except KeyboardInterrupt:
            print()
            info("Stopping the test fhempy")
        finally:
            stop_process(proc)
            reader.join(5)
        return log_path, counts

    @staticmethod
    def _read_output(proc, log_path, counts):
        with open(log_path, "w", encoding="utf-8") as log:
            for line in proc.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                log.write(line)
                log.flush()
                for key, pattern in LOG_PATTERNS.items():
                    if pattern.search(line):
                        counts[key] += 1

    def _report_fhem_state(self, proc):
        """Prints the connection and device states once FHEM had time to connect."""
        for _ in range(60):
            if proc.poll() is not None:
                return
            time.sleep(1)
        ios = self.fhem.devices("TYPE=BindingsIo") or []
        devices = self.fhem.devices("TYPE=fhempy") or []
        lines = [f"{d['Name']}: {d['Internals'].get('STATE')}" for d in ios]
        bad = [
            f"{d['Name']}: {d['Internals'].get('STATE')}"
            for d in devices
            if re.search(
                r"error|fail|offline|disconnect|exception",
                str(d["Internals"].get("STATE")),
                re.I,
            )
        ]
        lines.append(f"{len(devices)} fhempy devices, {len(bad)} with an error state")
        lines += bad
        info("FHEM status after 60 seconds:\n    " + "\n    ".join(lines))


def stop_process(proc):
    """Stops fhempy with SIGTERM like FHEM and systemd do."""
    for sig, timeout in ((signal.SIGTERM, 20), (signal.SIGKILL, None)):
        if proc.poll() is not None:
            return
        proc.send_signal(sig)
        try:
            proc.wait(timeout)
        except subprocess.TimeoutExpired:
            pass


def same_file(a, b):
    try:
        with open(a, "rb") as fa, open(b, "rb") as fb:
            return fa.read() == fb.read()
    except OSError:
        return False


def on_hangup(signum, frame):
    # SSH connection lost: unwind so the normal fhempy is started again
    raise KeyboardInterrupt


def parse_args():
    parser = argparse.ArgumentParser(
        description="Test a fhempy pull request instead of the installed fhempy."
    )
    parser.add_argument("--pr", help="pull request number or master")
    parser.add_argument("--dir", help="FHEM directory (local) or fhempy home (peer)")
    parser.add_argument("--mode", choices=["local", "peer"], help="override detection")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="fhempy port")
    parser.add_argument("--telnet-port", type=int, help="FHEM telnet port")
    parser.add_argument(
        "--fhem-url", help="FHEMWEB URL, e.g. http://user:pass@127.0.0.1:8083/fhem"
    )
    parser.add_argument(
        "--debug", action="store_true", help="start fhempy with --debug"
    )
    parser.add_argument("--fresh", action="store_true", help="recreate the test venv")
    parser.add_argument(
        "--restore", action="store_true", help="start the normal fhempy again"
    )
    parser.add_argument(
        "--clean", action="store_true", help="remove the test installation"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    ctx = detect(args)
    switch_user(ctx["user"])
    info(f"fhempy installation: {ctx['dir']} ({ctx['mode']}, user {ctx['user']})")
    runner = Runner(ctx, args)
    inst = runner.inst

    state = read_json(inst.state_file)
    if state:
        warn("The previous test didn't finish, starting the normal fhempy first")
        runner.start_normal(state)
    if args.restore:
        if not state:
            info("Nothing to restore")
        return
    if args.clean:
        shutil.rmtree(inst.base, ignore_errors=True)
        info(f"Removed {inst.base}")
        return

    target = choose_target(args.pr)
    inst.install(target, args.fresh)
    info(f"Installed: {inst.fhempy_version()} from {target['sha'][:10]}")

    modules = runner.select_fhem_modules(target)
    state = {"mode": ctx["mode"], "target": target["name"]}
    signal.signal(signal.SIGHUP, on_hangup)
    signal.signal(signal.SIGTERM, on_hangup)
    try:
        runner.stop_normal(state)
        runner.install_fhem_modules(modules, state)
        log_path, counts = runner.run_test_fhempy(target)
    except KeyboardInterrupt:
        log_path, counts = None, None
    finally:
        # Ctrl+C during the restore must not leave fhempy stopped
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        runner.start_normal(state)

    if counts is not None:
        print()
        info(f"Summary for {target['name']}")
        for key, count in counts.items():
            print(f"    {key}: {count}")
        print(f"    log: {log_path}")


if __name__ == "__main__":
    try:
        main()
    except TestError as err:
        warn(f"ERROR: {err}")
        sys.exit(1)
