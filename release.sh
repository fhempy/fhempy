#!/bin/bash

# .env file required with
# GH_TOKEN=...
# PYPI_TOKEN=...
export $(egrep -v '^#' .env | xargs)

# stash current changes
git stash --include-untracked

# checkout master
git checkout -q master

# merge development branch
git merge development -m "Merge branch 'development'"

# touch to update timestamp
touch FHEM/10_BindingsIo.pm
# update controls to force update
perl prepare_update.pl > controls_pythonbinding.txt
git commit -m "chore: update controls" controls_pythonbinding.txt

# update version / commit / push / create release / pypi upload
semantic-release --patch -D build_command="python3 setup.py sdist bdist_wheel" -D version_variable=FHEM/bindings/python/fhempy/lib/version.py:__version__ publish

# checkout development
git checkout -q development

# apply stash
git stash apply
