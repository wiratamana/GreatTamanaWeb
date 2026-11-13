#!/usr/bin/env python3
"""
Check that every image the site refers to exists (full size and thumbnail), and list unused images.

  python tools/check_assets.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")


def main():
    used = set()
    files = [os.path.join(ROOT, f) for f in os.listdir(ROOT) if f.endswith(".html")]
    for sub in ("js/data", "js/pages", "js/components", "js/core"):
        d = os.path.join(ROOT, sub)
        files += [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".js")]
    files += [os.path.join(ROOT, "i18n", "en", f) for f in os.listdir(os.path.join(ROOT, "i18n", "en"))]
    for p in files:
        s = open(p, encoding="utf-8").read()
        for m in re.finditer(r'(?:data-img="|img:\s*"|thumb:\s*"|\.img":\s*")([\w\-]+)"', s):
            used.add(m.group(1))
        for m in re.finditer(r'assets/img/(?:thumb/)?([\w\-]+)\.webp', s):
            used.add(m.group(1))
    bad = 0
    for n in sorted(used):
        for p in (os.path.join(IMG, n + ".webp"), os.path.join(IMG, "thumb", n + ".webp")):
            if not os.path.exists(p):
                print("MISSING", os.path.relpath(p, ROOT))
                bad += 1
    have = {f[:-5] for f in os.listdir(IMG) if f.endswith(".webp")}
    for n in sorted(have - used):
        print("unused  assets/img/%s.webp" % n)
    total = sum(os.path.getsize(os.path.join(IMG, f)) for f in os.listdir(IMG) if f.endswith(".webp"))
    print("%d images referenced, %d missing files, full-size images total %.1f MB" % (len(used), bad, total / 1048576.0))


if __name__ == "__main__":
    main()
