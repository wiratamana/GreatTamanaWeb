/* ==========================================================================
   gallery.js  -  everything shown on gallery.html (language neutral).
   Captions: i18n/<lang>/gallery.js  ->  gal.<img>   (slots: slot.<id> in slots.js)
   g = group:  final | process | tools | media
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};

  GTW.galleryGroups = ["final", "process", "tools", "media"];

  GTW.gallery = [
    /* engine demo scenes (Sponza and the terrain + cloud Open Scene), files live in assets/media/ */
    { slot: "terrain-golden-hour", kind: "image", g: "final" },
    { slot: "clouds-blue-sky", kind: "image", g: "final" },
    { slot: "terrain-sunset", kind: "image", g: "final" },
    { slot: "clouds-sunset-sky", kind: "image", g: "final" },
    { slot: "terrain-snow-clouds", kind: "image", g: "final" },
    { slot: "terrain-dusk", kind: "image", g: "final" },
    { slot: "sponza-atrium", kind: "image", g: "final" },
    { slot: "sponza-arcade", kind: "image", g: "final" },
    { slot: "sponza-banners", kind: "image", g: "final" },
    { slot: "sponza-lion", kind: "image", g: "final" },

    /* final looks of the volumetric cloud renderer */
    { img: "cloud-hero", g: "final", case: "cloud-depth" },
    { img: "cloud-final-s1", g: "final", case: "cloud-shape" },
    { img: "cloud-final-s3", g: "final", case: "cloud-bloom" },
    { img: "cloud-final-sunset", g: "final", case: "cloud-bloom" },
    { img: "cloud-final-cumulus", g: "final", case: "cloud-horizon" },
    { img: "cloud-final-horizon", g: "final", case: "cloud-horizon" },
    { img: "cloud-final-s8", g: "final", case: "cloud-shape" },
    { img: "cloud-presets-s8", g: "final", case: "cloud-cost" },
    { img: "cloud-sunset-tonemap", g: "final", case: "cloud-bloom" },
    { img: "cloud-shafts-sheet", g: "final", case: "cloud-shadows-rays" },
    { img: "cloud-shadow-onoff", g: "final", case: "cloud-shadows-rays" },
    { img: "cloud-look-l2", g: "final", case: "cloud-shadows-rays" },

    /* how it got there */
    { img: "cloud-first-march", g: "process", case: "cloud-start" },
    { img: "cloud-first-light", g: "process", case: "cloud-lighting" },
    { img: "cloud-occlusion-first", g: "process", case: "cloud-depth" },
    { img: "cloud-occlusion-mountain", g: "process", case: "cloud-depth" },
    { img: "cloud-noise-shape", g: "process", case: "cloud-noise" },
    { img: "cloud-noise-tiled", g: "process", case: "cloud-noise" },
    { img: "cloud-noise-detail", g: "process", case: "cloud-noise" },
    { img: "cloud-noise-curl", g: "process", case: "cloud-noise" },
    { img: "cloud-resolution-compare", g: "process", case: "cloud-temporal" },
    { img: "cloud-resolve-ba", g: "process", case: "cloud-temporal" },
    { img: "cloud-horizon-gap", g: "process", case: "cloud-horizon" },
    { img: "cloud-horizon-fix", g: "process", case: "cloud-horizon" },
    { img: "cloud-banding", g: "process", case: "cloud-banding" },
    { img: "cloud-detail-ba", g: "process", case: "cloud-shape" },
    { img: "cloud-weather-map", g: "process", case: "cloud-shape" },
    { img: "cloud-weather-ba", g: "process", case: "cloud-shape" },
    { img: "cloud-composition-ba", g: "process", case: "cloud-shape" },
    { img: "cloud-shape-before", g: "process", case: "cloud-shape" },
    { img: "cloud-shape-after", g: "process", case: "cloud-shape" },
    { img: "cloud-lut-before", g: "process", case: "cloud-lutbug" },
    { img: "cloud-lut-after", g: "process", case: "cloud-lutbug" },
    { img: "cloud-split-sun", g: "process", case: "cloud-lutbug" },
    { img: "cloud-split-ambient", g: "process", case: "cloud-lutbug" },
    { img: "cloud-bloom-halo", g: "process", case: "cloud-bloom" },
    { img: "cloud-bloom-threshold", g: "process", case: "cloud-bloom" },
    { img: "cloud-sunset-sat13", g: "process", case: "cloud-bloom" },
    { img: "cloud-sunset-sat11", g: "process", case: "cloud-bloom" },
    { img: "cloud-precision", g: "process", case: "cloud-precision" },
    { img: "cloud-1080", g: "process", case: "cloud-cost" },
    { img: "cloud-shafts-offon", g: "process", case: "cloud-shadows-rays" },
    { img: "mtn-leak-user", g: "process", case: "cloud-mountain-leak" },
    { img: "mtn-leak-toggles", g: "process", case: "cloud-mountain-leak" },
    { img: "mtn-leak-fixed", g: "process", case: "cloud-mountain-leak" },

    /* editor and physics tooling (real screenshots) */
    { img: "phys-bone-viewer", g: "tools", case: "mmd-physics" },
    { img: "phys-bug-editor", g: "tools", case: "mmd-physics" },
    { img: "phys-bug-colliders", g: "tools", case: "mmd-physics" },

    /* media you add later: file name = slot id, see core/media.js */
    { slot: "editor-overview", kind: "image", g: "media" },
    { slot: "editor-render-graph", kind: "image", g: "media" },
    { slot: "editor-frame-debugger", kind: "image", g: "media" },
    { slot: "editor-profiler", kind: "image", g: "media" },
    { slot: "editor-cluster-viewer", kind: "image", g: "media" },
    { slot: "engine-hiz-demo", kind: "image", g: "media" },
    { slot: "engine-toon-character", kind: "image", g: "media" },
    { slot: "app-chat-main", kind: "image", g: "media" },
    { slot: "app-tool-cards", kind: "image", g: "media" },
    { slot: "app-subagents", kind: "image", g: "media" },
    { slot: "app-tool-picker", kind: "image", g: "media" },
    { slot: "app-task-builder", kind: "image", g: "media" },
    { slot: "app-engine-bridge", kind: "image", g: "media" },
    { slot: "demo-agent-visual-debug", kind: "video", g: "media" },
    { slot: "demo-editor-tour", kind: "video", g: "media" },
    { slot: "demo-clouds-flythrough", kind: "video", g: "media" },
    { slot: "demo-physics-loop", kind: "webp", g: "media" }
  ];
})();
