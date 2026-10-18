"""README extensions must survive conversion and FHEMWEB serialization."""
import json
import logging
import os

import pytest
from fhempy.lib import generic


@pytest.fixture
def readme(tmp_path, monkeypatch):
    folder = tmp_path / "markdown_example"
    folder.mkdir()
    path = folder / "README.md"
    monkeypatch.setattr(generic.inspect, "getfile", lambda module: str(tmp_path / "__init__.py"))
    monkeypatch.setattr(generic, "_README_CACHE", {})
    device = generic.FhemModule(logging.getLogger("markdown_example"))
    device.hash = {"NAME": "test", "FHEMPYTYPE": "markdown_example"}
    return device, path


def test_tables_preserve_inline_markup_empty_cells_and_alignment(readme):
    device, path = readme
    path.write_text(
        "| Device | Action |\n|:-------|-------:|\n"
        "| **Bridge** | [Pair](https://example.org/) with `code` |\n"
        "| Sensor | |\n"
        "| A \\| B | *Share* |\n",
        encoding="utf-8",
    )
    html = device._get_readme_content()
    assert html.count("<table>") == 1
    assert html.count("<tr>") == 4
    assert "<thead>" in html and "<tbody>" in html
    assert '<th style="text-align:left;">Device</th>' in html
    assert '<td style="text-align:right;"></td>' in html
    assert "<strong>Bridge</strong>" in html
    assert '<a href="https://example.org/">Pair</a>' in html
    assert "<code>code</code>" in html
    assert "A | B" in html and "<em>Share</em>" in html


def test_lists_immediately_after_paragraphs(readme):
    device, path = readme
    path.write_text(
        "**Requirements**\n- IPv6 enabled\n- A controller\n\n"
        "**Pairing**\n1. Open the app\n2. Share the device\n",
        encoding="utf-8",
    )
    html = device._get_readme_content()
    assert "<ul>" in html and "<ol>" in html
    assert html.count("<li>") == 4


@pytest.mark.asyncio
async def test_fenced_code_and_table_survive_detail_page_and_reload(readme):
    device, path = readme
    for index, heading in enumerate(("Before", "After")):
        path.write_text(
            f"# {heading}\n\n| A | B |\n|---|---|\n| One | Two |\n\n"
            "```\n| literal | pipe |\n\n  </script>\n```\n",
            encoding="utf-8",
        )
        os.utime(path, (100 + index, 100 + index))
        output = await device.FW_detailFn(device.hash, ["", "", "", ""], {})
        serialized = output.split('$("#fhempyReadme").html(', 1)[1]
        html, _ = json.JSONDecoder().raw_decode(serialized)
        assert f"<h1>{heading}</h1>" in html
        assert html.count("<table>") == 1
        assert "| literal | pipe |\n\n  &lt;/script&gt;\n" in html
        assert "<br>" not in html
        assert output.lower().count("</script>") == 1
        assert "#fhempyReadme th, #fhempyReadme td" in output
