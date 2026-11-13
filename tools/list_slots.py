#!/usr/bin/env python3
"""
List every media slot on the site, whether its file exists in assets/media/, and what to capture.

  python tools/list_slots.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = {"image": ["webp", "png", "jpg", "jpeg"], "webp": ["webp"], "video": ["mp4", "webm"]}


def en_slots():
    s = open(os.path.join(ROOT, "i18n", "en", "slots.js"), encoding="utf-8").read()
    m = re.search(r'add\(\s*"en"\s*,\s*(\{.*\})\s*\)\s*;', s, re.S)
    return json.loads(m.group(1))


def find_slots():
    found = {}
    files = [os.path.join(ROOT, f) for f in os.listdir(ROOT) if f.endswith(".html")]
    for sub in ("js/data", "js/pages"):
        d = os.path.join(ROOT, sub)
        files += [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".js")]
    for p in files:
        s = open(p, encoding="utf-8").read()
        rel = os.path.relpath(p, ROOT)
        for m in re.finditer(r'data-slot="([\w\-]+)"(?:\s+data-kind="(\w+)")?', s):
            found.setdefault(m.group(1), [m.group(2) or "image", set()])[1].add(rel)
        for m in re.finditer(r'\{\s*(?:slot|id):\s*"([\w\-]+)",\s*kind:\s*"(\w+)"', s):
            found.setdefault(m.group(1), [m.group(2), set()])[1].add(rel)
    return found


def main():
    txt = en_slots()
    slots = find_slots()
    media = os.path.join(ROOT, "assets", "media")
    os.makedirs(media, exist_ok=True)
    have = set(os.listdir(media))
    missing = 0
    for sid in sorted(slots):
        kind = slots[sid][0]
        hit = [sid + "." + e for e in EXT.get(kind, EXT["image"]) if sid + "." + e in have]
        mark = "OK     " if hit else "MISSING"
        if not hit:
            missing += 1
        print("%s %-26s %-6s %s" % (mark, sid, kind, hit[0] if hit else "assets/media/" + sid + ".{" + ",".join(EXT[kind]) + "}"))
        if not hit:
            print("         " + txt.get("slot." + sid + ".hint", "(no hint in i18n/en/slots.js)"))
    print("\n%d slots, %d still empty." % (len(slots), missing))


if __name__ == "__main__":
    main()
