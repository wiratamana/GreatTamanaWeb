#!/usr/bin/env python3
"""
Build web images (WebP + thumbnails) from the original R&D screenshots.

  python tools/build_images.py            # build the OLD manifest (cloud story, physics, 2026-11-13)
  python tools/build_images.py --world    # build the NEW manifest (procedural world, projects 4 to 9, 2026-11-22)
  python tools/build_images.py --all      # both
  python tools/build_images.py --drop-in  # also convert any PNG/JPG you dropped into assets/drop-in/
  python tools/build_images.py --list     # show where the sources are expected and which ones exist

Needs Pillow:  pip install pillow

Where the original pictures live (they are NOT in this repository):
  GTW_IDEAS_DIR   folder with the R&D notes (the folders procedural-landscape-4 ... -9, volumetric-cloud-N ...)
  GTW_SRC_DIR     folder with a few loose screenshots (bone_viewer_too_noisy.png, phys_bug_a.png, phys_bug_b.png)
  or a git-ignored file  tools/local_paths.json :  {"ideas": "D:/notes", "src": "D:/shots"}
  assets/src/     (git-ignored) originals of the first cloud pictures
No absolute path of any person is stored in this file.

Output:
  assets/img/<name>.webp          full image
  assets/img/thumb/<name>.webp    thumbnail (640 px wide) used by cards

Rules:
  * Only publish images that are yours. Never add third-party reference shots
    (Unreal, game screenshots, paper figures). The script REFUSES a source whose path contains the word
    "reference" or whose file name is one of the banned third-party files below.
  * "crop_black" removes the empty black ground at the bottom of sky-only test renders.
  * "redact" paints over file paths / user names in editor screenshots.
  * Old manifest: full image max 1920 px, WebP q88. New manifest: max 1600 px, WebP q80 and lower until the file is under
    the size limit of the row (default 150 KB). A rebuild can differ by a few KB from the published files.
  * Pictures that were built by a helper script (labelled side-by-side composites, 4-panel sheets, charts drawn
    from numbers, animated loops) are listed in SCRIPTED below with their inputs. They are NOT rebuilt here.
"""
import json
import os
import sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "img")
OLD = os.path.join(ROOT, "assets", "src")  # originals copied here (optional, git-ignored)

# ---- local source folders: env vars first, then tools/local_paths.json (git-ignored) ----
def _local_cfg():
    p = os.path.join(HERE, "local_paths.json")
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            print("WARN: tools/local_paths.json is not valid JSON, ignored")
    return {}

_CFG = _local_cfg()
IDEAS = os.environ.get("GTW_IDEAS_DIR") or _CFG.get("ideas") or ""
SRC = os.environ.get("GTW_SRC_DIR") or _CFG.get("src") or ""

# third-party reference pictures that must never be published
BANNED_NAMES = ("images.jpg", "images (1).jpg", "images (2).jpg", "oy8o4bie4u6c1.png")


def refuse_if_third_party(path):
    low = path.replace("\\", "/").lower()
    if "reference" in low.split("/") or any(part.startswith("reference") for part in low.split("/")):
        raise SystemExit("REFUSED (path contains 'reference'): " + path)
    if os.path.basename(low) in BANNED_NAMES:
        raise SystemExit("REFUSED third-party image: " + path)


def ideas(p):
    return os.path.join(IDEAS, p) if IDEAS else "<set GTW_IDEAS_DIR>/" + p


def loose(p):
    return os.path.join(SRC, p) if SRC else "<set GTW_SRC_DIR>/" + p


def old(p):
    return os.path.join(OLD, p)


