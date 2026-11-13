#!/usr/bin/env python3
"""
Build web images (WebP + thumbnails) from the original R&D screenshots.

  python tools/build_images.py            # build everything in the manifest below
  python tools/build_images.py --drop-in  # also convert any PNG/JPG you dropped into assets/drop-in/

Needs Pillow:  pip install pillow

Output:
  assets/img/<name>.webp          full image (max 1920 px wide)
  assets/img/thumb/<name>.webp    thumbnail (640 px wide) used by cards

Rules:
  * Only publish images that are yours. Never add third-party reference shots
    (Unreal, game screenshots, paper figures) to the manifest.
  * "crop_black" removes the empty black ground at the bottom of sky-only test renders.
  * "redact" paints over file paths / user names in editor screenshots.
"""
import os
import sys
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img")
IDEAS = r"C:\Users\F5954\Documents\TAMANA\GreatTamanaEngin-Ideas"
TAMANA = r"C:\Users\F5954\Documents\TAMANA"
OLD = os.path.join(ROOT, "assets", "src")  # originals copied here (optional)

# (source, output name, options)
def ideas(p): return os.path.join(IDEAS, p)
def tam(p): return os.path.join(TAMANA, p)
def old(p): return os.path.join(OLD, p)

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
    (tam("bone_viewer_too_noisy.png"), "phys-bone-viewer", {}),
    (tam("furina_physics_bug1.png"), "phys-bug-colliders", {}),
    (tam("furina_physics_bug2.png"), "phys-bug-editor",
     {"redact": [(738, 36, 1274, 70), (58, 517, 500, 538)]}),
]


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


def save(im, name, q_full=88, q_thumb=78):
    w, h = im.size
    if w > 1920:
        im = im.resize((1920, int(h * 1920 / w)), Image.LANCZOS)
    os.makedirs(os.path.join(OUT, "thumb"), exist_ok=True)
    full = os.path.join(OUT, name + ".webp")
    im.save(full, "WEBP", quality=q_full, method=6)
    t = im
    if t.width > 640:
        t = t.resize((640, max(1, int(t.height * 640 / t.width))), Image.LANCZOS)
    t.save(os.path.join(OUT, "thumb", name + ".webp"), "WEBP", quality=q_thumb, method=6)
    return im.size, os.path.getsize(full) // 1024


def build():
    total = 0
    for src, name, opt in MANIFEST:
        if not os.path.exists(src):
            print("SKIP (missing):", src)
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


def drop_in():
    d = os.path.join(ROOT, "assets", "drop-in")
    if not os.path.isdir(d):
        return
    for f in os.listdir(d):
        base, ext = os.path.splitext(f)
        if ext.lower() in (".png", ".jpg", ".jpeg"):
            im = Image.open(os.path.join(d, f)).convert("RGB")
            print(base, *save(im, base))


if __name__ == "__main__":
    build()
    if "--drop-in" in sys.argv:
        drop_in()
