#!/usr/bin/env python3
"""
Find every placeholder that is STILL SHOWN on the site (dashed media boxes and unset contact entries).

It opens the real pages in headless Chrome (Edge only as fallback), waits for the media probing to finish, and reads
the rendered DOM. So it reports what a visitor really sees, not what the data files say.

  python tools/find_placeholders.py                  # local files, every *.html page of the repo
  python tools/find_placeholders.py --cases          # also render all case study pages (slower)
  python tools/find_placeholders.py --live https://wiratamana.github.io/GreatTamanaWeb/
  python tools/find_placeholders.py --out placeholders.md      # save a markdown report
  python tools/find_placeholders.py --json                     # machine readable output
  python tools/find_placeholders.py --jobs 4                   # parallel browsers (default 3)

Result: for each slot: file to create, kind, hint (what to capture), and the pages where it appears.
Exit code: 0 nothing left, 1 something is still a placeholder (usable in a pre-publish check),
           2 the tool itself cannot be trusted (no browser, empty DOM, positive control not seen). It never says "0 placeholders"
           when the browser returned nothing.
Browser helpers (Chrome first, positive control, temp folder cleanup) live in tools/smoke_test.py.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import smoke_test as st          # noqa: E402  (shared browser helpers)

ROOT = st.ROOT

_PH = re.compile(r'<div class="ph"[^>]*>.*?<span class="f">assets/media/([\w\-]+) ', re.S)
_TODO = re.compile(r'<li><span class="k"[^>]*>([^<]*)</span><span class="todo"')


def hints():
    s = open(os.path.join(ROOT, "i18n", "en", "slots.js"), encoding="utf-8").read()
    m = re.search(r'add\(\s*"en"\s*,\s*(\{.*\})\s*\)\s*;', s, re.S)
    return json.loads(m.group(1))


def parse(dom):
    """-> (list of slot ids still shown as placeholder, list of unset contact keys)"""
    slots = [m.group(1) for m in _PH.finditer(dom)]
    contacts = [html.unescape(m.group(1)).strip() for m in _TODO.finditer(dom)]
    return slots, contacts


def selftest():
    """the parser must see a placeholder in a known snippet, otherwise 'nothing found' would mean nothing"""
    snippet = ('<div class="ph" data-x="1"><span class="k">x</span><span class="f">assets/media/test-slot .mp4</span></div>'
               '<li><span class="k" data-i18n="contact.cv">CV</span><span class="todo">not set</span></li>')
    slots, cons = parse(snippet)
    if slots != ["test-slot"] or cons != ["CV"]:
        raise st.ToolBlind("TOOL BLIND: placeholder parser self test failed (%r, %r). The page markup changed: fix parse()." % (slots, cons))


def render(url):
    """-> rendered DOM. Raises ToolBlind when the DOM is empty or is not a rendered page."""
    r = st.run_browser(url, budget=9000, timeout=150)
    probs = st.dom_problems(r["dom"])
    if r["timeout"]:
        probs.append("browser timeout")
    if probs:
        raise st.ToolBlind("TOOL BLIND: %s : %s" % (url, "; ".join(probs)))
    return r["dom"]


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__)
        return 0
    live = None
    out = None
    jobs = 3
    if "--live" in args:
        live = args[args.index("--live") + 1].rstrip("/") + "/"
    if "--out" in args:
        out = args[args.index("--out") + 1]
    if "--jobs" in args:
        jobs = int(args[args.index("--jobs") + 1])
    want_json = "--json" in args

    st.sweep_stale()
    selftest()
    browser = st.control_check()
    if not want_json:
        print("browser: %s   positive control: OK" % browser)

    pages = [p for p in st.html_pages() if p != "case.html"]
    if "--cases" in args and "case.html" in st.html_pages():
        pages += ["case.html?id=" + c for c in st.case_ids()]
    base = live or (st.file_url(ROOT) + "/")

    def job(p):
        sep = "&" if "?" in p else "?"
        return p, parse(render(base + p + sep + "lang=en&static=1"))

    found = {}      # slot -> set(pages)
    contacts = {}   # key -> set(pages)
    for p, (slots, cons) in st.run_parallel(pages, job, jobs):
        for s in slots:
            found.setdefault(s, set()).add(p)
        for c in cons:
            contacts.setdefault(c, set()).add(p)
        if not want_json:
            print("%-34s %d placeholder(s)" % (p, len(slots) + len(cons)))

    # kinds from the source
    kinds = {}
    src = ""
    for f in os.listdir(ROOT):
        if f.endswith(".html"):
            src += open(os.path.join(ROOT, f), encoding="utf-8").read()
    for sub in ("js/data", "js/pages", "js/components"):
        d = os.path.join(ROOT, sub)
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith(".js"):
                    src += open(os.path.join(d, f), encoding="utf-8").read()
    for m in re.finditer(r'data-slot="([\w\-]+)"(?:\s+data-kind="(\w+)")?', src):
        kinds[m.group(1)] = m.group(2) or "image"
    for m in re.finditer(r'\{\s*(?:slot|id):\s*"([\w\-]+)",\s*kind:\s*"(\w+)"', src):
        kinds[m.group(1)] = m.group(2)
    ext = {"image": "webp | png | jpg", "webp": "webp (animated)", "video": "mp4 | webm"}
    h = hints()

    rows = []
    for s in sorted(found):
        k = kinds.get(s, "image")
        rows.append({"slot": s, "kind": k, "file": "assets/media/%s.(%s)" % (s, ext.get(k, "webp")),
                     "hint": h.get("slot." + s + ".hint", ""), "pages": sorted(found[s])})
    crow = [{"contact": c, "pages": sorted(p)} for c, p in sorted(contacts.items())]

    if want_json:
        print(json.dumps({"slots": rows, "contacts": crow}, indent=2, ensure_ascii=False))
    else:
        lines = ["", "STILL PLACEHOLDER: %d media slot(s), %d unset contact entr%s" % (len(rows), len(crow), "y" if len(crow) == 1 else "ies"), ""]
        for kind in ("image", "webp", "video"):
            sel = [r for r in rows if r["kind"] == kind]
            if not sel:
                continue
            lines.append("== %s (%d)" % ({"image": "Static images", "webp": "Animated WebP", "video": "Videos"}[kind], len(sel)))
            for r in sel:
                lines.append("  %s" % r["file"])
                lines.append("      capture: %s" % r["hint"])
                lines.append("      shown on: %s" % ", ".join(r["pages"]))
            lines.append("")
        if crow:
            lines.append("== Contact entries not set (js/data/site.js, set showPlaceholders:false to hide)")
            for c in crow:
                lines.append("  %s  (on: %s)" % (c["contact"], ", ".join(c["pages"])))
            lines.append("")
        if not rows and not crow:
            lines.append("Nothing left. No placeholder is visible on the %d checked pages (all DOMs were rendered and non-empty)." % len(pages))
        print("\n".join(lines))
        if out:
            md = ["# Placeholders still shown", ""]
            for kind, title in (("image", "Static images"), ("webp", "Animated WebP"), ("video", "Videos")):
                sel = [r for r in rows if r["kind"] == kind]
                if sel:
                    md += ["## " + title, "", "| File | What to capture | Pages |", "|---|---|---|"]
                    for r in sel:
                        md.append("| `%s` | %s | %s |" % (r["file"], r["hint"].replace("|", "/"), ", ".join(r["pages"])))
                    md.append("")
            if crow:
                md += ["## Contact entries", ""] + ["- " + c["contact"] for c in crow] + [""]
            open(out, "w", encoding="utf-8").write("\n".join(md))
            print("report written:", out)
    return 1 if (rows or crow) else 0


if __name__ == "__main__":
    try:
        code = main()
    except st.ToolBlind as e:
        print(e)
        code = 2
    except KeyboardInterrupt:
        st.cleanup_all()
        code = 130
    st.cleanup_all()
    sys.exit(code)
