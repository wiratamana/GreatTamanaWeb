/* ==========================================================================
   ui.js  -  small behaviours shared by all pages:
   lightbox, reveal on scroll, before/after bars, side table of contents.
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;"); }
  function has(k) { return GTW.i18n.has(k); }
  function raw(k) { return GTW.i18n.dict.en[k] != null ? GTW.i18n.dict.en[k] : ""; }

  /* ---------------- bars ----------------
     Static:  <div class="bars" data-bars="case.culling.bars"></div>
       keys:  <p>.title  <p>.N.lab (text)  <p>.N.b (before)  <p>.N.a (after)  <p>.N.u (unit)
     Smaller number = better. Each row has its own scale. */
  function buildBars(el) {
    var p = el.getAttribute("data-bars");
    if (el.getAttribute("data-built")) return;
    el.setAttribute("data-built", "1");
    el.classList.add("bars");
    var s = has(p + ".title") ? '<h4 data-i18n="' + p + '.title"></h4>' : "";
    for (var i = 1; has(p + "." + i + ".lab"); i++) {
      var q = p + "." + i, b = parseFloat(raw(q + ".b")), a = parseFloat(raw(q + ".a")), u = raw(q + ".u");
      var max = Math.max(b, a) || 1;
      s += '<div class="bar-row"><div class="lab" data-i18n="' + q + '.lab"></div><div class="bar-pair">' +
        '<div class="bar before"><i data-w="' + (b / max * 100).toFixed(1) + '"></i><b>' + esc(raw(q + ".b")) + " " + esc(u) + "</b></div>" +
        '<div class="bar after"><i data-w="' + (a / max * 100).toFixed(1) + '"></i><b>' + esc(raw(q + ".a")) + " " + esc(u) + "</b></div>" +
        "</div></div>";
    }
    s += '<div class="legend"><span class="b" data-i18n="ui.before"></span><span class="a" data-i18n="ui.after"></span></div>';
    el.innerHTML = s;
  }
  function buildAllBars(root) {
    var l = (root || document).querySelectorAll("[data-bars]");
    for (var i = 0; i < l.length; i++) buildBars(l[i]);
  }
  function animateBars(root) {
    var bars = (root || document).querySelectorAll(".bar > i[data-w]");
    function fill(i) { i.style.width = i.getAttribute("data-w") + "%"; }
    if (STATIC || !("IntersectionObserver" in window)) { for (var k = 0; k < bars.length; k++) fill(bars[k]); return; }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { fill(e.target); io.unobserve(e.target); } });
    }, { threshold: 0.3 });
    for (var j = 0; j < bars.length; j++) io.observe(bars[j]);
    setTimeout(function () { for (var m = 0; m < bars.length; m++) fill(bars[m]); }, 3500);
  }

  /* ---------------- lightbox ----------------
     Accessible: role=dialog + aria-modal, focus moves to the close button, Tab is trapped, Escape closes,
     focus goes back to the picture that opened it. Pictures are keyboard focusable (media.js: Enter or Space opens). */
  var lb, lbOpener = null;
  function closeLb() {
    if (!lb || !lb.classList.contains("on")) return;
    lb.classList.remove("on");
    if (lbOpener && lbOpener.focus) lbOpener.focus();
    lbOpener = null;
  }
  function openLb(src, cap) {
    if (!lb) {
      lb = document.createElement("div");
      lb.className = "lb";
      lb.setAttribute("role", "dialog");
      lb.setAttribute("aria-modal", "true");
      lb.setAttribute("aria-label", GTW.t("ui.zoom"));
      lb.innerHTML = '<button type="button" aria-label="' + esc(GTW.t("ui.close")) + '">✕</button><img alt=""><div class="cap"></div>';
      document.body.appendChild(lb);
      lb.addEventListener("click", function (e) { if (e.target.tagName !== "IMG") closeLb(); });
      document.addEventListener("keydown", function (e) {
        if (!lb.classList.contains("on")) return;
        if (e.key === "Escape") { e.preventDefault(); closeLb(); }
        else if (e.key === "Tab") { e.preventDefault(); lb.querySelector("button").focus(); }   // the close button is the only control: keep focus on it
      });
    }
    lbOpener = document.activeElement && document.activeElement !== document.body ? document.activeElement : null;
    lb.querySelector("img").src = src;
    lb.querySelector(".cap").innerHTML = cap || "";
    lb.classList.add("on");
    lb.querySelector("button").focus();
  }
  function initLightbox() {
    function open(im) {
      var full = im.getAttribute("data-full");
      if (!full) return;
      var fc = im.closest(".fig").querySelector("figcaption");
      openLb(full, fc ? fc.innerHTML : "");
    }
    document.addEventListener("click", function (e) {
      var im = e.target;
      if (im.tagName !== "IMG" || !im.closest(".fig .m")) return;
      open(im);
    });
    document.addEventListener("keydown", function (e) {
      var im = e.target;
      if ((e.key === "Enter" || e.key === " ") && im && im.tagName === "IMG" && im.closest && im.closest(".fig .m") && im.getAttribute("data-full")) {
        e.preventDefault();
        open(im);
      }
    });
  }

  /* ---------------- reveal on scroll ---------------- */
  var REVEAL = ".card, .metric, .fig, .callout, .flow, .layers, .bars, .dl, .table-wrap, .timeline, .stat";
  var STATIC = /[?&]static=1/.test(location.search);   // ?static=1 turns animations off (used by tools/smoke_test.py)
  function initReveal() {
    if (STATIC || !("IntersectionObserver" in window)) return;
    var els = document.querySelectorAll(REVEAL), io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.05 });
    for (var i = 0; i < els.length; i++) { els[i].classList.add("rv"); io.observe(els[i]); }
    setTimeout(function () { for (var j = 0; j < els.length; j++) els[j].classList.add("in"); }, 3000);
  }

  /* ---------------- side table of contents ---------------- */
  function initToc() {
    var toc = document.getElementById("toc");
    if (!toc) return;
    var hs = document.querySelectorAll(".page-grid h2[id]");
    if (!hs.length) { toc.style.display = "none"; return; }
    var s = '<h4 data-i18n="ui.toc"></h4>';
    for (var i = 0; i < hs.length; i++) s += '<a href="#' + hs[i].id + '">' + hs[i].textContent + "</a>";
    toc.innerHTML = s;
    GTW.i18n.apply(toc);
    document.querySelector(".page-grid").classList.add("has-toc");
    var links = toc.querySelectorAll("a");
    /* on phones the list is a horizontal row of chips (css/base.css): keep the current chip in view. On desktop nothing is wider than the box, so this does nothing. */
    function showChip(a) {
      if (toc.scrollWidth <= toc.clientWidth + 2) return;
      toc.scrollLeft = Math.max(0, a.offsetLeft - (toc.clientWidth - a.offsetWidth) / 2);
    }
    /* scroll spy: the current section = the last heading that has reached a line a little below the header.
       (An IntersectionObserver band missed the heading after a jump from the list: the jump puts the heading above the band, so no entry was marked.) */
    var header = document.querySelector(".site-header"), current = null, queued = false;
    function spy() {
      queued = false;
      var line = (header ? header.offsetHeight : 64) + 120, cur = null;
      for (var j = 0; j < hs.length; j++) { if (hs[j].getBoundingClientRect().top <= line) cur = hs[j]; else break; }
      if (cur === current) return;
      current = cur;
      for (var k = 0; k < links.length; k++) {
        var on = !!cur && links[k].getAttribute("href") === "#" + cur.id;
        links[k].classList.toggle("on", on);
        if (on) showChip(links[k]);
      }
    }
    window.addEventListener("scroll", function () {
      if (queued) return;
      queued = true;
      (window.requestAnimationFrame || setTimeout)(spy);
    }, { passive: true });
    window.addEventListener("resize", spy);
    spy();
  }

  GTW.ui = { buildAllBars: buildAllBars, buildBars: buildBars, animateBars: animateBars, initLightbox: initLightbox, initReveal: initReveal, initToc: initToc, openLightbox: openLb };
})();
