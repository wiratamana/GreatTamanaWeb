/* ==========================================================================
   cases-trees.js  -  project 9: procedural trees (oak + sakura) in the Big World.
   More entries for the R&D journal (language neutral). Same fields as js/data/cases.js.
   Texts: i18n/<lang>/cases-trees.js.  Loaded by loader.js right after data/cases.
   All of this work is finished locally but NOT committed or pushed yet: proofPending:true, no commit hash.
   Status is "partial" everywhere on purpose: every case has a real limit (see the "Not proven / limits" box).
   The wind loop slot uses assets/media/pl9-wind-loop.webp (slot text keys slot.pl9-wind-loop are in slots.js).
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};
  GTW.cases.push.apply(GTW.cases, [
    { id: "tree-generator", cat: "world", date: "2026-11", status: "partial", thumb: "pl9-sakura", order: 1,
      tags: ["Procedural generation", "C++20", "LOD", "Leaf cards", "Skinning", "Testing"], proofPending: true,
      figs: [{ img: "pl9-oak-variants", at: "fix" }, { img: "pl9-sakura-variants", at: "fix" }, { img: "pl9-oak-lods", at: "fix" },
             { img: "pl9-sakura", at: "result" }, { img: "pl9-petals", at: "result" }] },

    { id: "tree-placement", cat: "world", date: "2026-11", status: "partial", thumb: "pl9-aerial-r4", order: 2,
      tags: ["Procedural placement", "Matern spacing", "Density fields", "Streaming", "Seamless tiles"], proofPending: true,
      figs: [{ img: "pl9-aerial-r1", at: "problem" }, { img: "pl9-placement-map", at: "fix" }, { img: "pl9-aerial-r4", at: "result" },
             { img: "pl9-valley", at: "result" }, { img: "pl9-treeline", at: "result" }] },

    { id: "tree-wind-bones", cat: "world", date: "2026-11", status: "partial", thumb: "pl9-wind-diff", order: 3,
      tags: ["Skinning", "Compute", "glTF skin", "Wind", "Regression test"], proofPending: true,
      figs: [{ img: "pl9-oak-bones", at: "fix" }, { img: "pl9-bones-debug", at: "fix" }, { img: "pl9-wind-diff", at: "result" }],
      slots: [{ id: "pl9-wind-loop", kind: "webp", at: "result" }] },

    { id: "canopy-shafts", cat: "world", date: "2026-11", status: "partial", feat: true, thumb: "pl9-shafts-on", order: 4,
      tags: ["Light shafts", "Screen-space", "Diagnosis", "Shadow cascades", "GPU cost"], proofPending: true,
      figs: [{ img: "pl9-debug-views", at: "method" }, { img: "pl9-shafts-sheet", at: "cause" },
             { img: "pl9-shafts-off", at: "result" }, { img: "pl9-shafts-on", at: "result" },
             { img: "pl9-shafts-sakura-off", at: "result" }, { img: "pl9-shafts-sakura-on", at: "result" }] },

    { id: "tree-qa-loop", cat: "world", date: "2026-11", status: "partial", thumb: "pl9-default-open", order: 5,
      tags: ["Agent workflow", "QA rubric", "Evidence", "Honesty"], proofPending: true,
      figs: [{ img: "pl9-default-open-notrees", at: "problem" }, { img: "pl9-lod-r3", at: "cause" },
             { img: "pl9-lod-r4", at: "fix" }, { img: "pl9-default-open", at: "result" }] },

    { id: "tree-perf-budget", cat: "world", date: "2026-11", status: "partial", thumb: "pl9-aerial-1500", order: 6,
      tags: ["GPU budget", "Profiling", "Interleaved A/B", "Early-Z", "LOD"], proofPending: true,
      figs: [{ img: "pl9-default-open", at: "result" }, { img: "pl9-aerial-1500", at: "result" }] },

    { id: "forest-floor-mask", cat: "world", date: "2026-11", status: "partial", thumb: "pl9-carpet", order: 7,
      tags: ["Texture baking", "Terrain shader", "Profiling", "Grass", "Procedural placement"], proofPending: true,
      figs: [{ img: "pl9-aerial-nomask", at: "problem" }, { img: "pl9-aerial-1500", at: "result" }] }
  ]);
})();
