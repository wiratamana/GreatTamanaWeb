/* world.html - a selection of related case studies: featured "world" cases first (at most 6), and the cloud cases
   that continue the cloud story (order 15 and up, at most 3). The journal has the full list (journal.html#world). */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};

  function pick(list, max) {
    var feat = list.filter(function (c) { return c.feat; });
    var rest = list.filter(function (c) { return !c.feat; });
    return feat.concat(rest).slice(0, max);
  }

  GTW.pages.world = {
    init: function () {
      var list = GTW.casesSorted();
      var box = document.getElementById("rel-world");
      if (box) {
        pick(list.filter(function (c) { return c.cat === "world"; }), 6).forEach(function (c) { box.appendChild(GTW.caseCard(c)); });
      }
      var cbox = document.getElementById("rel-cloud"), chead = document.getElementById("rel-cloud-h");
      if (!cbox) return;
      var clouds = pick(list.filter(function (c) { return c.cat === "cloud" && (c.order || 0) >= 15; }), 3);
      if (!clouds.length) {
        cbox.style.display = "none";
        if (chead) chead.style.display = "none";
        return;
      }
      clouds.forEach(function (c) { cbox.appendChild(GTW.caseCard(c)); });
    }
  };
})();
