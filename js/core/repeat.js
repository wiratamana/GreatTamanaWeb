/* ==========================================================================
   repeat.js  -  build repeated blocks (cards, stats, table rows ...) from the text files.

     <div class="grid g3" data-repeat="home.can" data-tpl="card"></div>

   renders one item per index N = 1, 2, 3 ... as long as keys  home.can.N.t  (or .v / .k / .c1 / .q)  exist.
   So the NUMBER of items is decided by the text file. To add a card: add keys  home.can.7.t  home.can.7.d .
   The Japanese file only needs the same keys (missing ones fall back to English).

   Templates (fields = the key suffixes the template reads):
     card   t d [d2] [tag] [tagc] [ic] [href]      card, becomes a link when .href exists
     stat   v l                                    big number + label
     metric v l [tone]                             metric box (tone = good | warn)
     dl     k d                                    definition row
     step   t d                                    numbered pipeline stage (wrap in <div class="flow">)
     layer  k d [hl]                               architecture layer row (wrap in <div class="layers">)
     li     t                                      <li>   (use inside ul / ol / ul.ticks)
     chip   t                                      <li class="chip">
     tr     c1 c2 c3 ...                           table row (use on <tbody>)
     ev     when t d                               timeline event
     acc    q a                                    accordion
     fig    img|slot cap [kind] [ratio]            figure
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};
  function has(k) { return GTW.i18n.has(k); }
  function a(k) { return ' data-i18n="' + k + '"'; }
  function opt(p, f, html) { return has(p + "." + f) ? html : ""; }
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;"); }
  function raw(k) { return GTW.i18n.dict.en[k] != null ? GTW.i18n.dict.en[k] : ""; }

  var T = {
    card: function (p) {
      var href = has(p + ".href") ? raw(p + ".href") : "";
      var tag = opt(p, "tag", '<span class="badge ' + (raw(p + ".tagc") || "accent") + ' tag"' + a(p + ".tag") + "></span>");
      var ic = opt(p, "ic", '<div class="ic">' + esc(raw(p + ".ic")) + "</div>");
      var inner = ic + tag + "<h3" + a(p + ".t") + "></h3>" + opt(p, "d", "<p" + a(p + ".d") + "></p>") + opt(p, "d2", "<p" + a(p + ".d2") + "></p>");
      if (href) return '<a class="card" href="' + esc(href) + '">' + inner + '<span class="more" data-i18n="ui.more"></span></a>';
      return '<article class="card">' + inner + "</article>";
    },
    stat: function (p) { return '<div class="stat"><span class="v"' + a(p + ".v") + '></span><span class="l"' + a(p + ".l") + "></span></div>"; },
    metric: function (p) { return '<div class="metric ' + (raw(p + ".tone") || "") + '"><span class="v"' + a(p + ".v") + '></span><span class="l"' + a(p + ".l") + "></span></div>"; },
    dl: function (p) { return '<div class="r"><dt class="k"' + a(p + ".k") + '></dt><dd class="d"' + a(p + ".d") + "></dd></div>"; },
    step: function (p) { return '<div class="st"><h4' + a(p + ".t") + "></h4><p" + a(p + ".d") + "></p></div>"; },
    layer: function (p) { return '<div class="ly ' + (has(p + ".hl") ? "hl" : "") + '"><div class="k"' + a(p + ".k") + '></div><div class="d"' + a(p + ".d") + "></div></div>"; },
    li: function (p) { return "<li" + a(p + ".t") + "></li>"; },
    chip: function (p) { return '<li class="chip"' + a(p + ".t") + "></li>"; },
    tr: function (p) {
      var s = "<tr>";
      for (var c = 1; has(p + ".c" + c); c++) s += "<td" + (/^[\d.,~≈×+\-–→ %msKMBGiBk]+$/.test(raw(p + ".c" + c)) && c > 1 ? ' class="num"' : "") + a(p + ".c" + c) + "></td>";
      return s + "</tr>";
    },
    ev: function (p) { return '<div class="ev"><span class="when"' + a(p + ".when") + "></span><h3" + a(p + ".t") + "></h3><p" + a(p + ".d") + "></p></div>"; },
    acc: function (p) { return '<details class="acc"><summary' + a(p + ".q") + '></summary><div class="in"' + a(p + ".a") + "></div></details>"; },
    fig: function (p) {
      var at = has(p + ".img") ? ' data-img="' + esc(raw(p + ".img")) + '"' : ' data-slot="' + esc(raw(p + ".slot")) + '"';
      var kind = has(p + ".kind") ? ' data-kind="' + esc(raw(p + ".kind")) + '"' : "";
      var ratio = has(p + ".ratio") ? ' data-ratio="' + esc(raw(p + ".ratio")) + '"' : "";
      var thumb = has(p + ".thumb") ? " data-thumb" : "";
      return "<figure" + at + kind + ratio + thumb + ' data-cap="' + p + '.cap"></figure>';
    }
  };
  var PROBE = ["t", "v", "k", "c1", "q", "img", "slot"];

  function run(root) {
    var els = (root || document).querySelectorAll("[data-repeat]");
    for (var e = 0; e < els.length; e++) {
      var el = els[e], prefix = el.getAttribute("data-repeat"), tpl = T[el.getAttribute("data-tpl") || "card"];
      if (!tpl || el.getAttribute("data-built")) continue;
      el.setAttribute("data-built", "1");
      var html = "";
      for (var i = 1; i < 200; i++) {
        var p = prefix + "." + i, ok = false;
        for (var q = 0; q < PROBE.length; q++) if (has(p + "." + PROBE[q])) { ok = true; break; }
        if (!ok) break;
        html += tpl(p);
      }
      el.innerHTML = html;
    }
  }
  GTW.repeat = { run: run, templates: T };
})();
