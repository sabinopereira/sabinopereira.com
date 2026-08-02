from pathlib import Path


ROOT = Path(__file__).resolve().parent
generated = ROOT / "generated"
generated.mkdir(exist_ok=True)

second_half = (ROOT / "segunda-metade-reescrita.md").read_text(encoding="utf-8")
sections = []
current = []
for line in second_half.splitlines():
    if line.startswith("# CAPÍTULO ") or line == "# EPÍLOGO":
        if current:
            sections.append("\n".join(current).strip() + "\n")
        current = [line]
    else:
        current.append(line)
if current:
    sections.append("\n".join(current).strip() + "\n")

for number, section in zip(range(7, 13), sections[:6]):
    (generated / f"capitulo-{number:02d}.md").write_text(section, encoding="utf-8")
(generated / "epilogo.md").write_text(sections[6], encoding="utf-8")

parts = [ROOT / "front-matter.md"]
parts.extend(ROOT / "capitulos" / f"capitulo-{number:02d}.md" for number in range(1, 7))
parts.append(ROOT / "segunda-metade-reescrita.md")

text = "\n\n---\n\n".join(path.read_text(encoding="utf-8").strip() for path in parts)
output = ROOT / "um-lugar-a-mesa-manuscrito-revisao-emocional.md"
output.write_text(text + "\n", encoding="utf-8")
print(output)
