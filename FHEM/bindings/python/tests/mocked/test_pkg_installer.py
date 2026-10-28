import asyncio
import os
import sys

import pytest

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
        "UV_INDEX",
        "UV_EXTRA_INDEX_URL",
        "FHEMPY_NO_UV",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(pkg_installer, "pip_config_indexes", lambda: (None, []))
    monkeypatch.setattr(
        pkg_installer, "system_python_version", lambda: tuple(sys.version_info[:2])
    )


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


PIWHEELS = "https://www.piwheels.org/simple"


def test_piwheels_kept_for_system_python(monkeypatch):
    monkeypatch.setattr(pkg_installer, "pip_config_indexes", lambda: (None, [PIWHEELS]))
    monkeypatch.setattr(
        pkg_installer, "system_python_version", lambda: tuple(sys.version_info[:2])
    )

    assert pkg_installer.usable_indexes() == (None, [PIWHEELS], False)


def test_piwheels_skipped_for_other_python(monkeypatch):
    # e.g. Python 3.13 from uv on Raspberry Pi OS Bookworm (system Python 3.11)
    other = "https://example.org/simple"
    monkeypatch.setattr(
        pkg_installer, "pip_config_indexes", lambda: (None, [PIWHEELS, other])
    )
    monkeypatch.setattr(pkg_installer, "system_python_version", lambda: (3, 1))

    assert pkg_installer.usable_indexes() == (None, [other], True)

    env = {"PIP_EXTRA_INDEX_URL": PIWHEELS}
    assert pkg_installer.pip_index_args(env) == ["--extra-index-url", other]
    assert env["PIP_CONFIG_FILE"] == os.devnull
    assert "PIP_EXTRA_INDEX_URL" not in env


def test_uv_skips_piwheels_for_other_python(tmp_path, monkeypatch):
    no_pip_config(monkeypatch)
    monkeypatch.setattr(pkg_installer, "pip_config_indexes", lambda: (None, [PIWHEELS]))
    monkeypatch.setattr(pkg_installer, "system_python_version", lambda: (3, 1))
    monkeypatch.setenv("FHEMPY_UV", fake_uv(tmp_path))
    monkeypatch.setattr(pkg_installer, "is_virtual_env", lambda: True)

    args = pkg_installer.install_args("pyit600==0.5.1", False, None, None, False)

    assert "--extra-index-url" not in args
    assert "--index-strategy" not in args


def test_dependency_caching_and_invalidation(tmp_path, monkeypatch):
    pkg_installer.invalidate_dependency_cache()
    assert len(pkg_installer._VERIFIED_PACKAGES) == 0
    assert len(pkg_installer._VERIFIED_MODULES) == 0
    assert len(pkg_installer._MANIFEST_CACHE) == 0

    # Test is_installed caching
    call_count = 0

    def mock_dist(pkg):
        nonlocal call_count
        if pkg == "uninstalled-pkg-xyz":
            raise pkg_installer.PackageNotFoundError(pkg)
        call_count += 1
        return None

    monkeypatch.setattr(pkg_installer, "distribution", mock_dist)

    assert pkg_installer.is_installed("fake-pkg") is True
    assert call_count == 1
    assert "fake-pkg" in pkg_installer._VERIFIED_PACKAGES

    # Second call should hit the cache and not call distribution() again
    assert pkg_installer.is_installed("fake-pkg") is True
    assert call_count == 1

    # Invalidation should clear it
    pkg_installer.invalidate_dependency_cache()
    assert "fake-pkg" not in pkg_installer._VERIFIED_PACKAGES
    assert pkg_installer.is_installed("fake-pkg") is True
    assert call_count == 2

    # Test check_dependencies manifest caching
    fake_root = tmp_path / "fhempy_root"
    mod_dir = fake_root / "test_mod"
    mod_dir.mkdir(parents=True)
    manifest = mod_dir / "manifest.json"
    manifest.write_text('{"requirements": ["fake-pkg"]}')

    monkeypatch.setattr(pkg_installer.utils, "get_fhempy_root", lambda: str(fake_root))

    assert pkg_installer.check_dependencies("test_mod") is True
    assert "test_mod" in pkg_installer._VERIFIED_MODULES
    assert "test_mod" in pkg_installer._MANIFEST_CACHE

    # Modifying manifest on disk should not matter since it's cached in _VERIFIED_MODULES
    manifest.write_text('{"requirements": ["uninstalled-pkg-xyz"]}')
    assert pkg_installer.check_dependencies("test_mod") is True

    # After invalidation, the new manifest is read and fails because req is not installed
    pkg_installer.invalidate_dependency_cache()
    assert pkg_installer.check_dependencies("test_mod") is False

    # Check that successful install_package invalidates cache
    pkg_installer._VERIFIED_PACKAGES.add("some-cached-pkg")
    pkg_installer._VERIFIED_MODULES.add("some-cached-mod")
    pkg_installer._MANIFEST_CACHE["some-mod"] = {"requirements": []}

    class FakeSuccessfulPopen:
        def __init__(self, *args, **kwargs):
            self.returncode = 0
        def communicate(self):
            return b"", b""

    monkeypatch.setattr(pkg_installer, "Popen", FakeSuccessfulPopen)
    assert pkg_installer.install_package("some-cached-pkg") is True
    assert len(pkg_installer._VERIFIED_PACKAGES) == 0
    assert len(pkg_installer._VERIFIED_MODULES) == 0
    assert len(pkg_installer._MANIFEST_CACHE) == 0


