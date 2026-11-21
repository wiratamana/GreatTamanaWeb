#!/usr/bin/env python3
"""
i18n checker. No dependencies. Run from anywhere:

  python tools/i18n_check.py                       # report
  python tools/i18n_check.py --strict              # exit code 1 if anything is wrong (for CI / before publishing)
  python tools/i18n_check.py --numbers             # also compare the numbers in EN and JA texts (number drift check)
  python tools/i18n_check.py --full-ja             # a missing Japanese key counts as a problem (the site must stay 100% Japanese)
  python tools/i18n_check.py --stub                # write i18n/ja/<bundle>.todo.txt with every missing key + English text
  python tools/i18n_check.py --strict --full-ja --numbers      # the full pre-publish gate

What it checks
  1. Every i18n/en/*.js and i18n/ja/*.js file is valid JSON inside GTW.i18n.add("xx", {...}); (an empty or comment-only file is accepted)
  2. Every key used by the HTML pages / page scripts exists in the English files
     (data-i18n, data-cap, data-repeat, data-bars, data-title, data-desc, GTW.t(...), case keys, slot keys, gallery keys)
  3. English keys that nothing uses (warning only)
  4. Japanese coverage: which English keys have no Japanese text yet
  5. Japanese keys that do not exist in English (typos)
  6. Case index files: js/data/cases.js AND every other js/data/cases*.js (cases-world, cases-trees, cases-cloud2 ...):
     duplicate ids, entries that do not start with { id: "...", cat: "...", (the checker and the site tools would skip them),
     categories missing in GTW.cats, unknown status
  7. Bundles: every bundle named in <html data-bundles>, every entry of CASE_BUNDLES in js/core/loader.js, "slots" and
     "common" must exist for en AND ja. Every js file named in data-scripts and CASE_DATA must exist.
  8. --numbers: for every key in EN and JA, the numbers in the text must match (5,938 / 4.5 / 2026-11-22 ...). {tokens}
     like {cases} must be the same in both languages. Same stat label with two different values on different pages is reported.
     JA may add small numbers (month, day) but a missing or wrong big number is reported.

Keys ending in .href .img .ic .tagc .hl .slot .kind .ratio .thumb .tone .b .a .u are NOT text and are skipped.
"""
import json
import os
import re
import sys
import unicodedata
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NON_TEXT = ("href", "img", "ic", "tagc", "hl", "slot", "kind", "ratio", "thumb", "tone", "b", "a", "u")
STATUSES = ("landed", "partial", "diagnosed", "rejected")
CASE_START = re.compile(r'\{\s*id:\s*"([\w\-]+)",\s*cat:\s*"(\w+)"')
CASE_LOOSE = re.compile(r'\{\s*id:\s*"([\w\-]+)"\s*,(?!\s*(?:cat:|kind:))')   # { id: "x", <something else> }  = wrong order


def load_dict(path, expect_lang=None):
    s = open(path, encoding="utf-8").read()
    code = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    code = re.sub(r"(?m)^\s*//.*$", "", code)
    if not code.strip():
        return {}                       # empty skeleton file
    m = re.search(r'add\(\s*"(\w+)"\s*,\s*(\{.*\})\s*\)\s*;', s, re.S)
    if not m:
        raise ValueError("no GTW.i18n.add(...) found")
    if expect_lang and m.group(1) != expect_lang:
        # a ja file that says add("en", ...) silently overwrites the English texts and leaves ja empty (found by QA-A on 2026-11-22)
        raise ValueError('GTW.i18n.add("%s", ...) in the %s folder: wrong language code' % (m.group(1), expect_lang))
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
            data = load_dict(os.path.join(d, f), lang)
            for k, v in data.items():
                if k in out and out[k][1] != f[:-3]:
                    errors.append("%s: key %r is defined in two bundles (%s and %s)" % (lang, k, out[k][1], f[:-3]))
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


def js_files(sub):
    d = os.path.join(ROOT, sub)
    if not os.path.isdir(d):
        return []
    return [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".js")]


