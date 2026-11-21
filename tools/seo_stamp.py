#!/usr/bin/env python3
"""
seo_stamp.py - writes the STATIC head data (title, description, canonical, Open Graph, Twitter card,
hreflang, icons, JSON-LD) and a readable <noscript> into every root *.html page, and writes
sitemap.xml + robots.txt.

Why: the site builds all visible text with JavaScript. Link previews (Slack, LinkedIn, X, Teams, LINE),
search engines, ATS parsers and AI summary tools do not run it. They only see what is in the HTML file.

How it works
  * Reads data-title / data-desc of every <html> tag, resolves the keys in i18n/en/*.js (English).
    Tokens {cases} and {updated} are resolved the same way the site does it.
  * Writes everything between  <!--seo:begin-->  and  <!--seo:end-->  inside <head>.
    Block is created if missing, replaced if present (idempotent: a second run changes nothing).
    Old <title>, meta description, theme-color, og:*, twitter:*, icon, canonical, alternate and
    ld+json tags OUTSIDE the block are removed (no duplicates).
  * Writes a static <noscript> between  <!--seo:noscript-->  and  <!--seo:/noscript-->  in <body>.
    This block is hard-coded English text. It is the ONLY place where text is not an i18n key
    (it must work without JavaScript, so it cannot use the i18n files).
  * Writes sitemap.xml (all root pages + every case URL) and robots.txt.

Usage (run from anywhere)
  python tools/seo_stamp.py                 stamp all pages + sitemap.xml + robots.txt
  python tools/seo_stamp.py --check         change nothing, exit 1 if something would change
  python tools/seo_stamp.py --root <dir>    work on another copy of the site (for tests)
  python tools/seo_stamp.py --no-sitemap    only the pages
  python tools/seo_stamp.py --only-sitemap  only sitemap.xml + robots.txt
Run it as the LAST step before a release (after texts and page titles are final), and after tools/stamp.py.

Needs: Python 3.8+. Pillow is optional (used only to read the og:image size).
Needs assets/img/og-world.jpg (1200x630). If it is missing, the script falls back to cloud-hero.webp and prints a warning.
"""
import argparse
import glob
import html
import json
import os
import re
import sys

BASE = "https://wiratamana.github.io/GreatTamanaWeb/"
ROLE_LINE = ("Graphics, engine and tools programmer. Vulkan game engine in C++20, an AI agent desktop app in C#, "
             "and an R&D journal with measured results. Looking for a role in Japan.")
KNOWS_ABOUT = ["Vulkan", "C++20", "GLSL", "Game engine", "Procedural generation", "Volumetric clouds",
               "Real-time rendering", "Game engine tools"]
JOB_TITLE = "Graphics and engine programmer"

# og:image per page: first existing file wins (searched in assets/img and assets/media)
DEFAULT_IMG = ["og-world.jpg", "cloud-hero.webp"]
PAGE_IMG = {
    "animation.html": ["engine-toon-character.webp"] + DEFAULT_IMG,
    "tools.html":     ["editor-overview.webp"] + DEFAULT_IMG,
    "app.html":       ["app-chat-main.webp"] + DEFAULT_IMG,
    "workflow.html":  ["app-subagents.webp"] + DEFAULT_IMG,
}
IMG_ALT = {
    "og-world.jpg": "A landscape rendered in my own Vulkan engine",
    "cloud-hero.webp": "Volumetric clouds rendered in my own Vulkan engine",
    "engine-toon-character.webp": "A toon-shaded character rendered in my own engine",
    "editor-overview.webp": "The editor of my own game engine",
    "app-chat-main.webp": "The chat window of GreatTamanaApp",
    "app-subagents.webp": "Parallel sub-agents in GreatTamanaApp",
}
# pages where the generic rule is wrong (case.html is one template for 30+ cases; 404 must not be indexed)
OVERRIDE = {
    "case.html": {"title": "R&D case study · {site}",
                  "desc": "An engine investigation: problem, root cause, fix, result, and what was not proven.",
                  "canonical": False},
    "404.html": {"title": "Page not found · {site}", "desc": None, "noindex": True},
}
NOSCRIPT_LINKS = [("engine.html", "Engine and editor"), ("world.html", "Procedural world"),
                  ("journal.html", "R&D journal"), ("app.html", "AI agent app"),
                  ("about.html", "About and contact")]

# ---------------------------------------------------------------------------------------------
def read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()

def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

_STR = re.compile(r'^\s*"((?:[^"\\]|\\.)+)"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,?\s*(?://.*)?$')

