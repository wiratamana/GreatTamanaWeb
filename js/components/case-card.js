/* ==========================================================================
   case-card.js  -  the one card used for every case study on every page
   (home, journal, related cases). Keeps the look identical everywhere.
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};
  var BADGE = { landed: "good", partial: "warn", diagnosed: "accent", rejected: "bad" };

  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;"); }

  GTW.badgeClass = function (status) { return BADGE[status] || ""; };

  GTW.caseCard = function (c) {
    var a = document.createElement("a");
    a.className = "card case-card";
    a.href = "case.html?id=" + encodeURIComponent(c.id);
    a.setAttribute("data-id", c.id);
    a.setAttribute("data-cat", c.cat);

    var th = document.createElement("div");
    th.className = "thumb";
    if (c.thumb) {
      var im = document.createElement("img");
      im.loading = "lazy"; im.decoding = "async"; im.alt = "";
      im.src = GTW.base + "assets/img/thumb/" + c.thumb + ".webp";
      th.appendChild(im);
    } else {
      th.appendChild(GTW.media.metricTile(GTW.t("case." + c.id + ".hl"), GTW.t("cat." + c.cat)));
    }
    a.appendChild(th);

    var body = document.createElement("div");
    body.className = "body";
    body.innerHTML =
      '<div class="row"><span class="badge ' + (BADGE[c.status] || "") + '" data-i18n="status.' + c.status + '"></span>' +
      '<span class="dim mono" data-i18n="cat.' + c.cat + '"></span></div>' +
      '<h3 data-i18n="case.' + c.id + '.title"></h3>' +
      '<p data-i18n="case.' + c.id + '.summary"></p>' +
      '<ul class="chips tags">' + c.tags.slice(0, 4).map(function (t) { return '<li class="chip">' + esc(t) + "</li>"; }).join("") + "</ul>";
    a.appendChild(body);
    return a;
  };
})();
