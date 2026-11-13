/* workflow.html - case studies that show a corrected premise */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};
  GTW.pages.workflow = {
    init: function () {
      var box = document.getElementById("premise-cases");
      if (!box) return;
      ["skinning-physics", "render-graph-war", "culling"].forEach(function (id) {
        var c = GTW.caseById(id);
        if (c) box.appendChild(GTW.caseCard(c));
      });
    }
  };
})();
