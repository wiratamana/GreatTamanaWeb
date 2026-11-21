/* cases-cloud2.js  -  more entries for the R&D journal (language neutral). Same fields as js/data/cases.js.
   Texts: i18n/<lang>/cases-cloud2.js.  Loaded by loader.js right after data/cases.
   Cloud story, parts 15 to 20 (projects 6 and 7 of the procedural landscape work, 2026-11-18 and 2026-11-19).
   All proof hashes are on origin/dev (checked with git). Pictures show the OLD demo terrain and polygon lake: captions say so. */
(function () {
  var GTW = window.GTW = window.GTW || {};
  GTW.cases.push.apply(GTW.cases, [
    /* ------------------------------ PROJECT 6: atmosphere, shafts, cloud shadow ------------------------------ */
    { id: "cloud-aerial-haze", cat: "cloud", date: "2026-11", status: "landed", thumb: "pl6-haze-aerial-after", order: 15,
      tags: ["Atmosphere", "Aerial perspective", "Measurement", "Live tuning"], proof: "fd20675, 9c692ef, b6286ba",
      figs: [{ img: "pl6-haze-aerial-before", at: "problem" }, { img: "pl6-haze-aerial-after", at: "result" }] },
    { id: "cloud-sun-shafts", cat: "cloud", date: "2026-11", status: "partial", thumb: "pl6-shafts-mountain", order: 16,
      tags: ["God rays", "Compute shader", "Scene depth", "QA process"], proof: "4c9e4c9, 73c8ff6, 5c72059, 1eab69c, ca47c6b, 34354bf",
      figs: [{ img: "pl6-shafts-off", at: "method" }, { img: "pl6-shafts-on", at: "method" }, { img: "pl6-shafts-mountain-pillars", at: "fix" },
             { img: "pl6-shafts-mountain", at: "result" }, { img: "pl6-shafts-small-clouds", at: "result" }] },
    { id: "cloud-shadow-misdiagnosis", cat: "cloud", date: "2026-11", status: "partial", thumb: "pl6-cloudshadow-ab", order: 17,
      tags: ["Diagnosis", "Cloud shadows", "A/B proof", "Failure story"], proof: "b21a9fe, 5c72059, 3df267f",
      figs: [{ img: "pl6-cloudshadow-ab", at: "cause" }] },

    /* ------------------------------ PROJECT 7: cloud render quality (AI art director, still red) ------------------------------ */
    { id: "cloud-slab-rootcause", cat: "cloud", date: "2026-11", status: "partial", thumb: "pl7-cloud-journey-sheet", order: 18,
      tags: ["Density model", "Root cause", "Look dev", "QA scores"], proof: "485f9c4, ddcdc5a, e5ad091, 2a28bf8, e2fbd4f, 4327a8d",
      figs: [{ img: "pl7-cloud-slab-before", at: "problem" }, { img: "pl7-cloud-skin-after", at: "result" },
             { img: "pl7-cloud-final-v02", at: "result" }, { img: "pl7-qa-score-chart", at: "result" }] },
    { id: "cloud-barcode-stripes", cat: "cloud", date: "2026-11", status: "partial", thumb: "pl7-cloud-stripe-experiment", order: 19,
      tags: ["Ray marching", "Jitter", "Blue noise", "Debugging by toggles"], proof: "2a28bf8",
      figs: [{ img: "pl7-cloud-stripe-experiment", at: "method" }] },
    { id: "cloud-rejected-rewrite", cat: "cloud", date: "2026-11", status: "rejected", feat: true, thumb: "pl7-cloud-rejected-s10a", order: 20,
      tags: ["Rejected work", "AI coder review", "A/B testing", "Resolution limit"], proof: "a49db8e",
      figs: [{ img: "pl7-cloud-final-v02", at: "cause" }, { img: "pl7-cloud-rejected-s10a", at: "cause" }, { img: "pl7-march-cost-chart", at: "result" }] }
  ]);
})();
