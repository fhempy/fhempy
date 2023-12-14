#!/bin/bash

cd $HOME
echo -n "Creating .fhempy directory in $HOME..."
mkdir .fhempy
echo "OK"

echo -n "Creating virtual environment..."
python3 -m venv .fhempy/fhempy_venv
echo "OK"

echo -n "Download fhempy.service file..."
wget https://raw.githubusercontent.com/fhempy/fhempy/master/fhempy.service -O /tmp/fhempy.service
echo "OK"

echo -n "Copy fhempy.service to /etc/systemd/system/..."
cp /tmp/fhempy.service /etc/systemd/system/
echo "OK"

echo -n "Reload systemd..."
systemctl daemon-reload
echo "OK"

echo -n "Enable fhempy service..."
systemctl enable fhempy
echo "OK"

echo -n "Start fhempy service..."
systemctl start fhempy
echo "OK"

exit 0
