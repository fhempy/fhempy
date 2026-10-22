#!/bin/bash

# Installs fhempy on a remote peer and runs it as systemd service:
# curl -fsSL https://raw.githubusercontent.com/fhempy/fhempy/master/install_systemd_fhempy.sh | sudo bash
#
# The installer itself is part of the fhempy package, FHEM uses the same one
# for "set fhempy_local installPeer <host> <user> <password>".

INSTALLER_URL=https://raw.githubusercontent.com/fhempy/fhempy/master/FHEM/bindings/python/fhempy/lib/core/peer_installer/install_peer.sh

installer=$(mktemp) || exit 1
trap 'rm -f "$installer"' EXIT
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$INSTALLER_URL" -o "$installer"
else
  wget -qO "$installer" "$INSTALLER_URL"
fi || { echo "Downloading $INSTALLER_URL failed"; exit 1; }

bash "$installer" "$@" </dev/null
