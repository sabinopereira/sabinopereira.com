#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const oebps = path.resolve(process.argv[2] || "");
if (!oebps || !fs.existsSync(path.join(oebps, "content.opf"))) {
  throw new Error("Usage: node scripts/add_epub3_ncx.mjs /absolute/path/to/OEBPS");
}

const decode = (value) => value
  .replaceAll("&amp;", "&")
  .replaceAll("&lt;", "<")
  .replaceAll("&gt;", ">")
  .replaceAll("&quot;", '"')
  .replaceAll("&#39;", "'");
const escapeXml = (value) => value
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;");

const nav = fs.readFileSync(path.join(oebps, "nav.xhtml"), "utf8");
let opf = fs.readFileSync(path.join(oebps, "content.opf"), "utf8");
const uid = opf.match(/<dc:identifier[^>]*>([^<]+)<\/dc:identifier>/)?.[1];
const title = decode(opf.match(/<dc:title>([^<]+)<\/dc:title>/)?.[1] || "Ebook");
const links = [...nav.matchAll(/<a\s+href="([^"]+)"[^>]*>(.*?)<\/a>/gs)]
  .map((match) => ({ href: match[1], label: decode(match[2].replace(/<[^>]+>/g, "").trim()) }));
if (!uid || links.length === 0) throw new Error("Could not derive EPUB identifier or navigation links");

const points = links.map((link, index) =>
  `<navPoint id="navPoint-${index + 1}" playOrder="${index + 1}"><navLabel><text>${escapeXml(link.label)}</text></navLabel><content src="${escapeXml(link.href)}"/></navPoint>`
).join("");
const ncx = `<?xml version="1.0" encoding="UTF-8"?>\n<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="${escapeXml(uid)}"/><meta name="dtb:depth" content="1"/><meta name="dtb:totalPageCount" content="0"/><meta name="dtb:maxPageNumber" content="0"/></head><docTitle><text>${escapeXml(title)}</text></docTitle><navMap>${points}</navMap></ncx>\n`;
fs.writeFileSync(path.join(oebps, "toc.ncx"), ncx);

if (!opf.includes('id="ncx"')) {
  opf = opf.replace("</manifest>", '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/></manifest>');
}
opf = opf.replace(/<spine(?:\s+[^>]*)?>/, '<spine toc="ncx">');
fs.writeFileSync(path.join(oebps, "content.opf"), opf);
console.log(`Added NCX with ${links.length} entries to ${oebps}`);
