#!/usr/bin/env python3
"""
Build pipeline: src/main.js and its imports (real ES modules)  ->  app.src.js (bundled)  ->  app.js (minified)
                data.src.js (hand-edited)    ------------------------------------------>  data.js (minified)
                styles.src.css (hand-edited) ------------------------------------------>  styles.css (minified)

The app's logic is authored as genuine ES modules under src/. Native `<script
type="module">` is blocked by CORS when index.html is opened via file:// in Chrome,
and this app is deliberately built to work by just double-clicking index.html with
no local server. So esbuild bundles src/main.js into one classic IIFE script,
written unminified to app.src.js (committed for readability and diffing, and served
by the guess-rendering tests in place of app.js), then minifies that same text into
app.js. Edit files under src/, not app.src.js.

esbuild is the one piece of the pipeline that needs Node: `npm install` once (it's a
devDependency; the shipped app has no runtime dependencies and no server). It runs
through its JS API rather than its bin script, which npm replaces with a native
binary on Linux and macOS.

Every output is generated first and only written once all of them succeeded, each
through a temporary file and a rename, so a failed build leaves the previous
outputs in place.

Also stamps a content-hash cache-busting query string (?v=xxxxxxxx) onto the
app.js / data.js / styles.css references in index.html, so a normal page
reload always picks up the latest deploy instead of a browser-cached copy.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiki-sync"))
from common import slug_key_for  # noqa: E402

APP_ENTRY = "src/main.js"

# Reads a list of jobs as JSON on stdin and prints their outputs as JSON. A
# "bundle" job bundles an entry point without minifying; a "minify" job
# minifies one file's text (js or css).
ESBUILD_DRIVER = r"""
const esbuild = require("esbuild");
const jobs = JSON.parse(require("fs").readFileSync(0, "utf8"));
Promise.all(jobs.map((j) => j.kind === "bundle"
  ? esbuild.build({ entryPoints: [j.entry], bundle: true, format: "iife", write: false,
      legalComments: "none", banner: { js: j.banner } })
      .then((r) => r.outputFiles[0].text)
  : esbuild.transform(j.code, { loader: j.loader, minify: true, legalComments: "none" })
      .then((r) => r.code)))
  .then((out) => process.stdout.write(JSON.stringify(out)))
  .catch((e) => { console.error(e.message); process.exit(1); });
