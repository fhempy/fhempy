# lot of parts copied from HomeAssistant, many thanks!

import asyncio
import concurrent
import configparser
import functools
import inspect
import json
import logging
import os
import re
import shutil
import sys
from importlib.metadata import PackageNotFoundError, distribution, version
from pathlib import Path
from subprocess import PIPE, Popen, SubprocessError, run
from urllib.parse import urlparse

from packaging.requirements import InvalidRequirement, Requirement

from fhempy.lib import utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

pip_lock = asyncio.Lock()

if sys.version_info[:2] >= (3, 8):
    from importlib.metadata import (  # pylint: disable=no-name-in-module,import-error
        PackageNotFoundError,
        version,
    )
else:
    from importlib_metadata import (  # pylint: disable=import-error
        PackageNotFoundError,
        version,
    )


def is_virtual_env() -> bool:
    """Return if we run in a virtual environment."""
    # Check supports venv && virtualenv
    return getattr(sys, "base_prefix", sys.prefix) != sys.prefix or hasattr(
        sys, "real_prefix"
    )


def is_container_env():
    if Path("/.dockerenv").exists():
        """Return True if we run in a docker env."""
        container = True
    elif Path("/var/run/secrets/kubernetes.io").exists():
        """Return True if we run in a Kubernetes env."""
        container = True
    else:
        container = False
    return container


def pip_kwargs(config_dir):
    """Return keyword arguments for PIP install."""
    is_container = is_container_env()
    kwargs = {
        # "constraints": os.path.join(os.path.dirname(__file__), CONSTRAINT_FILE),
        "no_cache_dir": is_container,
    }
    if "WHEELS_LINKS" in os.environ:
        kwargs["find_links"] = os.environ["WHEELS_LINKS"]
    if not (config_dir is None or is_virtual_env()) and not is_container:
        kwargs["target"] = os.path.join(config_dir, "deps")
    return kwargs


def find_uv():
    """Return the uv binary to install packages with or None to use pip.

    uv is only used within a virtual environment. bin/fhempy sets FHEMPY_UV,
    remote peers find uv next to their venv (.fhempy/bin/uv) or in PATH.
    Set FHEMPY_NO_UV to always use pip.
    """
    if os.environ.get("FHEMPY_NO_UV") or not is_virtual_env():
        return None
    candidates = [
        os.environ.get("FHEMPY_UV"),
        os.path.join(os.path.dirname(sys.prefix), "bin", "uv"),
        shutil.which("uv"),
    ]
    for uv in candidates:
        if uv and os.path.isfile(uv) and os.access(uv, os.X_OK):
            return uv
    return None


def pip_config_indexes():
    """Return (index_url, extra_index_urls) from the pip configuration.

    uv doesn't read pip.conf, but e.g. Raspberry Pi OS configures piwheels there.
    """
    index_url = os.environ.get("PIP_INDEX_URL")
    extra_urls = os.environ.get("PIP_EXTRA_INDEX_URL", "").split()
    config_files = [
        "/etc/pip.conf",
        os.path.expanduser("~/.pip/pip.conf"),
        os.path.expanduser("~/.config/pip/pip.conf"),
        os.path.join(sys.prefix, "pip.conf"),
    ]
    if os.environ.get("PIP_CONFIG_FILE"):
        config_files.append(os.environ["PIP_CONFIG_FILE"])
    for config_file in config_files:
        config = configparser.ConfigParser()
        try:
            config.read(config_file)
        except configparser.Error:
            continue
        for section in ("global", "install"):
            if not config.has_section(section):
                continue
            if index_url is None and config.has_option(section, "index-url"):
                index_url = config.get(section, "index-url").strip() or None
            if config.has_option(section, "extra-index-url"):
                extra_urls += config.get(section, "extra-index-url").split()
    return index_url, list(dict.fromkeys(extra_urls))


def pip_args(package, upgrade, constraints, find_links, no_cache_dir):
    """Return the pip command to install package."""
    args = [sys.executable, "-m", "pip", "install", "--quiet", package]
    if no_cache_dir:
        args.append("--no-cache-dir")
    if upgrade:
        args.append("--upgrade")
    if constraints is not None:
        args += ["--constraint", constraints]
    if find_links is not None:
        args += ["--find-links", find_links, "--prefer-binary"]
    return args


