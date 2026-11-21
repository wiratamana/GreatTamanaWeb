/* cv.html - print-first CV page.
   1. The "Print / Save as PDF" button calls window.print().
   2. The contact list is built by layout.js from js/data/site.js and includes a link to this CV page.
      A CV that links to itself looks silly, so that one entry is removed here. */
(function () {
  var GTW = window.GTW;
  GTW.pages = GTW.pages || {};
  GTW.pages.cv = {
    init: function () {
      var links = document.querySelectorAll("[data-contact] a[href]");
      for (var i = 0; i < links.length; i++) {
        var href = links[i].getAttribute("href") || "";
        if (/(^|\/)cv\.html($|[?#])/.test(href)) {
          var li = links[i].parentNode;
          if (li && li.parentNode) li.parentNode.removeChild(li);
        }
      }
      var btn = document.querySelectorAll("[data-print]");
      for (var b = 0; b < btn.length; b++) {
        btn[b].addEventListener("click", function () { window.print(); });
      }
    }
  };
})();
