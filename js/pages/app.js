/* app.html - tool inventory (from js/data/apptools.js) */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};
  GTW.pages.app = {
    init: function () {
      var box = document.getElementById("tool-inv");
      if (!box) return;
      var total = 0, s = "";
      GTW.appTools.forEach(function (c) {
        total += c.n;
        var names = c.names.split(" ").map(function (n) { return '<li class="chip">' + n.replace(/</g, "&lt;") + "</li>"; }).join("");
        s += '<details class="acc"><summary><span><span data-i18n="app.tools.' + c.id + '.t"></span> <span class="badge accent">' + c.n + '</span></span></summary>' +
          '<div class="in"><p data-i18n="app.tools.' + c.id + '.d"></p><ul class="chips">' + names + "</ul></div></details>";
      });
      box.innerHTML = s;
      var tn = document.getElementById("tool-total");
      if (tn) tn.textContent = total;
    }
  };
})();
