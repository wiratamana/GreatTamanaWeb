/* clouds.html - the cloud story = all case studies of category "cloud", in story order */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};
  GTW.pages.clouds = {
    init: function () {
      var box = document.getElementById("cloud-cases");
      if (!box) return;
      GTW.casesSorted().filter(function (c) { return c.cat === "cloud"; }).forEach(function (c, i) {
        var a = GTW.caseCard(c);
        var n = document.createElement("span");
        n.className = "badge accent";
        n.textContent = "#" + (i + 1);
        a.querySelector(".row").insertBefore(n, a.querySelector(".row").firstChild);
        box.appendChild(a);
      });
    }
  };
})();
