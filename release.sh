#!/bin/bash

# .env file required with
# GH_TOKEN=...
# PYPI_TOKEN=...
export $(egrep -v '^#' .env | xargs)

# checkout master
git checkout -q master

# merge development branch
git merge development -m "Merge branch 'development'"

# update version / commit / push / release and pypi upload
semantic-release --patch -D version_variable=FHEM/bindings/python/fhempy/lib/version.py:__version__ publish
