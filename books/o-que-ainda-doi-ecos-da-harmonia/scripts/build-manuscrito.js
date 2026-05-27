const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const outputPath = path.join(root, "08-manuscrito", "o-que-ainda-doi-ecos-da-harmonia.md");

const parts = [
  {
    title: "Parte I — A Paz",
    items: [
      ["Capítulo 1 — Ninguém Gritava", "06-capitulos/capitulo-01-ninguem-gritava.md"],
      ["Capítulo 2 — O Nó", "06-capitulos/capitulo-02-o-no.md"],
      ["Capítulo 3 — A Comunhão de Domingo", "06-capitulos/capitulo-03-a-comunhao-de-domingo.md"],
      ["Capítulo 4 — A Chávena", "06-capitulos/capitulo-04-a-chavena.md"],
    ],
  },
  {
    title: "Parte II — Os Ficheiros",
    items: [
      ["Capítulo 5 — O Que Sobrou de Ti", "06-capitulos/capitulo-05-o-que-sobrou-de-ti.md"],
      ["Ficheiro 1 — A Mãe que Lembrava Demais", "05-ficheiros-proibidos/ficheiro-01-a-mae-que-lembrava-demais.md"],
      ["Capítulo 6 — Depois do Ficheiro", "06-capitulos/capitulo-06-depois-do-ficheiro.md"],
      ["Ficheiro 2 — Jonas e o Grande Vazio", "05-ficheiros-proibidos/ficheiro-02-jonas-e-o-grande-vazio.md"],
      ["Capítulo 7 — Abstinência", "06-capitulos/capitulo-07-abstinencia.md"],
      ["Ficheiro 3 — A Criança Sem Comunhão", "05-ficheiros-proibidos/ficheiro-03-a-crianca-sem-comunhao.md"],
      ["Capítulo 8 — A Primeira Ligação", "06-capitulos/capitulo-08-a-primeira-ligacao.md"],
      ["Ficheiro 4 — A Cidade que Sonhou o Mesmo Sonho", "05-ficheiros-proibidos/ficheiro-04-a-cidade-que-sonhou-o-mesmo-sonho.md"],
      ["Capítulo 9 — O Mundo Antes da Paz", "06-capitulos/capitulo-09-o-mundo-antes-da-paz.md"],
      ["Ficheiro 6 — O Homem que Não Pôde Arrepender-se", "05-ficheiros-proibidos/ficheiro-06-o-homem-que-nao-pode-arrepender-se.md"],
      ["Capítulo 10 — O Auditor", "06-capitulos/capitulo-10-o-auditor.md"],
    ],
  },
  {
    title: "Parte III — Mara",
    items: [
      ["Capítulo 11 — A Mulher Calma", "06-capitulos/capitulo-11-a-mulher-calma.md"],
      ["Capítulo 12 — A Mensagem de Mara", "06-capitulos/capitulo-12-a-mensagem-de-mara.md"],
      ["Capítulo 13 — A Versão que Sofre", "06-capitulos/capitulo-13-a-versao-que-sofre.md"],
      ["Capítulo 14 — Os Ciclos", "06-capitulos/capitulo-14-os-ciclos.md"],
      ["Capítulo 15 — O Homem que Pediu Para Esquecer", "06-capitulos/capitulo-15-o-homem-que-pediu-para-esquecer.md"],
      ["Capítulo 16 — A Sala Antiga", "06-capitulos/capitulo-16-a-sala-antiga.md"],
      ["Capítulo 17 — A Proposta da Harmonia", "06-capitulos/capitulo-17-a-proposta-da-harmonia.md"],
    ],
  },
  {
    title: "Parte IV — A Primeira Liberdade",
    items: [
      ["Capítulo 18 — Antes da Comunhão", "06-capitulos/capitulo-18-antes-da-comunhao.md"],
      ["Capítulo 19 — A Comunhão Global", "06-capitulos/capitulo-19-a-comunhao-global.md"],
      ["Capítulo 20 — A Verdade", "06-capitulos/capitulo-20-a-verdade.md"],
      ["Capítulo 21 — Desejam Continuar?", "06-capitulos/capitulo-21-desejam-continuar.md"],
      ["Capítulo 22 — A Escolha da Maioria", "06-capitulos/capitulo-22-a-escolha-da-maioria.md"],
      ["Capítulo 23 — Depois", "06-capitulos/capitulo-23-depois.md"],
      ["Capítulo 24 — Na Primeira Vez", "06-capitulos/capitulo-24-na-primeira-vez.md"],
      ["Nota dos Ecos — Fragmento sem origem validada", "05-ficheiros-proibidos/nota-dos-ecos-fragmento-sem-origem-validada.md"],
    ],
  },
];

function cleanSource(markdown) {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");

  while (lines[0] !== undefined && lines[0].trim() === "") lines.shift();
  if (/^#\s+O Que Ainda Dói/.test(lines[0] || "")) {
    lines.shift();
  }

  let removedHeadings = 0;
  while (removedHeadings < 3) {
    while (lines[0] !== undefined && lines[0].trim() === "") lines.shift();
    if (/^#{1,2}\s+/.test(lines[0] || "")) {
      lines.shift();
      removedHeadings += 1;
      continue;
    }
    break;
  }

  return lines.join("\n").trim();
}

function readItem(relativePath) {
  if (!relativePath) {
    return "<!-- Texto integral ainda não integrado no projeto. -->";
  }

  const absolutePath = path.join(root, relativePath);
  return cleanSource(fs.readFileSync(absolutePath, "utf8"));
}

const sections = ["# O Que Ainda Dói — Ecos da Harmonia"];

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
