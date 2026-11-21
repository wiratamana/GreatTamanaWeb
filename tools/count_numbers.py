#!/usr/bin/env python3
"""
count_numbers.py  -  recount the numbers shown on the portfolio website.

METHOD (calibrated: on engine commit 8ce30c6 this script reproduces EXACTLY the numbers of the Nov 13 site:
1,148 files, 139k lines C++ in src/, 4,909 test cases, 106k lines of test code, subsystem table, 11.3k render graph lines,
102 core HTTP routes ("about 100"), 12 render features).

  * Lines        = physical lines (count of '\\n', +1 if the file does not end with a newline). Blank lines and comments are included.
  * C++          = *.cpp *.h *.hpp *.inl under src/  (tests: under tests/). third_party/ is NOT in the repo (fetched by cmake) so it never counts.
  * GLSL         = *.glsl *.vert *.frag *.comp ... under src/
  * Test cases   = regex  ^\\s*(TEST|TEST_F|TEST_P|TYPED_TEST|TYPED_TEST_P)\\s*\\(  in tests/**.{cpp,h,hpp}
                   (a macro count. It is LOWER than the number gtest registers, see 'registered' below)
  * Registered   = `ctest -N` in the build dir: entries with a '.' in the name (gtest cases) / without '.' (ctest guard + probe checks).
                   Only valid for the LAST BUILD of that build dir (can be older than the working tree). Only in --worktree mode.
  * Render feat. = GTE_REGISTER_RENDER_FEATURE("Name", ...) in src/
  * HTTP routes  = unique "/path" literals of  server.Get( / server.Post( / registerCommand(  in src/  (core server routes)
                   + GTE_REGISTER_DEBUG_ROUTE_ALIAS paths + GTE_REGISTER_MODULE_ROUTES prefixes (each prefix = a family of routes).
  * Commits      = git rev-list --count HEAD
  * Source sets  : REF mode  = files of a git commit (git archive)   -> only COMMITTED work
                   WORKTREE   = tracked + untracked-not-ignored files on disk -> INCLUDES UNCOMMITTED WORK
Usage (run it from anywhere; the engine repo is a separate git repository):
  python tools/count_numbers.py --engine <engine repo> [--app <app repo>]    # full report: old ref, HEAD, working tree
  python tools/count_numbers.py --engine <engine repo> --json out.json        # also write the raw numbers
  python tools/count_numbers.py --engine <engine repo> --old 8ce30c6          # change the reference commit of the old snapshot
  (or set the env vars GTE_REPO and GTA_REPO instead of --engine / --app)
Use it after the engine work is pushed: then the HEAD column is what a visitor can verify on GitHub. Update the numbers in
i18n/en/*.js and i18n/ja/*.js (home, engine, rendering, tools, about, cv) by hand and run python tools/i18n_check.py --numbers.
Needs only python 3 stdlib and git. ctest is optional.
"""
import argparse, collections, datetime, io, json, os, re, subprocess, sys, zipfile

ENGINE = os.environ.get("GTE_REPO", "")   # path of the engine git repo (or use --engine)
APP = os.environ.get("GTA_REPO", "")      # path of the app git repo (or use --app); optional
OLD_REF = "8ce30c6"   # commit #1078 of 2026-11-13: the snapshot that the current site shows

