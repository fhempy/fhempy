#!/bin/bash

PYTHON_VERSION="3.9.1"

sudo apt update && sudo apt upgrade
sudo apt install libffi-dev libbz2-dev liblzma-dev libsqlite3-dev libncurses5-dev libgdbm-dev zlib1g-dev libreadline-dev libssl-dev tk-dev build-essential libncursesw5-dev libc6-dev openssl git

wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz
tar xf Python-$PYTHON_VERSION.tar.xz
cd Python-$PYTHON_VERSION

./configure
make -j -l 4

sudo make altinstall

rm -f Python-$PYTHON_VERSION.tar.xz
sudo rm -rf Python-$PYTHON_VERSION
