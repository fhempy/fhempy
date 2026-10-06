#!/bin/bash

# Installs fhempy on a remote peer and runs it as systemd service
# curl -sL https://raw.githubusercontent.com/fhempy/fhempy/master/install_systemd_fhempy.sh | sudo -E bash -

if [ -z "$SUDO_USER" ] || [ "$SUDO_USER" == "root" ]; then
  echo "Please run this script with sudo as the user which should run fhempy (e.g. pi)"
  exit 1
fi

FHEMPY_USER=$SUDO_USER
FHEMPY_HOME=$(getent passwd "$FHEMPY_USER" | cut -d: -f6)

sudo -u "$FHEMPY_USER" -H bash <<'USEREOF'
cd "$HOME"
FHEMPY_DIR="$HOME/.fhempy"
FHEMPY_VENV="$FHEMPY_DIR/fhempy_venv"
UV="$FHEMPY_DIR/bin/uv"
# Python version uv installs for fhempy if the system Python is older
UV_PYTHON_VERSION=3.13
UV_INSTALLER_URL=https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh
export UV_PYTHON_INSTALL_DIR="$FHEMPY_DIR/python"

echo -n "Creating .fhempy directory in $HOME..."
mkdir -p "$FHEMPY_DIR"
echo "OK"

if [ ! -x "$UV" ]; then
  echo -n "Installing uv..."
  if command -v curl >/dev/null 2>&1; then
    curl -LsSf "$UV_INSTALLER_URL" | env UV_UNMANAGED_INSTALL="$FHEMPY_DIR/bin" sh >/dev/null 2>&1
  else
    wget -qO- "$UV_INSTALLER_URL" | env UV_UNMANAGED_INSTALL="$FHEMPY_DIR/bin" sh >/dev/null 2>&1
  fi
  if [ -x "$UV" ]; then echo "OK"; else echo "FAILED, using pip instead"; fi
fi

if [ -x "$UV" ]; then
  echo -n "Creating virtual environment with uv..."
  if python3 -c 'import sys; sys.exit(sys.version_info < (3, 13))' 2>/dev/null; then
    "$UV" venv --quiet --seed --allow-existing --python "$(command -v python3)" "$FHEMPY_VENV" || exit 1
  else
    # piwheels wheels are built for the system Python of the OS release, not for uv's Python
    SKIP_PIWHEELS=1
    "$UV" venv --quiet --seed --allow-existing --python "$UV_PYTHON_VERSION" "$FHEMPY_VENV" || exit 1
  fi
  echo "OK"

  echo -n "Install fhempy..."
  # uv doesn't read pip.conf, pass e.g. piwheels on Raspberry Pi OS
  index_args=()
  for url in $(sed -n 's/^[[:space:]]*extra-index-url[[:space:]]*=[[:space:]]*//p' /etc/pip.conf 2>/dev/null); do
    if [ -n "$SKIP_PIWHEELS" ] && [[ "$url" == *piwheels* ]]; then
      continue
    fi
    index_args+=(--extra-index-url "$url")
  done
  if [ ${#index_args[@]} -gt 0 ]; then
    index_args+=(--index-strategy unsafe-best-match)
  fi
  "$UV" pip install --quiet --python "$FHEMPY_VENV/bin/python" "${index_args[@]}" --upgrade-package fhempy fhempy || exit 1
  echo "OK"
else
  echo -n "Creating virtual environment..."
  python3 -m venv "$FHEMPY_VENV" || exit 1
  echo "OK"

  echo -n "Install fhempy..."
  "$FHEMPY_VENV/bin/pip" install --quiet --upgrade fhempy > /dev/null || exit 1
  echo "OK"
fi
USEREOF

if [ $? -ne 0 ]; then
  echo "FAILED"
  echo "fhempy installation failed, please check the output above."
  exit 1
fi

echo -n "Create fhempy.service file..."
cat > /etc/systemd/system/fhempy.service <<SERVICEEOF
# Source: https://github.com/fhempy/fhempy

[Unit]
Description=fhempy
Wants=network.target
After=network.target

[Service]
User=$FHEMPY_USER
Group=dialout
WorkingDirectory=$FHEMPY_HOME/
ExecStart=$FHEMPY_HOME/.fhempy/fhempy_venv/bin/fhempy
Restart=always

[Install]
WantedBy=multi-user.target
SERVICEEOF
echo "OK"

echo -n "Reload systemd..."
systemctl daemon-reload
echo "OK"

echo -n "Enable fhempy service..."
systemctl enable fhempy
echo "OK"

echo -n "Start fhempy service..."
systemctl restart fhempy
sleep 10
echo "OK"

echo ""
echo "Installation successfully finished, have fun with fhempy :-)"
echo ""

exit 0
