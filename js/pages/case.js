/* ==========================================================================
   case.html?id=<id>  -  renders ONE case study from js/data/cases.js + the text files.
   Every case has the same structure, so every case looks the same:
     header -> numbers -> problem -> (how I investigated) -> cause -> fix -> bars -> result -> limits -> skills -> related
   ========================================================================== */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};

  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;"); }
  function has(k) { return GTW.i18n.has(k); }

  /* figures + slots that belong to one section */
  function mediaFor(c, at) {
    var items = [], n = 0;
    (c.figs || []).forEach(function (f) {
      n++;
      if ((f.at || "fix") === at) items.push('<figure data-img="' + esc(f.img) + '" data-cap="case.' + c.id + ".f" + n + '"></figure>');
    });
    (c.slots || []).forEach(function (s) {
      n++;
      if ((s.at || "result") === at) items.push('<figure data-slot="' + esc(s.id) + '" data-kind="' + (s.kind || "image") + '" data-cap="case.' + c.id + ".f" + n + '"></figure>');
    });
    if (!items.length) return "";
    return items.length === 1 ? items[0] : '<div class="fig-grid">' + items.join("") + "</div>";
  }

  function section(c, key, h, at) {
    var k = "case." + c.id + "." + key;
    if (!has(k)) return "";
    return '<h2 data-i18n="' + h + '"></h2><p data-i18n="' + k + '"></p>' + mediaFor(c, at);
  }
  /* proof line:  Engine commit: <hash> ... each hash is a link to <repo>/commit/<hash> when the repo is public.
     Ranges ("52909c0 … 5c567f7") and lists ("4695bcd, 0d29813") work, because every 7 to 40 char hex word is linked.
     proofPending:true (work finished locally, not pushed) shows a text instead and NEVER a hash. */
  function proofHtml(c) {
    /* pending: say it is not pushed, then give the real outcome of the work ("Works in my local build, with limits") */
    if (c.proofPending) return '<span><span class="proof-pending" data-i18n="case.proof.pending"></span> · <span data-i18n="status.local.' + c.status + '"></span></span>';
    if (!c.proof) return "";
    var repo = GTW.site.repos && GTW.site.repos.engine, pub = repo && repo.public && repo.url;
    var s = esc(c.proof).replace(/\b[0-9a-f]{7,40}\b/g, function (h) {
      return pub ? '<a href="' + esc(repo.url) + "/commit/" + h + '" target="_blank" rel="noopener"><code>' + h + "</code></a>" : "<code>" + h + "</code>";
    });
    return '<span><span data-i18n="case.proof"></span>: ' + s + "</span>";
  }

  function notFound(root) {
    root.innerHTML = '<div class="page-head"><div class="wrap"><h1 data-i18n="case.notfound"></h1>' +
      '<p><a class="btn primary" href="journal.html" data-i18n="case.back"></a></p></div></div>';
  }

  GTW.pages.case = {
    init: function () {
      var root = document.getElementById("case-root");
      var m = /[?&]id=([\w-]+)/.exec(location.search);
      var c = m && GTW.caseById(m[1]);
      if (!c) return notFound(root);

      var id = c.id, list = GTW.casesSorted(), idx = list.indexOf(c);
      var prev = list[idx - 1], next = list[idx + 1];
      var tags = c.tags.map(function (t) { return '<li class="chip">' + esc(t) + "</li>"; }).join("");
      var hasMetrics = has("case." + id + ".m.1.v"), hasBars = has("case." + id + ".bars.1.lab");

      var rel = list.filter(function (x) { return x.cat === c.cat && x.id !== id; }).slice(0, 3);

      var html =
        '<div class="page-head"><div class="wrap">' +
        '<nav class="crumbs" aria-label="' + esc(GTW.t("ui.crumbs")) + '"><a href="index.html" data-i18n="nav.home"></a><span class="sep">/</span><a href="journal.html" data-i18n="nav.journal"></a><span class="sep">/</span><a href="journal.html#' + c.cat + '" data-i18n="cat.' + c.cat + '"></a></nav>' +
        '<span class="eyebrow" data-i18n="cat.' + c.cat + '"></span>' +
        '<h1 data-i18n="case.' + id + '.title"></h1>' +
        '<p class="lead" data-i18n="case.' + id + '.summary"></p>' +
        '<div class="case-meta"><span class="badge ' + GTW.badgeClass(GTW.statusKey(c)) + '" data-i18n="status.' + GTW.statusKey(c) + '"></span>' +
        "<span>" + esc(c.date) + "</span>" +
        proofHtml(c) + "</div>" +
        "</div></div>" +
        '<section class="section"><div class="wrap"><div class="case-body">' +
        (hasMetrics ? '<div class="metrics" data-repeat="case.' + id + '.m" data-tpl="metric"></div>' : "") +
        section(c, "problem", "case.h.problem", "problem") +
        section(c, "method", "case.h.method", "method") +
        section(c, "cause", "case.h.cause", "cause") +
        section(c, "fix", "case.h.fix", "fix") +
        (hasBars ? '<div data-bars="case.' + id + '.bars"></div>' : "") +
        section(c, "result", "case.h.result", "result") +
        (has("case." + id + ".limits") ? '<div class="callout honest"><h4 data-i18n="case.h.limits"></h4><p data-i18n="case.' + id + '.limits"></p></div>' : "") +
        '<p class="dim"><small data-i18n="case.hw"></small></p>' +
        '<h2 data-i18n="case.h.skills"></h2><ul class="chips">' + tags + "</ul>" +
        "</div>" +
        (rel.length ? '<h2 class="sp-t" data-i18n="case.h.related"></h2><div class="grid g3" id="rel"></div>' : "") +
        '<div class="case-nav">' +
        (prev ? '<a class="prev" href="case.html?id=' + prev.id + '"><small data-i18n="case.prev"></small><span data-i18n="case.' + prev.id + '.title"></span></a>' : "<span></span>") +
        (next ? '<a class="next" href="case.html?id=' + next.id + '"><small data-i18n="case.next"></small><span data-i18n="case.' + next.id + '.title"></span></a>' : "<span></span>") +
        "</div></div></section>";

      root.innerHTML = html;
      var relBox = document.getElementById("rel");
      if (relBox) rel.forEach(function (x) { relBox.appendChild(GTW.caseCard(x)); });

      /* page title */
      document.documentElement.setAttribute("data-title", "case." + id + ".title");
      document.documentElement.setAttribute("data-desc", "case." + id + ".summary");
    }
  };
})();
