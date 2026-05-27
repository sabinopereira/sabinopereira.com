const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const manuscriptPath = path.join(root, "09-english", "manuscript", "what-still-hurts-echoes-of-harmony.md");
const outputPath = path.join(root, "output", "kdp-en", "what-still-hurts-echoes-of-harmony-paperback-interior.html");

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function paragraphClass(text) {
  if (/^[A-Z0-9 .:%/—'-]+$/.test(text) && text.length < 100) {
    return "screen";
  }

  if (/^(Classification|Main subject|Integrated dependent|Associated event|Risk assigned|Final state|Pedagogical use|Location|Affected population|Intervention applied|Associated victim|Age at first record):/.test(text)) {
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

fs.mkdirSync(path.dirname(outputPath), { recursive: true });

const manuscript = fs.readFileSync(manuscriptPath, "utf8");
const content = markdownToHtml(manuscript);

const document = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>What Still Hurts — Echoes of Harmony — Paperback Interior</title>
  <style>
    @page {
      size: 6in 9in;
      margin: 0.72in 0.5in 0.74in;
    }

    @page :left {
      margin-left: 0.5in;
      margin-right: 0.85in;
    }

    @page :right {
      margin-left: 0.85in;
      margin-right: 0.5in;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      color: #1b1d1f;
      background: #fff;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 10.2pt;
      line-height: 1.45;
      text-rendering: optimizeLegibility;
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
  <section class="title-page">
    <p class="title">What Still Hurts</p>
    <p class="subtitle">Echoes of Harmony</p>
    <p class="tagline">Real pain is a threat</p>
  </section>
  <section class="copyright-page">
    <p>Copyright © 2026 Sabino Pereira.<br>All rights reserved.</p>
    <p>This is a work of fiction. Names, characters, places, and events are either products of the author’s imagination or used fictitiously. Any resemblance to actual persons, living or dead, is coincidental.</p>
  </section>
  <section class="epigraph-page">
    <p>What still hurts, still lives.</p>
  </section>
  <main>
${content}
  </main>
</body>
</html>
`;

fs.writeFileSync(outputPath, document, "utf8");
console.log(outputPath);
