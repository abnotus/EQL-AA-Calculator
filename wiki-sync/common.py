#!/usr/bin/env python3
"""
Shared machinery for wiki-sync's data.src.js-parsing scripts
(assign_aa_ids.py, guess_costs.py, guess_effects.py): the AA identity
system (slugify + the auto-vs-non-auto disambiguation key every one of
those scripts needs to agree with keys.js on) and the generic parts of the
two guess generators (parse scaffolding, the parse-sanity tripwire,
bounded interpolation, confidence-tier vote constants, and the small
JS-literal emit helpers). Kept in one place specifically because this is
the layer where a hand-synced drift between scripts would silently break
guess/id resolution rather than just look inconsistent - three independent
copies of the same predicate is how identity keys quietly diverge.

This is a *three*-way unification, not four: src/keys.js computes this
same identity (scope, className, key) logic too, in JS, for the live app
to resolve saves/guesses against - that side still has to be kept in sync
with this one by hand, since a Python module can't be shared with the
browser runtime. Nothing here changes that; it just stops three Python
scripts from independently drifting from each other on top of it.

Not meant to be run directly - imported by the scripts above, each of
which inserts its own directory onto sys.path first so this resolves the
same way whether the script is run directly (`python wiki-sync/x.py`) or
loaded dynamically by a test (importlib.util.spec_from_file_location,
which does not put the script's own directory on sys.path the way a
direct `python` invocation does).
"""
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_SRC = HERE.parent / "data.src.js"
AA_IDS_SRC = HERE.parent / "src" / "aaIds.js"

DATA_CATEGORY_START = re.compile(r'^(general|archetype|special):\s*\[')
DATA_CLASS_START = re.compile(r'^"([^"]+)":\s*\[')
DATA_ENTRY_NAME = re.compile(r'name:\s*"((?:[^"\\]|\\.)*)"')
DATA_ENTRY_AUTO = re.compile(r'\bauto:\s*true')
DATA_ENTRY_AUTORANKS = re.compile(r'\bautoRanks:\s*\d+')

HIGH_MIN_SIBLINGS = 2
MEDIUM_MAJORITY = 2.0 / 3.0
LOW_MAJORITY = 0.5

# See check_parse_sanity.
MIN_ENTRY_FRACTION_OF_ID_TABLE = 0.9


def slugify(name):
    # ‘/’ are the curly "smart quotes" a wiki CMS's auto-formatting
    # commonly substitutes for a straight apostrophe - left unstripped, one
    # falls into the [^a-z0-9]+ catch-all below and becomes a literal "-",
    # so the same name slugifies differently depending only on which glyph
    # happened to be on the page that day. src/keys.js's own slugify must
    # be kept equivalent by hand (see this file's own docstring).
    s = name.lower().replace("'", "").replace("‘", "").replace("’", "")
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s


def iter_data_entries(data_src_path=DATA_SRC):
    """Walks data.src.js line by line, tracking which (scope, className)
    category each line falls inside, and yields (scope, className, line)
    for every raw AA-entry line ('{ name: ...}') found within a
    recognized category - the scaffolding every script that regex-parses
    data.src.js needs before it does its own script-specific field
    extraction on `line` (guess_costs.py wants ranks+costs, guess_effects.py
    wants description, assign_aa_ids.py wants neither). A line outside any
    recognized category, or before one has been seen, is skipped rather
    than yielded with a null category - callers never need to check for
    that case themselves."""
    text = data_src_path.read_text(encoding="utf-8")
    current_cat = None
    for line in text.split("\n"):
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
        if not current_cat:
            continue
        yield current_cat[0], current_cat[1], s


def check_parse_sanity(entries, aa_ids_path=AA_IDS_SRC):
    """parse_data_src is a regex over source text, same failure mode
    build_minify.py's own invariant checkers guard against: a data.src.js
    reformat it doesn't recognize makes it silently match far less than it
    should, which looks identical to "the dataset shrank" - every
    downstream guess/id would quietly get worse with no error anywhere.
    src/aaIds.js's AA_ID_TABLE is append-only and never drops an entry even
    for an AA later removed from data.src.js (see that file's own header),
    so its size is a safe upper-bound floor for how many AAs should still
    parse out today - a small fraction below it is normal (legitimate
    removals), a parser silently breaking is not."""
    id_table_size = len(re.findall(r'"[^"]+":\s*\d+', aa_ids_path.read_text(encoding="utf-8")))
    floor = int(id_table_size * MIN_ENTRY_FRACTION_OF_ID_TABLE)
    if len(entries) < floor:
        print(
            f"ERROR: parse_data_src() only found {len(entries)} AA entries, but "
            f"{aa_ids_path} has {id_table_size} - the regex parser almost certainly "
            "stopped matching data.src.js's current format rather than the dataset "
            f"actually shrinking this much (expected at least {floor}). Fix the "
            "parser before trusting anything it produces."
        )
        sys.exit(1)


def slug_key_for(entries, i):
    """The AA identity key: entries[i]["name"], slugified, with the same
    auto-vs-non-auto disambiguation src/keys.js's keyForEntryIdx applies for
    a repeated name within one (scope, className) bucket - the first
    non-auto occurrence (or the first occurrence at all, if every
    occurrence is auto) gets the bare slug; any auto occurrence beyond that
    gets "-auto" / "-auto-N" appended. entries: list of dicts with at least
    scope/className/name/auto keys, in data.src.js order."""
    scope, className = entries[i]["scope"], entries[i]["className"]
    bucket = [j for j, e in enumerate(entries) if e["scope"] == scope and e["className"] == className]
    names = [entries[j]["name"] for j in bucket]
    slugs = [slugify(n) for n in names]
    pos = bucket.index(i)
    base = slugs[pos]
    same = [p for p, s in enumerate(slugs) if s == base]
    if len(same) <= 1 or not entries[bucket[pos]]["auto"]:
        return base
    auto_siblings = [p for p in same if entries[bucket[p]]["auto"]]
    auto_pos = auto_siblings.index(pos)
    return f"{base}-auto" if auto_pos == 0 else f"{base}-auto-{auto_pos + 1}"


