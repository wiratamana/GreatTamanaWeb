/* journal.html - list of all case studies with category filter and search.
   Chips: Featured (default) | All | one per category (GTW.cats). Counts are computed from the data, never typed.
   Inside a category, cases that have a picture come first. A search always looks in ALL cases. */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};

  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;"); }

  GTW.pages.journal = {
    init: function () {
      var bar = document.getElementById("filters"), grid = document.getElementById("case-grid");
      if (!bar || !grid) return;

      /* stable sort: category order first (casesSorted), then picture before text tile; the story order of a category is kept */
      var base = GTW.casesSorted();
      var cases = base.map(function (c, i) { return { c: c, i: i }; }).sort(function (a, b) {
        if (a.c.cat !== b.c.cat) return a.i - b.i;
        var pa = a.c.thumb ? 0 : 1, pb = b.c.thumb ? 0 : 1;
        if ((a.c.order || 0) || (b.c.order || 0)) return a.i - b.i;   // ordered stories (cloud) keep their order
        return pa !== pb ? pa - pb : a.i - b.i;
      }).map(function (x) { return x.c; });

      var DEFAULT = "feat", cur = DEFAULT, q = "";
      var counts = { all: cases.length, feat: cases.filter(function (c) { return c.feat; }).length };
      cases.forEach(function (c) { counts[c.cat] = (counts[c.cat] || 0) + 1; });
      if (!counts.feat) { DEFAULT = "all"; cur = "all"; }

      var keys = (counts.feat ? ["feat"] : []).concat(["all"], GTW.cats);
      var chips = keys.map(function (k) {
        return '<button type="button" class="chip' + (k === cur ? " on" : "") + '" data-cat="' + k + '"><span data-i18n="cat.' + k + '"></span> · ' + (counts[k] || 0) + "</button>";
      }).join("");
      bar.innerHTML = chips + '<input type="search" data-i18n-attr="placeholder:journal.search" aria-label="' + esc(GTW.t("ui.search")) + '">';

      cases.forEach(function (c) { grid.appendChild(GTW.caseCard(c)); });
      var empty = document.getElementById("case-empty");

      function text(c) {
        return (GTW.t("case." + c.id + ".title") + " " + GTW.t("case." + c.id + ".summary") + " " + c.tags.join(" ")).toLowerCase();
      }
      function matches(c) {
        if (q) return text(c).indexOf(q) >= 0;   // searching = look in everything
        return cur === "all" || (cur === "feat" ? !!c.feat : c.cat === cur);
      }
      function filter() {
        var shown = 0;
        var cards = grid.children;
        for (var i = 0; i < cards.length; i++) {
          var c = GTW.caseById(cards[i].getAttribute("data-id"));
          var ok = matches(c);
          cards[i].style.display = ok ? "" : "none";
          if (ok) shown++;
        }
        if (empty) empty.style.display = shown ? "none" : "";
      }
      function select(k) {
        cur = k;
        var all = bar.querySelectorAll("button[data-cat]");
        for (var i = 0; i < all.length; i++) all[i].classList.toggle("on", all[i].getAttribute("data-cat") === k);
      }
      bar.addEventListener("click", function (e) {
        var b = e.target.closest("button[data-cat]");
        if (!b) return;
        select(b.getAttribute("data-cat"));
        filter();
        history.replaceState(null, "", cur === DEFAULT ? location.pathname : "#" + cur);
      });
      bar.querySelector("input").addEventListener("input", function () {
        q = this.value.trim().toLowerCase();
        if (q && cur === "feat") select("all");   // a search must not hide results behind the Featured chip
        filter();
      });

      var h = location.hash.replace("#", "");
      if (h && (h === "all" || h === "feat" || GTW.cats.indexOf(h) >= 0)) {
        var btn = bar.querySelector('button[data-cat="' + h + '"]');
        if (btn) btn.click();
      } else {
        filter();   // apply the default (Featured) filter
      }
    }
  };
})();
