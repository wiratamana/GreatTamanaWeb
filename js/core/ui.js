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

  /* ---------------- lightbox ---------------- */
  var lb;
  function openLb(src, cap) {
    if (!lb) {
      lb = document.createElement("div");
      lb.className = "lb";
      lb.innerHTML = '<button type="button" aria-label="Close">✕</button><img alt=""><div class="cap"></div>';
      document.body.appendChild(lb);
      lb.addEventListener("click", function (e) { if (e.target.tagName !== "IMG") lb.classList.remove("on"); });
      document.addEventListener("keydown", function (e) { if (e.key === "Escape") lb.classList.remove("on"); });
    }
    lb.querySelector("img").src = src;
    lb.querySelector(".cap").innerHTML = cap || "";
    lb.classList.add("on");
  }
  function initLightbox() {
    document.addEventListener("click", function (e) {
      var im = e.target;
      if (im.tagName !== "IMG" || !im.closest(".fig .m")) return;
      var full = im.getAttribute("data-full");
      if (!full) return;
      var fc = im.closest(".fig").querySelector("figcaption");
      openLb(full, fc ? fc.innerHTML : "");
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
    if (!("IntersectionObserver" in window)) return;
    var links = toc.querySelectorAll("a");
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        for (var k = 0; k < links.length; k++) links[k].classList.toggle("on", links[k].getAttribute("href") === "#" + e.target.id);
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    for (var j = 0; j < hs.length; j++) io.observe(hs[j]);
  }

  GTW.ui = { buildAllBars: buildAllBars, buildBars: buildBars, animateBars: animateBars, initLightbox: initLightbox, initReveal: initReveal, initToc: initToc, openLightbox: openLb };
})();