@pytest.mark.asyncio
async def test_install_runs_after_check_cached_manifest(tmp_path, monkeypatch):
    # Define calls check_dependencies first, which caches the manifest.
    # check_and_install_dependencies must still install missing packages.
    pkg_installer.invalidate_dependency_cache()
    mod_dir = tmp_path / "test_mod"
    mod_dir.mkdir()
    (mod_dir / "manifest.json").write_text('{"requirements": ["missing-pkg==1.0"]}')
    monkeypatch.setattr(pkg_installer.utils, "get_fhempy_root", lambda: str(tmp_path))
    monkeypatch.setattr(pkg_installer, "is_installed", lambda req: False)
    monkeypatch.setattr(pkg_installer, "pip_kwargs", lambda x: {})
    installed = []
    monkeypatch.setattr(
        pkg_installer,
        "install_package",
        lambda req, **kwargs: installed.append(req) or True,
    )

    assert pkg_installer.check_dependencies("test_mod") is False
    await pkg_installer.check_and_install_dependencies("test_mod")

    assert installed == ["missing-pkg==1.0"]
    pkg_installer.invalidate_dependency_cache()


def test_pygobject_kept_without_girepository2(monkeypatch):
    monkeypatch.setattr(pkg_installer, "pygobject_works", lambda: False)
    monkeypatch.setattr(pkg_installer, "has_girepository2", lambda: False)

    assert pkg_installer.platform_requirement("PyGObject<=3.50.0") == "PyGObject<=3.50.0"


def test_pygobject_replaced_with_girepository2(monkeypatch):
    monkeypatch.setattr(pkg_installer, "pygobject_works", lambda: False)
    monkeypatch.setattr(pkg_installer, "has_girepository2", lambda: True)

    assert (
        pkg_installer.platform_requirement("PyGObject<=3.50.0")
        == pkg_installer.PYGOBJECT_GIREPOSITORY2_REQUIREMENT
    )
    assert pkg_installer.platform_requirement("bleak==3.0.2") == "bleak==3.0.2"


def test_check_dependencies_uses_platform_requirement(tmp_path, monkeypatch):
    pkg_installer.invalidate_dependency_cache()
    mod_dir = tmp_path / "test_mod"
    mod_dir.mkdir()
    (mod_dir / "manifest.json").write_text('{"requirements": ["PyGObject<=3.50.0"]}')
    monkeypatch.setattr(pkg_installer.utils, "get_fhempy_root", lambda: str(tmp_path))
    monkeypatch.setattr(pkg_installer, "pygobject_works", lambda: False)
    monkeypatch.setattr(pkg_installer, "has_girepository2", lambda: True)
    checked = []

    def fake_is_installed(req):
        checked.append(req)
        return True

    monkeypatch.setattr(pkg_installer, "is_installed", fake_is_installed)

    assert pkg_installer.check_dependencies("test_mod") is True
    assert checked == [pkg_installer.PYGOBJECT_GIREPOSITORY2_REQUIREMENT]
    pkg_installer.invalidate_dependency_cache()


def test_working_pygobject_is_kept(monkeypatch):
    monkeypatch.setattr(pkg_installer, "pygobject_works", lambda: True)
    monkeypatch.setattr(pkg_installer, "has_girepository2", lambda: True)

    assert pkg_installer.platform_requirement("PyGObject<=3.50.0") == "PyGObject"


