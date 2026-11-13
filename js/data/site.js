/* ==========================================================================
   site.js  -  SITE CONFIG. Edit this first.
   Texts shown to the visitor (labels, headings) are NOT here: see i18n/<lang>/common.js
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};

  GTW.site = {
    /* Name shown in header, footer and page titles (per language) */
    name: { en: "Wira Tamana", ja: "ウィラ タマナ" },
    handle: "wiratamana",
    updated: "2026-11-13",

    /* ---------------- CONTACT: fill these in ----------------
       Empty string = not shown as a link. While showPlaceholders is true, an empty
       entry is shown as a dashed "not set yet" hint, so you do not forget it.
       Set showPlaceholders to false right before you publish. */
    showPlaceholders: false,
    contacts: {
      email:    "wiratamana@icloud.com",
      github:   "https://github.com/wiratamana",
      cv:       ""                                    // e.g. "assets/media/cv-wira-tamana.pdf"
    },

    /* ---------------- REPOSITORIES ----------------
       public:false  -> the site says "source on request" instead of linking.
       Set public:true only when the repository is really public. */
    repos: {
      engine: { url: "https://github.com/wiratamana/GreatTamanaEngine", public: true  },
      app:    { url: "https://github.com/wiratamana/GreatTamanaApp",    public: true  },
      web:    { url: "https://github.com/wiratamana/GreatTamanaWeb",    public: true  }
    },

    /* ---------------- NAVIGATION ----------------
       key = text key in i18n/<lang>/common.js. Add a page: add one entry here. */
    nav: [
      { id: "home", href: "index.html", key: "nav.home" },
      { id: "engine", key: "nav.engine", children: [
        { id: "engine",    href: "engine.html",    key: "nav.engine.overview" },
        { id: "rendering", href: "rendering.html", key: "nav.engine.rendering" },
        { id: "clouds",    href: "clouds.html",    key: "nav.engine.clouds" },
        { id: "animation", href: "animation.html", key: "nav.engine.animation" },
        { id: "tools",     href: "tools.html",     key: "nav.engine.tools" }
      ] },
      { id: "app", href: "app.html", key: "nav.app" },
      { id: "journal", href: "journal.html", key: "nav.journal", also: ["case"] },
      { id: "gallery", href: "gallery.html", key: "nav.gallery" },
      { id: "workflow", href: "workflow.html", key: "nav.workflow" },
      { id: "about", href: "about.html", key: "nav.about" }
    ]
  };
})();