# (source, output name, options)  -- OLD manifest, behaviour unchanged
MANIFEST = [
    (old("hero-clouds-mountain.png"), "cloud-hero", {}),
    (old("final-cumulus.png"), "cloud-final-cumulus", {"crop_black": True}),
    (old("final-horizon.png"), "cloud-final-horizon", {"crop_black": True}),
    (old("final-sunset.png"), "cloud-final-sunset", {}),
    (old("occlusion-mountain.png"), "cloud-occlusion-mountain", {}),
    (old("occlusion-first.png"), "cloud-occlusion-first", {}),
    (old("first-march.png"), "cloud-first-march", {"crop_black": True}),
    (old("first-march-2.png"), "cloud-first-march-2", {"crop_black": True}),
    (old("first-light.png"), "cloud-first-light", {}),
    (old("resolution-compare.png"), "cloud-resolution-compare", {}),
    (old("dusk-modes.png"), "cloud-dusk-modes", {"crop_black": True}),
    (old("before-start.png"), "cloud-s2-start", {"crop_black": True}),
    (old("before-horizon-gap.png"), "cloud-horizon-gap", {"crop_black": True}),
    (old("horizon-fix-proof.png"), "cloud-horizon-fix", {}),
    (old("banding-crops.png"), "cloud-banding", {}),
    (old("noise-shape-slices.png"), "cloud-noise-shape", {}),
    (old("noise-tiled.png"), "cloud-noise-tiled", {}),
    (old("noise-detail64.png"), "cloud-noise-detail", {}),
    (old("noise-curl128.png"), "cloud-noise-curl", {}),
    (old("detail-before-after.png"), "cloud-detail-ba", {}),
    (old("resolve-before-after.png"), "cloud-resolve-ba", {}),
    (old("composition-before-after.png"), "cloud-composition-ba", {}),
    (old("weather-map-v2.png"), "cloud-weather-map", {}),
    (old("weather-before-after.png"), "cloud-weather-ba", {}),
    (old("presets.png"), "cloud-presets", {}),
    (old("s3-lut-before.png"), "cloud-lut-before", {}),
    (old("s3-lut-after.png"), "cloud-lut-after", {}),
    (old("s3-split-sun-only.png"), "cloud-split-sun", {}),
    (old("s3-split-ambient-only.png"), "cloud-split-ambient", {}),
    (old("s3-r1-head-vs-r1.png"), "cloud-r1", {}),
    (old("s3-shape-before.png"), "cloud-shape-before", {}),
    (old("s3-shape-after.png"), "cloud-shape-after", {}),
    (old("s3-bloom-halo.png"), "cloud-bloom-halo", {}),
    (old("s3-bloom-threshold.png"), "cloud-bloom-threshold", {}),
    (old("s3-sunset-sat13.png"), "cloud-sunset-sat13", {}),
    (old("s3-sunset-sat11.png"), "cloud-sunset-sat11", {}),
    (old("s3-precision-old-new.png"), "cloud-precision", {}),
    (old("s3-1080-d4-d6.png"), "cloud-1080", {}),
    (old("s3-presets-s8.png"), "cloud-presets-s8", {}),
    (ideas(r"volumetric-cloud-3\work\shots\L7d_final_sheet.png"), "cloud-shafts-sheet", {}),
    (ideas(r"volumetric-cloud-3\work\shots\Q5_sheet_front.png"), "cloud-shadow-onoff", {}),
    (ideas(r"volumetric-cloud-3\work\shots\L7c_final_sheet.png"), "cloud-shafts-offon", {}),
    (ideas(r"volumetric-cloud-3\work\shots\L2_final_before_after.png"), "cloud-look-l2", {}),
    (ideas(r"volumetric-cloud-5\work\shots\R1_user_default.png"), "mtn-leak-user", {}),
    (ideas(r"volumetric-cloud-5\work\shots\R1_sheet_toggles_a.png"), "mtn-leak-toggles", {}),
    (ideas(r"volumetric-cloud-5\work\shots\R1_sheet_casterRange20000.png"), "mtn-leak-fixed", {}),
    (ideas(r"volumetric-cloud-2\work\shots\D_S_sheet_sunset_tm.png"), "cloud-sunset-tonemap", {}),
    (ideas(r"volumetric-cloud-2\work\shots\D_Q_final_S1.png"), "cloud-final-s1", {}),
    (ideas(r"volumetric-cloud-2\work\shots\D_Q_final_S3.png"), "cloud-final-s3", {}),
    (ideas(r"volumetric-cloud-2\work\shots\D_Q_final_S8.png"), "cloud-final-s8", {}),
    (loose("bone_viewer_too_noisy.png"), "phys-bone-viewer", {}),
    (loose("phys_bug_a.png"), "phys-bug-colliders", {}),
    (loose("phys_bug_b.png"), "phys-bug-editor",
     {"redact": [(738, 36, 1274, 70), (58, 517, 500, 538)]}),
]