CPP = {".cpp", ".h", ".hpp", ".inl"}
GLSL = {".glsl", ".vert", ".frag", ".comp", ".geom", ".tesc", ".tese", ".mesh", ".task"}
TEST_RE = re.compile(rb"^\s*(TEST|TEST_F|TEST_P|TYPED_TEST|TYPED_TEST_P)\s*\(", re.M)
FEATURE_RE = re.compile(rb'GTE_REGISTER_RENDER_FEATURE\s*\(\s*"([^"]+)"')
MODULE_ROUTES_RE = re.compile(rb'GTE_REGISTER_MODULE_ROUTES\s*\(\s*"([^"]+)"\s*,\s*"[^"]*"\s*((?:,\s*"[^"]*"\s*)*)\)')
ALIAS_RE = re.compile(rb'GTE_REGISTER_DEBUG_ROUTE_ALIAS\s*\(\s*"([^"]+)"')
ROUTE_RES = [
    re.compile(rb'\b(?:server|svr|srv|m_server)\s*(?:\.|->)\s*(?:Get|Post)\s*\(\s*"(/[^"]*)"'),
    re.compile(rb'registerCommand\s*\(\s*"(/[^"]*)"'),
]
ACTION_RE = re.compile(rb'\baction\s*==\s*"([a-z_]+)"')
PANEL_RE = re.compile(rb"GTE_REGISTER_BUILTIN_FEATURE_EDITOR_PANEL\s*\(")
MODULE_RE = re.compile(rb"GTE_REGISTER_BUILTIN_FEATURE_MODULE\s*\(")


def nlines(data):
    return data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)


def git(repo, *args, text=True):
    r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True)
    out = r.stdout.decode("utf-8", "replace") if text else r.stdout
    return out.strip() if text else out


# ------------------------------------------------------------------ sources
class RefSource:
    """Files of one git commit (committed work only)."""
    def __init__(self, repo, ref):
        self.label = "commit " + ref
        present = set(git(repo, "ls-tree", "--name-only", ref).splitlines())
        want = [p for p in ("src", "tests", "tools", "docs", "cmake", "README.md", "AGENTS.md", "BUILDING.md",
                            "TESTING.md", "TODO.md", "CMakeLists.txt") if p in present]
        blob = git(repo, "archive", "--format=zip", ref, "--", *want, text=False)
        self.zip = zipfile.ZipFile(io.BytesIO(blob))
        self.names = [n for n in self.zip.namelist() if not n.endswith("/")]

    def files(self):
        return self.names

    def read(self, rel):
        return self.zip.read(rel)


class WorktreeSource:
    """Tracked + untracked (not ignored) files on disk: includes UNCOMMITTED work. Deleted files are skipped."""
    def __init__(self, repo):
        self.repo = repo
        self.label = "working tree"
        raw = git(repo, "ls-files", "-z", "-c", "-o", "--exclude-standard", text=False).decode("utf-8", "replace")
        self.names = sorted({p for p in raw.split("\0") if p and os.path.isfile(os.path.join(repo, p))})

    def files(self):
        return self.names

    def read(self, rel):
        with open(os.path.join(self.repo, rel), "rb") as f:
            return f.read()


