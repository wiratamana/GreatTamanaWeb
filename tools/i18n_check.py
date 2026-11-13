#!/usr/bin/env python3
"""
i18n checker. No dependencies. Run from anywhere:

  python tools/i18n_check.py            # report
  python tools/i18n_check.py --stub     # write i18n/ja/<bundle>.todo.txt with every missing key + English text
  python tools/i18n_check.py --strict   # exit code 1 if anything is wrong (for CI)

What it checks
  1. Every i18n/en/*.js file is valid JSON inside GTW.i18n.add("en", {...});
  2. Every key used by the HTML pages / page scripts exists in the English files
     (data-i18n, data-cap, data-repeat, data-bars, data-title, data-desc, GTW.t(...), case keys, slot keys)
  3. English keys that nothing uses (warning only)
  4. Japanese coverage: which English keys have no Japanese text yet
  5. Japanese keys that do not exist in English (typos)

Keys ending in .href .img .ic .tagc .hl .slot .kind .ratio .thumb .tone .b .a .u are NOT text and are skipped.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NON_TEXT = ("href", "img", "ic", "tagc", "hl", "slot", "kind", "ratio", "thumb", "tone", "b", "a", "u")


def load_dict(path):
    s = open(path, encoding="utf-8").read()
    m = re.search(r'add\(\s*"(\w+)"\s*,\s*(\{.*\})\s*\)\s*;', s, re.S)
    if not m:
        raise ValueError("no GTW.i18n.add(...) found")
    return json.loads(m.group(2))


def load_lang(lang):
    out, errors = {}, []
    d = os.path.join(ROOT, "i18n", lang)
    if not os.path.isdir(d):
        return out, errors
    for f in sorted(os.listdir(d)):
        if not f.endswith(".js"):
            continue
        try:
            data = load_dict(os.path.join(d, f))
            for k, v in data.items():
                out[k] = (v, f[:-3])
        except Exception as e:
            errors.append("%s/%s: %s" % (lang, f, e))
    return out, errors


def is_text_key(k):
    return k.rsplit(".", 1)[-1] not in NON_TEXT


def read(p):
    return open(p, encoding="utf-8").read()


def read_code(p):
    """source without comments (so examples in comments are not counted as usage)"""
    s = read(p)
    if p.endswith(".js"):
        s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
        s = re.sub(r"(?m)^\s*//.*$", "", s)
    return s


def collect_used(en):
    used, repeats, notes = set(), set(), []
    files = [os.path.join(ROOT, f) for f in os.listdir(ROOT) if f.endswith(".html")]
    for sub in ("js/pages", "js/components", "js/core", "js/data"):
        d = os.path.join(ROOT, sub)
        files += [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".js")]
    for p in files:
        s = read_code(p)
        for m in re.finditer(r'data-(?:i18n|cap|title|desc)="([\w.\-]+)"', s):
            used.add(m.group(1))
        for m in re.finditer(r'data-i18n-attr="([^"]+)"', s):
            for pair in m.group(1).split(";"):
                if ":" in pair:
                    used.add(pair.split(":")[1].strip())
        for m in re.finditer(r'data-repeat="([\w.\-]+)"', s):
            repeats.add(m.group(1))
        for m in re.finditer(r'data-bars="([\w.\-]+)"', s):
            repeats.add(m.group(1))
        for m in re.finditer(r'GTW\.t\("([\w.\-]+)"', s):
            used.add(m.group(1))
        for m in re.finditer(r'data-slot="([\w\-]+)"', s):
            used.add("slot." + m.group(1)); used.add("slot." + m.group(1) + ".hint")
    return used, repeats


def main():
    strict = "--strict" in sys.argv
    stub = "--stub" in sys.argv
    problems = 0

    en, err = load_lang("en")
    for e in err:
        print("ERROR  invalid file:", e); problems += 1
    ja, err = load_lang("ja")
    for e in err:
        print("ERROR  invalid file:", e); problems += 1
    print("English keys: %d   Japanese keys: %d" % (len(en), len(ja)))

    used, repeats = collect_used(en)

    # case + slot + gallery keys that are built by code
    sys.path.insert(0, ROOT)
    cases_js = read(os.path.join(ROOT, "js", "data", "cases.js"))
    ids = re.findall(r'\{\s*id:\s*"([\w\-]+)",\s*cat:\s*"(\w+)"', cases_js)
    cats = set(c for _, c in ids)
    statuses = set(re.findall(r'status:\s*"(\w+)"', cases_js))
    for cid, cat in ids:
        for k in ("title", "summary", "hl", "problem", "fix", "result"):
            if k == "hl":
                # needed only when the card has no thumb
                m = re.search(r'id:\s*"%s".*?thumb:\s*(null|"[^"]*")' % re.escape(cid), cases_js, re.S)
                if not (m and m.group(1) == "null"):
                    continue
            used.add("case.%s.%s" % (cid, k))
    for c in cats:
        used.add("cat." + c)
    for s in statuses:
        used.add("status." + s)
    gal = read(os.path.join(ROOT, "js", "data", "gallery.js"))
    for m in re.finditer(r'img:\s*"([\w\-]+)"', gal):
        used.add("gal." + m.group(1))
    for m in re.finditer(r'slot:\s*"([\w\-]+)"', gal):
        used.add("slot." + m.group(1)); used.add("slot." + m.group(1) + ".hint")
    for m in re.finditer(r'\{\s*id:\s*"([\w\-]+)",\s*kind:', cases_js):
        used.add("slot." + m.group(1)); used.add("slot." + m.group(1) + ".hint")
    for cid, _ in ids:
        # figure captions
        blk = re.search(r'id:\s*"%s".*?(?=\n    \{ id:|\n  \];)' % re.escape(cid), cases_js, re.S)
        if blk:
            n = len(re.findall(r'\{\s*img:', blk.group(0))) + len(re.findall(r'\{\s*id:\s*"[\w\-]+",\s*kind:', blk.group(0)))
            for i in range(1, n + 1):
                used.add("case.%s.f%d" % (cid, i))
    apptools = read(os.path.join(ROOT, "js", "data", "apptools.js"))
    for m in re.finditer(r'id:\s*"(\w+)",\s*n:', apptools):
        used.add("app.tools.%s.t" % m.group(1)); used.add("app.tools.%s.d" % m.group(1))
    used.update(["nav.engine.overview", "contact.email", "contact.github", "contact.linkedin", "contact.x", "contact.cv",
                 "media.kind.image", "media.kind.webp", "media.kind.video", "ui.more", "ui.before", "ui.after", "ui.toc",
                 "contact.todo", "i18n.partial", "ui.source", "ui.source.request", "footer.updated", "cat.all",
                 "ui.open", "ui.top", "status.rejected"])

    # --- 2. used keys that do not exist
    missing = sorted(k for k in used if k not in en and not k.endswith("."))
    for k in missing:
        print("MISSING  en key used but not defined:", k)
    problems += len(missing)

    # repeat prefixes need at least one item
    for p in sorted(repeats):
        if not any(k.startswith(p + ".1.") for k in en):
            print("MISSING  data-repeat/bars prefix has no items:", p); problems += 1
        else:
            for k in en:
                if k.startswith(p + "."):
                    used.add(k)

    # --- 3. unused english keys
    unused = sorted(k for k in en if k not in used and not any(k.startswith(r + ".") for r in repeats)
                    and not k.startswith("case.") and not k.startswith("slot.") and not k.startswith("gal."))
    for k in unused:
        print("unused   en key (warning):", k)

    # --- 4/5. japanese coverage
    text_keys = [k for k in en if is_text_key(k)]
    todo = [k for k in text_keys if k not in ja]
    extra = sorted(k for k in ja if k not in en)
    for k in extra:
        print("EXTRA    ja key has no English twin:", k); problems += 1
    print("Japanese coverage: %d / %d text keys (%.0f%%)" % (len(text_keys) - len(todo), len(text_keys),
          100.0 * (len(text_keys) - len(todo)) / max(1, len(text_keys))))
    by = {}
    for k in todo:
        by.setdefault(en[k][1], []).append(k)
    for b in sorted(by):
        print("  %-14s %4d keys still in English" % (b, len(by[b])))

    if stub:
        out = os.path.join(ROOT, "i18n", "ja")
        os.makedirs(out, exist_ok=True)
        for b, keys in by.items():
            lines = ['// Missing Japanese keys for bundle "%s". Copy the lines you translate into i18n/ja/%s.js' % (b, b)]
            for k in keys:
                lines.append("%s\t%s" % (k, en[k][0]))
            open(os.path.join(out, b + ".todo.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("wrote i18n/ja/*.todo.txt")

    print("\n%d problem(s)." % problems)
    if strict and problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
