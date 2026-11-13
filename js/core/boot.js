/* ==========================================================================
   boot.js  -  runs once the page is parsed. The order matters:
     1. layout        header + footer (with data-i18n attributes)
     2. page module   GTW.pages.<page>.init()  builds page specific DOM
     3. repeat        data-repeat blocks   (cards, stats, rows ...)
     4. media         figures / slots / placeholders
     5. bars          before/after bars
     6. i18n          put the texts in
     7. polish        toc, lightbox, reveal, language note
   ========================================================================== */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};

  function boot() {
    try {
      GTW.layout.header();
      GTW.layout.footer();
      var contact = document.querySelectorAll("[data-contact]");
      for (var c = 0; c < contact.length; c++) GTW.layout.contactList(contact[c]);

      GTW.layout.repoLinks();
      var page = GTW.pages[GTW.page];
      if (page && page.init) page.init();

      GTW.repeat.run(document);
      GTW.media.mountAll(document);
      GTW.ui.buildAllBars(document);
      GTW.i18n.apply(document);
      GTW.i18n.setTitleAndMeta();

      GTW.ui.initToc();
      GTW.ui.initLightbox();
      GTW.ui.initReveal();
      GTW.ui.animateBars(document);
      GTW.layout.langNote();
    } catch (e) {
      if (window.console) console.error("[boot]", e);
    }
    document.documentElement.classList.remove("i18n-loading");
    if (location.hash && document.getElementById(location.hash.slice(1))) {
      document.getElementById(location.hash.slice(1)).scrollIntoView();
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
