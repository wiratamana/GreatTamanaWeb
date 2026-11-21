# Wira Tamana: portfolio website

Static site for GitHub Pages. Plain HTML, CSS and JavaScript. No framework, no build step, no network calls, no tracking.
English and Japanese: every text is in a language file, nothing is hard coded in the pages (one exception: the static `<noscript>` block, see section 6).

Open `index.html` in a browser (works from a plain folder too, except `404.html`), or push to GitHub Pages.

```
https://wiratamana.github.io/GreatTamanaWeb/      (project site: all links are relative)
```

Snapshot date of the texts and numbers: **2026-11-22**. Engine numbers are from the public repository (commit `8590884`). See section 8.

## 1. Pages

| Page | File | What it is |
|---|---|---|
| Home | `index.html` | 60 second overview: role, recruiter summary, tour, newest work, proof, limits, contact |
| Procedural World | `world.html` | Newest work (Nov 14 to 22): Big World demo, terrain, hydrology, grass, trees, wind, light shafts, QA loop, limits |
| Engine overview | `engine.html` | Architecture, rules, subsystems, numbers, limits, credits |
| Rendering | `rendering.html` | Render features, GPU-driven rendering, render graph, pass order |
| Volumetric clouds | `clouds.html` | Flagship feature, pipeline, numbers, the 20-part story (part 2: making it look right) |
| Animation and physics | `animation.html` | MMD, skinning, physics, toon shading, trees in the wind |
| Editor and tools | `tools.html` | Editor, HTTP debug server, profiler, hot reload, tests, validation layer |
| AI Agent App | `app.html` | GreatTamanaApp: agent loop, 173 tools, engine bridge, how the world projects were run |
| R&D Journal | `journal.html` | All case studies, filter + search, "Featured" first |
| One case study | `case.html?id=<id>` | Same template for every case |
| Gallery | `gallery.html` | Every picture, grouped. "Procedural world" group first |
| How I work | `workflow.html` | Spec, AI agents, measuring method, art-director QA loop, failures |
| About and contact | `about.html` | Roles, skills, timeline, contact |
| CV | `cv.html` | Printable CV (1 to 2 pages) built from the same site texts. Print or "Save as PDF" |
| 404 | `404.html` | Uses absolute path `/GreatTamanaWeb/` (change it if the repo name changes) |

Also: `sitemap.xml`, `robots.txt` (written by `tools/seo_stamp.py`, see section 6).
A sticky "Contact / CV" button appears after 600 px of scrolling (not on `cv.html`, not in print).

## 2. Architecture (why it is easy to change)

```
index.html ... *.html        only structure. No text. Texts are keys: data-i18n="home.hero.h1"
css/
  tokens.css                 colours, fonts, spacing. Change the whole look here (one accent colour)
  base.css                   reset, typography, page shell, header, footer, print rules
  components.css             every component: card, stat, metric, flow, layers, bars, callout, fig, hero v2 (.rs, .tour) ...
js/
  core/loader.js             THE only script a page includes. Chooses language, loads everything else
  core/i18n.js               translation engine: GTW.t("key"), data-i18n, fallback to English, tokens {cases} and {updated}
  core/repeat.js             data-repeat: builds cards/rows/steps from the text files
  core/media.js              figures, screenshots, video, animated WebP loops and the placeholders
  core/ui.js                 lightbox (keyboard, focus trap), reveal on scroll, bars, table of contents
  core/layout.js             SAME header + footer on every page (from js/data/site.js), nav badge, sticky contact button
  core/boot.js               starts it all in the right order
  data/site.js               EDIT FIRST: name, contacts, repo links, navigation, updated date
  data/cases.js              case index (language neutral) + the category list
  data/cases-world.js        more case index entries: procedural world (projects 4, 5, 8)
  data/cases-trees.js        more case index entries: trees (project 9)
  data/cases-cloud2.js       more case index entries: cloud story part 2 (projects 6, 7)
  data/gallery.js            gallery list        data/apptools.js   the 173 app tools
  components/case-card.js    the one case card used everywhere
  pages/*.js                 small page specific code (journal filter, case renderer, world related cases, cv print button ...)
i18n/
  en/<bundle>.js             English texts (the source of truth)
  ja/<bundle>.js             Japanese texts (complete)
  bundles: common home world engine rendering clouds animation tools app workflow about cv journal gallery slots
           cases-perf cases-anim cases-look cases-tools cases-cloud cases-world cases-trees cases-cloud2
assets/
  img/ + img/thumb/          WebP images (made by tools/build_images.py). og-world.jpg is the link-preview picture
  media/                     screenshots, WebP loops and videos (see section 5)
  icons/                     favicon.svg, favicon.ico, apple-touch-icon.png
tools/                       build_images.py, count_numbers.py, i18n_check.py, check_assets.py, list_slots.py,
                             smoke_test.py, find_placeholders.py, seo_stamp.py, stamp.py
```

