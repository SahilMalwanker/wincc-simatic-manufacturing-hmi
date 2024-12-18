import hashlib
import re
import zipfile
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree

import pypdfium2 as pdfium
import pytest

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = sorted([ROOT / "README.md", *ROOT.glob("docs/*.md")])
LINK = re.compile(r"\]\(([^)\s]+)\)|(?:src|href)=\"([^\"]+)\"")
MAX_FILE_MB = 20


def _local_targets(md: Path):
    text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
    for match in LINK.finditer(text):
        target = match.group(1) or match.group(2)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        yield unquote(target.split("#", 1)[0])


@pytest.mark.parametrize("md", MARKDOWN, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_local_links_and_images_resolve(md):
    missing = [t for t in _local_targets(md) if not (md.parent / t).exists()]
    assert not missing, f"broken links in {md.name}: {missing}"


def test_files_stay_small():
    tracked = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and ".venv" not in p.parts]
    too_big = [p.relative_to(ROOT).as_posix() for p in tracked if p.stat().st_size > MAX_FILE_MB * 1e6]
    assert not too_big, f"files over {MAX_FILE_MB} MB: {too_big}"


def _heading_ids(path):
    content = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
    headings = re.findall(r"^#{1,6}\s+(.+)$", content, flags=re.M)
    return {re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-") for heading in headings}


@pytest.mark.parametrize("md", MARKDOWN, ids=lambda path: path.relative_to(ROOT).as_posix())
def test_local_heading_links_resolve(md):
    text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
    for match in LINK.finditer(text):
        target = match.group(1) or match.group(2)
        if target.startswith(("http://", "https://", "mailto:")) or "#" not in target:
            continue
        filename, anchor = unquote(target).split("#", 1)
        document = md.parent / filename if filename else md
        if anchor and document.suffix == ".md":
            assert anchor in _heading_ids(document), f"Missing heading: {md.name} -> {target}"


def test_native_archive_is_the_intact_final_project():
    archive_path = ROOT / "project" / "wincc-simatic-manufacturing-hmi.zap17"
    expected = "6cc0b5e60fc339e1c5b45ce96311e1d86c5d0e491598f60e1437c77b3193e65d"
    assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == expected
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        project_files = [name for name in archive.namelist() if name.endswith(".ap17")]
        assert len(project_files) == 1
        project = ElementTree.fromstring(archive.read(project_files[0]))
        assert project.get("ProjectCompatibilityVersion") == "17.0.0.0"
        assert "System/PEData.plf" in archive.namelist()


def test_published_pdf_metadata_is_neutral():
    for path in (ROOT / "docs/pdf").glob("*.pdf"):
        with pdfium.PdfDocument(path) as document:
            metadata = document.get_metadata_dict()
            assert not metadata.get("Author"), path.name
            assert not metadata.get("Creator"), path.name
