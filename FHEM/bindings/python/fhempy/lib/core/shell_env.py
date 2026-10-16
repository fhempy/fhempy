"""Environment for external programs like node/npm started by modules."""

import os
import subprocess

PATH_MARKER = "__FHEMPY_PATH__="


def interactive_shell_env():
    """Environment with the PATH of an interactive bash.

    node/npm/pnpm are often installed via nvm, which is set up in .bashrc
    and only runs in interactive shells. Instead of running every command
    with bash -i (prints job control warnings to the fhempy log), the PATH
    is read once and the commands run in a non-interactive bash.
    """
    env = os.environ.copy()
    try:
        out = subprocess.run(
            ["bash", "-i", "-c", f'printf "\\n{PATH_MARKER}%s\\n" "$PATH"'],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=30,
            check=False,
        ).stdout.decode(errors="replace")
    except Exception:
        return env
    for line in out.splitlines():
        if line.startswith(PATH_MARKER) and line[len(PATH_MARKER) :]:
            env["PATH"] = line[len(PATH_MARKER) :]
    return env
