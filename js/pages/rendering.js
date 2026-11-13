/* rendering.html - related case studies under the GPU-driven section */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};
  GTW.pages.rendering = {
    init: function () {
      var box = document.getElementById("rel-gpu");
      if (!box) return;
      ["culling", "render-graph-war", "shadow-caster"].forEach(function (id) {
        var c = GTW.caseById(id);
        if (c) box.appendChild(GTW.caseCard(c));
      });
    }
  };
})();
