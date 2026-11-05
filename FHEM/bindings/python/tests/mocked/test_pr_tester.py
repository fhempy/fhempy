"""tools/pr-tester.py copies changed FHEM files for a test and restores them."""
import importlib.util
import json
import pathlib
from types import SimpleNamespace

import pytest

SCRIPT = pathlib.Path(__file__).parents[5] / "tools" / "pr-tester.py"


@pytest.fixture
def tester():
    spec = importlib.util.spec_from_file_location("pr_tester", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeFhem:
    method = "telnet"

    def __init__(self):
        self.commands = []

    def cmd_or_ask(self, cmd):
        self.commands.append(cmd)


def write(path, text, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(mode)


@pytest.fixture
def runner(tester, tmp_path):
    fhem_dir = tmp_path / "fhem"
    write(fhem_dir / "FHEM" / "98_update.pm", "fhem", 0o744)
    write(fhem_dir / "www" / "pgm2" / "fhemweb.js", "fhem", 0o744)
    write(fhem_dir / "FHEM" / "10_BindingsIo.pm", "old io", 0o744)
    write(fhem_dir / "www" / "fhempy" / "push.js", "old push", 0o744)
    runner = tester.Runner(
        {"dir": str(fhem_dir), "mode": "service", "user": "fhem"},
        SimpleNamespace(port=15733, telnet_port=None, yes=False),
    )
    src = pathlib.Path(runner.inst.src)
    write(src / "FHEM" / "10_BindingsIo.pm", "pr io", 0o600)
    write(src / "FHEM" / "10_newmod.pm", "pr new", 0o600)
    write(src / "www" / "fhempy" / "push.js", "pr push", 0o600)
    write(src / "www" / "fhempy" / "new.js", "pr new js", 0o600)
    runner.fhem = FakeFhem()
    runner.dir = fhem_dir
    return runner


def install(runner):
    state = {"mode": "service"}
    runner.install_fhem_modules(["10_BindingsIo", "10_newmod"], state)
    runner.install_www_files(["www/fhempy/push.js", "www/fhempy/new.js"], state)
    return state


def mode(path):
    return path.stat().st_mode & 0o777


def test_copied_files_keep_or_get_the_mode_of_fhem_files(runner):
    install(runner)
    fhem_dir = runner.dir
    assert (fhem_dir / "FHEM" / "10_BindingsIo.pm").read_text() == "pr io"
    assert mode(fhem_dir / "FHEM" / "10_BindingsIo.pm") == 0o744
    assert mode(fhem_dir / "FHEM" / "10_newmod.pm") == 0o744
    assert mode(fhem_dir / "www" / "fhempy" / "push.js") == 0o744
    assert mode(fhem_dir / "www" / "fhempy" / "new.js") == 0o744


def test_restore_twice_never_deletes_original_files(runner):
    install(runner)
    state = json.loads(pathlib.Path(runner.inst.state_file).read_text())
    assert sorted(state["new_files"]) == ["FHEM/10_newmod.pm", "www/fhempy/new.js"]

    runner.restore_fhem_modules(state)
    runner.restore_www_files(state)
    fhem_dir = runner.dir
    assert (fhem_dir / "FHEM" / "10_BindingsIo.pm").read_text() == "old io"
    assert mode(fhem_dir / "FHEM" / "10_BindingsIo.pm") == 0o744
    assert (fhem_dir / "www" / "fhempy" / "push.js").read_text() == "old push"
    assert not (fhem_dir / "FHEM" / "10_newmod.pm").exists()
    assert not (fhem_dir / "www" / "fhempy" / "new.js").exists()
    assert "reload 10_BindingsIo" in runner.fhem.commands

    # interrupted before the state file was removed: the next run restores again
    state = json.loads(pathlib.Path(runner.inst.state_file).read_text())
    runner.restore_fhem_modules(state)
    runner.restore_www_files(state)
    assert (fhem_dir / "FHEM" / "10_BindingsIo.pm").read_text() == "old io"
    assert (fhem_dir / "www" / "fhempy" / "push.js").read_text() == "old push"


def test_missing_file_with_backup_is_put_back(runner):
    state = install(runner)
    (runner.dir / "FHEM" / "10_BindingsIo.pm").unlink()
    runner.restore_fhem_modules(state)
    assert (runner.dir / "FHEM" / "10_BindingsIo.pm").read_text() == "old io"


def test_file_without_backup_stays_if_not_new(runner):
    state = install(runner)
    (pathlib.Path(runner.inst.backup_dir) / "www" / "fhempy" / "push.js").unlink()
    runner.restore_www_files(state)
    assert (runner.dir / "www" / "fhempy" / "push.js").read_text() == "pr push"


def changed_pr(runner, monkeypatch, tester, answer):
    monkeypatch.setattr(
        tester,
        "pr_changed_files",
        lambda pr: ["FHEM/10_BindingsIo.pm", "www/fhempy/push.js"],
    )
    asked = []
    monkeypatch.setattr(
        tester, "ask", lambda question, default=False: asked.append(question) or answer
    )
    runner.ctx["mode"] = "local"
    return asked


def test_yes_copies_changed_fhem_files_without_asking(runner, tester, monkeypatch):
    asked = changed_pr(runner, monkeypatch, tester, False)
    runner.args.yes = True
    modules, www = runner.select_fhem_files({"pr": 1})
    assert modules == ["10_BindingsIo"]
    assert www == ["www/fhempy/push.js"]
    assert not asked


def test_without_yes_the_user_is_asked(runner, tester, monkeypatch):
    asked = changed_pr(runner, monkeypatch, tester, False)
    runner.args.yes = False
    assert runner.select_fhem_files({"pr": 1}) == ([], [])
    assert len(asked) == 1


def test_yes_is_kept_when_the_script_restarts(tester):
    args = tester.argparse.Namespace(
        debug=False,
        fresh=False,
        restore=False,
        clean=False,
        yes=True,
        mode=None,
        port=15733,
        telnet_port=None,
    )
    assert "--yes" in tester.forwarded_args(args, 1)


def test_short_yes_flag(tester, monkeypatch):
    monkeypatch.setattr(tester.sys, "argv", ["pr-tester.py", "--pr", "5", "-y"])
    assert tester.parse_args().yes


def test_self_update_uses_newest_master_commit(tester, monkeypatch):
    sha = "a" * 40
    monkeypatch.setattr(tester, "github_get", lambda path: {"sha": sha})
    assert tester.latest_script_url().endswith(f"/{sha}/tools/pr-tester.py")


def test_self_update_falls_back_to_master_url(tester, monkeypatch):
    def fail(path):
        raise tester.TestError("rate limit")

    monkeypatch.setattr(tester, "github_get", fail)
    assert tester.latest_script_url() == tester.SCRIPT_URL
