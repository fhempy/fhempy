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


def test_log_party_only_once(marker, caplog):
    with caplog.at_level("INFO"):
        celebration.ReleaseBanner("1.0.0").show_in_log()
    assert "Welcome to fhempy 1.0.0" in caplog.text
    assert marker.read_text() == "1\n"

    caplog.clear()
    with caplog.at_level("INFO"):
        celebration.ReleaseBanner("1.0.0").show_in_log()
    assert caplog.text == ""


def test_no_banner_before_1_0(marker, caplog):
    with caplog.at_level("INFO"):
        celebration.ReleaseBanner("0.1.788").show_in_log()
    assert caplog.text == ""
    assert not marker.exists()
