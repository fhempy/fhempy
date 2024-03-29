#!/usr/bin/env python3

# This script is only installed by FHEM updates, it's NOT part of the fhempy package!

import logging
import os
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
    args = [sys.executable, "-m", "pip", "install", "--quiet", package]
    if no_cache_dir:
        args.append("--no-cache-dir")
    if upgrade:
        args.append("--upgrade")
    if constraints is not None:
        args += ["--constraint", constraints]
    if find_links is not None:
        args += ["--find-links", find_links, "--prefer-binary"]
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