"""

APP_SRC_BANNER = (
    "// GENERATED FILE - do not edit directly. Source lives in src/*.js; run\n"
    "// build_minify.py, which bundles them into this file and minifies it into\n"
    "// app.js (the file index.html actually loads).\n"
    '"use strict";'
)


def esbuild_available():
    return os.path.isfile(os.path.join("node_modules", "esbuild", "package.json"))


def run_esbuild(jobs):
    result = subprocess.run(
        ["node", "-e", ESBUILD_DRIVER], input=json.dumps(jobs),
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        print(f"ERROR: esbuild failed:\n{result.stderr}")
        sys.exit(1)
    return json.loads(result.stdout)


def write_atomic(path, text):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


DATA_CATEGORY_START = re.compile(r'^(general|archetype|special):\s*\[')
DATA_CLASS_START = re.compile(r'^"([^"]+)":\s*\[')
DATA_ENTRY_NAME = re.compile(r'name:\s*"((?:[^"\\]|\\.)*)"')
DATA_ENTRY_AUTO = re.compile(r'\bauto:\s*true')


MIN_EXPECTED_AA_ENTRIES = 100  # currently 144; floor with headroom for legitimate removals


def check_prereq_disambiguation_invariant(data_src: str):
    """
    resolvePrereqTarget (src/logic.js) resolves a prereq by name within a
    single category (its own class list, or general/archetype/special - never
    across two different classes, and a class AA's own list is always
    searched first), and when a name repeats WITHIN that one category (e.g.
    Cleric's two "Divine Aura" rows) it deterministically prefers whichever
    occurrence is NOT auto-granted, on the reasoning that a prereq gating
    something you get for free anyway isn't a meaningful gate. That tie-break
    only gives a well-defined answer if every name repeated *within the same
    category* has EXACTLY ONE non-auto occurrence - checked here.

    This is deliberately scoped per-category, not a global name-uniqueness
    check: a name can legitimately repeat *across* categories (e.g. "Quick
    Evacuation" exists in both Druid and Wizard) without being ambiguous,
    because a class AA's prereq always resolves within its own class first
    and never falls through to a different class's list. Don't read a clean
    result here as "every AA name in the game is unique" - it isn't, and
    doesn't need to be.

    This is a regex over source text, not a real parser, so it has the same
    failure mode wiki-sync's table parser had: a format change it doesn't
    recognize makes it match nothing and report zero problems, which looks
    identical to "no problems." The entry-count floor below exists so that
    "found nothing to check" fails loudly instead of passing silently.
    """
    current_cat = None
    buckets = {}
    total_entries = 0
    for line in data_src.split("\n"):
        s = line.strip()
        m = DATA_CATEGORY_START.match(s)
        if m:
            current_cat = m.group(1)
            continue
        m = DATA_CLASS_START.match(s)
        if m:
            current_cat = "class:" + m.group(1)
            continue
        if s.startswith("classes:") or not s.startswith("{ name:"):
            continue
        nm = DATA_ENTRY_NAME.search(s)
        if not nm or not current_cat:
            continue
        total_entries += 1
        buckets.setdefault(current_cat, []).append((nm.group(1), bool(DATA_ENTRY_AUTO.search(s))))

    if total_entries < MIN_EXPECTED_AA_ENTRIES:
        return [
            f"  Only recognized {total_entries} AA entries in data.src.js (expected at least "
            f"{MIN_EXPECTED_AA_ENTRIES}) - this checker's regex almost certainly stopped matching "
            "the current format rather than the dataset actually shrinking. Fix the regexes "
            "above before trusting this check (or anything else that regex-parses data.src.js)."
        ]

    problems = []
    for cat, entries in buckets.items():
        by_name = {}
        for name, auto in entries:
            by_name.setdefault(name, []).append(auto)
        for name, autos in by_name.items():
            if len(autos) <= 1:
                continue
            non_auto_count = sum(1 for a in autos if not a)
            if non_auto_count != 1:
                problems.append(
                    f'  [{cat}] "{name}" appears {len(autos)} times with auto flags {autos} - '
                    f"need exactly one non-auto occurrence for prereq resolution to stay deterministic, got {non_auto_count}."
                )
    return problems


AA_IDS_TABLE_RE = re.compile(r'AA_ID_TABLE\s*=\s*(\{.*?\n\});', re.DOTALL)


def check_aa_ids_current(data_src: str):
    """
    Every AA in data.src.js must have an entry in src/aaIds.js's
    AA_ID_TABLE. That table backs the compact share/export wire format
    (keys.js's idForKey) - an AA missing from it doesn't error, it just
    silently drops out of every share link/export text that includes it,
    since idForKey returning null is treated the same as any other
    unresolved key (degrade gracefully, don't guess). That's the wrong
    failure mode for "someone edited data.src.js and forgot to run
    wiki-sync/assign_aa_ids.py" - this catches it at build time instead.
    """
    import json as _json

    current_cat = None
    entries = []
    for line in data_src.split("\n"):
        s = line.strip()
        m = DATA_CATEGORY_START.match(s)
        if m:
            current_cat = (m.group(1), None)
            continue
        m = DATA_CLASS_START.match(s)
        if m:
            current_cat = ("class", m.group(1))
            continue
        if s.startswith("classes:") or not s.startswith("{ name:"):
            continue
        nm = DATA_ENTRY_NAME.search(s)
        if not nm or not current_cat:
            continue
        scope, class_name = current_cat
        entries.append({
            "scope": scope, "className": class_name,
            "name": nm.group(1), "auto": bool(DATA_ENTRY_AUTO.search(s)),
        })

    # Same identity keys.js's keyForEntryIdx / assign_aa_ids.py compute -
    # shared here via slug_key_for rather than a 4th reimplementation.
    expected_id_keys = [
        f"{e['scope']}:{e['className'] or ''}:{slug_key_for(entries, i)}"
        for i, e in enumerate(entries)
    ]

    ids_path = "src/aaIds.js"
    try:
        with open(ids_path, "r", encoding="utf-8") as f:
            ids_src = f.read()
    except FileNotFoundError:
        return [f'  {ids_path} does not exist. Run "python wiki-sync/assign_aa_ids.py" once to create it.']
    m = AA_IDS_TABLE_RE.search(ids_src)
    if not m:
        return [f"  Could not find AA_ID_TABLE in {ids_path} - has its format changed?"]
    table = _json.loads(m.group(1))

    missing = [k for k in expected_id_keys if k not in table]
    if not missing:
        return []
    return [
        f'  {len(missing)} AA(s) in data.src.js have no entry in {ids_path}: {", ".join(missing[:10])}'
        + (", ..." if len(missing) > 10 else ""),
        '  Run "python wiki-sync/assign_aa_ids.py" to assign them ids, then rebuild.',
    ]


VERSIONED_ASSET = re.compile(r'(href|src)="(app\.js|data\.js|styles\.css)(?:\?v=[a-f0-9]+)?"')


def stamp_index_html(outputs):
    combined = (outputs["app.js"] + outputs["data.js"] + outputs["styles.css"]).encode("utf-8")
    version = hashlib.sha1(combined).hexdigest()[:8]

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    stamped = VERSIONED_ASSET.sub(lambda m: f'{m.group(1)}="{m.group(2)}?v={version}"', html)
    if stamped != html:
        with open("index.html", "w", encoding="utf-8", newline="\n") as f:
            f.write(stamped)
    print(f"index.html stamped with cache-busting version {version}")


def main():
    if not esbuild_available():
        print("ERROR: esbuild isn't installed - run `npm install` first (devDependency only; the shipped app itself has none).")
        return 1
    with open("data.src.js", "r", encoding="utf-8") as f:
        data_src_check = f.read()
    problems = check_prereq_disambiguation_invariant(data_src_check)
    if problems:
        print("ERROR: data.src.js violates the duplicate-AA-name disambiguation invariant:")
        for p in problems:
            print(p)
        print("A prereq referencing one of these names would resolve unpredictably. Fix the data (add/remove an `auto` flag so exactly one occurrence is non-auto) before building.")
        return 1

    id_problems = check_aa_ids_current(data_src_check)
    if id_problems:
        print("ERROR: src/aaIds.js is out of date with data.src.js:")
        for p in id_problems:
            print(p)
        return 1

    [app_src] = run_esbuild([{"kind": "bundle", "entry": APP_ENTRY, "banner": APP_SRC_BANNER}])
    with open("styles.src.css", "r", encoding="utf-8") as f:
        styles_src = f.read()
    sources = {"app.js": app_src, "data.js": data_src_check, "styles.css": styles_src}
    loaders = {"app.js": "js", "data.js": "js", "styles.css": "css"}
    minified = run_esbuild([{"kind": "minify", "code": sources[k], "loader": loaders[k]} for k in sources])
    outputs = dict(zip(sources, minified))

    write_atomic("app.src.js", app_src)
    print(f"Bundled {APP_ENTRY} -> app.src.js")
    names = {"app.js": "app.src.js", "data.js": "data.src.js", "styles.css": "styles.src.css"}
    for out_name, text in outputs.items():
        write_atomic(out_name, text)
        before, after = len(sources[out_name]), len(text)
        print(f"{names[out_name]} -> {out_name}: {before} -> {after} bytes ({100 * after // before}%)")
    stamp_index_html(outputs)


if __name__ == "__main__":
    sys.exit(main())
