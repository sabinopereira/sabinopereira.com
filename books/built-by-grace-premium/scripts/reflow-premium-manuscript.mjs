import fs from "node:fs";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const sourcePath = path.join(root, "build", "built-by-grace-source-manuscript.md");
const outputPath = path.join(root, "build", "built-by-grace-premium-manuscript.md");

const source = fs.readFileSync(sourcePath, "utf8").replace(/\r\n/g, "\n");
const blocks = source.split(/\n{2,}/).map((block) => block.trim()).filter(Boolean);

const output = [];
let proseBuffer = [];
let protectedMode = false;
let inClosing = false;
let frontMatterProtected = false;

function words(text) {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

function isHeading(block) {
  return /^#{1,6}\s/.test(block);
}

function isStructural(block) {
  return isHeading(block) || block === "\\pagebreak";
}

function normalizeProse(block) {
  return block
    .replace(/ {2,}\n/g, " ")
    .replace(/\n+/g, " ")
    .replace(/\s{2,}/g, " ")
    .trim();
}

function flushProse() {
  if (!proseBuffer.length) return;

  let paragraph = "";
  let sentenceCount = 0;
  for (const item of proseBuffer) {
    const itemWords = words(item);
    const itemSentences = (item.match(/[.!?](?:[\"'”’)]|$)/g) || []).length || 1;
    const wouldBeLong = words(paragraph) + itemWords > 105;
    const wouldBeDense = sentenceCount + itemSentences > 5 && words(paragraph) >= 45;

    if (paragraph && (wouldBeLong || wouldBeDense)) {
      output.push(paragraph);
      paragraph = "";
      sentenceCount = 0;
    }

    paragraph = paragraph ? `${paragraph} ${item}` : item;
    sentenceCount += itemSentences;
  }

  if (paragraph) output.push(paragraph);
  proseBuffer = [];
}

function shouldStandAlone(block, nextBlock) {
  const text = normalizeProse(block);
  if (!text) return true;
  if (text.endsWith(":")) return true;
  if (/^(Amen\.?|By grace\.?|But always\.|And still\.|Maybe\.|Because\.|Listen\.)$/i.test(text)) return true;
  if (/^([“\"])?God,/.test(text) && words(text) < 18) return true;
  if (nextBlock && isStructural(nextBlock)) return words(text) <= 16;
  return false;
}

for (let index = 0; index < blocks.length; index += 1) {
  const block = blocks[index];
  const nextBlock = blocks[index + 1];

  if (isStructural(block)) {
    flushProse();
    output.push(block);

    if (/^# Closing\b/.test(block)) inClosing = true;
    if (/^## (Copyright|Dedication)\b/.test(block)) frontMatterProtected = true;
    if (/^## Author's Note\b/.test(block)) frontMatterProtected = false;
    if (/^# (Chapter|Bonus Reflection)\b/.test(block)) {
      protectedMode = false;
      inClosing = false;
    }
    if (/^### Prayer\b/.test(block)) protectedMode = true;
    if (/^### Closing Thought\b/.test(block)) protectedMode = true;
    continue;
  }

  if (protectedMode || inClosing || frontMatterProtected) {
    flushProse();
    output.push(block);
    continue;
  }

  const text = normalizeProse(block);
  if (shouldStandAlone(block, nextBlock)) {
    flushProse();
    output.push(text);
  } else {
    proseBuffer.push(text);
  }
}

flushProse();

const premiumNote = [
  "## Premium Edition",
  "",
  "This premium edition has been refined for a more immersive reading experience. The reflective voice and prayerful cadence remain, while the narrative passages have been shaped into fuller prose so the journey can breathe with greater clarity, warmth, and depth.",
  "",
  "The prayers, blessings, and intentional litanies retain their spacious form.",
  "",
  "\\pagebreak",
].join("\n");

const copyrightIndex = output.findIndex((block) => block === "## Copyright");
if (copyrightIndex >= 0) {
  const insertAt = output.findIndex((block, index) => index > copyrightIndex && block === "\\pagebreak");
  if (insertAt >= 0) output.splice(insertAt + 1, 0, premiumNote);
}

const finalText = output
  .join("\n\n")
  .replaceAll("God at the center", "God in the center")
  .replaceAll("God at the Center", "God in the Center");

fs.writeFileSync(outputPath, `${finalText}\n`, "utf8");
console.log(`Wrote ${outputPath}`);
