/* ==========================================================================
   gallery.js  -  everything shown on gallery.html (language neutral).
   Captions: i18n/<lang>/gallery.js  ->  gal.<img>   (slots: slot.<id> in slots.js)
   g = group:  world | final | process | tools | media
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};

  GTW.galleryGroups = ["world", "final", "process", "tools", "media"];
  GTW.galleryDefault = "world";   // the newest work is shown first (js/pages/gallery.js)

  GTW.gallery = [
    /* PROCEDURAL WORLD (newest work, own engine renders only; files in assets/img, loops in assets/media).
       Projects 4 to 7 pictures show the old demo terrain (old polygon lake): the captions say so.
       The gallery uses 3 CSS columns, so this list runs down column 1, then column 2, then column 3 (about 20 items each).
       Column 1 = trees and forests, column 2 = terrain, rivers and QA rounds, column 3 = sky, shafts, grass and history.
       The first picture of each column is a strong one (the column breaks fall near item 20 and item 40).
       Weak spots are shown on purpose, but never at a column start. */
    { img: "pl9-aerial-1500", g: "world", case: "tree-placement" },
    { img: "pl9-default-open", g: "world", case: "tree-qa-loop" },
    { img: "pl9-default-open-notrees", g: "world", case: "tree-generator" },
    { slot: "pl9-wind-loop", kind: "webp", g: "world" },
    { img: "pl9-valley", g: "world", case: "tree-placement" },
    { img: "pl9-coast", g: "world", case: "tree-placement" },
    { img: "pl9-meadow", g: "world", case: "tree-generator" },
    { img: "pl9-sakura", g: "world", case: "tree-generator" },
    { img: "pl9-shadow-off", g: "world", case: "tree-generator" },
    { img: "pl9-shadow", g: "world", case: "tree-generator" },
    { img: "pl9-oak-forest", g: "world", case: "tree-qa-loop" },
    { img: "pl9-shafts-off", g: "world", case: "canopy-shafts" },
    { img: "pl9-shafts-on", g: "world", case: "canopy-shafts" },
    { img: "pl9-wind-diff", g: "world", case: "tree-wind-bones" },
    { slot: "pl9-wind-loop-sakura", kind: "webp", g: "world" },
    { img: "pl9-oak-variants", g: "world", case: "tree-generator" },
    { img: "pl9-placement-map", g: "world", case: "tree-placement" },
    { img: "pl9-treeline", g: "world", case: "tree-placement" },
    { img: "pl9-carpet", g: "world", case: "tree-placement" },
    { img: "pl9-island", g: "world", case: "tree-placement" },

    { img: "pl8-river-mouth", g: "world", case: "hydrology-drainage-solver" },
    { img: "pl8-far-progress-sheet", g: "world", case: "terrain-analytic-relief" },
    { img: "pl8-default-open-final", g: "world", case: "world-honest-green" },
    { img: "pl8-alpine", g: "world", case: "terrain-analytic-relief" },
    { img: "pl8-ground-river", g: "world", case: "hydrology-drainage-solver" },
    { img: "pl9-aerial-r1", g: "world", case: "tree-qa-loop" },
    { img: "pl9-aerial-r4", g: "world", case: "tree-qa-loop" },
    { img: "pl9-lod-r3", g: "world", case: "tree-qa-loop" },
    { img: "pl9-lod-r4", g: "world", case: "tree-qa-loop" },
    { img: "pl8-valley-r3-bug", g: "world", case: "world-bugs-found-by-looking" },
    { img: "pl8-valley-after", g: "world", case: "world-bugs-found-by-looking" },
    { img: "pl8-hydro-accum", g: "world", case: "hydrology-drainage-solver" },
    { img: "pl8-hydro-relief", g: "world", case: "hydrology-drainage-solver" },
    { img: "pl8-lake-straight-shore", g: "world", case: "world-honest-green" },
    { img: "pl8-mid-before", g: "world", case: "terrain-analytic-relief" },
    { img: "pl8-topdown-3d", g: "world", case: "hydrology-drainage-solver" },

    { img: "pl7-cloud-final-v02", g: "world", case: "cloud-slab-rootcause" },
    { img: "pl7-cloud-journey-sheet", g: "world", case: "cloud-slab-rootcause" },
    { img: "pl6-shafts-mountain", g: "world", case: "cloud-sun-shafts" },
    { img: "pl7-cloud-lowsun", g: "world", case: "cloud-slab-rootcause" },
    { img: "pl6-shafts-off", g: "world", case: "cloud-sun-shafts" },
    { img: "pl6-shafts-on", g: "world", case: "cloud-sun-shafts" },
    { img: "pl6-shafts-small-clouds", g: "world", case: "cloud-sun-shafts" },
    { img: "pl6-cloudshadow-ab", g: "world", case: "cloud-shadow-misdiagnosis" },
    { img: "pl7-cloud-rejected-s10a", g: "world", case: "cloud-rejected-rewrite" },
    { img: "pl7-qa-score-chart", g: "world", case: "cloud-slab-rootcause" },
    { img: "pl6-bloom-before", g: "world", case: "cloud-sun-shafts" },
    { img: "pl6-bloom-after", g: "world", case: "cloud-sun-shafts" },
    { img: "pl5-ground-before", g: "world", case: "grass-realism-cost" },
    { img: "pl5-ground-after", g: "world", case: "grass-realism-cost" },
    { img: "pl5-cloudshadow-off", g: "world", case: "grass-shadows" },
    { img: "pl5-cloudshadow-on", g: "world", case: "grass-shadows" },
    { img: "pl6-lowsun-sea", g: "world", case: "cloud-sun-shafts" },
    { img: "pl7-cloud-overhead-weak", g: "world", case: "cloud-slab-rootcause" },
    { img: "pl7-cloud-aerial-weak", g: "world", case: "cloud-slab-rootcause" },
    { img: "pl4-lake-before", g: "world", case: "big-world-orchestrator" },
    { img: "pl4-lake-after", g: "world", case: "big-world-orchestrator" },
    { img: "pl4-blacksky-bug", g: "world", case: "big-world-orchestrator" },
    { img: "pl4-aerial-river-strip", g: "world", case: "big-world-orchestrator" },

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

    /* editor, app and demo media (real screenshots, videos and loops): file name = slot id, see core/media.js */
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
    { slot: "demo-editor-tour", kind: "video", g: "media" },
    { slot: "demo-clouds-flythrough", kind: "video", g: "media" },
    { slot: "demo-physics-loop", kind: "webp", g: "media" }
  ];
})();
