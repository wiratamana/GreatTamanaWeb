/* ==========================================================================
   loader.js  -  the ONLY script a page includes (in <head>).

   It decides the language and then loads, in order and synchronously:
     1. core/i18n.js                      translation engine
     2. i18n/en/<bundle>.js               English texts (always, it is the fallback)
     3. i18n/ja/<bundle>.js               Japanese texts (only when language = ja)
     4. data/site.js + core modules       site config, layout, media, ui, repeat
     5. <page scripts>                    from <html data-scripts="data/cases,pages/home">
     6. core/boot.js                      starts everything on DOMContentLoaded

   A page declares what it needs on the <html> tag:
     <html lang="en" data-page="home" data-bundles="common,home,cases" data-scripts="data/cases,pages/home">

   Bundle name "cases" expands to all case-study text files.
   Synchronous document.write is used on purpose: it works from file:// too,
   needs no build step and avoids a flash of untranslated text.
   ========================================================================== */
(function () {
  var d = document, root = d.documentElement;
  var GTW = window.GTW = window.GTW || {};
  var me = d.currentScript;
  var base = me ? me.src.replace(/js\/core\/loader\.js[^]*$/, "") : "";
  GTW.base = base;
  GTW.page = root.getAttribute("data-page") || "";

  /* ---- language: ?lang=xx  >  saved choice  >  browser language (ja -> ja, anything else -> en) ---- */
  var SUPPORTED = ["en", "ja"];
  var lang = "en", saved = null;
  try { saved = localStorage.getItem("gtw.lang"); } catch (e) {}
  var m = /[?&]lang=([a-z]{2})/.exec(location.search);
  if (m && SUPPORTED.indexOf(m[1]) >= 0) {
    lang = m[1];
    try { localStorage.setItem("gtw.lang", lang); } catch (e) {}
  } else if (saved && SUPPORTED.indexOf(saved) >= 0) {
    lang = saved;
  } else {
    var nav = (navigator.languages && navigator.languages[0]) || navigator.language || "";
    if (/^ja/i.test(nav)) lang = "ja";   // first visit: follow the browser language
  }
  GTW.lang = lang;
  GTW.langs = SUPPORTED;
  root.setAttribute("lang", lang);
  root.classList.add("js", "i18n-loading");
  /* safety: never leave the page hidden */
  setTimeout(function () { root.classList.remove("i18n-loading"); }, 2500);

  /* ---- bundles ---- */
  var CASE_BUNDLES = ["cases-perf", "cases-anim", "cases-look", "cases-tools", "cases-cloud"];
  var wanted = (root.getAttribute("data-bundles") || "common").split(",");
  var bundles = [];
  wanted.forEach(function (b) {
    b = b.trim();
    if (!b) return;
    if (b === "cases") CASE_BUNDLES.forEach(function (c) { bundles.push(c); });
    else bundles.push(b);
  });
  if (bundles.indexOf("common") < 0) bundles.unshift("common");
  if (bundles.indexOf("slots") < 0) bundles.push("slots");
  GTW.bundles = bundles;

  function w(path) { d.write('<script src="' + base + path + '"><\/script>'); }

  w("js/core/i18n.js");
  bundles.forEach(function (b) { w("i18n/en/" + b + ".js"); });
  if (lang !== "en") bundles.forEach(function (b) { w("i18n/" + lang + "/" + b + ".js"); });

  ["data/site", "core/media", "core/repeat", "core/ui", "core/layout"].forEach(function (s) { w("js/" + s + ".js"); });
  (root.getAttribute("data-scripts") || "").split(",").forEach(function (s) {
    s = s.trim();
    if (s) w("js/" + s + ".js");
  });
  w("js/core/boot.js");
})();
