#!/bin/bash

source .env

# checkout master
git checkout -q master

# merge development branch
git merge development -m "Merge branch 'development'"

# update version / commit / push
semantic-release -D version_variable=FHEM/bindings/python/fhempy/lib/version.py:__version__ publish
