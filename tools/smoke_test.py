#!/usr/bin/env python3
"""
Smoke test with headless Chrome (Edge is only the fallback). Opens every page of the site (both languages),
prints console errors and warnings ([i18n] missing key, JS errors, 404 resources) and can save screenshots.

  python tools/smoke_test.py                  # every *.html in the repo root + every case study, en + ja
  python tools/smoke_test.py --quick          # pages + ONE case per category (+ the "unknown case" page)
  python tools/smoke_test.py index.html       # only the given pages (case.html?id=culling works too)
  python tools/smoke_test.py --lang ja        # one language only
  python tools/smoke_test.py --jobs 4         # parallel browsers (default 3)
  python tools/smoke_test.py --shots out_dir  # also write full page PNG screenshots (1400 px wide)

Why this tool can be trusted (it failed silently before: headless Edge returned an empty page and the tool still printed OK):
  * Chrome is tried first. Edge only if Chrome is missing. Override with the env var GTW_BROWSER=<path to exe>.
  * POSITIVE CONTROL: before the real run it opens a tiny local page that calls console.error / console.warn and sets a
    DOM marker. If the tool does not see all three, it stops with "TOOL BLIND" (exit code 2).
  * Every page DOM must be at least 2000 characters, contain <main and the rendered <header (the layout script ran).
    Otherwise the page counts as a problem (not as OK).
  * A page that shows the blue "partly translated" note (class i18n-note) counts as a problem too: it means a key has no text
    in the chosen language (a JA file that registers its texts under "en" caused exactly this once).
  * Temp browser profiles are always deleted (try/finally, atexit, Ctrl+C). The browser's own TEMP is redirected into the
    profile folder, so it cannot leave "scoped_dir*" folders in %TEMP% any more. Old "gtw_*" folders (> 15 min) are swept.

Exit code: 0 clean, 1 console messages or page problems, 2 tool blind / no browser.

The helpers below (find_browser, run_browser, console_messages, dom_problems, control_check, html_pages, case_ids,
run_parallel) are reused by tools/find_placeholders.py.
"""
import atexit
import concurrent.futures as cf
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BROWSERS = [                      # Chrome FIRST (headless Edge returned an empty DOM on the author's PC)
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
MIN_DOM = 2000                    # a rendered page of this site is far bigger than this
TMP_PREFIX = "gtw_"               # every temp folder of these tools starts with this (so it can be swept)
STALE_MINUTES = 15
NOT_A_PAGE = ("404.html",)        # 404.html uses an absolute path, it cannot work from a plain folder


class ToolBlind(Exception):
    """The browser run cannot be trusted (no browser, empty DOM, positive control not seen)."""


# ---------------------------------------------------------------------------------------------------------------
# temp folder + process bookkeeping (nothing is ever left behind)
# ---------------------------------------------------------------------------------------------------------------
_lock = threading.Lock()
_profiles = set()
_procs = set()


def _kill_tree(pid):
    try:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, timeout=30)
    except Exception:
        pass


def _rmtree(path):
    def onerr(func, p, exc):
        try:
            os.chmod(p, 0o700)
            func(p)
        except Exception:
            pass
    for _ in range(6):
        shutil.rmtree(path, onerror=onerr)
        if not os.path.exists(path):
            return True
        time.sleep(0.5)       # the browser may still hold a file for a moment
    return not os.path.exists(path)


def new_profile(prefix=TMP_PREFIX + "run_"):
    path = tempfile.mkdtemp(prefix=prefix)
    with _lock:
        _profiles.add(path)
    return path


def drop_profile(path):
    _rmtree(path)
    with _lock:
        _profiles.discard(path)


def cleanup_all():
    with _lock:
        procs, profs = list(_procs), list(_profiles)
    for p in procs:
        try:
            if p.poll() is None:
                _kill_tree(p.pid)
        except Exception:
            pass
    for d in profs:
        drop_profile(d)


def sweep_stale():
    """delete leftovers of crashed earlier runs (folders gtw_* older than STALE_MINUTES in the temp folder)"""
    tmp = tempfile.gettempdir()
    now = time.time()
    n = 0
    try:
        names = os.listdir(tmp)
    except OSError:
        return 0
    for name in names:
        if not name.startswith(TMP_PREFIX):
            continue
        p = os.path.join(tmp, name)
        with _lock:
            if p in _profiles:
                continue
        try:
            if os.path.isdir(p) and now - os.path.getmtime(p) > STALE_MINUTES * 60:
                if _rmtree(p):
                    n += 1
        except OSError:
            pass
    return n


atexit.register(cleanup_all)


def _on_signal(signum, frame):
    cleanup_all()
    os._exit(130)


for _sig in ("SIGINT", "SIGTERM", "SIGBREAK"):
    if hasattr(signal, _sig):
        try:
            signal.signal(getattr(signal, _sig), _on_signal)
        except (ValueError, OSError):
            pass


