/* index.html - only the parts that come from data: featured case studies (feat:true), in the site order
   (world first, then performance ... clouds), so the newest and most visual work is on top. */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};
  GTW.pages.home = {
    init: function () {
      var box = document.getElementById("feat-cases");
      if (!box) return;
      GTW.casesSorted().filter(function (c) { return c.feat; }).forEach(function (c) { box.appendChild(GTW.caseCard(c)); });
    }
  };
})();
