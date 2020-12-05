#!/bin/bash

wget https://raw.githubusercontent.com/dominikkarall/fhempy/master/fhempy.service -O /tmp/fhempy.service
cp /tmp/fhempy.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable fhempy
systemctl start fhempy

