/* ==========================================================================
   cases.js  -  the R&D journal index (language neutral).
   Every case study = one entry here + its texts in i18n/<lang>/cases-*.js
   Text keys used (id = entry id):
     case.<id>.title   .summary   .problem   .cause   .fix   .result       (required)
     case.<id>.method  .limits                                              (optional)
     case.<id>.hl      short text for the thumbnail tile (when no thumb)
     case.<id>.f1 .f2 ...   captions of figs[] in order                     (figs / slots)
     case.<id>.m.N.v .l     metrics strip
     case.<id>.bars.*       before/after bars (see core/ui.js)

   Fields:
     cat     perf | anim | look | tools | cloud
     status  landed | partial | diagnosed | rejected
     thumb   image name from assets/img (no extension) or null -> metric tile
     figs    [{img, at}]   at = problem | cause | fix | result   (default fix)
     slots   [{id, kind, at}]  media you add later (see core/media.js)
     feat    true = shown on the home page
     proof   engine commit hash(es) where the work landed
   ========================================================================== */
(function () {
  var GTW = window.GTW = window.GTW || {};

  GTW.cats = ["perf", "anim", "look", "tools", "cloud"];

  GTW.cases = [
    /* ------------------------------ PERFORMANCE ------------------------------ */
    { id: "culling", cat: "perf", date: "2026-11", status: "landed", feat: true, thumb: null,
      tags: ["GPU-driven", "Compute", "Hi-Z", "Profiling", "Vulkan"], proof: "52c871d",
      slots: [{ id: "case-culling", kind: "image", at: "problem" }] },
    { id: "frames-in-flight", cat: "perf", date: "2026-11", status: "partial", feat: true, thumb: null,
      tags: ["Vulkan", "Synchronization", "Benchmarking", "Frame pacing"], proof: "00ec378",
      slots: [{ id: "case-frames-in-flight", kind: "image", at: "result" }] },
    { id: "render-graph-war", cat: "perf", date: "2026-11", status: "landed", thumb: null,
      tags: ["Render graph", "Barriers", "Validation layers", "GPU memory"], proof: "06b5c2d" },
    { id: "shadow-caster", cat: "perf", date: "2026-11", status: "partial", thumb: null,
      tags: ["Cascaded shadows", "Culling", "Geometry", "Testing"], proof: "7826fbc",
      slots: [{ id: "case-shadow-caster", kind: "image", at: "result" }] },
    { id: "skinning-physics", cat: "perf", date: "2026-11", status: "landed", feat: true, thumb: null,
      tags: ["SIMD", "SSE2", "CPU profiling", "Physics", "Skinning"], proof: "258c610" },

    /* ------------------------------ ANIMATION & PHYSICS ------------------------------ */
    { id: "mmd-physics", cat: "anim", date: "2026-11", status: "landed", feat: true, thumb: null,
      tags: ["Verlet", "MMD / PMX", "Physics", "Debug tooling"], proof: "52909c0 … 5c567f7",
      figs: [{ img: "phys-bug-editor", at: "problem" }, { img: "phys-bug-colliders", at: "problem" }, { img: "phys-bone-viewer", at: "method" }],
      slots: [{ id: "case-mmd-physics-after", kind: "webp", at: "result" }] },
    { id: "bend-floor", cat: "anim", date: "2026-11", status: "landed", thumb: null,
      tags: ["Physics", "Regression gates", "MMD / PMX"], proof: "4695bcd, 0d29813" },

    /* ------------------------------ LOOK ------------------------------ */
    { id: "toon", cat: "look", date: "2026-11", status: "landed", thumb: null,
      tags: ["Toon shading", "Outline", "Bloom", "Render feature"], proof: "f283019 … 515c1d4",
      slots: [{ id: "case-toon", kind: "image", at: "result" }] },
    { id: "taa", cat: "look", date: "2026-11", status: "partial", thumb: null,
      tags: ["TAA", "Compute", "GPU cost", "Reprojection"], proof: "8473e8c, ed9a7e1, b6ec2b1",
      slots: [{ id: "case-taa-onoff", kind: "image", at: "result" }] },
    { id: "toon-light", cat: "look", date: "2026-11", status: "landed", thumb: null,
      tags: ["Shaders", "Lighting", "Shadow sampling"], proof: "3aedcc2",
      slots: [{ id: "case-toon-light", kind: "image", at: "result" }] },

    /* ------------------------------ EDITOR & TOOLS ------------------------------ */
    { id: "profiler", cat: "tools", date: "2026-10", status: "landed", thumb: null,
      tags: ["Profiler", "Instrumentation", "ImGui", "HTTP API"], proof: "2607b3e … 55e1c66",
      slots: [{ id: "case-profiler", kind: "image", at: "result" }] },
    { id: "project-spikes", cat: "tools", date: "2026-10", status: "landed", thumb: null,
      tags: ["Main-thread hitches", "Worker thread", "File system"], proof: "d196dee … 0366817" },
    { id: "euler", cat: "tools", date: "2026-10", status: "landed", thumb: null,
      tags: ["Quaternions", "Euler angles", "Repro-first debugging"], proof: "b2d0780, f02050f, 7f092c6" },
    { id: "frame-debugger", cat: "tools", date: "2026-10", status: "landed", thumb: null,
      tags: ["Frame Debugger", "State machine", "Editor"], proof: "1462ada, ed2dfd4",
      slots: [{ id: "case-frame-debugger", kind: "image", at: "result" }] },
    { id: "scene-view", cat: "tools", date: "2026-11", status: "landed", thumb: null,
      tags: ["Shader math", "Camera", "Gizmo", "Editor UX"], proof: "3f88baa, 3a6b316, 016fb0e",
      slots: [{ id: "case-scene-view", kind: "image", at: "result" }] },
    { id: "editor-window", cat: "tools", date: "2026-11", status: "landed", thumb: null,
      tags: ["Dear ImGui", "Docking", "Refactoring"], proof: "333b744" },

    /* ------------------------------ VOLUMETRIC CLOUDS (in story order) ------------------------------ */
    { id: "cloud-start", cat: "cloud", date: "2026-11", status: "landed", thumb: "cloud-first-march-2", order: 1,
      tags: ["Planning", "Papers", "Atmosphere", "Prototype"],
      figs: [{ img: "cloud-first-march", at: "result" }, { img: "cloud-dusk-modes", at: "fix" }] },
    { id: "cloud-noise", cat: "cloud", date: "2026-11", status: "landed", thumb: "cloud-noise-tiled", order: 2,
      tags: ["3D noise", "Offline baking", "Tiling", "Engine upload path"],
      figs: [{ img: "cloud-noise-shape", at: "fix" }, { img: "cloud-noise-tiled", at: "fix" }, { img: "cloud-noise-detail", at: "result" }, { img: "cloud-noise-curl", at: "result" }] },
    { id: "cloud-depth", cat: "cloud", date: "2026-11", status: "landed", thumb: "cloud-occlusion-mountain", order: 3,
      tags: ["Ray marching", "Depth test", "Compute shader"],
      figs: [{ img: "cloud-occlusion-first", at: "fix" }, { img: "cloud-occlusion-mountain", at: "result" }] },
    { id: "cloud-lighting", cat: "cloud", date: "2026-11", status: "landed", thumb: "cloud-first-light", order: 4,
      tags: ["Beer-Lambert", "Phase functions", "Multiple scattering"],
      figs: [{ img: "cloud-first-light", at: "result" }] },
    { id: "cloud-temporal", cat: "cloud", date: "2026-11", status: "landed", thumb: "cloud-resolve-ba", order: 5,
      tags: ["Temporal reprojection", "Jitter", "Catmull-Rom", "fp16"],
      figs: [{ img: "cloud-resolution-compare", at: "fix" }, { img: "cloud-resolve-ba", at: "result" }] },
    { id: "cloud-horizon", cat: "cloud", date: "2026-11", status: "landed", thumb: "cloud-horizon-fix", order: 6,
      tags: ["Debugging", "Ray limits", "Evidence"],
      figs: [{ img: "cloud-horizon-gap", at: "problem" }, { img: "cloud-horizon-fix", at: "result" }] },
    { id: "cloud-banding", cat: "cloud", date: "2026-11", status: "landed", thumb: "cloud-banding", order: 7,
      tags: ["Noise", "Banding", "Sampling"],
      figs: [{ img: "cloud-banding", at: "problem" }] },
    { id: "cloud-shape", cat: "cloud", date: "2026-11", status: "partial", thumb: "cloud-detail-ba", order: 8,
      tags: ["Density model", "Weather map", "Cloud types", "Look dev"],
      figs: [{ img: "cloud-detail-ba", at: "fix" }, { img: "cloud-weather-map", at: "fix" }, { img: "cloud-shape-before", at: "result" }, { img: "cloud-shape-after", at: "result" }] },
    { id: "cloud-lutbug", cat: "cloud", date: "2026-11", status: "landed", feat: true, thumb: "cloud-lut-after", order: 9,
      tags: ["LUT", "Float precision", "Debugging by knobs"],
      figs: [{ img: "cloud-lut-before", at: "problem" }, { img: "cloud-lut-after", at: "result" }, { img: "cloud-split-sun", at: "cause" }, { img: "cloud-split-ambient", at: "cause" }] },
    { id: "cloud-bloom", cat: "cloud", date: "2026-11", status: "landed", thumb: "cloud-bloom-threshold", order: 10,
      tags: ["Bloom", "Tone mapping", "Post-processing"],
      figs: [{ img: "cloud-bloom-halo", at: "problem" }, { img: "cloud-bloom-threshold", at: "method" }, { img: "cloud-sunset-sat13", at: "cause" }, { img: "cloud-sunset-sat11", at: "result" }] },
    { id: "cloud-precision", cat: "cloud", date: "2026-11", status: "landed", feat: true, thumb: "cloud-precision", order: 11,
      tags: ["Float precision", "Large worlds", "Camera", "Test design"],
      figs: [{ img: "cloud-precision", at: "result" }] },
    { id: "cloud-cost", cat: "cloud", date: "2026-11", status: "partial", thumb: "cloud-presets-s8", order: 12,
      tags: ["GPU cost", "Texture fetch", "Resolution policy"],
      figs: [{ img: "cloud-1080", at: "fix" }, { img: "cloud-presets-s8", at: "result" }] },
    { id: "cloud-shadows-rays", cat: "cloud", date: "2026-11", status: "partial", thumb: "cloud-shafts-sheet", order: 13,
      tags: ["Cloud shadows", "God rays", "Froxel volume", "Temporal noise"],
      figs: [{ img: "cloud-shadow-onoff", at: "fix" }, { img: "cloud-shafts-sheet", at: "result" }, { img: "cloud-shafts-offon", at: "result" }] },
    { id: "cloud-mountain-leak", cat: "cloud", date: "2026-11", status: "diagnosed", thumb: "mtn-leak-toggles", order: 14,
      tags: ["Diagnosis", "Shadow cascades", "Toggle matrix"],
      figs: [{ img: "mtn-leak-user", at: "problem" }, { img: "mtn-leak-toggles", at: "cause" }, { img: "mtn-leak-fixed", at: "result" }] }
  ];

  GTW.caseById = function (id) {
    for (var i = 0; i < GTW.cases.length; i++) if (GTW.cases[i].id === id) return GTW.cases[i];
    return null;
  };
  /* stable order: perf, anim, look, tools, then the cloud story in story order */
  GTW.casesSorted = function () {
    return GTW.cases.slice().sort(function (a, b) {
      var ca = GTW.cats.indexOf(a.cat), cb = GTW.cats.indexOf(b.cat);
      if (ca !== cb) return ca - cb;
      return (a.order || 0) - (b.order || 0);
    });
  };
})();
