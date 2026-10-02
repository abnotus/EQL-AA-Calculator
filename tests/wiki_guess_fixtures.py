# -*- coding: utf-8 -*-
# Shared brace-matching helpers for freezing a guess-rendering test's "?"
# and its guess as fabricated, permanent fixtures - instead of pinning to
# whichever real AA currently happens to have an unconfirmed cost/effect
# value, which breaks (and needs a full rewrite) the moment the wiki (or
# the user's own edit) confirms it. See CLAUDE.md's former "Stop pinning
# guess-feature tests..." to-do and tests/README.md's "Tests pinned to
# live data" section for the history this replaces.
#
# Two targets, both found by a stable anchor substring and balanced from
# there - the logic test_manual_guess.py originated for one of them, lifted
# out and generalized for reuse:
#
# - A whole AA object in data.js (e.g. `{name:"Rapid Feign",...}`) -
#   data.js is minified but NOT mangled (AA_DATA, name, costs, description
#   all stay literally readable; esbuild only renames identifiers it can
#   prove are never referenced elsewhere, and these are read as globals
#   from app.js), so the real data.js is intercepted directly.
# - A guess-table entry's value in app.js (e.g. COST_GUESS_TABLE's
#   `"class:Monk:rapid-feign": {...}`) - app.js IS mangled (it's bundled),
#   so this instead serves app.src.js, the unminified-but-otherwise-
#   identical generated sibling, with just that one entry replaced.
#
# Both assert their anchor was found - a loud, specific failure (this AA
# got renamed/restructured, go pick a new host) instead of the route
# silently serving unpatched content and the test failing somewhere far
# from the real cause.
import os

APP_SRC_PATH = os.path.join(os.path.dirname(__file__), "..", "app.src.js")
DATA_JS_PATH = os.path.join(os.path.dirname(__file__), "..", "data.js")


def _replace_balanced(src, start, open_char, close_char, replacement):
    depth = 0
    i = start
    while True:
        if src[i] == open_char:
            depth += 1
        elif src[i] == close_char:
            depth -= 1
            if depth == 0:
                break
        i += 1
    end = i + 1
    return src[:start] + replacement + src[end:]


def replace_object_literal(src, start_marker, replacement):
    """Finds `start_marker` (beginning with the object's own `{`, e.g.
    '{name:"Rapid Feign"') in src, balances to the matching `}`, and
    splices in `replacement` (including its own braces) in place of the
    whole matched object."""
    start = src.find(start_marker)
    assert start != -1, f"could not find {start_marker!r} - has this AA been renamed or removed?"
    return _replace_balanced(src, start, "{", "}", replacement)


def replace_table_value(src, key_prefix, replacement):
    """Finds `key_prefix` (ending in the value's own opening brace, e.g.
    '\"class:Monk:rapid-feign\": {') in src, balances from that brace to
    its matching `}`, and splices in `replacement` (including its own
    braces) in place of the whole matched value. Only for a host AA that
    already has a real guess-table entry - most fabricated hosts won't
    (they're fully confirmed, so nothing is unresolved for the real
    algorithm to have guessed), so insert_table_entry below is the one
    actually used in practice."""
    key_start = src.find(key_prefix)
    assert key_start != -1, f"could not find {key_prefix!r} - has this guess-table entry's key changed shape?"
    brace_start = key_start + len(key_prefix) - 1
    return _replace_balanced(src, brace_start, "{", "}", replacement)


def insert_table_entry(src, table_decl, entry_text):
    """Finds `table_decl` (e.g. 'const COST_GUESS_TABLE = {') in src and
    inserts `entry_text` (a bare '\"key\": {...}' pair, no trailing comma)
    as the new first entry of that object literal - for a fabricated host
    AA that has no real guess-table entry of its own to replace (the
    common case: a host chosen for being ordinary and fully confirmed has
    nothing for the real algorithm to have guessed)."""
    decl_start = src.find(table_decl)
    assert decl_start != -1, f"could not find {table_decl!r} - has this table's declaration changed?"
    brace_pos = decl_start + len(table_decl) - 1
    assert src[brace_pos] == "{", f"{table_decl!r} doesn't end at its own opening brace as expected"
    return src[:brace_pos + 1] + f"\n  {entry_text},\n" + src[brace_pos + 1:]


def read_app_src():
    with open(APP_SRC_PATH, "r", encoding="utf-8") as f:
        return f.read()


def read_data_js():
    with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
        return f.read()