def collect_used():
    used, repeats = set(), set()
    files = [os.path.join(ROOT, f) for f in os.listdir(ROOT) if f.endswith(".html")]
    for sub in ("js/pages", "js/components", "js/core", "js/data"):
        files += js_files(sub)
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


def read_cases():
    """-> (entries, cats_list, problems). entries = [dict(id, cat, block, file)] from js/data/cases*.js"""
    entries, problems, cats_list = [], [], []
    d = os.path.join(ROOT, "js", "data")
    files = sorted(f for f in os.listdir(d) if f.startswith("cases") and f.endswith(".js")) if os.path.isdir(d) else []
    for f in files:
        s = read_code(os.path.join(d, f))
        m = re.search(r'GTW\.cats\s*=\s*\[([^\]]*)\]', s)
        if m:
            cats_list = re.findall(r'"(\w+)"', m.group(1))
        starts = list(CASE_START.finditer(s))
        for i, m in enumerate(starts):
            end = starts[i + 1].start() if i + 1 < len(starts) else len(s)
            entries.append({"id": m.group(1), "cat": m.group(2), "block": s[m.start():end], "file": f})
        for m in CASE_LOOSE.finditer(s):
            problems.append('js/data/%s: entry "%s" must start with { id: "...", cat: "...", (cat right after id), or the tools skip it' % (f, m.group(1)))
    return entries, cats_list, problems


def check_structure():
    """bundles and scripts named by pages and by the loader must exist. -> list of problem texts"""
    probs = []
    loader = read(os.path.join(ROOT, "js", "core", "loader.js")) if os.path.exists(os.path.join(ROOT, "js", "core", "loader.js")) else ""
    m = re.search(r'CASE_BUNDLES\s*=\s*\[([^\]]*)\]', loader)
    case_bundles = re.findall(r'"([\w\-]+)"', m.group(1)) if m else []
    m = re.search(r'CASE_DATA\s*=\s*\[([^\]]*)\]', loader)
    case_data = re.findall(r'"([\w\-/]+)"', m.group(1)) if m else []
    need = {"common", "slots"}
    for f in sorted(os.listdir(ROOT)):
        if not f.endswith(".html"):
            continue
        s = read(os.path.join(ROOT, f))
        mb = re.search(r'data-bundles="([^"]*)"', s)
        if mb:
            for b in (x.strip() for x in mb.group(1).split(",")):
                if b == "cases":
                    need.update(case_bundles)
                elif b:
                    need.add(b)
        ms = re.search(r'data-scripts="([^"]*)"', s)
        if ms:
            for sc in (x.strip() for x in ms.group(1).split(",")):
                if sc and not os.path.exists(os.path.join(ROOT, "js", sc + ".js")):
                    probs.append("%s: data-scripts names js/%s.js but the file does not exist" % (f, sc))
                if sc == "data/cases":
                    for c in case_data:
                        if not os.path.exists(os.path.join(ROOT, "js", c + ".js")):
                            probs.append("loader.js CASE_DATA names js/%s.js but the file does not exist" % c)
    for b in sorted(need):
        for lang in ("en", "ja"):
            if not os.path.exists(os.path.join(ROOT, "i18n", lang, b + ".js")):
                probs.append("bundle i18n/%s/%s.js is required by a page or by loader.js but does not exist" % (lang, b))
    for lang in ("en", "ja"):    # bundle files that no page and no loader entry can ever load
        d = os.path.join(ROOT, "i18n", lang)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".js") and f[:-3] not in need:
                    probs.append("bundle i18n/%s/%s is never loaded (no page lists it in data-bundles, not in CASE_BUNDLES)" % (lang, f))
    return probs