def load_i18n(root):
    d = {}
    for p in sorted(glob.glob(os.path.join(root, "i18n", "en", "*.js"))):
        for line in read_text(p).splitlines():
            m = _STR.match(line)
            if not m:
                continue
            try:
                d[m.group(1)] = json.loads('"' + m.group(2) + '"')
            except ValueError:
                d[m.group(1)] = m.group(2).replace('\\"', '"').replace("\\'", "'")
    return d

def load_site(root):
    s = read_text(os.path.join(root, "js", "data", "site.js"))
    def g(rx, default=""):
        m = re.search(rx, s)
        return m.group(1) if m else default
    return {
        "updated": g(r'updated:\s*"([^"]*)"', ""),
        "name": g(r'name:\s*\{\s*en:\s*"([^"]*)"', "Wira Tamana"),
        "email": g(r'email:\s*"([^"]*)"', ""),
        "github": g(r'github:\s*"([^"]*)"', ""),
    }

def case_ids(root):
    ids = []
    for p in sorted(glob.glob(os.path.join(root, "js", "data", "cases*.js"))):
        # only real case entries: { id: "x", cat: "y" ... (slot entries also have id: but never cat:)
        for m in re.finditer(r'\{\s*id:\s*"([a-z0-9][a-z0-9-]*)"\s*,\s*cat:', read_text(p)):
            if m.group(1) not in ids:
                ids.append(m.group(1))
    return ids

def clean_text(s, tokens):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\{(\w+)\}", lambda m: str(tokens.get(m.group(1), m.group(0))), s)
    return html.unescape(s).strip()

def esc(s):
    return html.escape(s, quote=True)

def find_image(root, names):
    for n in names:
        for sub in ("assets/img", "assets/media"):
            p = os.path.join(root, *sub.split("/"), n)
            if os.path.isfile(p):
                return n, sub, p
    return None

def image_size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None

# ---------------------------------------------------------------------------------------------
def build_head_block(root, fname, attrs, i18n, site, tokens, nl, warns, old_theme):
    ov = OVERRIDE.get(fname, {})
    page = attrs.get("data-page", "")
    site_name = site["name"]

    # --- title + description ---
    if "title" in ov:
        title = ov["title"].replace("{site}", site_name)
    else:
        tk = attrs.get("data-title")
        if not tk or tk not in i18n:
            warns.append("%s: title key %r not found in i18n/en (keeping old title)" % (fname, tk))
            return None
        title = clean_text(i18n[tk], tokens)
        if page != "home" and site_name:
            title += " \u00b7 " + site_name
    if "desc" in ov:
        desc = ov["desc"]
    else:
        dk = attrs.get("data-desc")
        if dk and dk in i18n:
            desc = clean_text(i18n[dk], tokens)
        else:
            desc = None
            if dk:
                warns.append("%s: description key %r not found in i18n/en" % (fname, dk))
    if desc and len(desc) > 200:
        warns.append("%s: description is %d chars (search engines cut at about 160)" % (fname, len(desc)))
    if title and len(title) > 90:
        warns.append("%s: title is %d chars (long)" % (fname, len(title)))

    noindex = bool(ov.get("noindex"))
    canon_ok = ov.get("canonical", True) and not noindex
    url = BASE if fname == "index.html" else BASE + fname

    L = ["<!--seo:begin-->", "<title>%s</title>" % esc(title)]
    if desc:
        L.append('<meta name="description" content="%s">' % esc(desc))
    if noindex:
        L.append('<meta name="robots" content="noindex">')
    L.append('<meta name="theme-color" content="%s">' % esc(old_theme or "#0d1014"))

    if canon_ok:
        L.append('<link rel="canonical" href="%s">' % url)
        L.append('<link rel="alternate" hreflang="en" href="%s">' % url)
        L.append('<link rel="alternate" hreflang="ja" href="%s?lang=ja">' % url)
        L.append('<link rel="alternate" hreflang="x-default" href="%s">' % url)

    if not noindex:
        img = find_image(root, PAGE_IMG.get(fname, DEFAULT_IMG))
        if img is None:
            warns.append("%s: no og:image file found (%s)" % (fname, ", ".join(PAGE_IMG.get(fname, DEFAULT_IMG))))
        else:
            if img[0] != PAGE_IMG.get(fname, DEFAULT_IMG)[0] and fname in ("index.html", "world.html"):
                warns.append("%s: using fallback og:image %s (preferred %s is missing)" % (fname, img[0], PAGE_IMG.get(fname, DEFAULT_IMG)[0]))
        L += ['<meta property="og:type" content="website">',
              '<meta property="og:site_name" content="%s">' % esc(site_name),
              '<meta property="og:title" content="%s">' % esc(title)]
        if desc:
            L.append('<meta property="og:description" content="%s">' % esc(desc))
        if canon_ok:
            L.append('<meta property="og:url" content="%s">' % url)
        L += ['<meta property="og:locale" content="en_US">',
              '<meta property="og:locale:alternate" content="ja_JP">']
        if img:
            iurl = BASE + img[1] + "/" + img[0]
            alt = IMG_ALT.get(img[0], "A render from my own engine")
            L.append('<meta property="og:image" content="%s">' % iurl)
            sz = image_size(img[2])
            if sz:
                L.append('<meta property="og:image:width" content="%d">' % sz[0])
                L.append('<meta property="og:image:height" content="%d">' % sz[1])
            L.append('<meta property="og:image:alt" content="%s">' % esc(alt))
        L.append('<meta name="twitter:card" content="summary_large_image">')
        L.append('<meta name="twitter:title" content="%s">' % esc(title))
        if desc:
            L.append('<meta name="twitter:description" content="%s">' % esc(desc))
        if img:
            L.append('<meta name="twitter:image" content="%s">' % iurl)
            L.append('<meta name="twitter:image:alt" content="%s">' % esc(alt))

    # icons (only the ones that exist)
    icons = os.path.join(root, "assets", "icons")
    if os.path.isfile(os.path.join(icons, "favicon.ico")):
        L.append('<link rel="icon" href="assets/icons/favicon.ico" sizes="any">')
    if os.path.isfile(os.path.join(icons, "favicon.svg")):
        L.append('<link rel="icon" href="assets/icons/favicon.svg" type="image/svg+xml">')
    if os.path.isfile(os.path.join(icons, "apple-touch-icon.png")):
        L.append('<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">')

    if fname == "index.html":
        person = {"@context": "https://schema.org", "@type": "Person", "name": site_name,
                  "jobTitle": JOB_TITLE, "url": BASE,
                  "description": "Portfolio of %s: a Vulkan game engine with editor, an AI agent desktop app and an R&D journal with measured results." % site_name,
                  "knowsAbout": KNOWS_ABOUT}
        if site["github"]:
            person["sameAs"] = [site["github"]]
        if site["email"]:
            person["email"] = "mailto:" + site["email"]
        ld = json.dumps(person, ensure_ascii=False, indent=2).replace("</", "<\\/")
        L.append('<script type="application/ld+json">')
        L.append(ld)
        L.append("</script>")
    L.append("<!--seo:end-->")
    return nl.join(L)

