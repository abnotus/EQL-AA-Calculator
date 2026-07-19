# -*- coding: utf-8 -*-
# Direct, data-independent test of wiki-sync/guess_effects.py's core logic -
# same spirit as test_guess_costs_interpolation.py: exercises the algorithm
# against synthetic inputs so it doesn't depend on the live dataset's
# current confidence state (which is expected to change as the wiki catches
# up - that's the feature working, not a reason for a test to break).
import sys, importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("guess_effects", REPO / "wiki-sync" / "guess_effects.py")
ge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ge)

# --- extract_progressions: finds every slash-progression in a description,
# in order of appearance, splitting known/unknown slots. ---
progs = ge.extract_progressions("Grants 20/40/?/?% chance to resist charm, and 15/30/?/?% chance to resist mesmerization.")
print("multi-progression extraction:", progs)
assert len(progs) == 2, f"FAIL: expected 2 independent progressions, got {len(progs)}"
assert progs[0]["known"] == {0: 20, 1: 40} and progs[0]["unknown"] == [2, 3]
assert progs[1]["known"] == {0: 15, 1: 30} and progs[1]["unknown"] == [2, 3]
print("PASS: two independent progressions in one description are extracted separately, in order")

progs2 = ge.extract_progressions("Increases your critical hit chance by 1/?/5/10%.")
assert progs2[0]["known"] == {0: 1, 2: 5, 3: 10} and progs2[0]["unknown"] == [1]
print("PASS: a single bounded gap is extracted correctly")

progs3 = ge.extract_progressions("No progression here at all.")
assert progs3 == []
print("PASS: a description with no slash-progression yields nothing to guess")

# --- interpolate_bounded_gaps: identical behavior to the cost version -
# bounded gap gets a floor-midpoint guess, trailing gap gets nothing. ---
known = {0: 1, 2: 5, 3: 10}
result = ge.interpolate_bounded_gaps(known, [1])
print("bounded gap (Combat Fury's actual shape):", result)
assert result[1]["value"] == 3 and result[1]["confidence"] == "low" and result[1]["interpolated"] is True

known2 = {0: 10}
result2 = ge.interpolate_bounded_gaps(known2, [1, 2])
print("trailing gap (a Mastery AA's actual shape):", result2)
assert result2 == {}, "FAIL: a trailing gap past every known rank must never get an interpolated guess"
print("PASS: interpolate_bounded_gaps only fills a gap boxed in on both sides, same as costs")

# --- guess_for_progression: sibling voting, same tiers as costs. ---
pool = [
    {"name": "Sib A", "values": [10, 20, 30]},
    {"name": "Sib B", "values": [10, 20, 30]},
]
prog = {"known": {0: 10}, "unknown": [1, 2]}
g = ge.guess_for_progression("Target", 0, prog, pool)
print("unanimous 2-sibling case:", g)
assert g[1]["value"] == 20 and g[1]["confidence"] == "high"
assert g[2]["value"] == 30 and g[2]["confidence"] == "high"

pool2 = [
    {"name": "A", "values": [10, 20]},
    {"name": "B", "values": [10, 20]},
    {"name": "C", "values": [10, 25]},
]
prog2 = {"known": {0: 10}, "unknown": [1]}
g2 = ge.guess_for_progression("Target", 0, prog2, pool2)
print("2-of-3 majority case:", g2)
assert g2[1]["value"] == 20 and g2[1]["confidence"] == "medium"

pool3 = [
    {"name": "A", "values": [10, 20]},
    {"name": "B", "values": [10, 25]},
]
prog3 = {"known": {0: 10}, "unknown": [1]}
g3 = ge.guess_for_progression("Target", 0, prog3, pool3)
print("exact tie case:", g3)
assert 1 not in g3, "FAIL: an exact tie between two siblings must not produce a guess"
print("PASS: sibling voting matches the same high/medium/tie rules as cost-guessing")

# --- group_for_name: sibling matching only works within a declared group -
# an AA not listed in EFFECT_SIBLING_GROUPS has no group at all, so main()
# never builds it a sibling pool regardless of what values happen to match
# elsewhere in the dataset (see the module docstring: a shared magnitude
# across unrelated AAs isn't evidence, unlike a shared cost curve). ---
assert ge.group_for_name("Alchemy Mastery") is not None
assert ge.group_for_name("Baking Mastery") == ge.group_for_name("Alchemy Mastery")
assert ge.group_for_name("Some Totally Unrelated AA") is None
print("PASS: group_for_name only recognizes AAs in an explicitly declared sibling group")

# --- MANUAL_EFFECT_GUESSES must be reachable even with zero known slots in
# the progression (the extreme evidence-free case, same as costs' zero-
# known-ranks fix) - synthetic entry, not a real one, so this test stays
# true regardless of what MANUAL_EFFECT_GUESSES holds on any given day. ---
ge.MANUAL_EFFECT_GUESSES[("__synthetic test AA__", 0)] = {1: 42}
try:
    prog4 = {"known": {}, "unknown": [0, 1]}
    g4 = ge.guess_for_progression("__synthetic test AA__", 0, prog4, [])
    print("zero-known manual fallback case:", g4)
    assert 0 not in g4, "FAIL: index 0 has no manual entry, shouldn't get one"
    assert g4[1]["value"] == 42 and g4[1]["confidence"] == "very-low" and g4[1]["manual"] is True
    print("PASS: MANUAL_EFFECT_GUESSES is reachable even with zero known slots")
finally:
    del ge.MANUAL_EFFECT_GUESSES[("__synthetic test AA__", 0)]

# No manual entry either -> nothing, safely.
prog5 = {"known": {}, "unknown": [0]}
g5 = ge.guess_for_progression("__totally unmapped__", 0, prog5, [])
assert g5 == {}, "FAIL: zero known slots and no manual entry must yield nothing, not a crash"
print("PASS: zero known slots with no manual entry yields nothing, safely")

print("ALL PASS")
