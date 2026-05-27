const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

const root = path.resolve(__dirname, "..");
const manuscriptPath = path.join(root, "08-manuscrito", "o-que-ainda-doi-ecos-da-harmonia.md");
const coverPath = "/Users/binopereira/Downloads/generated-image.png";
const outputPath = path.join(root, "output", "pdf", "o-que-ainda-doi", "o-que-ainda-doi-ecos-da-harmonia.html");

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
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

function markdownToHtml(markdown) {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const html = [];
  let inComment = false;

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();

    if (line.includes("<!--")) {
      inComment = true;
    }
    if (inComment) {
      if (line.includes("-->")) {
        inComment = false;
      }
      continue;
    }

    if (line.trim() === "") {
      continue;
    }

    if (line.startsWith("# ")) {
      html.push(`<h1>${escapeHtml(line.slice(2).trim())}</h1>`);
      continue;
    }

    if (line.startsWith("## ")) {
      html.push(`<section class="part"><h2>${escapeHtml(line.slice(3).trim())}</h2></section>`);
      continue;
    }

    if (line.startsWith("### ")) {
      html.push(`<h3>${escapeHtml(line.slice(4).trim())}</h3>`);
      continue;
    }

    const klass = paragraphClass(line.trim());
    const classAttr = klass ? ` class="${klass}"` : "";
    html.push(`<p${classAttr}>${escapeHtml(line.trim())}</p>`);
  }

  return html.join("\n");
}

const manuscript = fs.readFileSync(manuscriptPath, "utf8");
const content = markdownToHtml(manuscript);
const coverUrl = pathToFileURL(coverPath).href;

const document = `<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8">
  <title>O Que Ainda Dói — Ecos da Harmonia</title>
  <style>
    @page {
      size: 6in 9in;
      margin: 0.68in 0.62in 0.72in;
    }

    @page cover {
      margin: 0;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      color: #1b1d1f;
      background: #f7f5ef;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 10.2pt;
      line-height: 1.45;
      text-rendering: optimizeLegibility;
    }

    .cover {
      page: cover;
      width: 6in;
      height: 9in;
      break-after: page;
      background: #d8dde0;
    }

    .cover img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    .title-page {
      break-after: page;
      min-height: 7.45in;
      display: flex;
      flex-direction: column;
      justify-content: center;
      text-align: center;
    }

    .title-page .title {
      margin: 0;
      color: #20252a;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 29pt;
      font-weight: 300;
      letter-spacing: 0.08em;
      line-height: 1.22;
      text-transform: uppercase;
    }

    .title-page .subtitle {
      margin: 0.35in 0 0;
      color: #5d646a;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 11.2pt;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }

    .title-page .tagline {
      margin-top: 1.1in;
      color: #6f7578;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 8pt;
      letter-spacing: 0.22em;
      text-transform: uppercase;
    }

    .copyright-page,
    .epigraph-page {
      break-after: page;
      min-height: 7.45in;
      display: flex;
      flex-direction: column;
      justify-content: center;
      text-align: center;
    }

    .copyright-page p,
    .epigraph-page p {
      max-width: 4.45in;
      margin-left: auto;
      margin-right: auto;
      color: #3e4448;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 9pt;
      line-height: 1.55;
    }

    .epigraph-page p {
      font-family: Georgia, "Times New Roman", serif;
      font-size: 12pt;
      font-style: italic;
    }

    h1 {
      display: none;
    }

    .part {
      break-before: page;
      break-after: page;
      min-height: 7.45in;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
    }

    .part h2 {
      margin: 0;
      color: #2d3135;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 17pt;
      font-weight: 300;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    h3 {
      break-before: page;
      margin: 0.18in 0 0.34in;
      color: #25292d;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 16pt;
      font-weight: 300;
      letter-spacing: 0.03em;
      line-height: 1.24;
      text-align: center;
    }

    p {
      margin: 0 0 0.075in;
      orphans: 2;
      widows: 2;
    }

    p + p {
      margin-top: 0;
    }

    .metadata {
      margin-bottom: 0.045in;
      color: #43474a;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 8.9pt;
      line-height: 1.38;
    }

    .screen {
      margin: 0.18in 0;
      color: #34383c;
      font-family: Helvetica, Arial, sans-serif;
      font-size: 8.2pt;
      letter-spacing: 0.11em;
      line-height: 1.55;
      text-align: center;
    }
  </style>
</head>
<body>
  <section class="cover">
    <img src="${coverUrl}" alt="Capa de O Que Ainda Dói — Ecos da Harmonia">
  </section>
  <section class="title-page">
    <p class="title">O Que Ainda Dói</p>
    <p class="subtitle">Ecos da Harmonia</p>
    <p class="tagline">A verdadeira dor é uma ameaça</p>
  </section>
  <section class="copyright-page">
    <p>Copyright © 2026 Sabino Pereira.<br>Todos os direitos reservados.</p>
    <p>Esta é uma obra de ficção. Nomes, personagens, lugares e acontecimentos são produto da imaginação do autor ou usados de forma ficcional. Qualquer semelhança com pessoas reais, vivas ou mortas, é coincidência.</p>
  </section>
  <section class="epigraph-page">
    <p>O que ainda dói, ainda vive.</p>
  </section>
  <main>
${content}
  </main>
</body>
</html>
`;

fs.writeFileSync(outputPath, document, "utf8");
console.log(outputPath);
