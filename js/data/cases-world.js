/* ==========================================================================
   cases-world.js  -  journal entries for the procedural landscape projects 4, 5 and 8 (language neutral).
   Same fields as js/data/cases.js. Texts: i18n/<lang>/cases-world.js. Loaded by loader.js right after data/cases.
   Hashes: projects 4 and 5 are on origin/dev (checked with git). Project 8 is finished locally and NOT committed:
   it uses proofPending:true and never a hash. When project 8 is committed: replace proofPending by proof and set status "landed" where it fits.
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};
  GTW.cases.push.apply(GTW.cases, [

    /* ------------------------------ PROJECT 8: terrain + hydrology (uncommitted) ------------------------------ */
    { id: "terrain-analytic-relief", cat: "world", date: "2026-11", status: "partial", thumb: "pl8-far-after",
      tags: ["Procedural terrain", "Noise", "Analytic derivatives", "Streaming tiles", "Erosion-style relief"], proofPending: true,
      figs: [{ img: "pl8-far-before", at: "problem" }, { img: "pl8-far-progress-sheet", at: "fix" },
             { img: "pl8-far-after", at: "result" }, { img: "pl8-alpine", at: "result" }] },
    { id: "hydrology-drainage-solver", cat: "world", date: "2026-11", status: "partial", feat: true, thumb: "pl8-topdown-3d",
      tags: ["Hydrology", "Priority flood", "D8 flow", "Flow accumulation", "Procedural rivers", "Water carve"], proofPending: true,
      figs: [{ img: "pl8-hydro-before", at: "problem" }, { img: "pl8-default-open-before", at: "problem" },
             { img: "pl8-hydro-accum", at: "fix" }, { img: "pl8-hydro-bodies", at: "fix" },
             { img: "pl8-hydro-relief", at: "result" }, { img: "pl8-topdown-3d", at: "result" }, { img: "pl8-river-mouth", at: "result" }] },
    { id: "world-bugs-found-by-looking", cat: "world", date: "2026-11", status: "partial", thumb: "pl8-valley-after",
      tags: ["Live debugging", "Visual QA", "Water", "Terrain", "Regression"], proofPending: true,
      figs: [{ img: "pl8-valley-r3-bug", at: "problem" }, { img: "pl8-valley-after", at: "result" }] },
    { id: "world-honest-green", cat: "world", date: "2026-11", status: "partial", thumb: "pl8-default-open-final",
      tags: ["QA process", "Scope decision", "Gemini", "Honest reporting", "AI review"], proofPending: true,
      figs: [{ img: "pl8-default-open-final", at: "result" }, { img: "pl8-qa-score-chart", at: "result" },
             { img: "pl8-lake-straight-shore", at: "result" }] },

    /* ------------------------------ PROJECT 4: Big World + architecture ------------------------------ */
    { id: "big-world-orchestrator", cat: "world", date: "2026-11", status: "landed", thumb: "pl4-spot-mountains",
      tags: ["Orchestrator", "State machine", "Ports and adapters", "Unit tests with fakes", "Debugging", "Demo scene"],
      proof: "dbca039, d6b11e8, 44643d4, 007ffed, 246aa9d, 548aab2, 467a3c6",
      figs: [{ img: "pl4-lake-before", at: "problem" }, { img: "pl4-blacksky-bug", at: "problem" },
             { img: "pl4-lake-after", at: "result" }, { img: "pl4-blacksky-fixed", at: "result" },
             { img: "pl4-tiers-lean-big", at: "result" }, { img: "pl4-spot-mountains", at: "result" }] },
    { id: "feature-modules-leak-removal", cat: "tools", date: "2026-11", status: "partial", thumb: "pl4-water-editor",
      tags: ["Architecture", "Refactoring", "CI guards", "Module system", "Dependency rules"],
      proof: "d178cd2, 9454ef6, 75a05a0, 74cc26a, 7ad066a, 4ff06db, e8b63f4, 4dd7705",
      figs: [{ img: "pl4-file-menu", at: "fix" }, { img: "pl4-terrain-lod-map", at: "fix" }, { img: "pl4-water-editor", at: "result" }] },
    { id: "sync-validation-barriers", cat: "tools", date: "2026-11", status: "landed", thumb: null,
      tags: ["Vulkan", "Synchronization validation", "Render graph", "Barriers", "Debugging"], proof: "9a27625, 3802ca1" },

    /* ------------------------------ PROJECT 5: grass + one terrain bug ------------------------------ */
    { id: "grass-shadows", cat: "world", date: "2026-11", status: "partial", thumb: "pl5-cloudshadow-on",
      tags: ["Shadow cascades", "Compute culling", "Depth-only draw", "Feature Kit", "Vulkan validation"],
      proof: "deff43b, c1ed063, 652ee3d, 878afbc",
      figs: [{ img: "pl5-mtnshadow-off", at: "problem" }, { img: "pl5-cloudshadow-off", at: "problem" },
             { img: "pl5-mtnshadow-on", at: "result" }, { img: "pl5-cloudshadow-on", at: "result" }, { img: "pl5-cast-off-on", at: "result" }] },
    { id: "grass-realism-cost", cat: "world", date: "2026-11", status: "partial", thumb: "pl5-ground-after",
      tags: ["Shading", "Procedural variety", "LOD", "Per-blade culling", "GPU profiling"],
      proof: "de179e3, 4e4e085, 55df181, b303282, 97e5322, 484a995",
      figs: [{ img: "pl5-ground-before", at: "problem" }, { img: "pl5-hill-before", at: "problem" }, { img: "pl5-closeup-before", at: "problem" },
             { img: "pl5-ground-after", at: "result" }, { img: "pl5-hill-after", at: "result" }, { img: "pl5-closeup-after", at: "result" }] },
    { id: "terrain-evict-loop", cat: "world", date: "2026-11", status: "landed", thumb: null,
      tags: ["Live debugging", "Streaming", "Cache eviction", "Flicker", "Repro-first"], proof: "a934de8" }
  ]);
})();