# ------------------------------------------------------------------ engine metrics
def engine_metrics(src):
    m = collections.OrderedDict()
    sub = collections.defaultdict(lambda: [0, 0])      # src/<top>
    feat = collections.defaultdict(lambda: [0, 0])     # src/Features/<name>
    feat_tests = collections.defaultdict(lambda: [0, 0])  # tests/Features/<name>  [files, TEST macros]
    deep = collections.defaultdict(lambda: [0, 0])     # src/<top>/<sub>
    cpp_src = [0, 0]; cpp_tests = [0, 0]; gl_src = [0, 0]
    macros = collections.Counter()
    features, routes, aliases, mod_routes = [], set(), set(), []
    panels = modules = 0
    actions = collections.defaultdict(set)   # feature -> action names found in src/Features/<F>/Editor/*.cpp (APPROXIMATE)
    docs_md = [0, 0]; root_md = []
    tests_area = collections.Counter()       # TEST macros per tests/<area>
    tests_files_with_macro = 0
    shader_kinds = collections.Counter()     # src + tests, by extension
    shader_lines_all = 0
    feat_all = collections.defaultdict(int)  # src/Features/<F>: C++ + shader lines
    ci_scan_lines = removed_tokens = 0
    tools_files = 0
    for rel in src.files():
        ext = os.path.splitext(rel)[1].lower()
        parts = rel.split("/")
        top = parts[0]
        if top == "docs" and ext == ".md":
            docs_md[0] += 1; docs_md[1] += nlines(src.read(rel))
        if top == "tools":
            tools_files += 1
        if len(parts) == 1 and ext == ".md":
            root_md.append(rel)
        if rel == "tools/ci/common/CiScan.cpp":
            ci_scan_lines = nlines(src.read(rel))
        if rel == "tools/ci/removed_symbol_check/tokens.txt":
            removed_tokens = sum(1 for l in src.read(rel).decode("utf-8", "replace").splitlines()
                                 if l.strip() and not l.strip().startswith("#"))
        if ext not in CPP and ext not in GLSL:
            continue
        data = src.read(rel)
        n = nlines(data)
        if ext in GLSL and top in ("src", "tests"):
            shader_kinds[ext] += 1; shader_lines_all += n
        if top == "src" and len(parts) > 3 and parts[1] == "Features":
            feat_all[parts[2]] += n
        if top == "src":
            if ext in GLSL:
                gl_src[0] += 1; gl_src[1] += n
                continue
            cpp_src[0] += 1; cpp_src[1] += n
            key = parts[1] if len(parts) > 2 else "(root)"
            sub[key][0] += 1; sub[key][1] += n
            if len(parts) > 3:
                deep["/".join(parts[1:3])][0] += 1; deep["/".join(parts[1:3])][1] += n
            if parts[1] == "Features" and len(parts) > 3:
                feat[parts[2]][0] += 1; feat[parts[2]][1] += n
            for fm in FEATURE_RE.finditer(data):
                features.append(fm.group(1).decode())
            for rr in ROUTE_RES:
                for rm in rr.finditer(data):
                    routes.add(rm.group(1).decode())
            for am in ALIAS_RE.finditer(data):
                aliases.add(am.group(1).decode())
            for mm in MODULE_ROUTES_RE.finditer(data):
                acts = re.findall(rb'"([^"]*)"', mm.group(2))
                mod_routes.append((mm.group(1).decode(), [a.decode() for a in acts]))
            if len(parts) > 4 and parts[1] == "Features" and parts[3] == "Editor" and ext == ".cpp":
                for am in ACTION_RE.finditer(data):
                    actions[parts[2]].add(am.group(1).decode())
            panels += len(PANEL_RE.findall(data)) - (1 if rel.endswith("FeatureEditorPanelRegistry.h") else 0)
            modules += len(MODULE_RE.findall(data))
        elif top == "tests":
            if ext in GLSL:
                continue
            cpp_tests[0] += 1; cpp_tests[1] += n
            c = TEST_RE.findall(data)
            if c:
                tests_files_with_macro += 1
            if len(parts) > 2:
                tests_area[parts[1]] += len(c)
            for k in c:
                macros[k.decode()] += 1
            if len(parts) > 3 and parts[1] == "Features":
                feat_tests[parts[2]][0] += 1; feat_tests[parts[2]][1] += len(c)
    # guard checks (static, from tests/CMakeLists.txt)
    guards = {"scan": 0, "comment": 0, "probe": 0, "named": 0}
    try:
        cm = src.read("tests/CMakeLists.txt").decode("utf-8", "replace")
        guards["scan"] = len(re.findall(r"^gte_add_scan_test\(", cm, re.M))
        guards["comment"] = len(re.findall(r"^gte_add_comment_rules_test\(", cm, re.M))
        guards["probe"] = len(re.findall(r"^gte_add_build_probe_test\(", cm, re.M))
        guards["named"] = len(re.findall(r"^add_test\(NAME\s+[A-Za-z]", cm, re.M))
    except KeyError:
        pass
    m["cpp_src_files"], m["cpp_src_lines"] = cpp_src
    m["cpp_tests_files"], m["cpp_tests_lines"] = cpp_tests
    m["glsl_files"], m["glsl_lines"] = gl_src
    m["test_macros_total"] = sum(macros.values())
    m["test_macros"] = dict(macros)
    m["render_features"] = len(features)
    m["render_feature_names"] = sorted(features)
    m["editor_feature_modules"] = modules
    m["editor_feature_panels"] = panels
    m["core_http_routes"] = len(routes)
    m["debug_route_aliases"] = len(aliases)
    m["module_route_prefixes"] = [p for p, _ in mod_routes]
    m["module_readonly_actions"] = sum(len(a) for _, a in mod_routes)
    prefixes_feat = {"bigworld": "BigWorld", "terrain": "Terrain", "water": "Water", "tree": "Tree", "forestmask": "Terrain"}
    used = {prefixes_feat[p] for p, _ in mod_routes if p in prefixes_feat}
    m["module_actions_approx_by_feature"] = {k: len(v) for k, v in sorted(actions.items()) if k in used}
    m["module_actions_approx_total"] = sum(len(actions[k]) for k in used)
    m["tests_files_with_macro"] = tests_files_with_macro
    m["tests_macros_by_area"] = dict(tests_area.most_common())
    m["shader_files_src_plus_tests"] = sum(shader_kinds.values())
    m["shader_files_by_ext"] = dict(shader_kinds)
    m["shader_lines_src_plus_tests"] = shader_lines_all
    m["features_cpp_plus_shader_lines"] = dict(sorted(feat_all.items(), key=lambda x: -x[1]))
    m["ci_scan_lines"] = ci_scan_lines
    m["removed_symbol_tokens"] = removed_tokens
    m["ctest_guard_registrations_static"] = guards
    m["docs_md_files"], m["docs_md_lines"] = docs_md
    m["root_md_files"] = root_md
    m["tools_files"] = tools_files
    m["src_by_top"] = {k: v for k, v in sorted(sub.items(), key=lambda x: -x[1][1])}
    m["src_by_sub"] = {k: v for k, v in sorted(deep.items(), key=lambda x: -x[1][1])}
    m["features_cpp"] = {k: v for k, v in sorted(feat.items(), key=lambda x: -x[1][1])}
    m["features_tests"] = dict(feat_tests)
    return m


