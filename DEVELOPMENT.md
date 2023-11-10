Very quick & dirty instructions on how to run fhempy within VS Code for development.

1. Install VS Code
2. Checkout https://github.org/fhempy/fhempy to $HOME/vscode-github
3. sudo apt install python3-venv python3 python3-pip python3-dev libffi-dev libssl-dev libjpeg-dev zlib1g-dev autoconf build-essential libglib2.0-dev libdbus-1-dev bluez libbluetooth-dev git libprotocol-websocket-perl
4. cd $HOME/vscode-github/fhempy
5. python3 -m venv fhempy-venv
6. source fhempy-venv/bin/activate
7. You can now run fhempy within VSCode. Go to Run & Debug and click the play symbol.

If you want to create your own module:
1. Copy helloworld directory to mymodule (mymodule is the name you define)
2. Rename hellworld.py to mymodule.py
3. Rename the class helloworld in mymodule.py to mymodule
4. Run fhempy in VS Code
5. Do define test_mymodule fhempy mymodule in FHEM to see if the new module was found