A page declares what it needs on its `<html>` tag, nothing else:

```html
<html lang="en" data-page="home" data-bundles="common,home,cases"
      data-scripts="data/cases,components/case-card,pages/home"
      data-title="home.title" data-desc="home.desc">
```

The bundle name `cases` loads all `cases-*.js` text files. The script `data/cases` also loads the extra case index files (`cases-world`, `cases-trees`, `cases-cloud2`).
A page that shows a case count (token `{cases}`) must list `data/cases` in `data-scripts`.

### Unified UI
Every page is built from the same components in `css/components.css`. Header and footer are generated by
`js/core/layout.js`. A new page = copy any page, change the `<html>` attributes and the keys. Do not add per-page CSS.

### `data-repeat`: lists come from the text files
```html
<div class="grid g3" data-repeat="home.can" data-tpl="card"></div>
```
renders one card per `home.can.1.*`, `home.can.2.*` ... that exists. To add a card, add keys
`home.can.7.t` and `home.can.7.d`. Templates: `card stat metric dl step layer li chip tr ev acc fig`
(fields are listed at the top of `js/core/repeat.js`). A `step` with an `.href` key becomes a link (used by the 60 second tour).

### Tokens in texts
`{cases}` is replaced by the number of case studies, `{updated}` by `updated` in `js/data/site.js`. Use them instead of typing the numbers.
They are replaced in every language, so EN and JA never drift.

## 3. Japanese translation

Japanese is complete: every key of every bundle exists in `i18n/ja/`. It must stay that way. A blue "partly translated" note appears on any page with a missing key.

1. First visit: the browser language decides (Japanese browser = Japanese, anything else = English). The switch in the header (EN / 日本語) overrides it and the choice is stored in `localStorage`. `?lang=ja` forces it.
2. When you change an English text, change the Japanese twin in the same commit:
   ```js
   GTW.i18n.add("ja", {
     "home.hero.h1": "グラフィックス・エンジン・ツールプログラマー。",
   });
   ```
3. Keep these keys identical in both languages (links, icons, numbers inside bars): `.href .img .ic .tagc .hl .slot .kind .ratio .thumb .tone .b .a .u`.
   Numbers and product names that do not change still need to be copied.
4. Pictures that contain English text (the QA score charts) cannot be translated; only their captions are.
5. Checks:
   ```
   python tools/i18n_check.py                       # missing keys per file, typos, unused keys, cases, bundles
   python tools/i18n_check.py --strict --full-ja --numbers
                                                    # the publish gate: any problem = exit 1, missing Japanese keys count as problems,
                                                    # numbers must have the same VALUE in EN and JA (50,000 = 5万, 86k = 8.6万)
   python tools/i18n_check.py --stub                # writes i18n/ja/*.todo.txt: key <TAB> English text, for a translator (git-ignored)
   ```

## 4. Add or change content

* **New case study**: add one entry to a case index file (`js/data/cases-world.js`, `cases-trees.js`, `cases-cloud2.js` or `cases.js`), then its texts to the matching `i18n/en/cases-*.js` and `i18n/ja/cases-*.js`
  (`case.<id>.title .summary .problem .cause .fix .result .limits` + optional `.method .hl .f1 .m.1.v .bars.*`).
  The entry MUST start with `{ id: "...", cat: "...",` in that order, or the checker cannot read it.
  Fields: `status` (`landed | partial | diagnosed | rejected`), `thumb` (image name, no extension), `figs`, `slots`, `feat: true` (shown on the home page: keep it to about 6 in total), `order` (cloud story).
  Run `python tools/i18n_check.py` to see what you forgot.
