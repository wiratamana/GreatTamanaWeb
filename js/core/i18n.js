/* ==========================================================================
   i18n.js  -  tiny translation engine.

   Text files call:   GTW.i18n.add("en", { "home.hero.title": "..." });
   HTML uses:         <h1 data-i18n="home.hero.title"></h1>
                      <img data-i18n-attr="alt:some.key; title:other.key">
   Code uses:         GTW.t("key")  or  GTW.t("key", { n: 3 })   ->  "... {n} ..."

   Lookup order: current language -> English -> the key itself (and a console warning).
   Texts may contain simple inline HTML (<b>, <code>, <a>). They are written by the site owner only.
   Keys ending in .href .img .ic .tagc .hl .slot are NOT text (links, icons, flags): they live in the
   English file only and are never translated.
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};
  var dict = { en: {}, ja: {} };
  var missing = {};       // keys that fell back to English while language != en
  var warned = {};

  function add(lang, obj) {
    var t = dict[lang] || (dict[lang] = {});
    for (var k in obj) if (Object.prototype.hasOwnProperty.call(obj, k)) {
      if (obj[k] !== "" && obj[k] != null) t[k] = obj[k];   // empty string = "not translated yet"
    }
  }
  function has(key) { return dict[GTW.lang] && dict[GTW.lang][key] != null || dict.en[key] != null; }
  function raw(key) {
    var v = dict[GTW.lang] && dict[GTW.lang][key];
    if (v != null) return v;
    v = dict.en[key];
    if (v != null) { if (GTW.lang !== "en") missing[key] = 1; return v; }
    if (!warned[key]) { warned[key] = 1; if (window.console) console.warn("[i18n] missing key:", key); }
    return key;
  }
  function t(key, params) {
    var s = raw(key);
    if (params) s = s.replace(/\{(\w+)\}/g, function (m, p) { return params[p] != null ? params[p] : m; });
    return s;
  }

  /* apply texts to every [data-i18n] / [data-i18n-attr] below `root` */
  function apply(rootEl) {
    rootEl = rootEl || document;
    var list = rootEl.querySelectorAll("[data-i18n]");
    for (var i = 0; i < list.length; i++) list[i].innerHTML = t(list[i].getAttribute("data-i18n"));
    var al = rootEl.querySelectorAll("[data-i18n-attr]");
    for (var j = 0; j < al.length; j++) {
      al[j].getAttribute("data-i18n-attr").split(";").forEach(function (pair) {
        var p = pair.split(":");
        if (p.length === 2) al[j].setAttribute(p[0].trim(), t(p[1].trim()));
      });
    }
  }

  function setTitleAndMeta() {
    var r = document.documentElement;
    var tk = r.getAttribute("data-title"), dk = r.getAttribute("data-desc");
    if (tk && has(tk)) {
      var site = GTW.site && GTW.site.name ? (GTW.site.name[GTW.lang] || GTW.site.name.en) : "";
      document.title = t(tk).replace(/<[^>]+>/g, "") + (site && GTW.page !== "home" ? " · " + site : "");
    }
    if (dk && has(dk)) {
      var m = document.querySelector('meta[name="description"]');
      if (m) m.setAttribute("content", t(dk).replace(/<[^>]+>/g, ""));
    }
  }

  function setLang(l) {
    try { localStorage.setItem("gtw.lang", l); } catch (e) {}
    var u = location.href.replace(/([?&])lang=[a-z]{2}&?/, "$1").replace(/[?&]$/, "");
    if (u === location.href) location.reload();
    else location.href = u;   // reload: every script renders with the new language
  }

  GTW.i18n = { add: add, has: has, t: t, apply: apply, setLang: setLang, setTitleAndMeta: setTitleAndMeta, dict: dict,
    missingCount: function () { return Object.keys(missing).length; } };
  GTW.t = t;
})();
