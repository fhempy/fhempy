"""Published fhempy versions and exact package requirements for updates."""
import asyncio
import platform

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.utils import (
    InvalidSdistFilename,
    InvalidWheelFilename,
    parse_sdist_filename,
    parse_wheel_filename,
)
from packaging.version import Version

INDEX_URL = "https://pypi.org/simple/fhempy/"
CHECK_INTERVAL = 12 * 3600


def _file_version(file, python_version):
    if file.get("yanked", False) is not False:
        return None
    try:
        if python_version not in SpecifierSet(file.get("requires-python") or ""):
            return None
        filename = file["filename"]
        if filename.endswith(".whl"):
            name, version, _, _ = parse_wheel_filename(filename)
        else:
            name, version = parse_sdist_filename(filename)
        return version if name == "fhempy" else None
    except (InvalidSpecifier, InvalidSdistFilename, InvalidWheelFilename):
        return None


def available_versions(files, installed):
    """Include the installed version and compatible, non-yanked stable releases."""
    current = Version(installed)
    versions = {current}
    python_version = platform.python_version()
    for file in files:
        version = _file_version(file, python_version)
        if version is None or version < current or version.is_prerelease:
            continue
        versions.add(version)
    return [str(version) for version in sorted(versions, reverse=True)]


async def get_versions(installed):
    # Keep aiohttp's import out of the binding's startup path.
    import aiohttp

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
        async with session.get(
            INDEX_URL, headers={"Accept": "application/vnd.pypi.simple.v1+json"}
        ) as response:
            response.raise_for_status()
            data = await response.json()
    return await asyncio.to_thread(available_versions, data["files"], installed)


def package_requirement(args):
    """Unpinned updates always resolve afresh; explicit versions never fall back."""
    if len(args) > 1:
        raise ValueError("Expected update [latest|version].")
    if not args or args[0] == "latest":
        return "fhempy"
    target = Version(args[0])
    return f"fhempy=={target}"