def test_pygobject_build_failure_logs_hint_and_is_not_retried(
    tmp_path, monkeypatch, caplog
):
    pkg_installer.invalidate_dependency_cache()
    pkg_installer._FAILED_REQUIREMENTS.clear()
    mod_dir = tmp_path / "test_mod"
    mod_dir.mkdir()
    (mod_dir / "manifest.json").write_text('{"requirements": ["PyGObject<=3.50.0"]}')
    monkeypatch.setattr(pkg_installer.utils, "get_fhempy_root", lambda: str(tmp_path))
    monkeypatch.setattr(pkg_installer, "pygobject_works", lambda: False)
    monkeypatch.setattr(pkg_installer, "has_girepository2", lambda: True)
    monkeypatch.setattr(pkg_installer, "is_installed", lambda req: False)
    monkeypatch.setattr(pkg_installer, "is_virtual_env", lambda: False)
    calls = []

    class FakeFailingPopen:
        def __init__(self, args, *a, **kwargs):
            calls.append(args)
            self.returncode = 1

        def communicate(self):
            return b"", b"Dependency 'girepository-2.0' is required but not found."

    monkeypatch.setattr(pkg_installer, "Popen", FakeFailingPopen)

    asyncio.run(pkg_installer.check_and_install_dependencies("test_mod"))
    asyncio.run(pkg_installer.check_and_install_dependencies("test_mod"))

    assert len(calls) == 1
    assert pkg_installer.PYGOBJECT_GIREPOSITORY2_APT in caplog.text
    pkg_installer._FAILED_REQUIREMENTS.clear()
    pkg_installer.invalidate_dependency_cache()


def test_uv_drops_netifaces_with_override(tmp_path, monkeypatch):
    # python-miio requires netifaces, which has no wheels for Python >= 3.10
    no_pip_config(monkeypatch)
    monkeypatch.setenv("FHEMPY_UV", fake_uv(tmp_path))
    monkeypatch.setattr(pkg_installer, "is_virtual_env", lambda: True)

    args = pkg_installer.install_args("python-miio==0.5.12", True, None, None, False)

    overrides = args[args.index("--override") + 1]
    with open(overrides) as f:
        assert 'netifaces; python_version < "0"' in f.read().splitlines()

    # hyundai_kia_connect_api wants pycryptodome>=4, greeclimate <4
    with open(overrides) as f:
        assert "pycryptodome>=3.24,<4" in f.read().splitlines()

    # the file is written again if a tmp cleaner removed it
    os.remove(overrides)
    args = pkg_installer.install_args("python-miio==0.5.12", True, None, None, False)
    assert os.path.isfile(args[args.index("--override") + 1])


def test_pip_gets_no_override(tmp_path, monkeypatch):
    no_pip_config(monkeypatch)
    monkeypatch.setenv("FHEMPY_NO_UV", "1")
    monkeypatch.setattr(pkg_installer, "is_virtual_env", lambda: True)

    args = pkg_installer.install_args("python-miio==0.5.12", True, None, None, False)

    assert "--override" not in args


def test_failed_requirements(tmp_path, monkeypatch):
    pkg_installer.invalidate_dependency_cache()
    mod_dir = tmp_path / "test_mod"
    mod_dir.mkdir()
    (mod_dir / "manifest.json").write_text(
        '{"requirements": ["broken-pkg==1.0", "ok-pkg==1.0"]}'
    )
    monkeypatch.setattr(pkg_installer.utils, "get_fhempy_root", lambda: str(tmp_path))
    monkeypatch.setattr(pkg_installer, "is_installed", lambda req: False)
    monkeypatch.setattr(pkg_installer, "pip_kwargs", lambda x: {})
    monkeypatch.setattr(pkg_installer, "_FAILED_REQUIREMENTS", set())
    monkeypatch.setattr(
        pkg_installer,
        "install_package",
        lambda req, **kwargs: req == "ok-pkg==1.0",
    )

    assert pkg_installer.failed_requirements("test_mod") == []
    asyncio.run(pkg_installer.check_and_install_dependencies("test_mod"))

    assert pkg_installer.failed_requirements("test_mod") == ["broken-pkg==1.0"]
    pkg_installer.invalidate_dependency_cache()
