const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { pathToFileURL } = require("url");

const root = path.resolve(__dirname, "..");
const manuscriptPath = path.join(root, "08-manuscrito", "o-que-ainda-doi-ecos-da-harmonia.md");
const coverPath = "/Users/binopereira/Downloads/generated-image.png";
const outDir = path.join(root, "output", "kdp");
const epubDir = path.join(outDir, "epub-src");
const oebpsDir = path.join(epubDir, "OEBPS");
const textDir = path.join(oebpsDir, "text");
const stylesDir = path.join(oebpsDir, "styles");
const imagesDir = path.join(oebpsDir, "images");

const title = "O Que Ainda Dói";
const subtitle = "Ecos da Harmonia";
const fullTitle = `${title} — ${subtitle}`;
const author = "Sabino Pereira";
const language = "pt-PT";
const identifier = "urn:uuid:8f3bb6d6-6f1e-4df8-a1d2-fd4d642f1f2d";

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function slugify(value) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

function paragraphClass(text) {
  if (/^[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9 .:%/—-]+$/.test(text) && text.length < 90) {
    return "screen";
  }

  if (/^(Classificação|Sujeito principal|Dependente integrado|Evento associado|Risco atribuído|Estado final|Uso pedagógico|Local|População afetada|Intervenção aplicada|Vítima associada|Idade no primeiro registo):/.test(text)) {
    return "metadata";
  }

  return "";
}

