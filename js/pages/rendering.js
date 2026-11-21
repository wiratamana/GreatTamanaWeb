/* rendering.html - related case studies under the GPU-driven section and under the feature list */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};
  function fill(boxId, ids) {
    var box = document.getElementById(boxId);
    if (!box) return;
    ids.forEach(function (id) {
      var c = GTW.caseById(id);
      if (c) box.appendChild(GTW.caseCard(c));
    });
  }
  GTW.pages.rendering = {
    init: function () {
      fill("rel-gpu", ["culling", "render-graph-war", "shadow-caster"]);
      fill("rel-world", ["hydrology-drainage-solver", "grass-shadows", "canopy-shafts"]);
    }
  };
})();
