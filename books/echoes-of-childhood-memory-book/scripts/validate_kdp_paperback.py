#!/usr/bin/env python3
"""Run deterministic checks on the final KDP paperback PDFs."""

from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "amazon-kdp" / "paperback" / "interior" / "echoes-of-childhood-paperback-interior-kdp.pdf",
    ROOT / "amazon-kdp" / "paperback" / "cover" / "echoes-of-childhood-paperback-cover-kdp.pdf",
]


def font_status(reader):
    fonts = set()
    for page in reader.pages:
        resources = page.get("/Resources", {})
        for reference in (resources.get("/Font", {}) or {}).values():
            font = reference.get_object()
            descriptor = font.get("/FontDescriptor")
            descriptor = descriptor.get_object() if descriptor else {}
            embedded = bool(
                descriptor.get("/FontFile")
                or descriptor.get("/FontFile2")
                or descriptor.get("/FontFile3")
            )
            fonts.add((str(font.get("/BaseFont", "")), embedded))
    return sorted(fonts)


def main():
    for path in FILES:
        reader = PdfReader(str(path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        page = reader.pages[0]
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        print(path.name)
        print(f"  pages={len(reader.pages)} size={width:.3f}x{height:.3f}pt encrypted={reader.is_encrypted}")
        print(f"  text_chars={len(text)} memory_fragments={text.count('MEMORY FRAGMENT')}")
        print(f"  fonts={font_status(reader)}")


if __name__ == "__main__":
    main()