# ---- NEW manifest: procedural world, projects 4 to 9 (all own engine renders). Sources are relative to the Ideas folder. ----
# (source relative to GTW_IDEAS_DIR, output name, options)
# options: limit_kb (default 150), kind = "crop2x" (box) | "grid" (tile_w, cols, rows) | "og" (JPEG 1200x630 centre crop)
P4 = "procedural-landscape-4/work/screens/"
P5 = "procedural-landscape-5/work/screens/"
P6 = "procedural-landscape-6/work/screens/"
P7 = "procedural-landscape-7/work/screens/"
P8 = "procedural-landscape-8/evidence/"
P8L = "procedural-landscape-8/evidence/round4/live/"
P9 = "procedural-landscape-9/evidence/"
P9L = P9 + "live_round4/"
P9S = P9L + "shots/"
P9X = P9L + "extras/"

WORLD_MANIFEST = [
    # ---- project 4 (refactor + Big World demo) ----
    (P4 + "w6_open_http_a.png", "pl4-lake-before", {}),
    (P4 + "w6_v2_open.png", "pl4-lake-after", {}),
    (P4 + "w6_sky_p6.png", "pl4-blacksky-bug", {}),
    (P4 + "w6_v3_after_hiz.png", "pl4-blacksky-fixed", {}),
    (P4 + "w8_file_menu.png", "pl4-file-menu", {"kind": "crop2x", "box": (0, 0, 360, 205)}),
    (P4 + "w7_spot_s2_demo.png", "pl4-spot-mountains", {}),
    (P4 + "w8_pose_aerial300.png", "pl4-aerial-river-strip", {}),
    (P4 + "w4_terrain_map.png", "pl4-terrain-lod-map", {}),
    (P4 + "w7_water_panel_open_swapchain.png", "pl4-water-editor", {}),
    # ---- project 5 (grass quality) ----
    (P5 + "base_ground_sun35.png", "pl5-ground-before", {}),
    (P5 + "FINAL_ground_sun35.png", "pl5-ground-after", {}),
    (P5 + "base_closeup_sun35.png", "pl5-closeup-before", {}),
    (P5 + "FINAL_closeup_sun35.png", "pl5-closeup-after", {}),
    (P5 + "base_hill12_sun35.png", "pl5-hill-before", {}),
    (P5 + "FINAL_hill12_sun35.png", "pl5-hill-after", {}),
    (P5 + "A_demo_sun35_recvNone.png", "pl5-cloudshadow-off", {}),
    (P5 + "A_demo_sun35_recvAll.png", "pl5-cloudshadow-on", {}),
    (P5 + "A_mtn_normal_recvOff.png", "pl5-mtnshadow-off", {}),
    (P5 + "A_mtn_normal.png", "pl5-mtnshadow-on", {}),
    # ---- project 6 (atmosphere, shafts) ----
    (P6 + "base_sun88_aerial.png", "pl6-haze-aerial-before", {}),
    (P6 + "r8_QA_03_aerial_sun88.png", "pl6-haze-aerial-after", {}),
    (P6 + "r8_val_toggle_false.png", "pl6-shafts-off", {}),
    (P6 + "r8_val_toggle_true.png", "pl6-shafts-on", {}),
    (P6 + "r8_QA_08_mountain_rays.png", "pl6-shafts-mountain", {}),
    (P6 + "r8_val_mtn.png", "pl6-shafts-mountain-pillars", {}),
    (P6 + "r8_QA_07_godrays_partial_cloud.png", "pl6-shafts-small-clouds", {}),
    (P6 + "base_OCC_sun30_all_on.png", "pl6-bloom-before", {}),
    (P6 + "r8_QA_04_sun30_behind_cloud.png", "pl6-bloom-after", {}),
    (P6 + "r8_QA_05_sun12_water.png", "pl6-lowsun-sea", {}),
    # ---- project 7 (cloud render quality) ----
    (P7 + "s8_base_v02_ground_sun35.png", "pl7-cloud-slab-before", {}),
    (P7 + "s8_f_v02_ground_sun35.png", "pl7-cloud-skin-after", {}),
    (P7 + "s10_g_v02_ground_sun35.png", "pl7-cloud-final-v02", {}),
    (P7 + "s10_a_v02_ground_sun35.png", "pl7-cloud-rejected-s10a", {}),
    (P7 + "exp3_montage.png", "pl7-cloud-stripe-experiment", {}),
    (P7 + "s10_g_v06_water_low_sun.png", "pl7-cloud-lowsun", {}),
    (P7 + "s10_g_v04_overhead_lookup.png", "pl7-cloud-overhead-weak", {}),
    (P7 + "s10_g_v05_aerial_shadows.png", "pl7-cloud-aerial-weak", {}),
    # ---- project 8 (terrain + hydrology) ----
    (P8L + "shot_08_bigworld_default_open.png", "pl8-default-open-final", {}),
    (P8 + "baseline_00_default.png", "pl8-default-open-before", {}),
    (P8 + "baseline_04_far.png", "pl8-far-before", {}),
    (P8L + "ab_04_far.png", "pl8-far-after", {}),
    (P8 + "baseline_01_mid.png", "pl8-mid-before", {}),
    (P8L + "ab_01_mid.png", "pl8-mid-after", {}),
    (P8L + "detailoff_ab_01_mid.png", "pl8-detail-off", {}),
    (P8L + "shot_07_hydromap_accum.png", "pl8-hydro-accum", {}),
    (P8L + "shot_07_hydromap_relief.png", "pl8-hydro-relief", {}),
    (P8L + "shot_07_watermap.png", "pl8-hydro-bodies", {}),
    (P8 + "baseline_06_watermap.png", "pl8-hydro-before", {}),
    (P8L + "shot_04_alpine_high.png", "pl8-alpine", {}),
    (P8L + "shot_03_coast_mid.png", "pl8-river-mouth", {}),
    (P8L + "shot_01_valley_low.png", "pl8-valley-after", {}),
    (P8 + "round3/live/shot_01_valley_low.png", "pl8-valley-r3-bug", {}),
    (P8L + "shot_00_ground_riverbank.png", "pl8-ground-river", {}),
    (P8L + "shot_05_topdown_3d.png", "pl8-topdown-3d", {}),
    (P8L + "shot_02_lake_basin_mid.png", "pl8-lake-straight-shore", {}),
    # ---- project 9 (trees) ----
    (P9L + "default_open_FINAL.png", "pl9-default-open", {}),
    (P9L + "default_open_FINAL_notrees.png", "pl9-default-open-notrees", {}),
    (P9X + "aerial_1500m.png", "pl9-aerial-1500", {}),
    (P9S + "shot_09_aerial_topdown.png", "pl9-aerial-r4", {}),
    (P9 + "live_round1/shots2/shot_09_aerial_topdown.png", "pl9-aerial-r1", {}),
    (P9S + "shot_06_valley_river_mid.png", "pl9-valley", {}),
    (P9S + "shot_07_coast_lake_mid.png", "pl9-coast", {}),
    (P9 + "wp2_preview_r4/alt3000_far_overview.png", "pl9-placement-map", {"limit_kb": 200, "max_w": 1400}),
    (P9S + "shot_05_backlit_canopy_godrays.png", "pl9-shafts-on", {}),
    (P9S + "shot_05_backlit_canopy_godrays_shafts_off.png", "pl9-shafts-off", {}),
    (P9 + "live_round3_shafts/sheet_a_backlit_ground.png", "pl9-shafts-sheet", {"limit_kb": 180}),
    (P9L + "shot_11b_wind_oak/diff_max.png", "pl9-wind-diff", {"limit_kb": 200, "max_w": 1400}),
    (P9S + "shot_02_sakura_grove_ground.png", "pl9-sakura", {}),
    (P9S + "shot_03_meadow_riverbank_ground.png", "pl9-meadow", {}),
    (P9S + "shot_04_shadow_closeup_grass.png", "pl9-shadow", {}),
    (P9S + "shot_04_shadow_closeup_grass_nocast.png", "pl9-shadow-off", {}),
    (P9S + "shot_08_alpine_treeline_high.png", "pl9-treeline", {}),
    (P9S + "p05_aerial_far_carpet.png", "pl9-carpet", {}),
    (P9S + "p08_treeline_close.png", "pl9-island", {}),
    (P9S + "shot_10a_lod_near.png", "pl9-lod-r4", {}),
    (P9 + "live_round3/shots/shot_10a_lod_near.png", "pl9-lod-r3", {}),
    (P9L + "sheet_debugviews.png", "pl9-debug-views", {}),
    (P9 + "wp1_preview_r2/oak_variants.png", "pl9-oak-variants", {"kind": "grid", "tile_w": 760, "cols": 4, "rows": 2}),
    (P9 + "wp1_preview_r2/sakura_variants.png", "pl9-sakura-variants", {"kind": "grid", "tile_w": 760, "cols": 3, "rows": 2}),
    (P9 + "wp1_preview_r2/oak_bones.png", "pl9-oak-bones", {}),
    (P9 + "wp1_preview_r2/oak_lods.png", "pl9-oak-lods", {}),
    (P9X + "shot_01b_oak_forest_glade.png", "pl9-oak-forest", {}),
    (P9X + "dbg_tree_bones.png", "pl9-bones-debug", {}),
    (P9X + "aerial_1500m_nomask.png", "pl9-aerial-nomask", {}),
    (P9X + "shot_05b_backlit_sakura_shafts_on.png", "pl9-shafts-sakura-on", {}),
    (P9X + "shot_05b_backlit_sakura_shafts_off.png", "pl9-shafts-sakura-off", {}),
    (P9X + "petals_under_sakura.png", "pl9-petals", {}),
    # ---- hero + Open Graph picture (same source, aerial view at 1500 m) ----
    (P9X + "aerial_1500m.png", "world-hero", {"limit_kb": 220}),
    (P9X + "aerial_1500m.png", "og-world", {"kind": "og"}),
]

