/* tools.html - related case studies */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};
  GTW.pages.tools = {
    init: function () {
      var box = document.getElementById("tool-cases");
      if (!box) return;
      ["profiler", "frame-debugger", "project-spikes", "scene-view", "editor-window", "euler"].forEach(function (id) {
        var c = GTW.caseById(id);
        if (c) box.appendChild(GTW.caseCard(c));
      });
    }
  };
})();
