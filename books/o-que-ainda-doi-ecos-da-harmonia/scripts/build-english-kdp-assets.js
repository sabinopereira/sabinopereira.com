const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const root = path.resolve(__dirname, "..");
const manuscriptPath = path.join(root, "09-english", "manuscript", "what-still-hurts-echoes-of-harmony.md");
const coverPath = path.join(root, "images", "optimized", "what-still-hurts-cover.png");
const outDir = path.join(root, "output", "kdp-en");
const epubDir = path.join(outDir, "epub-src");
const oebpsDir = path.join(epubDir, "OEBPS");
const textDir = path.join(oebpsDir, "text");
const stylesDir = path.join(oebpsDir, "styles");
const imagesDir = path.join(oebpsDir, "images");

const title = "What Still Hurts";
const subtitle = "Echoes of Harmony";
const fullTitle = `${title} — ${subtitle}`;
const author = "Sabino Pereira";
const language = "en";
const identifier = "urn:uuid:92a4e1d5-e78e-4c46-94b8-5f7b16bcbaf5";

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
  if (/^[A-Z0-9 .:%/—'-]+$/.test(text) && text.length < 100) {
    return "screen";
  }

  if (/^(Classification|Main subject|Integrated dependent|Associated event|Risk assigned|Final state|Pedagogical use|Location|Affected population|Intervention applied|Associated victim|Age at first record):/.test(text)) {
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
  files.push({ id: "cover", href: "text/cover.xhtml", title: "Cover", level: 3 });
  fs.writeFileSync(path.join(textDir, "cover.xhtml"), `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="${language}" xml:lang="${language}">
<head><title>Cover</title><link rel="stylesheet" type="text/css" href="../styles/book.css"/></head>
<body><section class="cover"><img src="../images/cover.png" alt="${escapeHtml(fullTitle)}"/></section></body>
</html>
`, "utf8");

  const frontMatter = [
    { id: "title-page", href: "text/title-page.xhtml", title: "Title Page", body: `<section class="frontmatter"><p class="frontmatter-title">${escapeHtml(title)}</p><p class="frontmatter-subtitle">${escapeHtml(subtitle)}</p><p class="frontmatter-author">${escapeHtml(author)}</p></section>` },
    { id: "copyright", href: "text/copyright.xhtml", title: "Copyright", body: `<section class="frontmatter"><p class="frontmatter-text">Copyright © 2026 ${escapeHtml(author)}.<br/>All rights reserved.</p><p class="frontmatter-text">This is a work of fiction. Names, characters, places, and events are either products of the author’s imagination or used fictitiously. Any resemblance to actual persons, living or dead, is coincidental.</p></section>` },
    { id: "epigraph", href: "text/epigraph.xhtml", title: "Epigraph", body: `<section class="frontmatter"><p class="epigraph-text">What still hurts, still lives.</p></section>` },
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
    <dc:description>A psychological dystopian novel about memory, comfort, and the price of painless peace.</dc:description>
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
<head><title>Contents</title><link rel="stylesheet" type="text/css" href="styles/book.css"/></head>
<body>
<nav epub:type="toc">
  <h1>Contents</h1>
  <ol>
${navItems}
  </ol>
</nav>
</body>
</html>
`, "utf8");

  const epubPath = path.join(outDir, "what-still-hurts-echoes-of-harmony-kindle.epub");
  fs.rmSync(epubPath, { force: true });
  execFileSync("zip", ["-X0", epubPath, "mimetype"], { cwd: epubDir, stdio: "ignore" });
  execFileSync("zip", ["-Xr9D", epubPath, "META-INF", "OEBPS"], { cwd: epubDir, stdio: "ignore" });
  return epubPath;
}

function writeMetadata() {
  const metadataPath = path.join(outDir, "kdp-metadata.md");
  fs.writeFileSync(metadataPath, `# KDP Metadata

## Title
What Still Hurts

## Subtitle
Echoes of Harmony

## Author
${author}

## Short Description
A psychological dystopian novel about memory, comfort, and the price of painless peace.

## Long Description
In Harmony, nobody screamed.

Elias lives in a city where pain is no longer private. Harmony anticipates crises, softens memories, accompanies grief, and makes sure no mind suffers alone. The world appears saved.

Until a cracked cup opens the first flaw.

As he investigates forbidden files, Elias discovers mothers relieved until they forgot their children, cities that traded guilt for peace, criminals cured at the cost of remorse, and citizens who tried to live outside the network only to discover that freedom itself can be unbearable.

But the strongest evidence against Harmony is not in the archives.

It is him.

What Still Hurts — Echoes of Harmony is a psychological dystopian thriller about memory, love, guilt, and the most dangerous question of all: is freedom worth it if almost no one can bear it?

## Sales Lines
- In Harmony, nobody screamed.
- What still hurts, still lives.
- Peace had archives.
- Maybe freedom is the right for help to wait one second before saving us.

## Suggested Categories
- Dystopian Science Fiction
- Psychological Thriller
- Literary / Speculative Fiction

## Suggested Keywords
psychological dystopia, artificial intelligence, memory, freedom, philosophical thriller, speculative fiction, emotional control

## Suggested Pricing
eBook: €3.99 or €4.99
Paperback: calculate inside KDP after uploading the interior; likely range €12.99 to €16.99 depending on print cost and marketplace.

## Technical Notes
The EPUB file is for Kindle eBook upload. The paperback PDF is a 6x9 interior without cover. For KDP paperback, the cover needs a full wraparound file with spine and back cover, calculated after trim size, paper, ink, and final page count are confirmed.

Official paperback cover calculator:
https://kdp.amazon.com/cover-templates
`, "utf8");
  return metadataPath;
}

ensureDir(outDir);
const manuscript = fs.readFileSync(manuscriptPath, "utf8");
const blocks = markdownBlocks(manuscript);
const epubPath = writeEpub(blocks);
const metadataPath = writeMetadata();
fs.copyFileSync(coverPath, path.join(outDir, "front-cover.png"));

console.log(epubPath);
console.log(metadataPath);
console.log(path.join(outDir, "front-cover.png"));