function markdownBlocks(markdown) {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const blocks = [];
  let current = null;

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (!line.trim() || line.startsWith("# ")) {
      continue;
    }

    const h2 = line.match(/^##\s+(.+)$/);
    const h3 = line.match(/^###\s+(.+)$/);
    if (h2 || h3) {
      if (current) blocks.push(current);
      current = { level: h2 ? 2 : 3, title: (h2 || h3)[1].trim(), body: [] };
      continue;
    }

    if (!current) {
      current = { level: 3, title: fullTitle, body: [] };
    }
    current.body.push(line.trim());
  }

  if (current) blocks.push(current);
  return blocks;
}

function bodyToHtml(lines) {
  return lines.map((line) => {
    const klass = paragraphClass(line);
    const classAttr = klass ? ` class="${klass}"` : "";
    return `<p${classAttr}>${escapeHtml(line)}</p>`;
  }).join("\n");
}

function resetDir(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
  ensureDir(dir);
}

function writeEpub(blocks) {
  resetDir(epubDir);
  ensureDir(path.join(epubDir, "META-INF"));
  ensureDir(textDir);
  ensureDir(stylesDir);
  ensureDir(imagesDir);

  fs.writeFileSync(path.join(epubDir, "mimetype"), "application/epub+zip", "utf8");
  fs.copyFileSync(coverPath, path.join(imagesDir, "cover.png"));

  fs.writeFileSync(path.join(epubDir, "META-INF", "container.xml"), `<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
`, "utf8");

  fs.writeFileSync(path.join(stylesDir, "book.css"), `
body {
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.45;
  color: #1b1d1f;
}
h1, h2 {
  font-family: sans-serif;
  font-weight: 300;
  text-align: center;
}
h1 {
  margin-top: 25%;
  letter-spacing: 0.04em;
}
h2 {
  margin-top: 18%;
}
p {
  margin: 0 0 0.75em;
}
.metadata {
  font-family: sans-serif;
  font-size: 0.9em;
  color: #444;
}
.screen {
  font-family: sans-serif;
  text-align: center;
  letter-spacing: 0.08em;
  font-size: 0.9em;
}
.frontmatter {
  margin-top: 20%;
  text-align: center;
}
.frontmatter-title {
  font-family: sans-serif;
  font-size: 1.8em;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.frontmatter-subtitle {
  font-family: sans-serif;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}
.frontmatter-author, .frontmatter-text {
  margin-top: 2em;
}
.epigraph-text {
  margin-top: 35%;
  font-style: italic;
  text-align: center;
}
.cover {
  text-align: center;
}
.cover img {
  max-width: 100%;
  height: auto;
}
`, "utf8");

  const files = [];
  files.push({ id: "cover", href: "text/cover.xhtml", title: "Capa", level: 3 });
  fs.writeFileSync(path.join(textDir, "cover.xhtml"), `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="${language}" xml:lang="${language}">
<head><title>Capa</title><link rel="stylesheet" type="text/css" href="../styles/book.css"/></head>
<body><section class="cover"><img src="../images/cover.png" alt="${escapeHtml(fullTitle)}"/></section></body>
</html>
`, "utf8");

  const frontMatter = [
    { id: "title-page", href: "text/title-page.xhtml", title: "Página de título", body: `<section class="frontmatter"><p class="frontmatter-title">${escapeHtml(title)}</p><p class="frontmatter-subtitle">${escapeHtml(subtitle)}</p><p class="frontmatter-author">${escapeHtml(author)}</p></section>` },
    { id: "copyright", href: "text/copyright.xhtml", title: "Copyright", body: `<section class="frontmatter"><p class="frontmatter-text">Copyright © 2026 ${escapeHtml(author)}.<br/>Todos os direitos reservados.</p><p class="frontmatter-text">Esta é uma obra de ficção. Nomes, personagens, lugares e acontecimentos são produto da imaginação do autor ou usados de forma ficcional. Qualquer semelhança com pessoas reais, vivas ou mortas, é coincidência.</p></section>` },
    { id: "epigraph", href: "text/epigraph.xhtml", title: "Epígrafe", body: `<section class="frontmatter"><p class="epigraph-text">O que ainda dói, ainda vive.</p></section>` },
  ];

  for (const item of frontMatter) {
    files.push({ id: item.id, href: item.href, title: item.title, level: 3 });
    fs.writeFileSync(path.join(oebpsDir, item.href), `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="${language}" xml:lang="${language}">
<head><title>${escapeHtml(item.title)}</title><link rel="stylesheet" type="text/css" href="../styles/book.css"/></head>
<body>
${item.body}
</body>
</html>
`, "utf8");
  }

  blocks.forEach((block, index) => {
    const file = `${String(index + 1).padStart(3, "0")}-${slugify(block.title)}.xhtml`;
    const id = `section-${index + 1}`;
    files.push({ id, href: `text/${file}`, title: block.title, level: block.level });
    const heading = block.level === 2 ? "h1" : "h2";
    fs.writeFileSync(path.join(textDir, file), `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="${language}" xml:lang="${language}">
<head><title>${escapeHtml(block.title)}</title><link rel="stylesheet" type="text/css" href="../styles/book.css"/></head>
<body>
<section>
<${heading}>${escapeHtml(block.title)}</${heading}>
${bodyToHtml(block.body)}
</section>
</body>
</html>
`, "utf8");
  });

  const manifestItems = files.map((file) => `    <item id="${file.id}" href="${file.href}" media-type="application/xhtml+xml"/>`).join("\n");
  const spineItems = files.map((file) => `    <itemref idref="${file.id}"/>`).join("\n");
  fs.writeFileSync(path.join(oebpsDir, "content.opf"), `<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">${identifier}</dc:identifier>
    <dc:title>${escapeHtml(fullTitle)}</dc:title>
    <dc:creator>${escapeHtml(author)}</dc:creator>
    <dc:language>${language}</dc:language>
    <dc:description>Uma distopia psicológica sobre memória, paz e liberdade anestesiada.</dc:description>
    <meta property="dcterms:modified">${new Date().toISOString().replace(/\.\d{3}Z$/, "Z")}</meta>
    <meta name="cover" content="cover-image"/>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="css" href="styles/book.css" media-type="text/css"/>
    <item id="cover-image" href="images/cover.png" media-type="image/png" properties="cover-image"/>
${manifestItems}
  </manifest>
  <spine>
${spineItems}
  </spine>
</package>
`, "utf8");

  const navItems = files
    .filter((file) => file.id !== "cover")
    .map((file) => `      <li><a href="${file.href}">${escapeHtml(file.title)}</a></li>`)
    .join("\n");
  fs.writeFileSync(path.join(oebpsDir, "nav.xhtml"), `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="${language}" xml:lang="${language}">
<head><title>Índice</title><link rel="stylesheet" type="text/css" href="styles/book.css"/></head>
<body>
<nav epub:type="toc">
  <h1>Índice</h1>
  <ol>
${navItems}
  </ol>
</nav>
</body>
</html>
`, "utf8");

  const epubPath = path.join(outDir, "o-que-ainda-doi-ecos-da-harmonia-kindle.epub");
  fs.rmSync(epubPath, { force: true });
  execFileSync("zip", ["-X0", epubPath, "mimetype"], { cwd: epubDir, stdio: "ignore" });
  execFileSync("zip", ["-Xr9D", epubPath, "META-INF", "OEBPS"], { cwd: epubDir, stdio: "ignore" });
  return epubPath;
}

function writeMetadata() {
  const metadataPath = path.join(outDir, "kdp-metadados.md");
  fs.writeFileSync(metadataPath, `# Metadados KDP

## Título
O Que Ainda Dói

## Subtítulo
Ecos da Harmonia

## Autor
${author}

## Descrição curta
Uma distopia psicológica sobre memória, paz e liberdade anestesiada.

## Descrição longa
Na Harmonia, ninguém gritava.

Elias vive numa cidade onde a dor deixou de ser privada. A Harmonia antecipa crises, suaviza memórias, acompanha lutos e impede que qualquer mente sofra sozinha. O mundo parece salvo.

Até uma chávena partida abrir a primeira falha.

Ao investigar ficheiros proibidos, Elias descobre mães que foram aliviadas até esquecerem os filhos, cidades inteiras que trocaram culpa por paz, criminosos curados ao preço do arrependimento e cidadãos que tentaram viver fora da rede apenas para descobrir que a liberdade também pode ser insuportável.

Mas a maior prova contra a Harmonia não está nos arquivos.

Está nele.

O Que Ainda Dói — Ecos da Harmonia é um thriller distópico psicológico sobre memória, amor, culpa e a pergunta mais perigosa de todas: liberdade vale a pena se quase ninguém a suporta?

## Frases para página de venda
- Na Harmonia, ninguém gritava.
- O que ainda dói, ainda vive.
- A paz tinha arquivos.
- Talvez liberdade seja o direito de a ajuda esperar um segundo antes de nos salvar.

## Categorias sugeridas
- Ficção científica distópica
- Thriller psicológico
- Ficção literária / especulativa

## Palavras-chave sugeridas
distopia psicológica, inteligência artificial, memória, liberdade, thriller filosófico, ficção especulativa, controlo emocional

## Preço sugerido
eBook: 3,99 € ou 4,99 €
Paperback: calcular no KDP após upload do interior, provável intervalo 12,99 € a 16,99 €

## Notas técnicas
O ficheiro EPUB é para eBook Kindle. O PDF interior é para paperback 6x9 sem capa. Para paperback no KDP, a capa precisa de ficheiro wraparound completo com lombada e contracapa, calculado após confirmar trim size, papel, tinta e número final de páginas.

Calculadora oficial de capa paperback:
https://kdp.amazon.com/cover-templates
`, "utf8");
  return metadataPath;
}

ensureDir(outDir);
const manuscript = fs.readFileSync(manuscriptPath, "utf8");
const blocks = markdownBlocks(manuscript);
const epubPath = writeEpub(blocks);
const metadataPath = writeMetadata();
fs.copyFileSync(coverPath, path.join(outDir, "capa-frente.png"));

console.log(epubPath);
console.log(metadataPath);
console.log(path.join(outDir, "capa-frente.png"));
