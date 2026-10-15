import pytest
from fhempy.lib import celebration


@pytest.fixture
def marker(tmp_path, monkeypatch):
    monkeypatch.delenv("FHEMPY_CELEBRATE", raising=False)
    marker_file = tmp_path / ".fhempy" / "celebrated_major"
    monkeypatch.setattr(celebration, "MARKER_FILE", marker_file)
    return marker_file


def test_no_party_before_1_0(marker):
    assert not celebration.should_celebrate("0.1.788")


def test_party_once_per_major(marker):
    assert celebration.should_celebrate("1.0.0")
    celebration.mark_celebrated("1.0.0")
    assert marker.read_text() == "1\n"
    assert not celebration.should_celebrate("1.0.0")
    assert not celebration.should_celebrate("1.3.7")
    assert celebration.should_celebrate("2.0.0")


def test_party_env_override(marker, monkeypatch):
    monkeypatch.setenv("FHEMPY_CELEBRATE", "1")
    assert celebration.should_celebrate("0.1.788")
    monkeypatch.setenv("FHEMPY_CELEBRATE", "0")
    assert not celebration.should_celebrate("1.0.0")


def test_banner_shows_version():
    lines = celebration.banner_lines("1.0.0")
    assert len(lines) == 5
    # "1" "." "0" "." "0" next to fhempy
    assert "/ |" in lines[1]
    assert lines[3].count("(_)") == 2
    assert celebration.banner_lines("1.2.3.dev1") == celebration.banner_lines("1.2.3.")


def test_fhem_command_is_one_perl_block():
    cmd = celebration.fhem_party_command("1.0.0")
    assert cmd.startswith("{") and cmd.endswith("}")
    assert cmd.count("{") == cmd.count("}")
    assert "release_party" in cmd
    assert "FW_" not in cmd
    assert "Log3" not in cmd


def test_log_party_only_once(marker, caplog):
    with caplog.at_level("INFO"):
        celebration.ReleaseParty("1.0.0").show_in_log()
    assert "Welcome to fhempy 1.0.0" in caplog.text
    assert marker.read_text() == "1\n"

    caplog.clear()
    with caplog.at_level("INFO"):
        celebration.ReleaseParty("1.0.0").show_in_log()
    assert caplog.text == ""


@pytest.mark.asyncio
async def test_fhem_party_once(marker, mocker):
    send = mocker.patch(
        "fhempy.lib.fhem.sendCommandName", mocker.AsyncMock(return_value="")
    )
    party = celebration.ReleaseParty("1.0.0")
    await party.show_in_fhem()
    await party.show_in_fhem()
    send.assert_awaited_once()
    assert not party.pending


@pytest.mark.asyncio
async def test_no_party_no_command(marker, mocker):
    send = mocker.patch("fhempy.lib.fhem.sendCommandName", mocker.AsyncMock())
    party = celebration.ReleaseParty("0.1.788")
    party.show_in_log()
    await party.show_in_fhem()
    send.assert_not_awaited()
    assert not marker.exists()
