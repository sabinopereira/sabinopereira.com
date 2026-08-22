window.dataLayer = window.dataLayer || [];

function gtag() {
  window.dataLayer.push(arguments);
}

window.gtag = window.gtag || gtag;
window.gtag("js", new Date());
window.gtag("config", "G-KEVDEH8PGZ");

window.trackEvent = function trackEvent(name, params = {}) {
  if (typeof window.gtag !== "function") {
    return;
  }

  window.gtag("event", name, params);
};

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('a[href="/quiet-power-assessment.html"]').forEach((link) => {
    link.addEventListener("click", () => {
      window.trackEvent("assessment_cta_click", {
        page_path: window.location.pathname,
        link_text: (link.textContent || "").trim()
      });
    });
  });

  document.querySelectorAll("[data-tool-name]").forEach((link) => {
    link.addEventListener("click", () => {
      window.trackEvent("quiet_power_tool_click", {
        page_path: window.location.pathname,
        tool_name: link.dataset.toolName || "",
        link_type: link.dataset.toolLinkType || "",
        source: link.dataset.toolSource || "",
        destination_host: link.hostname || "",
        link_text: (link.textContent || "").trim()
      });
    });
  });

  document.querySelectorAll('a[href*="fourthwall.com"]').forEach((link) => {
    link.addEventListener("click", () => {
      const url = new URL(link.href, window.location.origin);
      const linkText = (link.textContent || "").trim();

      window.trackEvent("fourthwall_click", {
        page_path: window.location.pathname,
        page_title: document.title,
        link_text: linkText,
        destination_host: url.hostname,
        destination_path: url.pathname,
        destination_url: url.href,
        product_slug: url.pathname.split("/").filter(Boolean).pop() || "",
        outbound_type: "digital_product"
      });
    });
  });

  document.querySelectorAll('a[href^="http"]').forEach((link) => {
    link.addEventListener("click", () => {
      const url = new URL(link.href, window.location.origin);
      if (url.hostname === window.location.hostname) {
        return;
      }

      const platformMap = [
        ["spotify.com", "spotify"],
        ["music.apple.com", "apple_music"],
        ["youtube.com", "youtube"],
        ["youtu.be", "youtube"],
        ["instagram.com", "instagram"],
        ["tiktok.com", "tiktok"],
        ["amazon.", "amazon"],
        ["fourthwall.com", "fourthwall"],
        ["x.com", "x"]
      ];
      const match = platformMap.find(([host]) => url.hostname.includes(host));

      window.trackEvent("outbound_platform_click", {
        page_path: window.location.pathname,
        page_title: document.title,
        link_text: (link.textContent || "").trim(),
        platform: match ? match[1] : "other",
        destination_host: url.hostname,
        destination_path: url.pathname
      });
    });
  });
});