* **Proof of a case**: `proof: "52c871d"` (commit hashes, ranges like `a1b2c3d … e4f5a6b` and lists work). Each hash becomes a link to the public engine repository.
  Work that is finished but NOT pushed yet: `proofPending: true` and no hash. The case page then says "Work finished locally, not pushed to GitHub yet". Never invent a hash.
  When the work is pushed: replace `proofPending` by `proof` and check the `status`.
* **Categories**: `GTW.cats` in `js/data/cases.js` (world, perf, anim, look, tools, cloud). Label key: `cat.<id>` in `i18n/*/common.js`.
* **New image**: put the PNG/JPG in `assets/drop-in/`, run `python tools/build_images.py --drop-in`
  (needs `pip install pillow`), then use `<figure data-img="name" data-cap="key">`.
  Only publish your own images. Never third-party reference pictures. The script refuses sources named `reference*` and the known third-party files.
  Where the originals live is set outside the repo: env vars `GTW_IDEAS_DIR` and `GTW_SRC_DIR`, or the git-ignored file `tools/local_paths.json`. Run `python tools/build_images.py --list` to see what is found.
* **New page**: copy a page, add it to `nav` in `js/data/site.js`, add its bundle in `i18n/en` and `i18n/ja`. Run `python tools/seo_stamp.py` (section 6).
* **Contacts, repo links, CV, nav badge**: `js/data/site.js`. `contacts.cv` points to `cv.html`. The "New" badge in the nav ends on `badgeUntil`.
  Set `repos.engine.public: true` only if the repository is really public. Otherwise the site says "source on request".

## 5. Screenshots, WebP loops and videos: placeholders

Every dashed box on the site is a **slot**. Put a file with the slot name into `assets/media/` and it replaces the box
automatically. No HTML to edit. Today every slot has a file (no dashed box is left).

| Slot kind | File names it looks for | Use |
|---|---|---|
| `image` | `<slot>.webp` `.png` `.jpg` `.jpeg` | static screenshot |
| `webp` | `<slot>.webp` | short animated loop (3 to 6 s, under about 2 MB) |
| `video` | `<slot>.mp4` `.webm` | demo video |

The world loops are `pl9-wind-loop.webp` (oak stand) and `pl9-wind-loop-sakura.webp`: 8 frames from the wind sequence tool of the engine, ping-pong, 960 px.

```
python tools/list_slots.py            # which slots are empty (reads the pages and data files, fast). --strict = exit 1 if one is empty
python tools/find_placeholders.py     # what a visitor REALLY still sees as placeholder (renders the pages in Chrome)
python tools/find_placeholders.py --cases --out placeholders.md     # also all case pages, saves a report
python tools/find_placeholders.py --live https://wiratamana.github.io/GreatTamanaWeb/   # check the deployed site
```
The capture hint for every slot is in `i18n/en/slots.js`.
Safety: no company names, no chat sessions, no file paths with user names, no corporate screenshots, no third-party pictures.

## 6. Check before you publish

Use Chrome. On the author's PC headless Edge returns an EMPTY page, so the browser tools search Chrome first
(`GTW_BROWSER=<path to exe>` forces another browser). They are fail-loud now: they run a positive control first, and if the browser is blind
they print `TOOL BLIND` and exit with 2 instead of saying "OK". Exit codes: 0 clean, 1 problems, 2 tool blind.

```
python tools/stamp.py                  # writes today's date into js/data/site.js (updated)   (--date 2026-11-22 to set it)
python tools/seo_stamp.py              # static title, description, canonical, Open Graph, Twitter card, hreflang, JSON-LD, <noscript>,
                                       # sitemap.xml and robots.txt for every page. Run it AFTER texts and pages are final
python tools/seo_stamp.py --check      # exit 1 if a file is not up to date

python tools/i18n_check.py --strict --full-ja --numbers     # texts: 0 problems, 100% Japanese, same numbers EN and JA
python tools/check_assets.py                                # images: full + thumb pairs, every reference resolves, weight
python tools/list_slots.py --strict                         # media slots
python tools/smoke_test.py                                  # every page and every case, EN + JA, console errors (6 to 8 min)
python tools/smoke_test.py --quick                          # pages + one case per category (1 to 2 min)
python tools/smoke_test.py --shots out                      # also saves screenshots
python tools/find_placeholders.py --cases                   # dashed boxes a visitor really sees (0 expected)
```
Add `?static=1` to a URL to turn animations off.