SYSTEM_PYTHON = "/usr/bin/python3"


@functools.lru_cache(maxsize=None)
def system_python_version():
    """Return (major, minor) of the system Python or None if it doesn't run."""
    try:
        result = run(
            [SYSTEM_PYTHON, "-c", "import sys; print(*sys.version_info[:2])"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return tuple(int(v) for v in result.stdout.split())
    except (OSError, ValueError, SubprocessError):
        return None


def piwheels_compatible():
    """Return if piwheels wheels fit to the running Python.

    piwheels builds the wheels for one Python version on the Raspberry Pi OS
    release which ships it (cp311 on Bookworm, cp313 on Trixie). If fhempy runs
    with another Python (e.g. Python 3.13 from uv on Bookworm), those wheels were
    built for another release and might need a newer glibc, so skip piwheels.
    """
    return system_python_version() == tuple(sys.version_info[:2])


def usable_indexes():
    """Return (index_url, extra_index_urls, piwheels_skipped) from pip config."""
    index_url, extra_urls = pip_config_indexes()
    if piwheels_compatible():
        return index_url, extra_urls, False
    usable_extra_urls = [url for url in extra_urls if "piwheels" not in url]
    skipped = len(usable_extra_urls) != len(extra_urls)
    if index_url and "piwheels" in index_url:
        index_url = None
        skipped = True
    return index_url, usable_extra_urls, skipped


def index_args(index_url, extra_urls):
    """Return pip/uv arguments for the given indexes."""
    args = ["--index-url", index_url] if index_url else []
    for url in extra_urls:
        args += ["--extra-index-url", url]
    return args


def pip_index_args(env):
    """Return pip index arguments, adjusts env so that pip skips piwheels if needed."""
    index_url, extra_urls, skipped = usable_indexes()
    if not skipped:
        return []
    # pip reads piwheels from pip.conf, ignore the config files and pass the rest
    env["PIP_CONFIG_FILE"] = os.devnull
    env.pop("PIP_INDEX_URL", None)
    env.pop("PIP_EXTRA_INDEX_URL", None)
    return index_args(index_url, extra_urls)


def uv_index_args():
    """Return the index arguments for uv, taken from the pip configuration."""
    uv_index_vars = (
        "UV_INDEX_URL",
        "UV_DEFAULT_INDEX",
        "UV_INDEX",
        "UV_EXTRA_INDEX_URL",
    )
    if any(os.environ.get(var) for var in uv_index_vars):
        # set by bin/fhempy or the user, uv reads them itself
        return []
    index_url, extra_urls, _ = usable_indexes()
    args = index_args(index_url, extra_urls)
    if extra_urls:
        # pick the best version of all indexes like pip does
        args += ["--index-strategy", "unsafe-best-match"]
    return args


def install_args(package, upgrade, constraints, find_links, no_cache_dir, use_uv=True):
    """Return the command to install package, with uv if available, else pip."""
    uv = find_uv() if use_uv else None
    if uv is None:
        return pip_args(package, upgrade, constraints, find_links, no_cache_dir)

    args = [uv, "pip", "install", "--python", sys.executable, "--quiet", package]
    if no_cache_dir:
        args.append("--no-cache")
    if upgrade:
        # like pip --upgrade: only upgrade the package itself, not all dependencies
        name = re.match(r"[A-Za-z0-9._-]+", package)
        if name:
            args += ["--upgrade-package", name.group(0)]
    if constraints is not None:
        args += ["--constraint", constraints]
    if find_links is not None:
        args += ["--find-links", find_links]
    return args + uv_index_args()


def check_dependencies(module):
    """Checks the manifest of a specific module and check installation
    of dependencies
    """
    try:
        fhempy_root = utils.get_fhempy_root()
        with open(fhempy_root + "/" + module + "/manifest.json", "r") as f:
            manifest = json.load(f)

            if "requirements" in manifest:
                for req in manifest["requirements"]:
                    logger.debug("Check requirement: " + req)
                    if is_installed(req) is False:
                        logger.debug("  NOK")
                        return False
                    else:
                        logger.debug("  OK")
    except FileNotFoundError:
        logger.error("manifest.json not found!")

    return True


async def force_update_package(package):
    kwargs = pip_kwargs(None)
    ret = False
    async with pip_lock:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            ret = await asyncio.get_event_loop().run_in_executor(
                pool, functools.partial(install_package, package, **kwargs)
            )
    return ret


async def check_and_install_dependencies(module):
    """Checks the manifest of a specific module and starts installation
    of dependencies
    """
    try:
        async with pip_lock:
            kwargs = pip_kwargs(None)
            from fhempy import lib

            initfile = inspect.getfile(lib)
            fhempy_root = os.path.dirname(initfile)
            with open(fhempy_root + "/" + module + "/manifest.json", "r") as f:
                manifest = json.load(f)

                if "requirements" in manifest:
                    for req in manifest["requirements"]:
                        if is_installed(req) is False:
                            inst_tries = 0
                            while inst_tries < 3:
                                with concurrent.futures.ThreadPoolExecutor() as pool:
                                    ret = (
                                        await asyncio.get_event_loop().run_in_executor(
                                            pool,
                                            functools.partial(
                                                install_package, req, **kwargs
                                            ),
                                        )
                                    )
                                if ret:
                                    break
                                inst_tries += 1
    except FileNotFoundError:
        pass

    return


def is_installed(package: str) -> bool:
    """Check if a package is installed and will be loaded when we import it.
    Returns True when the requirement is met.
    Returns False when the package is not installed or doesn't meet req.
    """
    try:
        distribution(package)
        return True
    except (IndexError, PackageNotFoundError):
        try:
            req = Requirement(package)
        except InvalidRequirement:
            # This is a zip file. We no longer use this in Home Assistant,
            # leaving it in for custom components.
            req = Requirement(urlparse(package).fragment)

    try:
        installed_version = version(req.name)
        # This will happen when an install failed or
        # was aborted while in progress see
        # https://github.com/home-assistant/core/issues/47699
        if installed_version is None:
            logger.error(  # type: ignore[unreachable]
                "Installed version for %s resolved to None", req.name
            )
            return False
        return req.specifier.contains(installed_version, prereleases=True)
    except PackageNotFoundError:
        return False


def install_package(
    package: str,
    upgrade: bool = True,
    target: [str] = None,
    constraints: [str] = None,
    find_links: [str] = None,
    no_cache_dir: [bool] = False,
) -> bool:
    """Install a package on PyPi. Accepts pip compatible package strings.
    Return boolean if install successful.
    """
    # Not using 'import pip; pip.main([])' because it breaks the logger
    logger.info("Attempting install of %s", package)
    env = os.environ.copy()
    # uv is only used within a virtual environment, target is only used outside of it
    args = install_args(package, upgrade, constraints, find_links, no_cache_dir)
    if args[0] == sys.executable and is_virtual_env():
        args += pip_index_args(env)
    if target:
        assert not is_virtual_env()
        # This only works if not running in venv
        args += ["--user"]
        env["PYTHONUSERBASE"] = os.path.abspath(target)
        if sys.platform != "win32":
            # Workaround for incompatible prefix setting
            # See http://stackoverflow.com/a/4495175
            args += ["--prefix="]
    process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)
    _, stderr = process.communicate()
    if process.returncode != 0 and not target and args[0] != sys.executable:
        logger.warning(
            "Unable to install package %s with uv, trying pip: %s",
            package,
            stderr.decode("utf-8").lstrip().strip(),
        )
        args = install_args(
            package, upgrade, constraints, find_links, no_cache_dir, use_uv=False
        )
        if is_virtual_env():
            args += pip_index_args(env)
        process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)
        _, stderr = process.communicate()
    if process.returncode != 0:
        logger.error(
            "Unable to install package %s: %s",
            package,
            stderr.decode("utf-8").lstrip().strip(),
        )
        return False

    logger.info("Successfully installed " + package + " update!")
    return True
