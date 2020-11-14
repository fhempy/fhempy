#!/usr/bin/env python3

import sys
import os
import logging
from subprocess import Popen, PIPE

logging.basicConfig(format='%(asctime)s - %(levelname)-8s - %(name)s: %(message)s', level=logging.INFO)

MIN_PYTHON_VERSION = (3,7,0)

if sys.version_info < MIN_PYTHON_VERSION:
  logging.getLogger(__name__).error(f"FHEM_PythonBinding requires Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}.{MIN_PYTHON_VERSION[2]}")
  logging.getLogger(__name__).error(f"You are running: {sys.version}")
  sys.exit(1)

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
      logging.getLogger(__name__).info(f"Successfully installed {package}")

    return True

try:
  import asyncio
except:
  install_package("asyncio")

try:
  import websockets
except:
  install_package("websockets")

try:
  import importlib
except:
  install_package("importlib_metadata")


import lib.fhem_pythonbinding as fpb

fpb.run()