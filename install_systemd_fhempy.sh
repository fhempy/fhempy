#!/bin/bash

wget https://raw.githubusercontent.com/dominikkarall/fhem_pythonbinding/master/fhempy.service -O /tmp/fhempy.service
cp /tmp/fhempy.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable fhempy
systemctl start fhempy

