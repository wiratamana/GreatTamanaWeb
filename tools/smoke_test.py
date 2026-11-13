#!/usr/bin/env python3
"""
Smoke test with headless Edge/Chrome. Opens every page (both languages), prints console errors
and warnings ([i18n] missing key, JS errors, 404 resources) and can save screenshots.

  python tools/smoke_test.py                  # all pages, en + ja, console check only
  python tools/smoke_test.py --shots out_dir  # also write PNG screenshots
  python tools/smoke_test.py index.html       # only one page
"""
import os
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
PAGES = ["index.html", "engine.html", "rendering.html", "clouds.html", "animation.html", "tools.html", "app.html",
         "journal.html", "gallery.html", "workflow.html", "about.html", "case.html?id=culling",
         "case.html?id=cloud-precision", "case.html?id=mmd-physics", "case.html?id=nope"]


def browser():
    for b in BROWSERS:
        if os.path.exists(b):
            return b
    sys.exit("no Edge/Chrome found")


def run(page, lang, shots):
    b = browser()
    url = "file:///" + ROOT.replace("\\", "/") + "/" + page
    url += ("&" if "?" in page else "?") + "lang=" + lang + "&static=1"
    prof = tempfile.mkdtemp(prefix="gtw_smoke_")
    args = [b, "--headless=new", "--disable-gpu", "--enable-logging=stderr", "--v=0", "--hide-scrollbars",
            "--user-data-dir=" + prof, "--window-size=1400,%d" % (4200 if shots else 900), "--virtual-time-budget=8000"]
    if shots:
        os.makedirs(shots, exist_ok=True)
        name = page.replace("?", "_").replace("=", "_").replace(".html", "") + "_" + lang + ".png"
        args.append("--screenshot=" + os.path.join(shots, name))
    else:
        args.append("--dump-dom")
    args.append(url)
    try:
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    finally:
        shutil.rmtree(prof, ignore_errors=True)   # the browser profile is big, never leave it behind
    out = []
    for line in r.stderr.splitlines():
        if "CONSOLE" in line and "ProtocolLaunch" not in line and "chrome-extension" not in line:
            out.append(line.split("CONSOLE:", 1)[1][:260])
        elif "ERR_FILE_NOT_FOUND" in line or "Failed to load resource" in line:
            out.append(line[-200:])
    return out


def main():
    shots = None
    args = sys.argv[1:]
    if "--shots" in args:
        i = args.index("--shots")
        shots = args[i + 1]
        del args[i:i + 2]
    pages = args or PAGES
    bad = 0
    for p in pages:
        for lang in ("en", "ja"):
            msgs = run(p, lang, shots)
            print("%-34s %s  %s" % (p, lang, "OK" if not msgs else "%d message(s)" % len(msgs)))
            for m in msgs[:12]:
                print("      ", m)
            bad += len(msgs)
    print("\nconsole messages: %d" % bad)


if __name__ == "__main__":
    main()
