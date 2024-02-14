#!/bin/bash

sudo -u $SUDO_USER -s -- bash -c '
echo -n "Creating .fhempy directory in $HOME...";
mkdir .fhempy;
echo "OK";

echo -n "Creating virtual environment...";
python3 -m venv .fhempy/fhempy_venv;
echo "OK";

echo -n "Activate virtual environment...";
source .fhempy/fhempy_venv/bin/activate;
echo "OK";

echo -n "Install fhempy...";
pip3 install fhempy > /dev/null;
deactivate;
echo "OK";
'

echo -n "Download fhempy.service file..."
wget https://raw.githubusercontent.com/fhempy/fhempy/master/fhempy.service -O /tmp/fhempy.service > /dev/null
echo "OK"

echo -n "Move fhempy.service to /etc/systemd/system/..."
mv /tmp/fhempy.service /etc/systemd/system/
echo "OK"

echo -n "Reload systemd..."
systemctl daemon-reload
echo "OK"

echo -n "Enable fhempy service..."
systemctl enable fhempy
echo "OK"

echo -n "Start fhempy service..."
systemctl start fhempy
sleep 10
echo "OK"

echo ""
echo "Installation successfully finished, have fun with fhempy :-)"
echo ""

exit 0