# Pictures built by a helper script (not rebuilt here). name: what it is and which sources went in (relative to the Ideas folder).
SCRIPTED = {
    "pl4-tiers-lean-big": "labelled side-by-side composite: procedural-landscape-4/work/screens/w7_tier_lean_demo.png + w7_tier_big_demo.png",
    "pl5-cast-off-on": "labelled side-by-side composite: procedural-landscape-5/work/screens/B_terrOnly_s20side_cast0.png + B_terrOnly_s20side_cast1.png",
    "pl6-cloudshadow-ab": "labelled side-by-side composite: procedural-landscape-6/work/screens/r8_cs_try0_off.png + r8_cs_try0_on.png",
    "pl7-cloud-journey-sheet": "labelled 2x2 sheet, same camera view, 4 builds: procedural-landscape-7/work/screens/s8_base_v02_ground_sun35.png, s8_f_v02_ground_sun35.png, s10_a_v02_ground_sun35.png, s10_g_v02_ground_sun35.png",
    "pl8-far-progress-sheet": "labelled 2x2 sheet, same camera pose, panels cropped to 2:1: procedural-landscape-8/evidence/baseline_04_far.png, round1/ab_04_far.png, round3/live/ab_04_far.png, round4/live/ab_04_far.png",
    "pl7-qa-score-chart": "own chart drawn with Pillow. Data: procedural-landscape-7 report (score history, same QA recipe)",
    "pl7-march-cost-chart": "own chart drawn with Pillow. Data: procedural-landscape-7 report section 5 (cloud march ms per build)",
    "pl8-qa-score-chart": "own chart drawn with Pillow. Data: procedural-landscape-8 report section 4 and its QA round files",
    "assets/media/pl9-wind-loop.webp": "animated WebP, 960 px, 14 frames at 125 ms (8 frames + ping-pong): procedural-landscape-9/evidence/live_round4/shot_11b_wind_oak/frame_00..07.png",
    "assets/media/pl9-wind-loop-sakura.webp": "animated WebP, 960 px, 14 frames at 125 ms (8 frames + ping-pong): procedural-landscape-9/evidence/live_round4/shot_11_wind_sequence/frame_00..07.png",
}