# ---------------------------------------------------------------------------------------------------------------
# browser
# ---------------------------------------------------------------------------------------------------------------
def find_browser():
    env = os.environ.get("GTW_BROWSER")
    if env:
        if os.path.exists(env):
            return env
        raise ToolBlind("GTW_BROWSER points to a file that does not exist: " + env)
    for b in BROWSERS:
        if os.path.exists(b):
            return b
    raise ToolBlind("no Chrome or Edge found (set GTW_BROWSER=<path to exe>)")


def file_url(path):
    return "file:///" + os.path.abspath(path).replace("\\", "/")


def run_browser(url, shot=None, budget=8000, window="1400,900", timeout=120):
    """Open url in a fresh headless browser. Returns dict(dom, err, rc, timeout).
    shot=<png path>: write a screenshot instead of dumping the DOM. The profile is deleted in every case."""
    prof = new_profile()
    try:
        tmpd = os.path.join(prof, "tmp")
        os.makedirs(tmpd, exist_ok=True)
        env = dict(os.environ, TEMP=tmpd, TMP=tmpd)          # browser temp files stay inside the profile folder
        args = [find_browser(), "--headless=new", "--disable-gpu", "--disable-extensions", "--no-first-run",
                "--no-default-browser-check", "--disable-background-networking", "--disable-component-update",
                "--enable-logging=stderr", "--v=0", "--hide-scrollbars",
                "--user-data-dir=" + os.path.join(prof, "ud"), "--window-size=" + window,
                "--virtual-time-budget=%d" % budget]
        if shot:
            os.makedirs(os.path.dirname(os.path.abspath(shot)), exist_ok=True)
            if os.path.exists(shot):
                os.remove(shot)
            args.append("--screenshot=" + os.path.abspath(shot))
        else:
            args.append("--dump-dom")
        args.append(url)
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        with _lock:
            _procs.add(p)
        timed_out = False
        try:
            out, err = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_tree(p.pid)
            out, err = p.communicate()
        finally:
            with _lock:
                _procs.discard(p)
        if shot:                                              # the file can arrive late, wait until it is not empty
            t0 = time.time()
            while time.time() - t0 < 20:
                if os.path.exists(shot) and os.path.getsize(shot) > 1000:
                    break
                time.sleep(0.4)
        dec = lambda b: b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")
        return {"dom": dec(out), "err": dec(err), "rc": p.returncode, "timeout": timed_out}
    finally:
        drop_profile(prof)


_CONSOLE = re.compile(r"CONSOLE[^\]]*\]\s*(.*)")


def console_messages(stderr):
    out = []
    for line in stderr.splitlines():
        if "CONSOLE" in line and "ProtocolLaunch" not in line and "chrome-extension" not in line:
            m = _CONSOLE.search(line)
            out.append((m.group(1) if m else line)[:260])
        elif "ERR_FILE_NOT_FOUND" in line or "Failed to load resource" in line:
            out.append(line[-200:])
    return out


def dom_problems(dom):
    """a page that did not really render must never count as OK"""
    if len(dom) < MIN_DOM:
        return ["DOM only %d chars (browser blind or page empty)" % len(dom)]
    p = []
    if "<main" not in dom:
        p.append("no <main> in the DOM")
    if "<header" not in dom:
        p.append("no rendered <header> (layout script did not run)")
    return p


_CONTROL_HTML = """<!doctype html><html><head><meta charset="utf-8"><title>control</title></head>
<body><main id="m">control page</main>
<script>
console.error("GTW-CONTROL-ERROR");
console.warn("GTW-CONTROL-WARN");
document.getElementById("m").setAttribute("data-js", "ran");
</script></body></html>
"""


def control_check():
    """Positive control. Raises ToolBlind when the browser run cannot see a console error, a warning and a DOM change."""
    d = new_profile(TMP_PREFIX + "ctl_")
    try:
        page = os.path.join(d, "control.html")
        with open(page, "w", encoding="utf-8") as f:
            f.write(_CONTROL_HTML)
        r = run_browser(file_url(page), budget=3000, timeout=60)
    finally:
        drop_profile(d)
    msgs = console_messages(r["err"])
    seen_err = any("GTW-CONTROL-ERROR" in m for m in msgs)
    seen_warn = any("GTW-CONTROL-WARN" in m for m in msgs)
    seen_dom = 'data-js="ran"' in r["dom"]
    if not (seen_err and seen_warn and seen_dom):
        raise ToolBlind("TOOL BLIND: positive control failed (console.error seen: %s, console.warn seen: %s, DOM change seen: %s, "
                        "dom chars: %d, exit code: %s, timeout: %s). This browser run cannot be trusted. Browser: %s"
                        % (seen_err, seen_warn, seen_dom, len(r["dom"]), r["rc"], r["timeout"], find_browser()))
    return find_browser()


# ---------------------------------------------------------------------------------------------------------------
# page lists come from the repo (nothing is hard coded)
# ---------------------------------------------------------------------------------------------------------------
def html_pages():
    """every *.html in the repo root (index first, 404.html excluded)"""
    names = sorted(f for f in os.listdir(ROOT) if f.endswith(".html") and f not in NOT_A_PAGE)
    if "index.html" in names:
        names.remove("index.html")
        names.insert(0, "index.html")
    return names


