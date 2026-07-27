#!/usr/bin/env python3
"""Normalize the Portuguese Xadrez no Comando manuscript as prose.

The original HTML used ``stanza`` containers for rhetorical lists. Those
containers forced line breaks in both the paperback and Kindle editions and
made a prose manuscript look like verse. This script keeps every sentence but
joins each false stanza into a normal prose paragraph.
"""

from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output/pdf/xadrez-no-comando/xadrez-no-comando.html"
MANUSCRIPT = ROOT / "books/xadrez-no-comando/xadrez-no-comando-manuscrito-limpo.md"


def plain_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def normalize_stanzas(source: str) -> tuple[str, int]:
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        lines = [plain_text(item) for item in re.findall(r"<p>(.*?)</p>", match.group(1), re.S)]
        lines = [line for line in lines if line]
        if not lines:
            return ""
        count += 1
        return f"<p>{html.escape(' '.join(lines), quote=False)}</p>"

    cleaned = re.sub(r'<div class="stanza">(.*?)</div>', replace, source, flags=re.S)
    return cleaned, count


def write_markdown(source: str) -> None:
    chapters = re.findall(r'<section class="chapter">(.*?)</section>', source, re.S)
    output = ["# Xadrez no Comando", "", "Sabino Pereira", ""]
    for chapter in chapters:
        heading = re.search(r"<h2>(.*?)</h2>", chapter, re.S)
        if not heading:
            continue
        output.extend([f"## {plain_text(heading.group(1))}", ""])
        content = chapter[heading.end() :]
        token_re = re.compile(r'<div class="quote">(.*?)</div>|<p>(.*?)</p>', re.S)
        for token in token_re.finditer(content):
            quote, paragraph = token.groups()
            if quote is not None:
                lines = [plain_text(item) for item in re.findall(r"<p>(.*?)</p>", quote, re.S)]
                output.extend([f"> {line}" for line in lines if line])
                output.append("")
            else:
                text = plain_text(paragraph)
                if text:
                    output.extend([text, ""])
    MANUSCRIPT.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    cleaned, count = normalize_stanzas(source)
    SOURCE.write_text(cleaned, encoding="utf-8")
    write_markdown(cleaned)
    print(f"Normalized {count} false-stanza blocks.")
    print(f"Wrote {MANUSCRIPT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
