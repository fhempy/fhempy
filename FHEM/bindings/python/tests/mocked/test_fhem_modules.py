"""FHEM modules (.pm) of the running fhempy version are installed in FHEM."""
import shutil
import subprocess
from unittest.mock import AsyncMock

import pytest
from fhempy.lib import fhem, fhem_modules

CONTROLS = """DIR FHEM/bindings
UPD 2026-10-21_23:17:46 35359 FHEM/10_BindingsIo.pm
UPD 2026-10-06_19:02:38 7088 FHEM/bindings/python/bin/fhempy
UPD 2026-10-06_19:02:38 7088 FHEM/../../etc/passwd
UPD 2026-10-06_19:02:38 7088 /etc/passwd
UPD 2026-10-06_19:02:38 7088 FHEM/it's.pm
MOV FHEM/a FHEM/b
"""


def test_controls_files_stay_in_fhem_directory():
    assert fhem_modules.controls_files(CONTROLS) == [
        "FHEM/10_BindingsIo.pm",
        "FHEM/bindings/python/bin/fhempy",
    ]


@pytest.mark.parametrize(
    "installed,running,expected",
    [
        ("", "2.5.1", True),
        ("2.5.0", "2.5.1", True),
        ("2.5.1", "2.5.1", False),
        ("2.6.0", "2.5.1", False),
        ("garbage", "2.5.1", True),
    ],
)
def test_only_newer_modules_are_installed(installed, running, expected):
    assert fhem_modules.needs_install(installed, running) == expected


@pytest.fixture
def commands(monkeypatch):
    monkeypatch.setattr(fhem_modules, "__version__", "2.6.0")
    send = AsyncMock(side_effect=["2.5.1", "FHEM/10_BindingsIo.pm"])
    monkeypatch.setattr(fhem, "sendCommandName", send)
    return send


@pytest.mark.asyncio
async def test_install_sends_files_of_running_version(commands, monkeypatch):
    download = AsyncMock(return_value={"FHEM/10_BindingsIo.pm": b"new"})
    monkeypatch.setattr(fhem_modules, "download", download)
    await fhem_modules.install()
    download.assert_awaited_once_with("2.6.0")
    assert commands.await_count == 2
    name, cmd = commands.await_args.args
    assert name == fhem_modules.COMMAND_NAME
    assert "'2.6.0'" in cmd and "FHEM/10_BindingsIo.pm" in cmd


@pytest.mark.asyncio
async def test_install_skips_current_modules(commands, monkeypatch):
    commands.side_effect = ["2.6.0"]
    download = AsyncMock()
    monkeypatch.setattr(fhem_modules, "download", download)
    await fhem_modules.install()
    download.assert_not_awaited()


@pytest.mark.asyncio
async def test_failed_download_changes_nothing(commands, monkeypatch):
    monkeypatch.setattr(
        fhem_modules, "download", AsyncMock(side_effect=OSError("404 no tag"))
    )
    await fhem_modules.install()
    assert commands.await_count == 1


PERL_HARNESS = r"""
package main;
use strict;
use warnings;
our (%attr, %modules, @timers, %kv, @readings, @reloads);
$attr{global}{modpath} = shift @ARGV;
$modules{BindingsIo}{LOADED} = 1;
sub Log3 {}
sub readingsSingleUpdate { push @readings, "$_[1]=$_[2]" }
sub setKeyValue { $kv{$_[0]} = $_[1]; return undef }
sub getKeyValue { return (undef, $kv{$_[0]}) }
sub InternalTimer { push @timers, $_[1] }
sub gettimeofday { time }
sub CommandReload { push @reloads, $_[1]; return undef }
my $hash = { NAME => 'binding' };
local $/;
my $cmd = <STDIN>;
my $ret = eval $cmd;
die $@ if $@;
$_->(undef) foreach @timers;
my $again = eval $cmd;
die $@ if $@;
my $stored = eval $ARGV[0];
print join("|", $ret, $again, $stored, join(",", @reloads), join(",", @readings));
"""


@pytest.mark.skipif(shutil.which("perl") is None, reason="perl not installed")
def test_perl_writes_changed_files_and_reloads_loaded_modules(tmp_path):
    fhem_dir = tmp_path / "FHEM"
    fhem_dir.mkdir()
    (fhem_dir / "10_BindingsIo.pm").write_bytes(b"old")
    (fhem_dir / "10_fhempy.pm").write_bytes(b"same")
    files = {
        "FHEM/10_BindingsIo.pm": b"new \x00\xff",
        "FHEM/10_fhempy.pm": b"same",
        "FHEM/bindings/python/bin/fhempy": b"#!/bin/sh\n",
        "FHEM/controls_pythonbinding.txt": b"UPD x",
    }
    harness = tmp_path / "harness.pl"
    harness.write_text(PERL_HARNESS)
    result = subprocess.run(
        ["perl", str(harness), str(tmp_path), fhem_modules.STORED_VERSION_CMD],
        input=fhem_modules.install_command("2.6.0", files),
        capture_output=True,
        text=True,
        check=True,
    )
    ret, again, stored, reloads, readings = result.stdout.split("|")
    assert ret == (
        "FHEM/10_BindingsIo.pm,FHEM/bindings/python/bin/fhempy,"
        "FHEM/controls_pythonbinding.txt"
    )
    assert again == ""
    assert stored == "2.6.0"
    assert reloads == "10_BindingsIo"
    assert "FHEM modules updated" in readings
    assert (fhem_dir / "10_BindingsIo.pm").read_bytes() == b"new \x00\xff"
    script = fhem_dir / "bindings" / "python" / "bin" / "fhempy"
    assert script.stat().st_mode & 0o111
    assert not list(fhem_dir.glob("*.fhempy_new"))
