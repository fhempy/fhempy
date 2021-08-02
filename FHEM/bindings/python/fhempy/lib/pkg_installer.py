# lot of parts copied from HomeAssistant, many thanks!

import asyncio
import concurrent
import functools
import inspect
import json
import logging
import os
import sys
from pathlib import Path
from subprocess import PIPE, Popen

import pkg_resources

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


def is_docker_env() -> bool:
    """Return True if we run in a docker env."""
    return Path("/.dockerenv").exists()


def pip_kwargs(config_dir):
    """Return keyword arguments for PIP install."""
    is_docker = is_docker_env()
    kwargs = {
        # "constraints": os.path.join(os.path.dirname(__file__), CONSTRAINT_FILE),
        "no_cache_dir": is_docker,
    }
    if "WHEELS_LINKS" in os.environ:
        kwargs["find_links"] = os.environ["WHEELS_LINKS"]
    if not (config_dir is None or is_virtual_env()) and not is_docker:
        kwargs["target"] = os.path.join(config_dir, "deps")
    return kwargs


def check_dependencies(module):
    """Checks the manifest of a specific module and check installation
    of dependencies
    """
    try:
        from fhempy import lib

        initfile = inspect.getfile(lib)
        fhempy_root = os.path.dirname(initfile)
        with open(fhempy_root + "/" + module + "/manifest.json", "r") as f:
            manifest = json.load(f)

            if "requirements" in manifest:
                for req in manifest["requirements"]:
                    logger.debug("Check requirement: " + req)
                    if is_installed(req) == False:
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
                        if is_installed(req) == False:
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
        req = pkg_resources.Requirement.parse(package)
    except ValueError:
        raise

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

    logger.info("Successfully installed fhempy update!")
    return True
