/* ==========================================================================
   media.js  -  figures, screenshots, video and placeholders.

   1) A figure with a known image from assets/img/ (made by tools/build_images.py):
        <figure data-img="cloud-hero" data-cap="home.hero.cap"></figure>
        optional: data-ratio="16/9" (crop to a ratio), data-thumb (use the small version)

   2) A SLOT = a media file you will add later. Nothing to edit in the HTML:
        <figure data-slot="app-chat-main" data-kind="image" data-cap="..."></figure>
      The script looks for a file named after the slot inside assets/media/ :
        data-kind="image"  ->  assets/media/<slot>.webp | .png | .jpg | .jpeg      (static screenshot)
        data-kind="webp"   ->  assets/media/<slot>.webp                           (short animated loop)
        data-kind="video"  ->  assets/media/<slot>.mp4  | .webm                   (demo video)
      If no file exists, a dashed placeholder is shown with the capture hint.
      Texts for a slot are in i18n/<lang>/slots.js:  slot.<id>  and  slot.<id>.hint
      Run  python tools/list_slots.py  to see which slots are still empty.
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};
  var CANDIDATES = {
    image: ["webp", "png", "jpg", "jpeg"],
    webp: ["webp"],
    video: ["mp4", "webm"]
  };
  var KIND_LABEL = { image: "media.kind.image", webp: "media.kind.webp", video: "media.kind.video" };
  var found = {};   // slot -> {url, type} | null

  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;"); }

  function probeImage(url, ok, fail) {
    var im = new Image();
    im.onload = function () { ok(url); };
    im.onerror = fail;
    im.src = url;
  }
  function probeVideo(url, ok, fail) {
    var v = document.createElement("video");
    v.preload = "metadata";
    v.onloadedmetadata = function () { ok(url); };
    v.onerror = fail;
    v.src = url;
  }
  function resolveSlot(slot, kind, cb) {
    var key = slot + "|" + kind;
    if (key in found) return cb(found[key]);
    var list = (CANDIDATES[kind] || CANDIDATES.image).slice();
    (function next() {
      if (!list.length) { found[key] = null; return cb(null); }
      var ext = list.shift(), url = GTW.base + "assets/media/" + slot + "." + ext;
      var isVid = ext === "mp4" || ext === "webm";
      (isVid ? probeVideo : probeImage)(url, function (u) { found[key] = { url: u, video: isVid }; cb(found[key]); }, next);
    })();
  }

  function placeholder(slot, kind, ratio) {
    var h = document.createElement("div");
    h.className = "ph";
    if (ratio) h.style.setProperty("--ratio", ratio);
    var ext = (CANDIDATES[kind] || CANDIDATES.image).join(" / ").replace(/(\w+)/g, ".$1");
    h.innerHTML =
      '<span class="kind" data-i18n="' + KIND_LABEL[kind] + '"></span>' +
      '<span class="t" data-i18n="slot.' + esc(slot) + '"></span>' +
      '<span class="h" data-i18n="slot.' + esc(slot) + '.hint"></span>' +
      '<span class="f">assets/media/' + esc(slot) + ' ' + ext + '</span>';
    GTW.i18n.apply(h);
    return h;
  }

  /* big metric tile used as a thumbnail when a case study has no screenshot */
  function metricTile(text, label) {
    var h = document.createElement("div");
    h.className = "ph metric-tile";
    var span = document.createElement("span");
    span.className = "small"; span.textContent = label || "";
    var big = document.createElement("span");
    big.className = "big"; big.innerHTML = text;
    h.appendChild(span); h.appendChild(big);
    return h;
  }
  /* keyboard users can open the lightbox too: Tab to the picture, press Enter or Space (see ui.js).
     Not done inside a link (project cards), because a link inside a link is invalid. */
  function zoomable(im, box) {
    if (box && box.closest && box.closest("a")) return;
    im.tabIndex = 0;
    im.setAttribute("role", "button");
    if (!im.alt) im.setAttribute("aria-label", GTW.t("ui.zoom"));
  }

  function mountInto(box, o) {
    /* o: {img, thumb, slot, kind, ratio, alt} */
    if (o.img) {
      var im = document.createElement("img");
      im.loading = "lazy"; im.decoding = "async";
      im.src = GTW.base + "assets/img/" + (o.thumb ? "thumb/" : "") + o.img + ".webp";
      im.setAttribute("data-full", GTW.base + "assets/img/" + o.img + ".webp");
      im.alt = o.alt || "";
      zoomable(im, box);
      box.appendChild(im);
      return;
    }
    if (o.slot) {
      var kind = o.kind || "image";
      var ph = placeholder(o.slot, kind, o.ratio);
      box.appendChild(ph);
      resolveSlot(o.slot, kind, function (r) {
        if (!r) return;
        var el;
        if (r.video) {
          el = document.createElement("video");
          el.controls = true; el.preload = "metadata"; el.playsInline = true; el.src = r.url;
          el.setAttribute("aria-label", o.alt || o.label || "");
        } else {
          el = document.createElement("img");
          el.loading = "lazy"; el.src = r.url; el.alt = o.alt || "";
          el.setAttribute("data-full", r.url);
          zoomable(el, box);
          if (kind === "webp") el.setAttribute("data-anim", "1");
        }
        box.replaceChild(el, ph);
      });
    }
  }

  /* turn a <figure data-img | data-slot> into the full figure component */
  function mount(fig) {
    if (fig.getAttribute("data-mounted")) return;
    fig.setAttribute("data-mounted", "1");
    var cap = fig.getAttribute("data-cap");
    var ratio = fig.getAttribute("data-ratio");
    fig.classList.add("fig");
    if (ratio) { fig.classList.add("crop"); fig.style.setProperty("--ratio", ratio); }
    var box = document.createElement("div");
    box.className = "m";
    fig.appendChild(box);
    /* The caption is shown right under the picture, so the picture gets an empty alt (a screen reader would read the same text twice).
       Exception: a figure inside a link (project cards): the caption is hidden there (css), so alt keeps the text.
       A video with controls has no alt: its aria-label takes the caption text (o.label). */
    var capText = cap && GTW.i18n.has(cap) ? GTW.t(cap).replace(/<[^>]+>/g, "") : "";
    var alt = capText && fig.closest && fig.closest("a") ? capText : "";
    mountInto(box, {
      img: fig.getAttribute("data-img"), thumb: fig.hasAttribute("data-thumb"),
      slot: fig.getAttribute("data-slot"), kind: fig.getAttribute("data-kind"), ratio: ratio, alt: alt, label: capText
    });
    if (cap) {
      var fc = document.createElement("figcaption");
      fc.setAttribute("data-i18n", cap);
      fig.appendChild(fc);
    }
  }
  function mountAll(root) {
    var l = (root || document).querySelectorAll("figure[data-img], figure[data-slot]");
    for (var i = 0; i < l.length; i++) mount(l[i]);
  }

  GTW.media = { mount: mount, mountAll: mountAll, mountInto: mountInto, metricTile: metricTile, placeholder: placeholder };
})();
