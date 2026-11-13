#!/usr/bin/env python3
"""
Find every placeholder that is STILL SHOWN on the site (dashed media boxes and unset contact entries).

It opens the real pages in headless Edge/Chrome, waits for the media probing to finish, and reads the
rendered DOM. So it reports what a visitor really sees, not what the data files say.

  python tools/find_placeholders.py                  # local files, all pages
  python tools/find_placeholders.py --cases          # also render all case study pages (slower)
  python tools/find_placeholders.py --live https://wiratamana.github.io/GreatTamanaWeb/
  python tools/find_placeholders.py --out placeholders.md      # save a markdown report
  python tools/find_placeholders.py --json                     # machine readable output

Result: for each slot: file to create, kind, hint (what to capture), and the pages where it appears.
Exit code 1 when something is still a placeholder (usable in a pre-publish check).
"""
import concurrent.futures as cf
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]
MAIN_PAGES = ["index.html", "engine.html", "rendering.html", "clouds.html", "animation.html", "tools.html",
              "app.html", "journal.html", "gallery.html", "workflow.html", "about.html"]


def browser():
    for b in BROWSERS:
        if os.path.exists(b):
            return b
    sys.exit("no Edge/Chrome found")


def case_ids():
    s = open(os.path.join(ROOT, "js", "data", "cases.js"), encoding="utf-8").read()
    return re.findall(r'\{\s*id:\s*"([\w\-]+)",\s*cat:', s)


def hints():
    s = open(os.path.join(ROOT, "i18n", "en", "slots.js"), encoding="utf-8").read()
    m = re.search(r'add\(\s*"en"\s*,\s*(\{.*\})\s*\)\s*;', s, re.S)
    return json.loads(m.group(1))


def render(url):
    prof = tempfile.mkdtemp(prefix="gtw_ph_")
    try:
        r = subprocess.run([browser(), "--headless=new", "--disable-gpu", "--user-data-dir=" + prof,
                            "--virtual-time-budget=9000", "--dump-dom", url],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=150)
        return r.stdout
    finally:
        shutil.rmtree(prof, ignore_errors=True)


def parse(dom):
    """-> (list of slot ids still shown as placeholder, list of unset contact keys)"""
    slots = []
    for m in re.finditer(r'<div class="ph"[^>]*>.*?<span class="f">assets/media/([\w\-]+) ', dom, re.S):
        slots.append(m.group(1))
    contacts = []
    for m in re.finditer(r'<li><span class="k"[^>]*>([^<]*)</span><span class="todo"', dom):
        contacts.append(html.unescape(m.group(1)).strip())
    return slots, contacts


def main():
    args = sys.argv[1:]
    live = None
    out = None
    if "--live" in args:
        live = args[args.index("--live") + 1].rstrip("/") + "/"
    if "--out" in args:
        out = args[args.index("--out") + 1]
    want_json = "--json" in args

    pages = list(MAIN_PAGES)
    if "--cases" in args:
        pages += ["case.html?id=" + c for c in case_ids()]
    base = live or ("file:///" + ROOT.replace("\\", "/") + "/")

    def job(p):
        sep = "&" if "?" in p else "?"
        return p, parse(render(base + p + sep + "lang=en&static=1"))

    found = {}      # slot -> set(pages)
    contacts = {}   # key -> set(pages)
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for p, (slots, cons) in ex.map(job, pages):
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
    for sub in ("js/data", "js/pages"):
        d = os.path.join(ROOT, sub)
        for f in os.listdir(d):
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
            lines.append("Nothing left. No placeholder is visible on the checked pages.")
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
    sys.exit(1 if (rows or crow) else 0)


if __name__ == "__main__":
    main()
