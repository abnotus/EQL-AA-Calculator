#!/usr/bin/env python3
"""
Build pipeline: src/*.js (real ES modules)  ->  app.src.js (generated)  ->  app.js (minified)
                data.src.js (hand-edited)    ------------------------->  data.js (minified)
                styles.src.css (hand-edited) ------------------------->  styles.css (minified)

The app's logic is authored as genuine ES modules under src/ (see SRC_MODULE_ORDER
below for the current file set and assembly order - not repeated here, since a list
in a docstring drifts the moment a module is added and nothing catches it) using real
import/export, so editors and readers get proper module boundaries. But native `<script type="module">`
is blocked by CORS when index.html is opened via file:// in Chrome, and this app is
deliberately built to work by just double-clicking index.html with no local server.
So instead: this script assembles the src/ modules back into a single classic script
(stripping import/export syntax, since after concatenation everything shares one
scope and no runtime module resolution is needed), writes that to app.src.js, then
minifies app.src.js -> app.js exactly as before. Edit files under src/, not app.src.js
directly — it's a generated artifact now (kept committed for readability/diffing).

Minification (app.js/data.js/styles.css) is done by esbuild - a real parser, not a
regex/line-based stripper, so it handles template literals, strings, and comments
correctly by construction and additionally mangles local identifiers for a real size
win. This is the one piece of the pipeline that needs Node: `npm install` once (pulls
just esbuild, a devDependency - the shipped app itself still has zero runtime
dependencies and no server, exactly as before) before running this script. Edit
data.src.js/styles.src.css directly; they're hand-authored sources, same as src/*.js.

Also stamps a content-hash cache-busting query string (?v=xxxxxxxx) onto the
app.js / data.js / styles.css references in index.html, so a normal page
reload always picks up the latest deploy instead of a browser-cached copy.
"""
import hashlib
import os
import re
import subprocess
import sys

SRC_MODULE_ORDER = [
    "src/aaIds.js",
    "src/costGuesses.js",
    "src/effectGuesses.js",
    "src/keys.js",
    "src/changelogData.js",
    "src/state.js",
    "src/logic.js",
    "src/builds.js",
    "src/dom.js",
    "src/render.js",
    "src/exportImport.js",
    "src/events.js",
    "src/main.js",
]

IMPORT_BLOCK = re.compile(r'^import\s*\{.*?\}\s*from\s*["\'][^"\']+["\'];?\s*$\n?', re.MULTILINE | re.DOTALL)
EXPORT_PREFIX = re.compile(r"^(\s*)export\s+(async\s+function|function|const|let)\s")


def strip_module_syntax(src: str) -> str:
    # Import statements (possibly spanning multiple lines) are only needed for real
    # module resolution — once everything's concatenated into one scope, drop them.
    no_imports = IMPORT_BLOCK.sub("", src)
    # "export function/const/let" -> "function/const/let"; same-scope concatenation
    # means nothing needs the export keyword anymore.
    out_lines = []
    for line in no_imports.split("\n"):
        m = EXPORT_PREFIX.match(line)
        if m:
            line = f"{m.group(1)}{m.group(2)} " + line[m.end():]
        out_lines.append(line)
    return "\n".join(out_lines)


def assemble_app_src():
    parts = []
    for path in SRC_MODULE_ORDER:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        parts.append(strip_module_syntax(content).strip("\n"))
    body = "\n\n".join(parts)
    assembled = (
        "// GENERATED FILE — do not edit directly.\n"
        "// Source lives in src/*.js (real ES modules). Edit those, then re-run\n"
        "// build_minify.py, which assembles + strips them into this file and then\n"
        "// minifies it into app.js (the file index.html actually loads).\n"
        "(function () {\n"
        '  "use strict";\n\n'
        f"{body}\n"
        "})();\n"
    )
    with open("app.src.js", "w", encoding="utf-8", newline="\n") as f:
        f.write(assembled)
    print(f"Assembled {len(SRC_MODULE_ORDER)} src/*.js modules -> app.src.js")


ESBUILD_BIN = os.path.join("node_modules", "esbuild", "bin", "esbuild")


def esbuild_minify(src_path: str, out_path: str):
    """
    Minifies src_path -> out_path via esbuild (loader picked from the file
    extension: .js or .css). No --bundle - these files have no imports left
    to resolve by this point (app.src.js's were already stripped by
    strip_module_syntax; data.src.js/styles.src.css never had any) - so this
    is a plain single-file transform, not a bundling step.
    """
    if not os.path.exists(ESBUILD_BIN):
        print(f"ERROR: esbuild not found at {ESBUILD_BIN} - run `npm install` first (devDependency only; the shipped app itself has none).")
        sys.exit(1)
    result = subprocess.run(
        ["node", ESBUILD_BIN, src_path, "--minify", f"--outfile={out_path}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: esbuild failed on {src_path}:\n{result.stderr}")
        sys.exit(1)


DATA_CATEGORY_START = re.compile(r'^(general|archetype|special):\s*\[')
DATA_CLASS_START = re.compile(r'^"([^"]+)":\s*\[')
DATA_ENTRY_NAME = re.compile(r'name:\s*"((?:[^"\\]|\\.)*)"')
DATA_ENTRY_AUTO = re.compile(r'\bauto:\s*true')


MIN_EXPECTED_AA_ENTRIES = 100  # currently 143; floor with headroom for legitimate removals


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
    buckets = {}
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
        buckets.setdefault(current_cat, []).append((nm.group(1), bool(DATA_ENTRY_AUTO.search(s))))

    # Same disambiguation as keys.js's keyForEntryIdx / assign_aa_ids.py.
    def slugify(name):
        s = name.lower().replace("'", "")
        return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

    expected_id_keys = []
    for (scope, class_name), entries in buckets.items():
        slugs = [slugify(n) for n, _ in entries]
        autos = [a for _, a in entries]
        for pos in range(len(entries)):
            base = slugs[pos]
            same = [j for j in range(len(entries)) if slugs[j] == base]
            if len(same) <= 1 or not autos[pos]:
                key = base
            else:
                auto_siblings = [j for j in same if autos[j]]
                auto_pos = auto_siblings.index(pos)
                key = f"{base}-auto" if auto_pos == 0 else f"{base}-auto-{auto_pos + 1}"
            expected_id_keys.append(f"{scope}:{class_name or ''}:{key}")

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

    assemble_app_src()
    pairs = [("app.src.js", "app.js"), ("data.src.js", "data.js"), ("styles.src.css", "styles.css")]
    outputs = {}
    for src_name, out_name in pairs:
        with open(src_name, "r", encoding="utf-8") as f:
            before = len(f.read())
        esbuild_minify(src_name, out_name)
        with open(out_name, "r", encoding="utf-8") as f:
            minified = f.read()
        outputs[out_name] = minified
        after = len(minified)
        print(f"{src_name} -> {out_name}: {before} -> {after} bytes ({100 * after // before}%)")
    stamp_index_html(outputs)


if __name__ == "__main__":
    sys.exit(main())
