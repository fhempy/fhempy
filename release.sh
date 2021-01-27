#!/bin/bash

# checkout master
git checkout -q master

# merge development branch
git merge development

# update version / commit / push
semantic-release -D version_variable=FHEM/bindings/python/fhempy/lib/version.py:__version__ publish