def autocrop_black(im, thr=14):
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    last = h - 1
    while last > 0:
        if max(px[x, last] for x in range(0, w, 4)) > thr:
            break
        last -= 1
    return im.crop((0, 0, w, min(h, last + 6)))


def save(im, name, q_full=88, q_thumb=78, max_w=1920, limit_kb=None, min_q=58):
    """Old manifest: one save at q_full. New manifest: start at q_full and go down by 3 until under limit_kb."""
    w, h = im.size
    if w > max_w:
        im = im.resize((max_w, int(h * max_w / w)), Image.LANCZOS)
    os.makedirs(os.path.join(OUT, "thumb"), exist_ok=True)
    full = os.path.join(OUT, name + ".webp")
    q = q_full
    while True:
        im.save(full, "WEBP", quality=q, method=6)
        if limit_kb is None or os.path.getsize(full) / 1024 <= limit_kb or q <= min_q:
            break
        q -= 3
    t = im
    if t.width > 640:
        t = t.resize((640, max(1, int(t.height * 640 / t.width))), Image.LANCZOS)
    t.save(os.path.join(OUT, "thumb", name + ".webp"), "WEBP", quality=q_thumb, method=6)
    return im.size, os.path.getsize(full) // 1024


def build():
    total = 0
    for src, name, opt in MANIFEST:
        refuse_if_third_party(src)
        if not os.path.exists(src):
            print("SKIP (missing):", name)
            continue
        im = Image.open(src).convert("RGB")
        for box in opt.get("redact", []):
            ImageDraw.Draw(im).rectangle(box, fill=(20, 20, 24))
        if opt.get("crop_black"):
            im = autocrop_black(im)
        size, kb = save(im, name)
        total += kb
        print("%-28s %-12s %5d KB" % (name, size, kb))
    print("total ~%d KB" % total)


