#!/usr/bin/env python3
"""Build the four Bad Girl Gospel direct-sale ZIP packages."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
BOOKS = {
    "selah": "Bad Girl Gospel: The Story of Selah",
    "diana": "Bad Girl Gospel: The Story of Diana",
    "noa": "Bad Girl Gospel: The Story of Noa",
    "naomi": "Bad Girl Gospel: The Story of Naomi",
}


def build_package(slug: str, title: str) -> None:
    folder = ROOT / "direct-sale" / slug
    stem = f"bad-girl-gospel-the-story-of-{slug}"
    readme = folder / "README.txt"
    readme.write_text(
        f"""{title.upper()} — PREMIUM DIGITAL EDITION

Included files
--------------
1. {stem}-premium-ebook.epub
   Reflowable edition for Apple Books, Kobo, Google Play Books, tablets,
   phones, and compatible e-readers. Narrative chapters use prose paragraphs;
   deliberate poetic passages retain their original lineation.

2. {stem}-premium-ebook.pdf
   Designed fixed-layout prose edition for reading on tablets and computers.

3. {stem}-digital-cover.jpg
   High-resolution digital cover (1800 x 2700 px).

Series: Bad Girl Gospel
Author: Sabino Pereira
Language: English
Website: https://sabinopereira.com/bad-girl-gospel.html

Copyright © 2026 Sabino Pereira. All rights reserved.
""",
        encoding="utf-8",
    )

    package = folder / f"{stem}-complete-digital-edition.zip"
    with ZipFile(package, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(folder.iterdir()):
            if path.is_file() and path != package:
                archive.write(path, path.name)
    print(f"Created {package}")


def main() -> None:
    for slug, title in BOOKS.items():
        build_package(slug, title)


if __name__ == "__main__":
    main()
