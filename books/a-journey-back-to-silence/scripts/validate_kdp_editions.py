#!/usr/bin/env python3
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
INTERIOR = ROOT / "amazon-kdp/paperback/interior/a-journey-back-to-silence-paperback-interior-kdp.pdf"
COVER = ROOT / "amazon-kdp/paperback/cover/a-journey-back-to-silence-paperback-cover-kdp.pdf"
EPUB = ROOT / "amazon-kdp/ebook/a-journey-back-to-silence-kindle.epub"
EBOOK_COVER = ROOT / "amazon-kdp/ebook/a-journey-back-to-silence-kindle-cover.jpg"


def embedded_fonts(reader):
    result = set()
    for page in reader.pages:
        resources = page.get("/Resources", {})
        for reference in (resources.get("/Font", {}) or {}).values():
            font = reference.get_object()
            descriptor = font.get("/FontDescriptor")
            descriptor = descriptor.get_object() if descriptor else {}
            embedded = bool(descriptor.get("/FontFile") or descriptor.get("/FontFile2") or descriptor.get("/FontFile3"))
            result.add((str(font.get("/BaseFont", "")), embedded))
    return sorted(result)


def validate_pdf():
    interior = PdfReader(str(INTERIOR))
    assert len(interior.pages) == 38
    assert len(interior.pages) % 2 == 0
    for page in interior.pages:
        assert abs(float(page.mediabox.width) - 432) < 0.1
        assert abs(float(page.mediabox.height) - 648) < 0.1
    text = "\n".join(page.extract_text() or "" for page in interior.pages)
    for title in [
        "The Tide's Quiet Return", "Before the Morning Speaks", "Rooms Filled With Light",
        "Echoes Between Waves", "Where the Ocean Waits", "The Weight of Silence",
        "Where the Land Ends", "After the Rain Leaves",
    ]:
        assert title in text, title
    fonts = embedded_fonts(interior)
    # ReportLab declares Helvetica as a standard PDF base font resource even
    # though all visible book typography uses the embedded Georgia family.
    non_standard = [(name, status) for name, status in fonts if "Helvetica" not in name]
    assert non_standard and all(status for _, status in non_standard), fonts

    cover = PdfReader(str(COVER))
    assert len(cover.pages) == 1
    width = float(cover.pages[0].mediabox.width) / 72
    height = float(cover.pages[0].mediabox.height) / 72
    expected_width = 0.125 + 6 + (38 * 0.0025) + 6 + 0.125
    assert abs(width - expected_width) < 0.002, (width, expected_width)
    assert abs(height - 9.25) < 0.002, height
    print(f"interior: pages={len(interior.pages)} size=6x9 fonts={fonts}")
    print(f"cover: size={width:.3f}x{height:.3f}in spine={38 * 0.0025:.3f}in")


def validate_epub():
    with zipfile.ZipFile(EPUB) as archive:
        names = archive.namelist()
        assert names[0] == "mimetype"
        assert archive.read("mimetype") == b"application/epub+zip"
        assert archive.getinfo("mimetype").compress_type == zipfile.ZIP_STORED
        assert "OEBPS/nav.xhtml" in names
        assert "OEBPS/content.opf" in names
        for name in names:
            if name.endswith((".xhtml", ".opf", ".xml")):
                ET.fromstring(archive.read(name))
        nav = archive.read("OEBPS/nav.xhtml").decode("utf-8")
        hrefs = re.findall(r'href="([^"]+\.xhtml)"', nav)
        for href in hrefs:
            assert f"OEBPS/{href}" in names, href
        opf = archive.read("OEBPS/content.opf").decode("utf-8")
        assert 'properties="cover-image"' in opf
        assert '<dc:title>A Journey Back to Silence</dc:title>' in opf
        assert '<dc:creator>Sabino Pereira</dc:creator>' in opf
        passages = sum(1 for name in names if name.startswith("OEBPS/section-") and name.endswith(".xhtml") and b'class="section passage"' in archive.read(name))
        assert passages == 8, passages
    with Image.open(EBOOK_COVER) as image:
        assert image.size == (1600, 2400)
        assert image.mode == "RGB"
    print(f"epub: files={len(names)} nav_links={len(hrefs)} passages={passages} cover=1600x2400")


if __name__ == "__main__":
    validate_pdf()
    validate_epub()
