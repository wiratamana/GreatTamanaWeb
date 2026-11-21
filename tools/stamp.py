#!/usr/bin/env python3
"""stamp.py - writes today's date (or --date YYYY-MM-DD) into js/data/site.js  `updated:`  and nothing else.

  python tools/stamp.py                 today
  python tools/stamp.py --date 2026-11-22

Run it on release day, before tools/seo_stamp.py (the sitemap lastmod reads this value).
"""
import argparse
import datetime
import os
import re
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=datetime.date.today().isoformat())
a = ap.parse_args()
if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date):
    sys.exit("date must be YYYY-MM-DD")

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "js", "data", "site.js")
with open(path, "r", encoding="utf-8", newline="") as f:
    s = f.read()
new, n = re.subn(r'(\bupdated:\s*")[^"]*(")', lambda m: m.group(1) + a.date + m.group(2), s, count=1)
if n != 1:
    sys.exit("updated: not found in js/data/site.js")
if new != s:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new)
print("site.updated =", a.date)
