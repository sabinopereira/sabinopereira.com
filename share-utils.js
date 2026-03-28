(function () {
  function buildShareLinks(title, url) {
    const text = title ? `${title} — ${url}` : url;
    return {
      text,
      x: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
      whatsapp: `https://wa.me/?text=${encodeURIComponent(text)}`
    };
  }

  async function copyText(text, control) {
    const originalText = control.textContent;

    try {
      await navigator.clipboard.writeText(text);
      control.textContent = "Copied";
    } catch (error) {
      control.textContent = "Copy failed";
    }

    window.setTimeout(() => {
      control.textContent = originalText;
    }, 1400);
  }

  function wireShareControls(container, links) {
    container.querySelectorAll("[data-share]").forEach((control) => {
      const type = control.dataset.share;

      if (type === "copy") {
        control.dataset.copyText = links.text;

        if (!control.dataset.copyBound) {
          control.addEventListener("click", () => copyText(control.dataset.copyText || "", control));
          control.dataset.copyBound = "true";
        }
        return;
      }

      if (links[type]) {
        control.href = links[type];
        control.target = "_blank";
        control.rel = "noopener";
      }
    });
  }

  function createInlineShareBlock(label) {
    const share = document.createElement("div");
    share.className = "share-inline";
    share.innerHTML = `
      <span class="share-inline-label">${label}</span>
      <div class="share-inline-actions">
        <a href="#" class="share-inline-link" data-share="x">X</a>
        <a href="#" class="share-inline-link" data-share="linkedin">LinkedIn</a>
        <a href="#" class="share-inline-link" data-share="whatsapp">WhatsApp</a>
        <button type="button" class="share-inline-link" data-share="copy">Copy link</button>
      </div>
    `;
    return share;
  }

  window.ShareUtils = {
    buildShareLinks,
    wireShareControls,
    createInlineShareBlock
  };
})();
