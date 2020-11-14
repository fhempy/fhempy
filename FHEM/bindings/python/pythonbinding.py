#!/usr/bin/env python3

import sys
import lib.fhem_pythonbinding as fpb

MIN_PYTHON_VERSION = (3,7,0)

if sys.version_info < MIN_PYTHON_VERSION:
  print(f"FHEM_PythonBinding requires Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}.{MIN_PYTHON_VERSION[2]}")
  print(f"You are running: {sys.version}")
  sys.exit(1)

fpb.run()

