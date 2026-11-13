/* journal.html - list of all case studies with category filter and search */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};

  GTW.pages.journal = {
    init: function () {
      var bar = document.getElementById("filters"), grid = document.getElementById("case-grid");
      if (!bar || !grid) return;
      var cases = GTW.casesSorted(), cur = "all", q = "";

      var counts = { all: cases.length };
      cases.forEach(function (c) { counts[c.cat] = (counts[c.cat] || 0) + 1; });
      var chips = ["all"].concat(GTW.cats).map(function (k) {
        return '<button type="button" class="chip' + (k === "all" ? " on" : "") + '" data-cat="' + k + '"><span data-i18n="' + (k === "all" ? "cat.all" : "cat." + k) + '"></span> · ' + counts[k] + "</button>";
      }).join("");
      bar.innerHTML = chips + '<input type="search" data-i18n-attr="placeholder:journal.search" aria-label="Search">';

      cases.forEach(function (c) { grid.appendChild(GTW.caseCard(c)); });
      var empty = document.getElementById("case-empty");

      function text(c) {
        return (GTW.t("case." + c.id + ".title") + " " + GTW.t("case." + c.id + ".summary") + " " + c.tags.join(" ")).toLowerCase();
      }
      function filter() {
        var shown = 0;
        var cards = grid.children;
        for (var i = 0; i < cards.length; i++) {
          var c = GTW.caseById(cards[i].getAttribute("data-id"));
          var ok = (cur === "all" || c.cat === cur) && (!q || text(c).indexOf(q) >= 0);
          cards[i].style.display = ok ? "" : "none";
          if (ok) shown++;
        }
        if (empty) empty.style.display = shown ? "none" : "";
      }
      bar.addEventListener("click", function (e) {
        var b = e.target.closest("button[data-cat]");
        if (!b) return;
        cur = b.getAttribute("data-cat");
        var all = bar.querySelectorAll("button[data-cat]");
        for (var i = 0; i < all.length; i++) all[i].classList.toggle("on", all[i] === b);
        filter();
        history.replaceState(null, "", cur === "all" ? location.pathname : "#" + cur);
      });
      bar.querySelector("input").addEventListener("input", function () { q = this.value.trim().toLowerCase(); filter(); });

      var h = location.hash.replace("#", "");
      if (h && GTW.cats.indexOf(h) >= 0) {
        var btn = bar.querySelector('button[data-cat="' + h + '"]');
        if (btn) btn.click();
      }
    }
  };
})();
