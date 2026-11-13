/* animation.html - related case studies */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};
  GTW.pages.animation = {
    init: function () {
      var box = document.getElementById("anim-cases");
      if (!box) return;
      ["skinning-physics", "mmd-physics", "bend-floor", "toon", "toon-light", "taa"].forEach(function (id) {
        var c = GTW.caseById(id);
        if (c) box.appendChild(GTW.caseCard(c));
      });
    }
  };
})();