def id_key(scope, className, key):
    return f"{scope}:{className or ''}:{key}"


def js_string(s):
    return json.dumps(s)


def interpolate_bounded_gaps(known, unknown):
    """A DIFFERENT, weaker kind of evidence than sibling matching: for an
    unknown rank strictly between two ranks THIS SAME AA already has real
    numbers for, linearly interpolate against those two anchors and floor
    to an integer - e.g. a cost curve (1, ?, 4, 6) with no same-rank-count
    sibling to corroborate against still has rank 2 boxed in on both sides
    by real numbers (1 and 4), floor(1 + (4-1)*0.5) = 2.

    Deliberately only for a gap with a known value on BOTH sides - bounded
    interpolation and open-ended extrapolation are not the same risk. A
    gap with nothing after it to bound it (e.g. Turn Summoned's cost curve
    3/6/?) is left alone here - guessing from an AA's own trailing trend
    alone is exactly the mistake both guess scripts exist to avoid (see
    their own docstrings) - only sibling matching (or nothing) applies to
    a trailing gap. Never returns a confidence above "low": zero external
    corroboration, purely this AA's own two endpoints."""
    if not known:
        return {}
    known_idxs = sorted(known.keys())
    result = {}
    for i in unknown:
        below = max((k for k in known_idxs if k < i), default=None)
        above = min((k for k in known_idxs if k > i), default=None)
        if below is None or above is None:
            continue
        v_below, v_above = known[below], known[above]
        frac = (i - below) / (above - below)
        result[i] = {
            "value": v_below + math.floor((v_above - v_below) * frac),
            "confidence": "low",
            "basedOn": [],
            "interpolated": True,
        }
    return result


def vote_guesses(known, unknown, matching, manual_lookup):
    """Shared confidence-tier voting, bounded-interpolation fallback,
    manual-fallback, and own-shape sanity check behind both guess_costs.py's
    guess_for_entry and guess_effects.py's guess_for_progression - identical
    in both except where/how the last-resort MANUAL_GUESSES-style fallback
    is keyed (an AA name alone for costs; (AA name, progression index) for
    effects, since a description can hold more than one independent
    progression) - manual_lookup(rank_idx) -> value or None abstracts that
    one difference away.

    known: {rank_idx: value}, already known/real for this entry. unknown:
    [rank_idx, ...] still needing a guess. matching: list of {"name": str,
    "values": [value, ...]} for every sibling whose own known slots already
    agree with `known` - already filtered (same rank/slot count, monotonic
    where that applies) by the caller, since what counts as a valid sibling
    differs between costs and effects. Returns {rank_idx: {"value",
    "confidence", "basedOn", ["interpolated"], ["manual"]}} for whichever
    unknown ranks got a confident-enough guess."""
    result = {}
    for i in unknown:
        confidence = None
        top_value = None
        based_on = []

        if matching:
            votes = Counter(r["values"][i] for r in matching)
            top_value, top_count = votes.most_common(1)[0]
            share = top_count / len(matching)
            if len(matching) >= HIGH_MIN_SIBLINGS and top_count == len(matching):
                confidence = "high"
            elif len(matching) == 1 or share >= MEDIUM_MAJORITY:
                confidence = "medium"
            elif share > LOW_MAJORITY:
                confidence = "low"
            # else: exact tie or worse - sibling evidence doesn't clear the
            # bar, fall through to the interpolation attempt below instead
            # of giving up on this rank entirely.
            if confidence:
                based_on = sorted({r["name"] for r in matching if r["values"][i] == top_value})

        if confidence is None:
            interp = interpolate_bounded_gaps(known, [i]).get(i)
            if interp:
                top_value, confidence = interp["value"], interp["confidence"]

        manual_entry = False
        if confidence is None:
            manual_value = manual_lookup(i)
            if manual_value is not None:
                top_value, confidence = manual_value, "very-low"
                manual_entry = True

        if confidence is None:
            continue

        # A guess must not contradict this entry's own already-known shape:
        # never below the previous rank's (known or already-guessed) value,
        # never above the next rank's if that one's already known.
        prev_val = known.get(i - 1, result.get(i - 1, {}).get("value"))
        next_val = known.get(i + 1)
        if prev_val is not None and top_value < prev_val:
            continue
        if next_val is not None and top_value > next_val:
            continue

        entry_out = {"value": top_value, "confidence": confidence, "basedOn": based_on}
        if not based_on and confidence == "low":
            entry_out["interpolated"] = True
        if manual_entry:
            entry_out["manual"] = True
        result[i] = entry_out
    return result


def guess_to_js_literal(rank_idx, g):
    """One rank's guess -> its JS object literal, e.g.
    '"2": { value: 40, confidence: "medium", basedOn: ["Sib A"] }' - shared
    by guess_costs.py's and guess_effects.py's write_output, which nest
    this identically except effects has an extra progression-index layer
    of keys between the AA and its ranks."""
    based_on = ", ".join(js_string(n) for n in g["basedOn"])
    interp = ", interpolated: true" if g.get("interpolated") else ""
    manual = ", manual: true" if g.get("manual") else ""
    return (
        f'"{rank_idx}": {{ value: {g["value"]}, confidence: {js_string(g["confidence"])}, '
        f'basedOn: [{based_on}]{interp}{manual} }}'
    )
