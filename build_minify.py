#!/usr/bin/env python3
"""
Minifies app.src.js / data.src.js into app.js / data.js (the files index.html
actually loads). Edit the .src.js files, then re-run this script.

Conservative on purpose: strips full-line "//" comments, blank lines, and
leading indentation from ordinary code lines. Any line that falls inside a
multi-line `template literal` is passed through byte-for-byte untouched, so
no HTML-in-JS string content is ever touched. Lines containing quote/backtick
characters keep any trailing inline comment as-is rather than risk mismatching
a "//" inside a string.
"""
import re
import sys

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


def main():
    pairs = [("app.src.js", "app.js"), ("data.src.js", "data.js")]
    for src_name, out_name in pairs:
        with open(src_name, "r", encoding="utf-8") as f:
            src = f.read()
        minified = minify(src)
        with open(out_name, "w", encoding="utf-8") as f:
            f.write(minified)
        before = len(src)
        after = len(minified)
        print(f"{src_name} -> {out_name}: {before} -> {after} bytes ({100 * after // before}%)")


if __name__ == "__main__":
    sys.exit(main())
