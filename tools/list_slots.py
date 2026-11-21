#!/usr/bin/env python3
"""
List every media slot on the site, whether its file exists in assets/media/, and what to capture.
It reads the html files, js/data, js/pages and js/components of the repo, so new pages and new case index files
(js/data/cases-*.js) are found without any edit here.

  python tools/list_slots.py            # list
  python tools/list_slots.py --strict   # exit code 1 when a slot is empty or has no capture hint in i18n/en/slots.js

Also reports files in assets/media/ that no slot and no page refers to (unused media).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = {"image": ["webp", "png", "jpg", "jpeg"], "webp": ["webp"], "video": ["mp4", "webm"]}


def en_slots():
    s = open(os.path.join(ROOT, "i18n", "en", "slots.js"), encoding="utf-8").read()
    m = re.search(r'add\(\s*"en"\s*,\s*(\{.*\})\s*\)\s*;', s, re.S)
    return json.loads(m.group(1))


def source_files():
    files = [os.path.join(ROOT, f) for f in sorted(os.listdir(ROOT)) if f.endswith(".html")]
    for sub in ("js/data", "js/pages", "js/components"):
        d = os.path.join(ROOT, sub)
        if os.path.isdir(d):
            files += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".js")]
    return files


def find_slots(files):
    found = {}
    for p in files:
        s = open(p, encoding="utf-8").read()
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        for m in re.finditer(r'<[^>]*\bdata-slot="([\w\-]+)"[^>]*>', s):          # attribute order does not matter
            km = re.search(r'\bdata-kind="(\w+)"', m.group(0))
            found.setdefault(m.group(1), [km.group(1) if km else "image", set()])[1].add(rel)
        for m in re.finditer(r'\{\s*(?:slot|id):\s*"([\w\-]+)",\s*kind:\s*"(\w+)"', s):
            found.setdefault(m.group(1), [m.group(2), set()])[1].add(rel)
    return found


def main():
    strict = "--strict" in sys.argv
    txt = en_slots()
    files = source_files()
    slots = find_slots(files)
    media = os.path.join(ROOT, "assets", "media")
    os.makedirs(media, exist_ok=True)
    have = set(os.listdir(media))
    missing = nohint = 0
    for sid in sorted(slots):
        kind = slots[sid][0]
        hit = [sid + "." + e for e in EXT.get(kind, EXT["image"]) if sid + "." + e in have]
        mark = "OK     " if hit else "MISSING"
        if not hit:
            missing += 1
        print("%s %-26s %-6s %s" % (mark, sid, kind, hit[0] if hit else "assets/media/" + sid + ".{" + ",".join(EXT.get(kind, EXT["image"])) + "}"))
        if not hit:
            hint = txt.get("slot." + sid + ".hint")
            if not hint:
                nohint += 1
            print("         " + (hint or "(no hint in i18n/en/slots.js)"))
        if ("slot." + sid) not in txt:
            print("         no caption text 'slot.%s' in i18n/en/slots.js" % sid)

    # media files that no slot and no literal reference uses
    src = "".join(open(p, encoding="utf-8").read() for p in files)
    claimed = {sid + "." + e for sid, (kind, _) in slots.items() for e in EXT.get(kind, EXT["image"])}
    orphan = sorted(f for f in have if f not in claimed and f not in src and not f.startswith(".") and not f.lower().endswith(".md"))
    for f in orphan:
        print("unused   assets/media/%s (no slot and no page refers to it)" % f)

    print("\n%d slots, %d still empty, %d unused media file(s)." % (len(slots), missing, len(orphan)))
    return 1 if (strict and (missing or nohint)) else 0


if __name__ == "__main__":
    sys.exit(main())
