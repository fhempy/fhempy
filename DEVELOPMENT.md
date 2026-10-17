Very quick & dirty instructions on how to run fhempy within VS Code for development.

1. Install VS Code
2. Checkout https://github.com/fhempy/fhempy to $HOME/vscode-github
3. sudo apt install python3-venv python3 python3-pip python3-dev libffi-dev libssl-dev libjpeg-dev zlib1g-dev autoconf build-essential libglib2.0-dev libdbus-1-dev bluez libbluetooth-dev git libprotocol-websocket-perl libcpanel-json-xs-perl libjson-xs-perl
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

## Keep the event loop responsive

While fhempy runs synchronous code in the event loop, FHEM waits and is frozen.
Two checks catch this before a change is merged:

- `ruff check FHEM/bindings/python/fhempy` reports blocking calls (`time.sleep`,
  `requests`, `open`, `os.path`, `subprocess`) in async functions. Use
  `utils.run_blocking` for them. Mark an intended exception with `# noqa: ASYNC230`; older
  exceptions are listed in `pyproject.toml`.
- The mocked tests fail when a single loop step takes longer than 500 ms
  (`tests/mocked/conftest.py`). Tests that block on purpose use
  `@pytest.mark.allow_blocking`.

## Test a pull request on your system

`tools/pr-tester.py` runs fhempy from a pull request (or from master) instead of the
installed fhempy, e.g. on a Raspberry Pi. It works for fhempy started by FHEM
(fhempyServer, usually in /opt/fhem) and for fhempy running as systemd service on a peer.

```
curl -fsSLO https://raw.githubusercontent.com/fhempy/fhempy/master/tools/pr-tester.py
python3 pr-tester.py              # choose a pull request from the list
python3 pr-tester.py --pr 123     # or test pull request 123 directly
```

1. The pull request is installed into its own virtual environment
   `.fhempy/pr_test/venv`, the normal fhempy installation stays untouched.
2. The normal fhempy is stopped (`set fhempy_local stop` via telnet or FHEMWEB,
   `systemctl stop fhempy` on peers).
3. fhempy from the pull request runs in the foreground, its log is shown and saved in
   `.fhempy/pr_test/`. Check FHEM now.
4. Ctrl+C stops the test, starts the normal fhempy again and prints the number of
   errors, tracebacks and event loop blocks.

If the pull request changes FHEM modules (e.g. `10_BindingsIo.pm`), the script offers
to copy and reload them and restores the original files afterwards.
Run the script within tmux or screen when connected via SSH. If it was interrupted,
`python3 pr-tester.py --restore` starts the normal fhempy again,
`python3 pr-tester.py --clean` removes the test installation.
See `python3 pr-tester.py --help` for all options.
