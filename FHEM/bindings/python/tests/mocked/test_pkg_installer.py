import sys

from fhempy.lib import pkg_installer


def fake_uv(tmp_path):
    uv = tmp_path / "uv"
    uv.write_text("#!/bin/sh\nexit 0\n")
    uv.chmod(0o755)
    return str(uv)


def no_pip_config(monkeypatch):
    for var in (
        "PIP_INDEX_URL",
        "PIP_EXTRA_INDEX_URL",
        "PIP_CONFIG_FILE",
        "UV_INDEX_URL",
        "UV_DEFAULT_INDEX",
        "FHEMPY_NO_UV",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(pkg_installer, "pip_config_indexes", lambda: (None, []))


def test_uses_uv_in_venv(tmp_path, monkeypatch):
    no_pip_config(monkeypatch)
    uv = fake_uv(tmp_path)
    monkeypatch.setenv("FHEMPY_UV", uv)
    monkeypatch.setattr(pkg_installer, "is_virtual_env", lambda: True)

    args = pkg_installer.install_args("fhempy>=0.1.462", True, None, None, False)

    assert args[:6] == [uv, "pip", "install", "--python", sys.executable, "--quiet"]
    assert "fhempy>=0.1.462" in args
    # only the requested package gets upgraded, like pip --upgrade
    assert args[args.index("--upgrade-package") + 1] == "fhempy"
    assert "--upgrade" not in args


def test_uses_pip_without_uv(tmp_path, monkeypatch):
    no_pip_config(monkeypatch)
    monkeypatch.setenv("FHEMPY_UV", fake_uv(tmp_path))
    monkeypatch.setenv("FHEMPY_NO_UV", "1")
    monkeypatch.setattr(pkg_installer, "is_virtual_env", lambda: True)

    args = pkg_installer.install_args("aiohttp==3.14.3", True, None, None, True)

    assert args[:4] == [sys.executable, "-m", "pip", "install"]
    assert "--upgrade" in args
    assert "--no-cache-dir" in args


def test_uses_pip_outside_venv(tmp_path, monkeypatch):
    no_pip_config(monkeypatch)
    monkeypatch.setenv("FHEMPY_UV", fake_uv(tmp_path))
    monkeypatch.setattr(pkg_installer, "is_virtual_env", lambda: False)

    assert pkg_installer.find_uv() is None


def test_pip_conf_indexes(tmp_path, monkeypatch):
    for var in ("PIP_INDEX_URL", "PIP_EXTRA_INDEX_URL"):
        monkeypatch.delenv(var, raising=False)
    pip_conf = tmp_path / "pip.conf"
    pip_conf.write_text("[global]\nextra-index-url=https://www.piwheels.org/simple\n")
    monkeypatch.setenv("PIP_CONFIG_FILE", str(pip_conf))

    _, extra_urls = pkg_installer.pip_config_indexes()

    assert "https://www.piwheels.org/simple" in extra_urls


def test_uv_gets_extra_indexes(tmp_path, monkeypatch):
    no_pip_config(monkeypatch)
    monkeypatch.setattr(
        pkg_installer,
        "pip_config_indexes",
        lambda: (None, ["https://www.piwheels.org/simple"]),
    )
    monkeypatch.setenv("FHEMPY_UV", fake_uv(tmp_path))
    monkeypatch.setattr(pkg_installer, "is_virtual_env", lambda: True)

    args = pkg_installer.install_args("pyit600==0.5.1", False, None, None, False)

    assert (
        args[args.index("--extra-index-url") + 1] == "https://www.piwheels.org/simple"
    )
    assert args[args.index("--index-strategy") + 1] == "unsafe-best-match"
    assert "--upgrade-package" not in args


def test_falls_back_to_pip_if_uv_fails(tmp_path, monkeypatch):
    no_pip_config(monkeypatch)
    failing_uv = tmp_path / "uv"
    failing_uv.write_text("#!/bin/sh\necho uv failed >&2\nexit 1\n")
    failing_uv.chmod(0o755)
    monkeypatch.setenv("FHEMPY_UV", str(failing_uv))
    monkeypatch.setattr(pkg_installer, "is_virtual_env", lambda: True)

    calls = []

    class FakePopen:
        def __init__(self, args, **kwargs):
            calls.append(args)
            self.returncode = 1 if args[0] == str(failing_uv) else 0

        def communicate(self):
            return b"", b"uv failed"

    monkeypatch.setattr(pkg_installer, "Popen", FakePopen)

    assert pkg_installer.install_package("helloworld-pkg") is True
    assert calls[0][0] == str(failing_uv)
    assert calls[1][:4] == [sys.executable, "-m", "pip", "install"]
