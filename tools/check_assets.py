#!/usr/bin/env python3
"""
Check the image and media files of the site.

  python tools/check_assets.py            # report, exit code 1 when a problem is found
  python tools/check_assets.py --all      # also list every unused image (default: first 25)

Checks
  1. Every assets/img/<name>.webp has a thumbnail assets/img/thumb/<name>.webp, and every thumbnail has a full image.
  2. Every image name the site refers to resolves to both files:
     data-img="x", img: "x", thumb: "x", "<key>.img": "x" (html, js, i18n en + ja) and assets/img/x.webp / assets/img/thumb/x.webp.
  3. Every literal asset path in html, js (not texts) and css resolves to a real file:
     assets/img/*.jpg|png|svg, assets/icons/*, assets/media/*, and absolute og:image / twitter:image URLs of the published site.
  4. Weight: warns about images over 400 KB and media files over 3 MB; prints the totals.
  5. Unused images (warning only).
Exit code 1 when a file is missing or a full image / thumbnail pair is broken.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
THUMB = os.path.join(IMG, "thumb")
MAX_IMG_KB = 400
MAX_MEDIA_MB = 3.0


def listdir(p):
    return sorted(os.listdir(p)) if os.path.isdir(p) else []


def files_under(sub, exts):
    d = os.path.join(ROOT, sub)
    return [os.path.join(d, f) for f in listdir(d) if f.endswith(exts)]


def read(p):
    return open(p, encoding="utf-8").read()


def main():
    show_all = "--all" in sys.argv
    problems = 0

    # ---- 1. pairs
    full = {f[:-5] for f in listdir(IMG) if f.endswith(".webp")}
    thumbs = {f[:-5] for f in listdir(THUMB) if f.endswith(".webp")}
    for n in sorted(full - thumbs):
        print("NO-THUMB  assets/img/%s.webp has no assets/img/thumb/%s.webp" % (n, n)); problems += 1
    for n in sorted(thumbs - full):
        print("NO-FULL   assets/img/thumb/%s.webp has no assets/img/%s.webp" % (n, n)); problems += 1

    # ---- 2. image names the site refers to
    html = [os.path.join(ROOT, f) for f in listdir(ROOT) if f.endswith(".html")]
    code = html + files_under("js/data", ".js") + files_under("js/pages", ".js") + files_under("js/components", ".js") \
        + files_under("js/core", ".js") + files_under("css", ".css")
    texts = files_under("i18n/en", ".js") + files_under("i18n/ja", ".js")
    used = set()
    for p in code + texts:
        s = read(p)
        for m in re.finditer(r'(?:data-img="|\bimg:\s*"|\bthumb:\s*"|\.img":\s*")([\w\-]+)"', s):
            used.add(m.group(1))
        for m in re.finditer(r'assets/img/(?:thumb/)?([\w\-]+)\.webp', s):
            used.add(m.group(1))
    for n in sorted(used):
        for p in (os.path.join(IMG, n + ".webp"), os.path.join(THUMB, n + ".webp")):
            if not os.path.exists(p):
                print("MISSING   " + os.path.relpath(p, ROOT).replace("\\", "/")); problems += 1

    # ---- 3. literal asset paths in html / js / css (and the published og:image URLs)
    lit = set()
    for p in code:
        s = read(p)
        if p.endswith(".js"):
            s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
        for m in re.finditer(r'assets/[\w\-./]+\.(?:webp|png|jpe?g|gif|svg|ico|mp4|webm)', s):
            lit.add((m.group(0), os.path.relpath(p, ROOT).replace("\\", "/")))
    seen = set()
    for path, src in sorted(lit):
        if path in seen:
            continue
        seen.add(path)
        if not os.path.exists(os.path.join(ROOT, path.replace("/", os.sep))):
            print("MISSING   %s   (referenced in %s)" % (path, src)); problems += 1

    # ---- 4. weight
    heavy, total_full, total_thumb = [], 0, 0
    for n in sorted(full):
        sz = os.path.getsize(os.path.join(IMG, n + ".webp"))
        total_full += sz
        if sz > MAX_IMG_KB * 1024:
            heavy.append((sz, n))
    for n in sorted(thumbs):
        total_thumb += os.path.getsize(os.path.join(THUMB, n + ".webp"))
    for f in listdir(IMG):
        if f.endswith((".jpg", ".jpeg", ".png")):
            sz = os.path.getsize(os.path.join(IMG, f))
            if sz > MAX_IMG_KB * 1024:
                heavy.append((sz, f))
    for sz, n in sorted(heavy, reverse=True)[:15]:
        print("heavy    image %s is %d KB (over %d KB)" % (n, sz // 1024, MAX_IMG_KB))
    media_total = 0
    media = os.path.join(ROOT, "assets", "media")
    for f in listdir(media):
        sz = os.path.getsize(os.path.join(media, f))
        media_total += sz
        if sz > MAX_MEDIA_MB * 1048576:
            print("heavy    media %s is %.1f MB (over %.0f MB)" % (f, sz / 1048576.0, MAX_MEDIA_MB))

    # ---- 5. unused
    unused = sorted(full - used)
    for n in (unused if show_all else unused[:25]):
        print("unused   assets/img/%s.webp" % n)
    if len(unused) > 25 and not show_all:
        print("unused   ... and %d more (use --all)" % (len(unused) - 25))

    print("%d image names referenced, %d full images, %d thumbnails, %d literal asset paths checked" % (len(used), len(full), len(thumbs), len(seen)))
    print("weight: full images %.1f MB, thumbnails %.1f MB, assets/media %.1f MB" % (total_full / 1048576.0, total_thumb / 1048576.0, media_total / 1048576.0))
    print("%d problem(s)." % problems)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
