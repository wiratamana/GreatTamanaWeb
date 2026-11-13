/* index.html - only the parts that come from data: featured case studies */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};
  GTW.pages.home = {
    init: function () {
      var box = document.getElementById("feat-cases");
      if (!box) return;
      GTW.cases.filter(function (c) { return c.feat; }).forEach(function (c) { box.appendChild(GTW.caseCard(c)); });
    }
  };
})();