def build_noscript(root, site, nl):
    items = []
    for f, label in NOSCRIPT_LINKS:
        if os.path.isfile(os.path.join(root, f)):
            items.append('<li><a href="%s">%s</a></li>' % (f, esc(label)))
    if site["email"]:
        items.append('<li><a href="mailto:%s">%s</a></li>' % (esc(site["email"]), esc(site["email"])))
    if site["github"]:
        items.append('<li><a href="%s">GitHub</a></li>' % esc(site["github"]))
    L = ["<!--seo:noscript-->",
         "<noscript>",
         '<div class="wrap" style="padding-block:2rem">',
         "<p><strong>%s</strong>: %s</p>" % (esc(site["name"]), esc(ROLE_LINE)),
         "<p>This site needs JavaScript for its texts and the language switch. Without it, use these links:</p>",
         "<ul>"] + items + ["</ul>", "</div>", "</noscript>", "<!--seo:/noscript-->"]
    return nl.join(L)

# ---------------------------------------------------------------------------------------------
HEAD_JUNK = re.compile(
    r'(?im)^[ \t]*<(?:meta\s+(?:name="(?:description|theme-color|robots)"|property="og:[^"]*"|name="twitter:[^"]*")'
    r'|link\s+rel="(?:icon|shortcut icon|apple-touch-icon|canonical|alternate)")[^>]*>[ \t]*\r?\n')
TITLE_TAG = re.compile(r'(?is)[ \t]*<title>.*?</title>[ \t]*\r?\n')
LD_TAG = re.compile(r'(?is)[ \t]*<script type="application/ld\+json">.*?</script>[ \t]*\r?\n')
BLOCK = re.compile(r'(?s)<!--seo:begin-->.*?<!--seo:end-->')
NS_BLOCK = re.compile(r'(?s)<!--seo:noscript-->.*?<!--seo:/noscript-->')
NS_OLD = re.compile(r'(?is)<noscript>.*?</noscript>')

