document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-preview-open]").forEach((trigger) => {
    trigger.addEventListener("click", () => {
      const dialog = document.getElementById(trigger.dataset.previewOpen);

      if (!dialog) {
        return;
      }

      if (typeof dialog.showModal === "function") {
        dialog.showModal();
      } else {
        dialog.setAttribute("open", "");
      }
    });
  });

  document.querySelectorAll("[data-preview-close]").forEach((trigger) => {
    trigger.addEventListener("click", () => {
      trigger.closest("dialog")?.close();
    });
  });

  document.querySelectorAll(".author-preview-dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) {
        dialog.close();
      }
    });
  });
});
