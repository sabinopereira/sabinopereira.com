(function () {
  function getCopyText(url) {
    return url;
  }

  function getLabels() {
    const isPortuguese = document.documentElement.lang.toLowerCase().startsWith("pt");

    return isPortuguese
      ? {
          permalink: "Link direto",
          copy: "Copiar link",
          copied: "Copiado",
          failed: "Falhou",
          open: "Abrir bug",
          close: "Fechar bug",
          reader: "Leitor de bugs"
        }
      : {
          permalink: "Permalink",
          copy: "Copy link",
          copied: "Copied",
          failed: "Copy failed",
          open: "Open bug",
          close: "Close bug",
          reader: "Bug reader"
        };
  }

  async function copyToClipboard(text, button, labels) {
    const original = button.textContent;

    try {
      await navigator.clipboard.writeText(text);
      button.textContent = labels.copied;
    } catch (error) {
      button.textContent = labels.failed;
    }

    window.setTimeout(() => {
      button.textContent = original;
    }, 1400);
  }

  function initLifeBugShare() {
    const labels = getLabels();
    const entries = document.querySelectorAll(".life-bug-entry[id]");

    entries.forEach((entry) => {
      const header = entry.querySelector(".life-bug-entry-header");

      if (!header || header.querySelector(".life-bug-share")) {
        return;
      }

      const url = new URL(window.location.href);
      url.search = "";
      url.hash = entry.id;

      const share = document.createElement("div");
      share.className = "life-bug-share";

      const permalink = document.createElement("a");
      permalink.href = `#${entry.id}`;
      permalink.className = "life-bug-share-link";
      permalink.textContent = labels.permalink;

      const copy = document.createElement("button");
      copy.type = "button";
      copy.className = "life-bug-share-link";
      copy.textContent = labels.copy;
      copy.addEventListener("click", () => {
        copyToClipboard(getCopyText(url.toString()), copy, labels);
      });

      share.append(permalink, copy);
      header.appendChild(share);
    });

    if (!entries.length) return;

    const index = document.querySelector(".life-bug-index");
    const indexGrid = document.querySelector(".life-bug-index-grid");
    if (!index || !indexGrid) return;

    // The original short list remains a set of featured shortcuts. The full
    // catalogue is generated from the articles so titles never drift apart.
    indexGrid.classList.add("life-bug-index-grid--featured");
    const catalogue = document.createElement("div");
    catalogue.className = "life-bug-catalogue";

    entries.forEach((entry) => {
      const title = entry.querySelector(".life-bug-entry-header .author-section-title");
      const number = entry.id.replace("bug-", "");
      const link = document.createElement("a");
      link.className = "life-bug-card";
      link.href = `#${entry.id}`;
      link.innerHTML = `<span>${number}</span><strong>${title ? title.textContent : entry.id}</strong><small>${labels.open} →</small>`;
      catalogue.appendChild(link);
    });
    index.appendChild(catalogue);

    const reader = document.createElement("div");
    reader.className = "life-bug-reader";
    reader.setAttribute("role", "dialog");
    reader.setAttribute("aria-modal", "true");
    reader.setAttribute("aria-hidden", "true");
    reader.setAttribute("aria-label", labels.reader);

    const readerPanel = document.createElement("div");
    readerPanel.className = "life-bug-reader-panel";
    const close = document.createElement("button");
    close.type = "button";
    close.className = "life-bug-reader-close";
    close.setAttribute("aria-label", labels.close);
    close.textContent = "×";
    readerPanel.appendChild(close);
    reader.appendChild(readerPanel);
    document.body.appendChild(reader);

    entries.forEach((entry) => readerPanel.appendChild(entry));

    let lastTrigger = null;
    function openEntry(id, trigger) {
      const selected = document.getElementById(id);
      if (!selected || !readerPanel.contains(selected)) return;
      lastTrigger = trigger || null;
      entries.forEach((entry) => entry.classList.toggle("is-open", entry === selected));
      reader.classList.add("is-open");
      reader.setAttribute("aria-hidden", "false");
      document.body.classList.add("life-bug-reader-open");
      history.replaceState(null, "", `#${id}`);
      close.focus();
    }

    function closeEntry() {
      reader.classList.remove("is-open");
      reader.setAttribute("aria-hidden", "true");
      entries.forEach((entry) => entry.classList.remove("is-open"));
      document.body.classList.remove("life-bug-reader-open");
      history.replaceState(null, "", `${location.pathname}${location.search}#life-bug-index-title`);
      if (lastTrigger) lastTrigger.focus();
    }

    document.querySelectorAll('a[href^="#bug-"]').forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        openEntry(link.hash.slice(1), link);
      });
    });
    close.addEventListener("click", closeEntry);
    reader.addEventListener("click", (event) => {
      if (event.target === reader) closeEntry();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && reader.classList.contains("is-open")) closeEntry();
    });

    if (/^#bug-\d{3}$/.test(location.hash)) openEntry(location.hash.slice(1));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initLifeBugShare);
  } else {
    initLifeBugShare();
  }
})();