def case_entries():
    """[(id, cat)] from js/data/cases.js and every other js/data/cases*.js (missing files are fine)"""
    out, d = [], os.path.join(ROOT, "js", "data")
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if f.startswith("cases") and f.endswith(".js"):
            s = open(os.path.join(d, f), encoding="utf-8").read()
            out += re.findall(r'\{\s*id:\s*"([\w\-]+)",\s*cat:\s*"(\w+)"', s)
    return out


def case_ids():
    return [c for c, _ in case_entries()]


def run_parallel(items, fn, workers):
    """ordered parallel map. Ctrl+C kills the browsers and removes the temp folders at once."""
    ex = cf.ThreadPoolExecutor(max_workers=max(1, workers))
    try:
        for r in ex.map(fn, items):
            yield r
    except KeyboardInterrupt:
        cleanup_all()
        ex.shutdown(wait=False, cancel_futures=True)
        print("\ninterrupted, temp folders removed")
        os._exit(130)
    finally:
        ex.shutdown(wait=True)


# ---------------------------------------------------------------------------------------------------------------
# the smoke test
# ---------------------------------------------------------------------------------------------------------------
def check(page, lang, shots):
    url = file_url(os.path.join(ROOT, page.split("?")[0]))
    if "?" in page:
        url += "?" + page.split("?", 1)[1] + "&"
    else:
        url += "?"
    url += "lang=" + lang + "&static=1"
    r = run_browser(url, budget=8000)
    msgs = console_messages(r["err"])
    probs = dom_problems(r["dom"])
    if 'class="i18n-note"' in r["dom"]:      # js/core/layout.js adds this blue bar when a key has no translation in the chosen language
        probs.append("the blue 'partly translated' note is shown: some keys have no %s text" % lang.upper())
    if r["timeout"]:
        probs.append("browser timeout")
    if shots:
        name = page.replace("?", "_").replace("=", "_").replace(".html", "") + "_" + lang + ".png"
        path = os.path.join(shots, name)
        run_browser(url, shot=path, budget=8000, window="1400,4200")
        if not (os.path.exists(path) and os.path.getsize(path) > 1000):
            probs.append("screenshot is empty or missing: " + name)
    return page, lang, msgs, probs


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__)
        return 0
    shots = None
    langs = ["en", "ja"]
    jobs = 3
    quick = "--quick" in args
    if quick:
        args.remove("--quick")
    for flag in ("--shots", "--lang", "--jobs"):
        if flag in args:
            i = args.index(flag)
            if i + 1 >= len(args):
                print("missing value for", flag)
                return 2
            val = args[i + 1]
            del args[i:i + 2]
            if flag == "--shots":
                shots = val
            elif flag == "--lang":
                langs = [val]
            else:
                jobs = int(val)

    swept = sweep_stale()
    try:
        browser = control_check()
    except ToolBlind as e:
        print(e)
        return 2
    print("browser: %s   positive control: OK%s" % (browser, ("   (swept %d old temp folders)" % swept) if swept else ""))

    if args:
        pages = args
    else:
        pages = [p for p in html_pages() if p != "case.html"]
        entries = case_entries()
        if quick:
            seen, ids = set(), []
            for cid, cat in entries:
                if cat not in seen:
                    seen.add(cat)
                    ids.append(cid)
        else:
            ids = [c for c, _ in entries]
        if "case.html" in html_pages():
            pages += ["case.html?id=" + c for c in ids] + ["case.html?id=nope"]
    todo = [(p, l) for p in pages for l in langs]
    print("%d pages x %d language(s) = %d browser runs\n" % (len(pages), len(langs), len(todo)))

    bad_msgs, bad_pages = 0, 0
    shown = {}                               # message -> number of pages that had it (each text is printed in full only once)
    base = file_url(ROOT) + "/"
    for page, lang, msgs, probs in run_parallel(todo, lambda t: check(t[0], t[1], shots), jobs):
        msgs = [m.replace(base, "") for m in msgs]
        n = len(msgs) + len(probs)
        print("%-40s %s  %s" % (page, lang, "OK" if not n else "%d message(s)" % n))
        for m in probs[:6]:
            print("       PAGE PROBLEM:", m)
        for m in msgs:
            shown[m] = shown.get(m, 0) + 1
            if shown[m] == 1 and len(shown) <= 40:
                print("      ", m)
        bad_msgs += len(msgs)
        bad_pages += 1 if probs else 0
    repeated = sorted(((c, m) for m, c in shown.items() if c > 1), reverse=True)
    if repeated:
        print("\nmessages seen on more than one page (printed in full only at first sight):")
        for c, m in repeated[:20]:
            print("  x%-3d %s" % (c, m[:150]))
    print("\nconsole messages: %d (%d different)   pages with a DOM problem: %d   browser runs: %d"
          % (bad_msgs, len(shown), bad_pages, len(todo)))
    return 1 if (bad_msgs or bad_pages) else 0


if __name__ == "__main__":
    try:
        code = main()
    except ToolBlind as e:
        print(e)
        code = 2
    except KeyboardInterrupt:
        cleanup_all()
        code = 130
    cleanup_all()
    sys.exit(code)