Then look at the pages yourself: `world.html`, `index.html`, a case page, `cv.html` (print preview, 1 to 2 pages), in EN and `?lang=ja`, desktop and phone width.
Search the whole repo for the local Windows user name, drive-letter user paths, names of third-party characters and employer names: the result must be empty.

The static `<noscript>` block (written by `seo_stamp.py`) is hard-coded English on purpose: it must work without JavaScript, for link previews and parsers.
Browsers also use the static `<head>` (English only); the tab title in Japanese is set by JavaScript after load.
`robots.txt` and `sitemap.xml` sit under `/GreatTamanaWeb/`. Crawlers only read `robots.txt` at the host root, which a project site cannot control. Submit the sitemap URL in a search console if you want it indexed. Do not expect it.
Case pages share one static title and preview picture (one template).

## 7. Publish on GitHub Pages

Repository: `https://github.com/wiratamana/GreatTamanaWeb`. Settings, Pages, Source: `main` branch, `/ (root)`.
`.nojekyll` is already there. All links are relative, so the site works under `/GreatTamanaWeb/`.
Release steps: `python tools/stamp.py`, `python tools/seo_stamp.py`, the gate in section 6, commit, push `main`.

## 8. Honesty rules used on this site

* Every number comes from the source code, git history or the R&D notes, with the file or commit named.
  Recount with `python tools/count_numbers.py --engine <path of the engine repo>` (also `--app <path>`). Method and calibration are in its header.
* **Public vs local**: headline numbers are from the PUBLIC engine repository (commit `8590884` = `origin/dev`): about 163k lines of C++, 5,411 tests, 14 render features, 1,208 commits in 95 days.
  Work that exists only in the author's working tree (projects 8 and 9: terrain quality, hydrology, trees, canopy shafts; about +24.5k lines, 5,961 test macros, 16 render features)
  is always labelled "local, not pushed yet". Cases of that work use `proofPending` and show no commit hash.
* Every case study has a **Not proven / limits** box. Failures and missed targets are published (cloud QA stayed red, a misdiagnosis, a rejected rewrite).
* AI judge scores (Gemini art-director QA) are shown with who scored. Where the author's own score was lower, both are shown. A "green light" is not called proof.
* All timings: one laptop with an Intel Iris Xe iGPU. The site says so. Numbers marked "measured" were read live, "estimated" ones were not.
* Most engine code is written by AI agents under my specs and review. The site says so (see How I work). The credits say so too.
* Third-party content is credited (libraries on the engine page incl. FastNoiseLite, Sponza, MMD assets on the animation page).
  Only own renders and own charts are published. No third-party reference pictures (the earlier draft used crops of Unreal and other screenshots; they were removed).
* The old counts "1,181 spec files, 96 task folders, 20 investigations" on the workflow page could not be recounted. They are labelled with their date (2026-11-13).

## 9. Things to decide or fix before or after publishing

* **Facts only the owner knows** (the site does not invent them, so they are not on the site yet): Japanese level (e.g. JLPT), work permit / visa status, available-from date,
  location and relocation, a PDF CV if wanted. Add them to `i18n/en/about.js`, `i18n/ja/about.js`, `home.js` (recruiter card) and `cv.js`. A Japanese recruiter looks for these first.
* **Push the engine's local work**, then recount (`tools/count_numbers.py`), update the numbers (home, engine, rendering, tools, about, cv, world; EN and JA), change `proofPending` to `proof` with real hashes, remove the
  "local, not pushed yet" labels, run `python tools/i18n_check.py --strict --full-ja --numbers`.
  The app repository also has uncommitted work (an extra plug-in project, 2 more tools). The site counts only the committed 7 projects and 173 tools.
* **Privacy**: the engine repository history has commits authored with a work-PC identity and an employer email domain
  (about 1,037 commits). If the repository is public, consider rewriting the author with a `.mailmap` or `git filter-repo`.
  This site never shows that identity. The history of this website repository still contains an old version of `tools/build_images.py` with a local user path and
  a third-party character file name. The current file has none. Rewrite the history only if that matters to you.
* The MMD test character is a third-party asset. If you want zero risk, replace the Bone Viewer and editor
  screenshots (`phys-*`) with ones that use your own model.
* The two QA score charts (`pl7-qa-score-chart`, `pl8-qa-score-chart`) and the march cost chart have English text inside the picture.
* Numbers are a snapshot of 2026-11-22. Re-check them when the engine changes.
