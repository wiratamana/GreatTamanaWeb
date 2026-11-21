/* gallery.html - every picture on the site in one place, filtered by group.
   Optional in js/data/gallery.js:  GTW.galleryDefault = "world"  -> that group is selected first (default "all").
   A hash (#world) selects a group too. */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};

  GTW.pages.gallery = {
    init: function () {
      var bar = document.getElementById("filters"), box = document.getElementById("gallery");
      if (!bar || !box) return;
      var counts = { all: GTW.gallery.length };
      GTW.gallery.forEach(function (x) { counts[x.g] = (counts[x.g] || 0) + 1; });
      var keys = ["all"].concat(GTW.galleryGroups);
      var h = location.hash.replace("#", "");
      var start = keys.indexOf(h) >= 0 ? h : (keys.indexOf(GTW.galleryDefault) >= 0 ? GTW.galleryDefault : "all");
      bar.innerHTML = keys.map(function (k) {
        return '<button type="button" class="chip' + (k === start ? " on" : "") + '" data-g="' + k + '"><span data-i18n="gal.g.' + k + '"></span> · ' + (counts[k] || 0) + "</button>";
      }).join("");

      GTW.gallery.forEach(function (x) {
        var f = document.createElement("figure");
        f.setAttribute("data-g", x.g);
        if (x.img) {
          f.setAttribute("data-img", x.img);
          f.setAttribute("data-thumb", "");
          f.setAttribute("data-cap", "gal." + x.img);
        } else {
          f.setAttribute("data-slot", x.slot);
          f.setAttribute("data-kind", x.kind || "image");
          f.setAttribute("data-cap", "slot." + x.slot);
        }
        box.appendChild(f);
      });

      function show(g) {
        var figs = box.children;
        for (var j = 0; j < figs.length; j++) figs[j].style.display = (g === "all" || figs[j].getAttribute("data-g") === g) ? "" : "none";
      }
      show(start);

      bar.addEventListener("click", function (e) {
        var b = e.target.closest("button[data-g]");
        if (!b) return;
        var all = bar.querySelectorAll("button");
        for (var i = 0; i < all.length; i++) all[i].classList.toggle("on", all[i] === b);
        show(b.getAttribute("data-g"));
      });
    }
  };
})();
