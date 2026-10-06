#!/usr/bin/env python3

# This script is only installed by FHEM updates, it's NOT part of the fhempy package!

import configparser
import logging
import os
import re
import shutil
import sys
import time
from subprocess import PIPE, Popen

logging.basicConfig(
    format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s", level=logging.INFO
)

# 0x030703F0 = Python 3.7.3 releaselevel=final, serial=0
MIN_PYTHON_VERSION_HEX = 0x030703F0
MIN_PYTHON_VERSION_STR = "3.7.3"

if sys.hexversion < MIN_PYTHON_VERSION_HEX:
    logging.getLogger(__name__).error(
        "fhempy requires Python " + MIN_PYTHON_VERSION_STR
    )
    logging.getLogger(__name__).error(
        "You are running: " + sys.version.replace("\n", "")
    )
    time.sleep(60)
    logging.getLogger(__name__).error("Exiting now")
    sys.exit(1)

# Python 3 can start here
from pathlib import Path


def version_compare(v1, v2):
    # This will split both the versions by '.'
    arr1 = v1.split(".")
    arr2 = v2.split(".")
    n = len(arr1)
    m = len(arr2)

    # converts to integer from string
    arr1 = [int(i) for i in arr1]
    arr2 = [int(i) for i in arr2]

    # compares which list is bigger and fills
    # smaller list with zero (for unequal delimiters)
    if n > m:
        for i in range(m, n):
            arr2.append(0)
    else:
        if m > n:
            for i in range(n, m):
                arr1.append(0)

    # returns 1 if version 1 is bigger and -1 if
    # version 2 is bigger and 0 if equal
    for i in range(len(arr1)):
        if arr1[i] > arr2[i]:
            return 1
        else:
            if arr2[i] > arr1[i]:
                return -1
    return 0


def is_virtual_env():
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
    if not (config_dir is None or is_virtual_env()) and not is_docker:
        kwargs["target"] = os.path.join(config_dir, "deps")
    return kwargs


def find_uv():
    """Return the uv binary to install packages with or None to use pip."""
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


def uv_index_args():
    """Return the index arguments for uv, taken from the pip configuration."""
    if os.environ.get("UV_INDEX_URL") or os.environ.get("UV_DEFAULT_INDEX"):
        return []
    args = []
    index_url, extra_urls = pip_config_indexes()
    if index_url:
        args += ["--index-url", index_url]
    for url in extra_urls:
        args += ["--extra-index-url", url]
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


def install_package(
    package,
    upgrade=True,
    target=None,
    constraints=None,
    find_links=None,
    no_cache_dir=False,
):
    """Install a package on PyPi. Accepts pip compatible package strings.
    Return boolean if install successful.
    """
    # Not using 'import pip; pip.main([])' because it breaks the logger
    logging.getLogger(__name__).info("Attempting install of %s", package)
    env = os.environ.copy()
    args = install_args(package, upgrade, constraints, find_links, no_cache_dir)
    process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)
    _, stderr = process.communicate()
    if process.returncode != 0 and args[0] != sys.executable:
        logging.getLogger(__name__).warning(
            "Unable to install package %s with uv, trying pip: %s",
            package,
            stderr.decode("utf-8").lstrip().strip(),
        )
        args = install_args(
            package, upgrade, constraints, find_links, no_cache_dir, use_uv=False
        )
        process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)
        _, stderr = process.communicate()
    if process.returncode != 0:
        logging.getLogger(__name__).error(
            "Unable to install package %s: %s",
            package,
            stderr.decode("utf-8").lstrip().strip(),
        )
        return False
    else:
        logging.getLogger(__name__).info("Successfully installed " + package)

    return True


kwargs = pip_kwargs(None)

try:
    import fhempy.lib.fhem_pythonbinding as fpb

    if version_compare(fpb.version.__version__, "0.1.462") < 0:
        raise ImportError(
            f"fhempy version {fpb.version.__version__} too old, installing new one"
        )
except ImportError:
    logging.getLogger(__name__).exception("Failed to load fhempy")
    if install_package("fhempy>=0.1.462", **kwargs) is False:
        logging.getLogger(__name__).error("Failed to install fhempy, exit now...")
        time.sleep(60)
        sys.exit(1)
    else:
        try:
            import fhempy.lib.fhem_pythonbinding as fpb
        except Exception:
            logging.getLogger(__name__).error("Failed to import fhempy, exit now...")
            time.sleep(60)
            sys.exit(1)
except Exception:
    logging.getLogger(__name__).exception("Failed to load fhempy")
    sys.exit(1)

fpb.run()