def ctest_registered(build_dir):
    try:
        r = subprocess.run(["ctest", "--test-dir", build_dir, "-N"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
    except Exception as e:  # ctest missing
        return {"error": str(e)}
    names = [re.sub(r"^\s*Test\s+#\d+:\s*", "", l) for l in r.stdout.splitlines() if re.match(r"^\s*Test\s+#\d+:", l)]
    guards = [n for n in names if "." not in n]
    return {"total_ctest_entries": len(names), "gtest_registered": len(names) - len(guards),
            "non_gtest_entries": len(guards), "non_gtest_names": guards}


def git_history(repo, old_ref):
    h = collections.OrderedDict()
    h["head"] = git(repo, "log", "-1", "--format=%h %cI")
    h["branch"] = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    h["commits_head"] = int(git(repo, "rev-list", "--count", "HEAD"))
    h["commits_old_ref"] = int(git(repo, "rev-list", "--count", old_ref))
    h["commits_since_old_ref"] = int(git(repo, "rev-list", "--count", old_ref + "..HEAD"))
    first = git(repo, "log", "--reverse", "--format=%cI", "--max-parents=0").splitlines()[0]
    last = git(repo, "log", "-1", "--format=%cI")
    h["first_commit"], h["last_commit"] = first, last
    d0 = datetime.date.fromisoformat(first[:10]); d1 = datetime.date.fromisoformat(last[:10])
    h["days_first_to_last_commit"] = (d1 - d0).days
    h["days_first_to_today"] = (datetime.date.today() - d0).days
    old_date = git(repo, "log", "-1", "--format=%cI", old_ref)
    h["old_ref_date"] = old_date
    h["days_first_to_old_ref"] = (datetime.date.fromisoformat(old_date[:10]) - d0).days
    months = collections.Counter(l[:7] for l in git(repo, "log", "--format=%cI").splitlines())
    h["commits_per_month"] = dict(sorted(months.items()))
    h["landscape_prefix_commits"] = int(git(repo, "rev-list", "--count", "--grep=^landscape:", "HEAD"))
    rem = git(repo, "rev-parse", "--verify", "-q", "origin/dev")
    if rem:
        ahead_behind = git(repo, "rev-list", "--left-right", "--count", "HEAD...origin/dev").split()
        h["vs_origin_dev_ahead_behind"] = ahead_behind
        h["origin_dev_head"] = git(repo, "log", "-1", "--format=%h", "origin/dev")
    # uncommitted work
    por = git(repo, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
    h["uncommitted_modified_tracked"] = sum(1 for l in por if not l.startswith("??"))
    h["uncommitted_untracked_files"] = sum(1 for l in por if l.startswith("??"))
    h["uncommitted_shortstat_tracked"] = git(repo, "diff", "HEAD", "--shortstat")
    unt = [l[3:].strip('"') for l in por if l.startswith("??")]
    ul = 0
    for p in unt:
        fp = os.path.join(repo, p)
        if os.path.isfile(fp) and os.path.splitext(p)[1].lower() in (CPP | GLSL | {".md"}):
            with open(fp, "rb") as f:
                ul += nlines(f.read())
    h["uncommitted_untracked_lines_cpp_glsl_md"] = ul
    return h


# ------------------------------------------------------------------ app metrics (C#)
def app_metrics():
    out = collections.OrderedDict()
    skip = {".git", "obj", "bin", "publish", "build_secrets", ".vs"}
    per = collections.defaultdict(lambda: [0, 0])
    tool_info = avalonia = 0
    names_avalonia = []
    ti_re = re.compile(rb"\[\s*ToolInfo\s*\(")
    av_re = re.compile(rb'\[\s*AvaloniaOnlyTool\s*\(\s*"([^"]+)"')
    for root, dirs, files in os.walk(APP):
        dirs[:] = [d for d in dirs if d not in skip]
        for f in files:
            if f.endswith(".cs") and not f.endswith((".g.cs", ".Designer.cs", ".AssemblyInfo.cs")):
                p = os.path.join(root, f)
                with open(p, "rb") as fh:
                    d = fh.read()
                proj = os.path.relpath(p, APP).split(os.sep)[0]
                per[proj][0] += 1; per[proj][1] += nlines(d)
                tool_info += len(ti_re.findall(d))
                for m in av_re.finditer(d):
                    avalonia += 1; names_avalonia.append(m.group(1).decode())
    projects = {k: v for k, v in per.items() if k.startswith("GTA.")}
    out["worktree_cs_files"] = sum(v[0] for v in projects.values())
    out["worktree_cs_lines"] = sum(v[1] for v in projects.values())
    out["worktree_projects"] = len(projects)
    out["worktree_per_project"] = {k: v for k, v in sorted(projects.items(), key=lambda x: -x[1][1])}
    out["non_project_cs"] = {k: v for k, v in per.items() if not k.startswith("GTA.")}
    out["worktree_toolinfo"] = tool_info
    out["worktree_avalonia_only_tools"] = avalonia
    out["worktree_tools_total"] = tool_info + avalonia
    out["worktree_avalonia_only_names"] = names_avalonia
    # HEAD (committed) numbers
    blob = git(APP, "archive", "--format=zip", "HEAD", text=False)
    z = zipfile.ZipFile(io.BytesIO(blob))
    t = a = 0
    hp = collections.defaultdict(lambda: [0, 0])
    for n in z.namelist():
        if n.endswith(".cs") and not n.endswith((".g.cs", ".Designer.cs")):
            d = z.read(n)
            t += len(ti_re.findall(d)); a += len(av_re.findall(d))
            proj = n.split("/")[0]
            if proj.startswith("GTA."):
                hp[proj][0] += 1; hp[proj][1] += nlines(d)
    out["head_toolinfo"], out["head_avalonia_only_tools"], out["head_tools_total"] = t, a, t + a
    out["head_cs_files"] = sum(v[0] for v in hp.values()); out["head_cs_lines"] = sum(v[1] for v in hp.values())
    out["head_per_project"] = dict(hp)
    out["commits"] = int(git(APP, "rev-list", "--count", "HEAD"))
    out["first_commit"] = git(APP, "log", "--reverse", "--format=%cI", "--max-parents=0").splitlines()[0]
    out["last_commit"] = git(APP, "log", "-1", "--format=%cI")
    por = git(APP, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
    out["uncommitted_modified_tracked"] = sum(1 for l in por if not l.startswith("??"))
    out["uncommitted_untracked_files"] = sum(1 for l in por if l.startswith("??"))
    out["untracked_projects"] = sorted({l[3:].split("/")[0] for l in por if l.startswith("??") and l.endswith(".csproj\"")
                                        or (l.startswith("??") and l.endswith(".csproj"))})
    return out


def kfmt(n):
    return "%.1fk" % (n / 1000.0)


def main():
    global ENGINE, APP
    ap = argparse.ArgumentParser(description="Recount the numbers of the portfolio site from the engine (and app) git repos.")
    ap.add_argument("--engine", default="", help="path of the engine git repository (or env GTE_REPO)")
    ap.add_argument("--app", default="", help="path of the app git repository (or env GTA_REPO); optional")
    ap.add_argument("--old", default=OLD_REF)
    ap.add_argument("--json", default="")
    ap.add_argument("--no-app", action="store_true")
    a = ap.parse_args()
    ENGINE = a.engine or ENGINE
    APP = a.app or APP
    if not ENGINE or not os.path.isdir(os.path.join(ENGINE, ".git")):
        ap.error("give the engine git repository with --engine <path> (or set GTE_REPO)")
    if not APP or not os.path.isdir(os.path.join(APP, ".git")):
        a.no_app = True

    result = collections.OrderedDict()
    old = engine_metrics(RefSource(ENGINE, a.old))
    head_ref = git(ENGINE, "rev-parse", "--short", "HEAD")
    head = engine_metrics(RefSource(ENGINE, "HEAD"))
    wt = engine_metrics(WorktreeSource(ENGINE))
    result["engine_old_ref"] = a.old; result["engine_head_ref"] = head_ref
    result["engine_old"], result["engine_head_committed"], result["engine_worktree"] = old, head, wt
    result["engine_ctest_build_dir"] = ctest_registered(os.path.join(ENGINE, "build"))
    result["engine_git"] = git_history(ENGINE, a.old)
    third = os.path.join(ENGINE, "third_party")
    result["third_party_dirs"] = sorted(os.listdir(third)) if os.path.isdir(third) else []
    if not a.no_app:
        result["app"] = app_metrics()

    def row(name, k):
        return "| %s | %s | %s | %s |" % (name, old[k], head[k], wt[k])
    print("# counts (generated by count_numbers.py on %s)\n" % datetime.date.today())
    print("| metric | old (%s) | HEAD %s (committed) | working tree (incl. uncommitted) |" % (a.old, head_ref))
    print("|---|---|---|---|")
    for name, k in [("C++ files in src/", "cpp_src_files"), ("C++ lines in src/", "cpp_src_lines"),
                    ("test files", "cpp_tests_files"), ("test lines", "cpp_tests_lines"),
                    ("GLSL files", "glsl_files"), ("GLSL lines", "glsl_lines"),
                    ("TEST macros", "test_macros_total"), ("render features", "render_features"),
                    ("core HTTP routes", "core_http_routes"), ("route aliases", "debug_route_aliases"),
                    ("module read-only actions", "module_readonly_actions"),
                    ("module actions (APPROX, grep of action names)", "module_actions_approx_total"),
                    ("docs .md files", "docs_md_files"), ("docs .md lines", "docs_md_lines")]:
        print(row(name, k))
    g = result["engine_git"]
    print("\ncommits HEAD=%s  old=%s  since old=%s  first=%s last=%s" % (
        g["commits_head"], g["commits_old_ref"], g["commits_since_old_ref"], g["first_commit"], g["last_commit"]))
    print("per month:", g["commits_per_month"])
    print("ctest -N:", {k: v for k, v in result["engine_ctest_build_dir"].items() if k != "non_gtest_names"})
    if "app" in result:
        print("app:", {k: v for k, v in result["app"].items() if not isinstance(v, (dict, list))})
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1, default=str)
        print("\nwrote", a.json)


if __name__ == "__main__":
    sys.exit(main())
