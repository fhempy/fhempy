# lot of parts copied from HomeAssistant, many thanks!

import logging
import pkg_resources
import json
import sys
import os
import importlib
from subprocess import PIPE, Popen

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

def check_dependencies(module):
    """Checks the manifest of a specific module and check installation
    of dependencies
    """
    try:
        with open('FHEM/bindings/python/lib/' + module + '/manifest.json', 'r') as f:
            manifest = json.load(f)

            if "requirements" in manifest:
                for req in manifest["requirements"]:
                    logger.debug("Check requirement: " + req);
                    if is_installed(req) == False:
                      logger.debug("  NOK")
                      return False
                    else:
                      logger.debug("  OK")
    except FileNotFoundError:
        pass

    return True

def check_and_install_dependencies(module):
    """Checks the manifest of a specific module and starts installation
    of dependencies
    """
    try:
        with open('FHEM/bindings/python/lib/' + module + '/manifest.json', 'r') as f:
            manifest = json.load(f)

            if "requirements" in manifest:
                for req in manifest["requirements"]:
                    if is_installed(req) == False:
                        inst_tries = 0
                        while inst_tries < 3:
                            if install_package(req):
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
        req = pkg_resources.Requirement.parse(package)
    except ValueError:
        # This is a zip file. We no longer use this in Home Assistant,
        # leaving it in for custom components.
        req = pkg_resources.Requirement.parse(urlparse(package).fragment)

    try:
        ret = version(req.project_name) in req
        return ret
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
    args = [sys.executable, "-m", "pip", "install", "--quiet", package]
    if no_cache_dir:
        args.append("--no-cache-dir")
    if upgrade:
        args.append("--upgrade")
    if constraints is not None:
        args += ["--constraint", constraints]
    if find_links is not None:
        args += ["--find-links", find_links, "--prefer-binary"]
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
    if process.returncode != 0:
        logger.error(
            "Unable to install package %s: %s",
            package,
            stderr.decode("utf-8").lstrip().strip(),
        )
        return False

    return True
