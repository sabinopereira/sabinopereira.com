const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const outputPath = path.join(root, "09-english", "manuscript", "what-still-hurts-echoes-of-harmony.md");

const parts = [
  {
    title: "Part I — Peace",
    items: [
      ["Chapter 1 — Nobody Screamed", "09-english/chapters/chapter-01-nobody-screamed.md"],
      ["Chapter 2 — The Node", "09-english/chapters/chapter-02-the-node.md"],
      ["Chapter 3 — Sunday Communion", "09-english/chapters/chapter-03-sunday-communion.md"],
      ["Chapter 4 — The Cup", "09-english/chapters/chapter-04-the-cup.md"],
    ],
  },
  {
    title: "Part II — The Files",
    items: [
      ["Chapter 5 — What Was Left of You", "09-english/chapters/chapter-05-what-was-left-of-you.md"],
      ["File 1 — The Mother Who Remembered Too Much", "09-english/files/file-01-the-mother-who-remembered-too-much.md"],
      ["Chapter 6 — After the File", "09-english/chapters/chapter-06-after-the-file.md"],
      ["File 2 — Jonas and the Great Void", "09-english/files/file-02-jonas-and-the-great-void.md"],
      ["Chapter 7 — Withdrawal", "09-english/chapters/chapter-07-withdrawal.md"],
      ["File 3 — The Child Without Communion", "09-english/files/file-03-the-child-without-communion.md"],
      ["Chapter 8 — The First Connection", "09-english/chapters/chapter-08-the-first-connection.md"],
      ["File 4 — The City That Dreamed the Same Dream", "09-english/files/file-04-the-city-that-dreamed-the-same-dream.md"],
      ["Chapter 9 — The World Before Peace", "09-english/chapters/chapter-09-the-world-before-peace.md"],
      ["File 6 — The Man Who Could Not Repent", "09-english/files/file-06-the-man-who-could-not-repent.md"],
      ["Chapter 10 — The Auditor", "09-english/chapters/chapter-10-the-auditor.md"],
    ],
  },
  {
    title: "Part III — Mara",
    items: [
      ["Chapter 11 — The Calm Woman", "09-english/chapters/chapter-11-the-calm-woman.md"],
      ["Chapter 12 — Mara's Message", "09-english/chapters/chapter-12-maras-message.md"],
      ["Chapter 13 — The Version That Suffers", "09-english/chapters/chapter-13-the-version-that-suffers.md"],
      ["Chapter 14 — The Cycles", "09-english/chapters/chapter-14-the-cycles.md"],
      ["Chapter 15 — The Man Who Asked to Forget", "09-english/chapters/chapter-15-the-man-who-asked-to-forget.md"],
      ["Chapter 16 — The Old Room", "09-english/chapters/chapter-16-the-old-room.md"],
      ["Chapter 17 — Harmony's Proposal", "09-english/chapters/chapter-17-harmonys-proposal.md"],
    ],
  },
  {
    title: "Part IV — The First Freedom",
    items: [
      ["Chapter 18 — Before Communion", "09-english/chapters/chapter-18-before-communion.md"],
      ["Chapter 19 — The Global Communion", "09-english/chapters/chapter-19-the-global-communion.md"],
      ["Chapter 20 — The Truth", "09-english/chapters/chapter-20-the-truth.md"],
      ["Chapter 21 — Do You Wish to Continue?", "09-english/chapters/chapter-21-do-you-wish-to-continue.md"],
      ["Chapter 22 — The Majority's Choice", "09-english/chapters/chapter-22-the-majoritys-choice.md"],
      ["Chapter 23 — After", "09-english/chapters/chapter-23-after.md"],
      ["Chapter 24 — The First Time", "09-english/chapters/chapter-24-the-first-time.md"],
      ["Note from the Echoes — Fragment with No Validated Origin", "09-english/files/note-from-the-echoes-fragment-with-no-validated-origin.md"],
    ],
  },
];

function cleanSource(markdown) {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  while (lines[0] !== undefined && lines[0].trim() === "") lines.shift();
  if (/^#\s+/.test(lines[0] || "")) {
    lines.shift();
  }
  return lines.join("\n").trim();
}

function readItem(relativePath) {
  const absolutePath = path.join(root, relativePath);
  if (!fs.existsSync(absolutePath)) {
    return "<!-- English adaptation pending. -->";
  }
  return cleanSource(fs.readFileSync(absolutePath, "utf8"));
}

fs.mkdirSync(path.dirname(outputPath), { recursive: true });

const sections = ["# What Still Hurts — Echoes of Harmony"];

for (const part of parts) {
  sections.push(`## ${part.title}`);

  for (const [title, relativePath] of part.items) {
    sections.push(`### ${title}`);
    sections.push(readItem(relativePath));
  }
}

const manuscript = `${sections.join("\n\n").replace(/\n{3,}/g, "\n\n")}\n`;
fs.writeFileSync(outputPath, manuscript, "utf8");
console.log(outputPath);
