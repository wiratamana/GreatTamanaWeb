/* ==========================================================================
   layout.js  -  builds the SAME header and footer on every page.
   Pages only contain:  <div id="site-header"></div> ... <div id="site-footer"></div>
   Also builds the small sticky "Contact / CV" pill (appears after the visitor scrolled down).
   No visible text is written here: every label is a key in i18n/<lang>/common.js.
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};

  /* one gradient id per logo instance (duplicate ids are invalid HTML) */
  function logo(id) {
    return '<svg viewBox="0 0 32 32" aria-hidden="true"><defs><linearGradient id="lg-' + id + '" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7cc7ff"/><stop offset="1" stop-color="#2b8fe0"/></linearGradient></defs>' +
      '<rect x="1.5" y="1.5" width="29" height="29" rx="8" fill="#12161c" stroke="url(#lg-' + id + ')" stroke-width="1.6"/>' +
      '<path d="M9 10h14M16 10v13" stroke="url(#lg-' + id + ')" stroke-width="3" stroke-linecap="round" fill="none"/></svg>';
  }

  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;"); }
  function link(href) { return /^(https?:|mailto:)/.test(href) ? href : GTW.base + href; }
  function activePage() { return GTW.page; }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function today() { var d = new Date(); return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  /* a nav badge ("New") is shown until n.badgeUntil (YYYY-MM-DD), then it disappears by itself */
  function badgeOn(n) { return !!n.badge && (!n.badgeUntil || today() <= n.badgeUntil); }

  function navHtml() {
    var cur = activePage(), s = "";
    GTW.site.nav.forEach(function (n) {
      if (n.children) {
        var on = n.children.some(function (c) { return c.id === cur; });
        s += '<div class="dd' + (on ? " on" : "") + '"><button type="button" aria-haspopup="true" aria-expanded="false" data-i18n="' + n.key + '"></button><div class="dd-menu">';
        n.children.forEach(function (c) {
          s += '<a href="' + c.href + '"' + (c.id === cur ? ' class="on" aria-current="page"' : "") + ' data-i18n="' + c.key + '"></a>';
        });
        s += "</div></div>";
      } else {
        var isOn = n.id === cur || (n.also && n.also.indexOf(cur) >= 0);
        var attrs = ' href="' + n.href + '"' + (isOn ? ' class="on" aria-current="page"' : "");
        if (badgeOn(n)) s += "<a" + attrs + '><span data-i18n="' + n.key + '"></span><span class="badge accent nav-new" data-i18n="' + n.badge + '"></span></a>';
        else s += "<a" + attrs + ' data-i18n="' + n.key + '"></a>';
      }
    });
    return s;
  }

  function header() {
    var el = document.getElementById("site-header");
    if (!el) return;
    var L = GTW.lang;
    el.outerHTML =
      '<header class="site-header"><div class="wrap">' +
      '<a class="brand" href="index.html" aria-label="' + esc(GTW.t("ui.home")) + '">' + logo("head") + "<span>" + esc(GTW.site.name[L] || GTW.site.name.en) + " <small>/ " + esc(GTW.t("brand.sub")) + "</small></span></a>" +
      '<button class="burger" type="button" aria-label="' + esc(GTW.t("ui.menu")) + '" aria-expanded="false">☰</button>' +
      '<nav class="nav" aria-label="' + esc(GTW.t("ui.nav")) + '">' + navHtml() +
      '<div class="lang" role="group" aria-label="' + esc(GTW.t("ui.lang")) + '">' +
      '<button type="button" data-lang="en" aria-pressed="' + (L === "en") + '">EN</button>' +
      '<button type="button" data-lang="ja" aria-pressed="' + (L === "ja") + '">日本語</button></div>' +
      "</nav></div></header>";

    var hd = document.querySelector(".site-header");
    hd.querySelector(".burger").addEventListener("click", function () {
      var nav = hd.querySelector(".nav"), open = nav.classList.toggle("open");
      this.setAttribute("aria-expanded", open);
    });
    var langBtns = hd.querySelectorAll("[data-lang]");
    for (var i = 0; i < langBtns.length; i++) langBtns[i].addEventListener("click", function () {
      if (this.getAttribute("data-lang") !== GTW.lang) GTW.i18n.setLang(this.getAttribute("data-lang"));
    });
    var dds = hd.querySelectorAll(".dd > button");
    for (var j = 0; j < dds.length; j++) dds[j].addEventListener("click", function (e) {
      var dd = this.parentNode, o = dd.classList.toggle("open");
      dd.removeAttribute("data-closed");
      this.setAttribute("aria-expanded", o);
      e.stopPropagation();
    });
    function closeMenus(escape) {
      var all = hd.querySelectorAll(".dd");
      for (var k = 0; k < all.length; k++) {
        var b = all[k].querySelector("button"), had = all[k].classList.contains("open") || all[k].contains(document.activeElement);
        all[k].classList.remove("open");
        b.setAttribute("aria-expanded", "false");
        if (escape && had) {
          all[k].setAttribute("data-closed", "1");   // CSS hides the menu even while it still has hover / focus (until the visitor moves on)
          if (all[k].contains(document.activeElement)) b.focus();
        }
      }
    }
    document.addEventListener("click", function () { closeMenus(false); });
    /* Escape closes the dropdown and gives the focus back to its button */
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeMenus(true); });
    hd.addEventListener("focusin", function (e) {
      var cur = e.target.closest ? e.target.closest(".dd") : null, all = hd.querySelectorAll(".dd[data-closed]");
      for (var k = 0; k < all.length; k++) if (all[k] !== cur) all[k].removeAttribute("data-closed");
    });
    var ddAll = hd.querySelectorAll(".dd");
    for (var m = 0; m < ddAll.length; m++) ddAll[m].addEventListener("mouseleave", function () { this.removeAttribute("data-closed"); });
  }

  /* contact entries: used by footer and the contact blocks */
  var CONTACT_KEYS = ["email", "github", "cv"];
  function contactItems() {
    var c = GTW.site.contacts, out = [];
    CONTACT_KEYS.forEach(function (k) {
      var v = c[k];
      if (v) {
        var href = k === "email" ? "mailto:" + v : link(v);
        var newTab = k === "github" || /\.pdf($|[?#])/i.test(v);
        var inner = k === "cv" ? ' data-i18n="contact.cv.link"' : "";
        var label = k === "cv" ? "" : k === "email" ? esc(v) : esc(v.replace(/^https?:\/\/(www\.)?/, "").replace(/\/$/, ""));
        out.push({ k: k, html: '<a href="' + esc(href) + '"' + (newTab ? ' target="_blank" rel="noopener"' : "") + inner + ">" + label + "</a>" });
      } else if (GTW.site.showPlaceholders) {
        out.push({ k: k, html: '<span class="todo" data-i18n="contact.todo"></span>' });
      }
    });
    return out;
  }
  function contactList(el) {
    var s = "";
    contactItems().forEach(function (i) {
      s += '<li><span class="k" data-i18n="contact.' + i.k + '"></span>' + i.html + "</li>";
    });
    el.innerHTML = s;
  }

  function footer() {
    var el = document.getElementById("site-footer");
    if (!el) return;
    var L = GTW.lang, S = GTW.site, name = esc(S.name[L] || S.name.en);
    var year = new Date().getFullYear();
    var mini = contactItems().filter(function (i) { return /<a /.test(i.html); }).map(function (i) { return "<li>" + i.html + "</li>"; }).join("");
    el.outerHTML =
      '<footer class="site-footer"><div class="wrap">' +
      '<div class="foot-grid">' +
      '<div><a class="brand" href="index.html">' + logo("foot") + "<span>" + name + "</span></a>" +
      '<p class="muted" style="margin-top:.9rem;max-width:34ch" data-i18n="footer.blurb"></p></div>' +
      '<div><h4 data-i18n="footer.h.projects"></h4><ul>' +
      '<li><a href="engine.html" data-i18n="nav.engine.overview"></a></li>' +
      '<li><a href="app.html" data-i18n="nav.app"></a></li>' +
      '<li><a href="journal.html" data-i18n="nav.journal"></a></li>' +
      '<li><a href="gallery.html" data-i18n="nav.gallery"></a></li></ul></div>' +
      '<div><h4 data-i18n="footer.h.engine"></h4><ul>' +
      '<li><a href="world.html" data-i18n="nav.world"></a></li>' +
      '<li><a href="rendering.html" data-i18n="nav.engine.rendering"></a></li>' +
      '<li><a href="clouds.html" data-i18n="nav.engine.clouds"></a></li>' +
      '<li><a href="animation.html" data-i18n="nav.engine.animation"></a></li>' +
      '<li><a href="tools.html" data-i18n="nav.engine.tools"></a></li></ul></div>' +
      '<div><h4 data-i18n="footer.h.contact"></h4><ul>' + mini +
      '<li><a href="about.html#contact" data-i18n="footer.contact.more"></a></li></ul></div>' +
      "</div>" +
      '<div class="foot-note"><p data-i18n="footer.credits"></p>' +
      '<p>© ' + year + " " + name + " · <span data-i18n=\"footer.updated\"></span> " + esc(S.updated) + "</p></div>" +
      "</div></footer>";
  }

  /* sticky "Contact / CV" pill: hidden at the top, shown after 600 px of scrolling.
     Hidden state is visibility:hidden, so it cannot take keyboard focus while invisible. Not printed. */
  function contactPill() {
    if (GTW.page === "cv" || document.querySelector(".cta-pill")) return;
    var c = GTW.site.contacts, parts = "";
    if (c.email) parts += '<a class="btn primary" href="mailto:' + esc(c.email) + '" data-i18n="cta.contact"></a>';
    if (c.cv) parts += '<a class="btn" href="' + esc(link(c.cv)) + '" data-i18n="cta.cv"></a>';
    if (!parts) return;
    var el = document.createElement("div");
    el.className = "cta-pill";
    el.setAttribute("role", "group");
    el.setAttribute("aria-label", GTW.t("cta.label"));
    el.innerHTML = parts;
    document.body.appendChild(el);

    var shown = false, queued = false;
    function update() {
      queued = false;
      var on = (window.pageYOffset || document.documentElement.scrollTop || 0) > 600;
      if (on !== shown) { shown = on; el.classList.toggle("on", on); }
    }
    window.addEventListener("scroll", function () {
      if (queued) return;
      queued = true;
      (window.requestAnimationFrame || setTimeout)(update);
    }, { passive: true });
    update();
  }

  /* notice when the Japanese text is only partly translated */
  function langNote() {
    if (GTW.lang === "en" || !GTW.i18n.missingCount()) return;
    var n = document.createElement("div");
    n.className = "i18n-note";
    n.innerHTML = GTW.t("i18n.partial");
    var h = document.querySelector(".site-header");
    if (h) h.parentNode.insertBefore(n, h.nextSibling);
  }

  /* <span data-repo="engine"></span>  ->  link button when the repo is public, "on request" badge otherwise */
  function repoLinks() {
    var els = document.querySelectorAll("[data-repo]");
    for (var i = 0; i < els.length; i++) {
      var r = GTW.site.repos[els[i].getAttribute("data-repo")];
      if (r && r.public && r.url) els[i].innerHTML = '<a class="btn" href="' + esc(r.url) + '" target="_blank" rel="noopener" data-i18n="ui.source"></a>';
      else els[i].innerHTML = '<span class="badge warn" data-i18n="ui.source.request"></span>';
    }
  }

  GTW.layout = { repoLinks: repoLinks, header: header, footer: footer, contactList: contactList, contactItems: contactItems, contactPill: contactPill, langNote: langNote };
})();
