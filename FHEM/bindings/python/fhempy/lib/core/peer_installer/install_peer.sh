#!/bin/bash

# Installs fhempy on a remote peer (e.g. a Raspberry Pi close to your Bluetooth
# devices) and runs it as systemd service. FHEM finds the peer on its own.
#
# On the peer:
#   curl -fsSL https://raw.githubusercontent.com/fhempy/fhempy/master/install_systemd_fhempy.sh | sudo bash
# or from FHEM, without logging in to the peer:
#   set fhempy_local installPeer <host> <user> <password>
#
# The script can be run again at any time, e.g. to repair an installation.
# Lines starting with "fhempy-install:" report the progress to FHEM.
#
# Environment:
#   FHEMPY_USER                  user running fhempy (default: the user calling sudo, otherwise fhempy)
#   FHEMPY_SKIP_SYSTEM_PACKAGES  1 skips the apt packages for the Bluetooth modules

STEPS=5

step() {
  echo "fhempy-install: $1/$STEPS $2"
}

fail() {
  echo "fhempy-install: failed: $1"
  exit 1
}

# everything runs in main, so that commands can't read the rest of the
# script from stdin when it's piped into bash (curl ... | sudo bash)
main() {
if [[ "$(id -u)" -ne 0 ]]; then
  echo "Please run this script with sudo:"
  echo "curl -fsSL https://raw.githubusercontent.com/fhempy/fhempy/master/install_systemd_fhempy.sh | sudo bash"
  exit 1
fi

if [[ -z "$FHEMPY_USER" ]]; then
  if [[ -n "$SUDO_USER" ]] && [[ "$SUDO_USER" != "root" ]]; then
    FHEMPY_USER=$SUDO_USER
  else
    FHEMPY_USER=fhempy
  fi
fi

if ! id "$FHEMPY_USER" >/dev/null 2>&1; then
  echo -n "Creating user $FHEMPY_USER..."
  useradd --system --create-home --shell /usr/sbin/nologin "$FHEMPY_USER" || fail "creating user $FHEMPY_USER failed"
  echo "OK"
fi
FHEMPY_HOME=$(getent passwd "$FHEMPY_USER" | cut -d: -f6)
if [[ -z "$FHEMPY_HOME" ]] || [[ ! -d "$FHEMPY_HOME" ]]; then
  fail "home directory of user $FHEMPY_USER not found"
fi

# all packages at once, so that no module needs to install anything later
# (only the Bluetooth modules and piclock need them, fhempy itself doesn't)
step 1 "installing system packages"
if [[ "$FHEMPY_SKIP_SYSTEM_PACKAGES" != "1" ]] && command -v apt-get >/dev/null 2>&1; then
  packages="python3 python3-venv python3-dev curl ca-certificates bluez libbluetooth-dev libglib2.0-dev libdbus-1-dev build-essential autoconf libffi-dev libssl-dev libjpeg-dev zlib1g-dev git"
  # PyGObject (eq3bt pairing) builds against libgirepository-2.0 on Debian 13 Trixie
  if apt-cache show libgirepository-2.0-dev >/dev/null 2>&1; then
    packages="$packages libgirepository-2.0-dev libcairo2-dev"
  else
    packages="$packages libgirepository1.0-dev libcairo2-dev"
  fi
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq || echo "apt-get update failed, trying to install the packages anyway"
  # shellcheck disable=SC2086
  if ! apt-get install -y -qq $packages >/dev/null; then
    echo "Some system packages couldn't be installed, Bluetooth modules might not work."
  fi
else
  echo "Skipped, please install python3 and curl yourself if they are missing."
fi
command -v python3 >/dev/null 2>&1 || command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1 \
  || fail "neither python3 nor curl/wget found"

step 2 "installing Python environment"
sudo -u "$FHEMPY_USER" -H bash <<'USEREOF' || fail "creating the Python environment failed, see output above"
cd "$HOME"
FHEMPY_DIR="$HOME/.fhempy"
FHEMPY_VENV="$FHEMPY_DIR/fhempy_venv"
UV="$FHEMPY_DIR/bin/uv"
# Python version uv installs for fhempy if the system Python is older
UV_PYTHON_VERSION=3.13
UV_INSTALLER_URL=https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh
export UV_PYTHON_INSTALL_DIR="$FHEMPY_DIR/python"

mkdir -p "$FHEMPY_DIR"

if [[ ! -x "$UV" ]]; then
  echo -n "Installing uv..."
  if command -v curl >/dev/null 2>&1; then
    curl --proto "=https" --tlsv1.2 -LsSf "$UV_INSTALLER_URL" | env UV_UNMANAGED_INSTALL="$FHEMPY_DIR/bin" sh >/dev/null 2>&1
  else
    wget --https-only -qO- "$UV_INSTALLER_URL" | env UV_UNMANAGED_INSTALL="$FHEMPY_DIR/bin" sh >/dev/null 2>&1
  fi
  if [[ -x "$UV" ]]; then echo "OK"; else echo "FAILED, using pip instead"; fi
fi

if [[ -x "$UV" ]]; then
  echo -n "Creating virtual environment with uv..."
  if python3 -c 'import sys; sys.exit(sys.version_info < (3, 13))' 2>/dev/null; then
    "$UV" venv --quiet --seed --allow-existing --python "$(command -v python3)" "$FHEMPY_VENV" || exit 1
  else
    "$UV" venv --quiet --seed --allow-existing --python "$UV_PYTHON_VERSION" "$FHEMPY_VENV" || exit 1
  fi
else
  echo -n "Creating virtual environment..."
  python3 -m venv "$FHEMPY_VENV" || exit 1
fi
echo "OK"
USEREOF

step 3 "installing fhempy"
sudo -u "$FHEMPY_USER" -H bash <<'USEREOF' || fail "installing fhempy failed, see output above"
cd "$HOME"
FHEMPY_DIR="$HOME/.fhempy"
FHEMPY_VENV="$FHEMPY_DIR/fhempy_venv"
UV="$FHEMPY_DIR/bin/uv"
export UV_PYTHON_INSTALL_DIR="$FHEMPY_DIR/python"

echo -n "Installing fhempy..."
if [[ -x "$UV" ]]; then
  # uv doesn't read pip.conf, pass e.g. piwheels on Raspberry Pi OS
  # piwheels wheels are built for the system Python of the OS release only
  SKIP_PIWHEELS=
  if [[ "$("$FHEMPY_VENV/bin/python" -c 'import sys; print(sys.version_info[:2])')" != "$(python3 -c 'import sys; print(sys.version_info[:2])' 2>/dev/null)" ]]; then
    SKIP_PIWHEELS=1
  fi
  index_args=()
  for url in $(sed -n 's/^[[:space:]]*extra-index-url[[:space:]]*=[[:space:]]*//p' /etc/pip.conf 2>/dev/null); do
    if [[ -n "$SKIP_PIWHEELS" ]] && [[ "$url" == *piwheels* ]]; then
      continue
    fi
    index_args+=(--extra-index-url "$url")
  done
  if [[ ${#index_args[@]} -gt 0 ]]; then
    index_args+=(--index-strategy unsafe-best-match)
  fi
  "$UV" pip install --quiet --python "$FHEMPY_VENV/bin/python" "${index_args[@]}" --upgrade-package fhempy fhempy || exit 1
else
  "$FHEMPY_VENV/bin/pip" install --quiet --upgrade fhempy > /dev/null || exit 1
fi
echo "OK"
USEREOF

step 4 "setting up the fhempy service"
groups=""
for group in bluetooth gpio; do
  getent group "$group" >/dev/null 2>&1 && groups="$groups $group"
done
groups=${groups# }

# CAP_NET_ADMIN/CAP_NET_RAW allow the Bluetooth auto recovery to reset the adapter
# and the BLE modules to scan without root
cat > /etc/systemd/system/fhempy.service <<SERVICEEOF || fail "writing /etc/systemd/system/fhempy.service failed"
# Source: https://github.com/fhempy/fhempy

[Unit]
Description=fhempy
Wants=network-online.target
After=network-online.target bluetooth.target

[Service]
User=$FHEMPY_USER
Group=dialout
SupplementaryGroups=$groups
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_RAW
WorkingDirectory=$FHEMPY_HOME/
ExecStart=$FHEMPY_HOME/.fhempy/fhempy_venv/bin/fhempy
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

# the Bluetooth auto recovery may restart bluetoothd as last resort
SYSTEMCTL=$(command -v systemctl)
if [[ -n "$SYSTEMCTL" ]] && [[ -d /etc/sudoers.d ]]; then
  sudoers_tmp=$(mktemp)
  echo "$FHEMPY_USER ALL=NOPASSWD: $SYSTEMCTL restart bluetooth" > "$sudoers_tmp"
  if visudo -c -f "$sudoers_tmp" >/dev/null 2>&1; then
    install -m 0440 "$sudoers_tmp" /etc/sudoers.d/fhempy-bluetooth
  fi
  rm -f "$sudoers_tmp"
fi

systemctl daemon-reload || fail "systemctl daemon-reload failed"
systemctl enable fhempy >/dev/null 2>&1 || fail "enabling the fhempy service failed"

step 5 "starting fhempy"
systemctl restart fhempy || fail "starting fhempy failed, see: sudo journalctl -u fhempy"

# the first start can take a while on a Raspberry Pi
started=0
for _ in $(seq 1 120); do
  if (exec 3<>/dev/tcp/127.0.0.1/15733) 2>/dev/null; then
    started=1
    break
  fi
  sleep 1
done
if [[ "$started" -ne 1 ]]; then
  fail "fhempy didn't start within 2 minutes, see: sudo journalctl -u fhempy"
fi

IP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo ""
echo "fhempy is running on $(hostname) (${IP:-unknown IP}), port 15733."
echo "FHEM finds this peer on its own and creates the device fhempy_peer_${IP//./_}."
echo "If it doesn't show up, define it in FHEM: define fhempy_peer_${IP//./_} BindingsIo ${IP:-<IP>}:15733 fhempy"
echo "fhempy-install: done ${IP}"
}

main "$@" </dev/null
exit $?
