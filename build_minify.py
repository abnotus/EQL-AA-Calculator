#!/usr/bin/env python3
"""
Build pipeline: src/*.js (real ES modules)  ->  app.src.js (generated)  ->  app.js (minified)
                data.src.js (hand-edited)    ------------------------->  data.js (minified)

The app's logic is authored as genuine ES modules under src/ (state.js, logic.js,
dom.js, render.js, exportImport.js, events.js, main.js) using real import/export,
so editors and readers get proper module boundaries. But native `<script type="module">`
is blocked by CORS when index.html is opened via file:// in Chrome, and this app is
deliberately built to work by just double-clicking index.html with no local server.
So instead: this script assembles the src/ modules back into a single classic script
(stripping import/export syntax, since after concatenation everything shares one
scope and no runtime module resolution is needed), writes that to app.src.js, then
minifies app.src.js -> app.js exactly as before. Edit files under src/, not app.src.js
directly — it's a generated artifact now (kept committed for readability/diffing).

Minification is conservative on purpose: strips full-line "//" comments, blank lines,
and leading indentation from ordinary code lines. Any line that falls inside a
multi-line `template literal` is passed through byte-for-byte untouched, so
no HTML-in-JS string content is ever touched. Lines containing quote/backtick
characters keep any trailing inline comment as-is rather than risk mismatching
a "//" inside a string.

Also stamps a content-hash cache-busting query string (?v=xxxxxxxx) onto the
app.js / data.js / styles.css references in index.html, so a normal page
reload always picks up the latest deploy instead of a browser-cached copy.
"""
import hashlib
import re
import sys

SRC_MODULE_ORDER = [
    "src/keys.js",
    "src/changelogData.js",
    "src/state.js",
    "src/logic.js",
    "src/dom.js",
    "src/render.js",
    "src/exportImport.js",
    "src/events.js",
    "src/main.js",
]

IMPORT_BLOCK = re.compile(r'^import\s*\{.*?\}\s*from\s*["\'][^"\']+["\'];?\s*$\n?', re.MULTILINE | re.DOTALL)
EXPORT_PREFIX = re.compile(r"^(\s*)export\s+(function|const|let)\s")


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
    with open("app.src.js", "w", encoding="utf-8") as f:
        f.write(assembled)
    print(f"Assembled {len(SRC_MODULE_ORDER)} src/*.js modules -> app.src.js")


TRAILING_COMMENT_SAFE = re.compile(r"^(?P<code>[^'\"`]*?)\s*//.*$")


def minify(src: str) -> str:
    out_lines = []
    in_template = False
    for raw_line in src.split("\n"):
        line = raw_line

        if in_template:
            # Inside a multi-line template literal: pass through untouched.
            out_lines.append(line)
            backtick_count = line.count("`")
            if backtick_count % 2 == 1:
                in_template = False
            continue

        stripped = line.strip()

        # Whole-line comment -> drop entirely.
        if stripped.startswith("//"):
            continue

        # Blank line -> drop.
        if stripped == "":
            continue

        # Trailing comment on an otherwise quote-free line -> safe to strip.
        m = TRAILING_COMMENT_SAFE.match(stripped)
        if m:
            stripped = m.group("code").rstrip()
            if stripped == "":
                continue

        out_lines.append(stripped)

        backtick_count = stripped.count("`")
        if backtick_count % 2 == 1:
            in_template = True

    return "\n".join(out_lines) + "\n"


VERSIONED_ASSET = re.compile(r'(href|src)="(app\.js|data\.js|styles\.css)(?:\?v=[a-f0-9]+)?"')


def stamp_index_html(outputs):
    with open("styles.css", "r", encoding="utf-8") as f:
        css = f.read()
    combined = (outputs["app.js"] + outputs["data.js"] + css).encode("utf-8")
    version = hashlib.sha1(combined).hexdigest()[:8]

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    stamped = VERSIONED_ASSET.sub(lambda m: f'{m.group(1)}="{m.group(2)}?v={version}"', html)
    if stamped != html:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(stamped)
    print(f"index.html stamped with cache-busting version {version}")


def main():
    assemble_app_src()
    pairs = [("app.src.js", "app.js"), ("data.src.js", "data.js")]
    outputs = {}
    for src_name, out_name in pairs:
        with open(src_name, "r", encoding="utf-8") as f:
            src = f.read()
        minified = minify(src)
        with open(out_name, "w", encoding="utf-8") as f:
            f.write(minified)
        outputs[out_name] = minified
        before = len(src)
        after = len(minified)
        print(f"{src_name} -> {out_name}: {before} -> {after} bytes ({100 * after // before}%)")
    stamp_index_html(outputs)


if __name__ == "__main__":
    sys.exit(main())
