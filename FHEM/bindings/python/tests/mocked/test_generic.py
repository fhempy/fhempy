import logging
from unittest.mock import MagicMock

import pytest
from fhempy.lib import generic

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_readme_caching(tmp_path, monkeypatch):
    # Setup temporary directory structure mimicking fhempy/lib/testmod/README.md
    mod_dir = tmp_path / "testmod"
    mod_dir.mkdir()
    readme_file = mod_dir / "README.md"
    readme_file.write_text("# Initial Title\n\nSome documentation.")

    # Monkeypatch inspect.getfile to return a dummy file inside tmp_path
    dummy_init = tmp_path / "__init__.py"
    dummy_init.write_text("")
    monkeypatch.setattr(
        "inspect.getfile",
        lambda obj: str(dummy_init),
    )

    # Clear any preexisting cache
    generic._README_CACHE.clear()

    instance = generic.FhemModule(logger)
    instance.hash = {"NAME": "test_device", "FHEMPYTYPE": "testmod"}

    # First call: reads from disk, renders, and populates cache
    content1 = instance._get_readme_content()
    assert "Initial Title" in content1
    assert "testmod" in generic._README_CACHE
    mtime1, cached_html1 = generic._README_CACHE["testmod"]
    assert cached_html1 == content1

    # Second call without modifying file: must return exact cached content
    content2 = instance._get_readme_content()
    assert content2 is content1

    # Modify the README file (update content and timestamp)
    readme_file.write_text("# Updated Title\n\nNew documentation.")
    # Ensure mtime is different
    new_mtime = mtime1 + 10
    import os
    os.utime(readme_file, (new_mtime, new_mtime))

    # Third call: detects updated mtime and reloads
    content3 = instance._get_readme_content()
    assert "Updated Title" in content3
    mtime2, cached_html2 = generic._README_CACHE["testmod"]
    assert mtime2 == new_mtime
    assert cached_html2 == content3


@pytest.mark.asyncio
async def test_readme_not_found(tmp_path, monkeypatch):
    dummy_init = tmp_path / "__init__.py"
    dummy_init.write_text("")
    monkeypatch.setattr(
        "inspect.getfile",
        lambda obj: str(dummy_init),
    )
    generic._README_CACHE.clear()

    instance = generic.FhemModule(logger)
    instance.hash = {"NAME": "test_device", "FHEMPYTYPE": "nonexistent_mod"}

    content = instance._get_readme_content()
    assert content == "No README.md file found for nonexistent_mod."
    assert "nonexistent_mod" not in generic._README_CACHE