def _grid(path, tile_w, cols, rows):
    """Re-arrange a horizontal strip of equal tiles into a grid."""
    im = Image.open(path).convert("RGB")
    n = im.width // tile_w
    th = im.height
    canvas = Image.new("RGB", (cols * tile_w, rows * th))
    for i in range(min(n, cols * rows)):
        canvas.paste(im.crop((i * tile_w, 0, (i + 1) * tile_w, th)), ((i % cols) * tile_w, (i // cols) * th))
    return canvas


def build_world():
    if not IDEAS:
        print("Set GTW_IDEAS_DIR (or tools/local_paths.json) to the folder with the R&D notes. Nothing built.")
        return
    total = 0
    for rel, name, opt in WORLD_MANIFEST:
        src = ideas(rel)
        refuse_if_third_party(src)
        if not os.path.exists(src):
            print("SKIP (missing):", name)
            continue
        kind = opt.get("kind", "single")
        if kind == "grid":
            im = _grid(src, opt["tile_w"], opt["cols"], opt["rows"])
        else:
            im = Image.open(src).convert("RGB")
        if kind == "crop2x":
            im = im.crop(opt["box"])
            im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
        if kind == "og":
            w, h = im.size
            cw = round(h * 1200 / 630)
            x0 = (w - cw) // 2
            og = im.crop((x0, 0, x0 + cw, h)).resize((1200, 630), Image.LANCZOS)
            p = os.path.join(OUT, name + ".jpg")
            og.save(p, "JPEG", quality=85, optimize=True, progressive=True)
            print("%-28s %-12s %5d KB" % (name + ".jpg", "1200x630", os.path.getsize(p) // 1024))
            continue
        size, kb = save(im, name, q_full=80, max_w=opt.get("max_w", 1600), limit_kb=opt.get("limit_kb", 150))
        total += kb
        print("%-28s %-12s %5d KB" % (name, size, kb))
    print("total ~%d KB (full images only)" % total)
    print("\nNot rebuilt here (built by a helper script, see SCRIPTED in this file):")
    for k in sorted(SCRIPTED):
        print("  -", k)


def drop_in():
    d = os.path.join(ROOT, "assets", "drop-in")
    if not os.path.isdir(d):
        return
    for f in os.listdir(d):
        base, ext = os.path.splitext(f)
        if ext.lower() in (".png", ".jpg", ".jpeg"):
            refuse_if_third_party(os.path.join(d, f))
            im = Image.open(os.path.join(d, f)).convert("RGB")
            print(base, *save(im, base))


def list_sources():
    print("ideas folder :", IDEAS or "(not set: GTW_IDEAS_DIR / tools/local_paths.json)")
    print("loose folder :", SRC or "(not set: GTW_SRC_DIR / tools/local_paths.json)")
    print("assets/src   : (exists)" if os.path.isdir(OLD) else "assets/src   : (missing)")
    ok = miss = 0
    for src, name, _ in MANIFEST:
        if os.path.exists(src):
            ok += 1
        else:
            miss += 1
    print("old manifest : %d sources present, %d missing" % (ok, miss))
    ok = miss = 0
    for rel, name, _ in WORLD_MANIFEST:
        if IDEAS and os.path.exists(ideas(rel)):
            ok += 1
        else:
            miss += 1
    print("new manifest : %d sources present, %d missing" % (ok, miss))


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--list" in args:
        list_sources()
        sys.exit(0)
    do_world = "--world" in args or "--all" in args
    do_old = "--all" in args or not do_world
    if do_old:
        build()
    if do_world:
        build_world()
    if "--drop-in" in args:
        drop_in()