# ---------------------------------------------------------------------------------------------------------------
# number drift (EN vs JA)
# ---------------------------------------------------------------------------------------------------------------
_NUM = re.compile(r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(億|万|k(?![A-Za-z])|K(?![A-Za-z])|\s?million(?![A-Za-z]))?")
_TOKEN = re.compile(r"\{[\w.]+\}")
_SUP = str.maketrans({c: " " for c in "⁰¹²³⁴⁵⁶⁷⁸⁹"})        # 128³ : the exponent is not a number of its own
_MULT = {"億": 1e8, "万": 1e4, "k": 1e3, "K": 1e3}


def num_values(text):
    """all numbers of a text as VALUES, so that EN '50,000' / '50k' and JA '5万' are the same number (万 = 10,000, 億 = 100,000,000)"""
    t = unicodedata.normalize("NFKC", text.translate(_SUP))        # full width digits -> normal digits
    t = _TOKEN.sub(" ", t)
    t = re.sub(r"<[^>]*>", " ", t)
    ms = list(_NUM.finditer(t))
    vals, i = set(), 0
    while i < len(ms):
        m = ms[i]
        v = float(m.group(1).replace(",", ""))
        u = m.group(2)
        mult = 1e6 if (u and "million" in u) else _MULT.get(u, 1.0)
        v *= mult
        if u == "億" and i + 1 < len(ms) and ms[i + 1].start() == m.end():   # 1億200万 = 102,000,000
            nx = ms[i + 1]
            v += float(nx.group(1).replace(",", "")) * _MULT.get(nx.group(2), 1.0)
            i += 1
        vals.add(round(v, 6))
        i += 1
    return vals


def fmt(vs):
    return ", ".join(("%d" % v) if v == int(v) else ("%g" % v) for v in sorted(vs))


def number_problems(en, ja):
    out = []
    for k in sorted(en):
        if k not in ja or not is_text_key(k):
            continue
        te, tj = en[k][0], ja[k][0]
        if not isinstance(te, str) or not isinstance(tj, str):
            continue
        pe, pj = sorted(_TOKEN.findall(te)), sorted(_TOKEN.findall(tj))
        if pe != pj:
            out.append((k, "placeholder tokens differ: EN %s  JA %s" % (pe, pj), te, tj))
            continue
        ne, nj = num_values(te), num_values(tj)
        if not ne and not nj:
            continue
        missing = ne - nj                                   # in EN, not in JA: a number the translator dropped or did not update
        big = [v for v in (nj - ne) if v >= 100]            # in JA, not in EN: JA may add small numbers (month, day, "0.5" for "half")
        if missing or big:
            msg = []
            if missing:
                msg.append("EN has, JA lacks: " + fmt(missing))
            if big:
                msg.append("JA has, EN lacks: " + fmt(big))
            out.append((k, "; ".join(msg), te, tj))
    # the same stat label must not carry two different values on two pages (home vs engine ...)
    stats = {}
    for k, (v, _) in en.items():
        m = re.match(r"^(\w+)\.stats\.(\d+)\.v$", k)
        if m and (m.group(1) + ".stats." + m.group(2) + ".l") in en:
            label = re.sub(r"\W+", " ", en[m.group(1) + ".stats." + m.group(2) + ".l"][0].lower()).strip()
            stats.setdefault(label, {})[k] = v
    for label, kv in sorted(stats.items()):
        if len(set(kv.values())) > 1:
            out.append((", ".join(sorted(kv)), "same stat label %r has different values: %s" % (label, sorted(set(kv.values()))), "", ""))
    return out


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__)
        return 0
    strict = "--strict" in args
    stub = "--stub" in args
    numbers = "--numbers" in args
    full_ja = "--full-ja" in args
    problems = 0

    en, err = load_lang("en")
    for e in err:
        print("ERROR  invalid file:", e); problems += 1
    ja, err = load_lang("ja")
    for e in err:
        print("ERROR  invalid file:", e); problems += 1
    print("English keys: %d   Japanese keys: %d" % (len(en), len(ja)))

    for e in check_structure():
        print("STRUCT  ", e); problems += 1

    used, repeats = collect_used()

    # case + slot + gallery keys that are built by code
    entries, cats_list, cprobs = read_cases()
    for e in cprobs:
        print("CASES   ", e); problems += 1
    seen_ids = {}
    for e in entries:
        if e["id"] in seen_ids:
            print("CASES    duplicate case id %r (in %s and %s)" % (e["id"], seen_ids[e["id"]], e["file"])); problems += 1
        seen_ids[e["id"]] = e["file"]
        if cats_list and e["cat"] not in cats_list:
            print("CASES    case %r uses category %r that is not in GTW.cats %s" % (e["id"], e["cat"], cats_list)); problems += 1
        st = re.search(r'status:\s*"(\w+)"', e["block"])
        if not st:
            print("CASES    case %r has no status" % e["id"]); problems += 1
        elif st.group(1) not in STATUSES:
            print("CASES    case %r has unknown status %r" % (e["id"], st.group(1))); problems += 1
    print("Case studies: %d in %d index file(s)" % (len(entries), len(set(e["file"] for e in entries))))

    cats, statuses = set(), set()
    for e in entries:
        cid, blk = e["id"], e["block"]
        cats.add(e["cat"])
        st = re.search(r'status:\s*"(\w+)"', blk)
        if st:
            statuses.add(st.group(1))
        for k in ("title", "summary", "hl", "problem", "fix", "result"):
            if k == "hl":
                th = re.search(r'thumb:\s*(null|"[^"]*")', blk)      # the tile text is needed only when the card has no thumb
                if th and th.group(1) != "null":
                    continue
            used.add("case.%s.%s" % (cid, k))
        n = len(re.findall(r'\{\s*img:', blk)) + len(re.findall(r'\{\s*id:\s*"[\w\-]+",\s*kind:', blk))
        for i in range(1, n + 1):                                      # figure captions
            used.add("case.%s.f%d" % (cid, i))
        for m in re.finditer(r'\{\s*id:\s*"([\w\-]+)",\s*kind:', blk):
            used.add("slot." + m.group(1)); used.add("slot." + m.group(1) + ".hint")
    for c in cats:
        used.add("cat." + c)
    for c in cats_list:
        used.add("cat." + c)
    for s in statuses:
        used.add("status." + s)
    gal = read(os.path.join(ROOT, "js", "data", "gallery.js"))
    for m in re.finditer(r'img:\s*"([\w\-]+)"', gal):
        used.add("gal." + m.group(1))
    for m in re.finditer(r'slot:\s*"([\w\-]+)"', gal):
        used.add("slot." + m.group(1)); used.add("slot." + m.group(1) + ".hint")
    mg = re.search(r'galleryGroups\s*=\s*\[([^\]]*)\]', gal)
    if mg:
        used.add("gal.g.all")
        for g in re.findall(r'"(\w+)"', mg.group(1)):
            used.add("gal.g." + g)
    apptools = read(os.path.join(ROOT, "js", "data", "apptools.js"))
    for m in re.finditer(r'id:\s*"(\w+)",\s*n:', apptools):
        used.add("app.tools.%s.t" % m.group(1)); used.add("app.tools.%s.d" % m.group(1))
    used.update(["nav.engine.overview", "contact.email", "contact.github", "contact.cv",
                 "media.kind.image", "media.kind.webp", "media.kind.video", "ui.more", "ui.before", "ui.after", "ui.toc",
                 "contact.todo", "i18n.partial", "ui.source", "ui.source.request", "footer.updated", "cat.all",
                 "ui.open", "ui.top", "status.rejected",
                 # used dynamically (badge / nav code builds the key at run time)
                 "status.local", "status.local.landed", "status.local.partial", "status.local.diagnosed",
                 "status.local.rejected", "cat.feat", "nav.new"])

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
    if full_ja:
        problems += len(todo)
        for k in todo[:40]:
            print("NO-JA    ja key missing:", k)
        if len(todo) > 40:
            print("NO-JA    ... and %d more (run --stub for the full list)" % (len(todo) - 40))

    # --- 8. number drift
    if numbers:
        nm = number_problems(en, ja)
        for k, msg, te, tj in nm:
            print("NUMBERS  %s : %s" % (k, msg))
            if te:
                print("           EN: %s" % te[:150].replace("\n", " "))
                print("           JA: %s" % tj[:150].replace("\n", " "))
        print("Number check: %d mismatch(es) in %d keys that have a Japanese twin" % (len(nm), sum(1 for k in en if k in ja)))
        problems += len(nm)

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
    return 1 if (strict and problems) else 0


if __name__ == "__main__":
    sys.exit(main())