def stamp_page(root, path, i18n, site, tokens, warns):
    fname = os.path.basename(path)
    text = read_text(path)
    nl = "\r\n" if "\r\n" in text else "\n"
    m = re.search(r"<html\b([^>]*)>", text)
    if not m:
        warns.append("%s: no <html> tag" % fname)
        return text, text
    attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
    hm = re.search(r"(?is)<head>(.*?)</head>", text)
    if not hm:
        warns.append("%s: no <head>" % fname)
        return text, text
    head = hm.group(1)

    tm = re.search(r'<meta name="theme-color" content="([^"]*)"', head)
    old_theme = tm.group(1) if tm else None
    block = build_head_block(root, fname, attrs, i18n, site, tokens, nl, warns, old_theme)
    new_head = head
    if block is not None:
        # take the old block out, remember where it was
        had_block = bool(BLOCK.search(new_head))
        if had_block:
            marker = "\x00SEO\x00"
            new_head = BLOCK.sub(marker, new_head, count=1)
        new_head = HEAD_JUNK.sub("", new_head)
        new_head = TITLE_TAG.sub("", new_head)
        new_head = LD_TAG.sub("", new_head)
        if had_block:
            new_head = new_head.replace(marker, block)
        else:
            sm = re.search(r'(?im)^[ \t]*<link rel="stylesheet"', new_head)
            if sm:
                new_head = new_head[:sm.start()] + block + nl + new_head[sm.start():]
            else:
                new_head = new_head.rstrip() + nl + block + nl
    out = text[:hm.start(1)] + new_head + text[hm.end(1):]

    # noscript
    ns = build_noscript(root, site, nl)
    if NS_BLOCK.search(out):
        out = NS_BLOCK.sub(lambda _m: ns, out, count=1)
    elif NS_OLD.search(out):
        out = NS_OLD.sub(lambda _m: ns, out, count=1)
    else:
        hm2 = re.search(r'<div id="site-header"></div>[ \t]*\r?\n?', out)
        if hm2:
            out = out[:hm2.end()].rstrip("\r\n") + nl + ns + nl + out[hm2.end():].lstrip("\r\n")
        else:
            warns.append("%s: no #site-header div, noscript not added" % fname)
    return text, out

def write_sitemap(root, site, pages, ids, check):
    lm = site["updated"]
    def url(loc, prio):
        s = "  <url>\n    <loc>%s</loc>\n" % html.escape(loc, quote=False)
        if lm:
            s += "    <lastmod>%s</lastmod>\n" % lm
        s += "    <priority>%s</priority>\n  </url>\n" % prio
        return s
    out = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for f in pages:
        out += url(BASE if f == "index.html" else BASE + f, "1.0" if f == "index.html" else "0.8")
    for i in ids:
        out += url(BASE + "case.html?id=" + i, "0.6")
    out += "</urlset>\n"
    robots = "User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n" % BASE
    changed = []
    for name, content in (("sitemap.xml", out), ("robots.txt", robots)):
        p = os.path.join(root, name)
        old = read_text(p) if os.path.isfile(p) else None
        if old != content:
            changed.append(name)
            if not check:
                write_text(p, content)
    return changed

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
    ap.add_argument("--check", action="store_true", help="change nothing, exit 1 if something would change")
    ap.add_argument("--no-sitemap", action="store_true")
    ap.add_argument("--only-sitemap", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    i18n = load_i18n(root)
    site = load_site(root)
    ids = case_ids(root)
    tokens = {"cases": len(ids), "updated": site["updated"]}
    pages = sorted(os.path.basename(p) for p in glob.glob(os.path.join(root, "*.html")))
    warns, changed = [], []

    if not a.only_sitemap:
        for f in pages:
            old, new = stamp_page(root, os.path.join(root, f), i18n, site, tokens, warns)
            if old != new:
                changed.append(f)
                if not a.check:
                    write_text(os.path.join(root, f), new)
    if not a.no_sitemap:
        # case.html alone (no ?id=) is an empty template: only the case URLs are listed
        listed = ["index.html"] + [f for f in pages if f not in ("index.html", "404.html", "case.html")]
        listed = [f for f in listed if f in pages]
        changed += write_sitemap(root, site, listed, ids, a.check)

    print("pages: %d  cases: %d  i18n keys: %d  updated: %s" % (len(pages), len(ids), len(i18n), site["updated"]))
    print(("would change: " if a.check else "changed: ") + (", ".join(changed) if changed else "nothing"))
    for w in warns:
        print("WARN", w)
    if a.check and changed:
        sys.exit(1)

if __name__ == "__main__":
    main()
