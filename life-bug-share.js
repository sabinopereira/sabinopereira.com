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
          failed: "Falhou"
        }
      : {
          permalink: "Permalink",
          copy: "Copy link",
          copied: "Copied",
          failed: "Copy failed"
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
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initLifeBugShare);
  } else {
    initLifeBugShare();
  }
})();
