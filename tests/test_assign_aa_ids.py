# -*- coding: utf-8 -*-
# Direct, data-independent test of wiki-sync/assign_aa_ids.py's rename-
# detection logic (compute_vanished) - same philosophy as
# test_guess_costs_interpolation.py/test_guess_effects.py: exercise the
# algorithm with synthetic inputs rather than depending on the live
# dataset ever actually containing a pending rename to test against.
#
# The real risk this guards: a wiki rename (a typo fix, a capitalization
# change) makes the next assign_aa_ids.py run compute a new slug for that
# AA, find no existing table entry for it, and append a brand-new id -
# the OLD id is left in the table pointing at a key nothing resolves to,
# silently dropping that AA from every share link that already encoded
# it (reported as "N picks no longer exist", indistinguishable from a
# genuine removal). compute_vanished is what main() uses to detect and
# warn about this specific shape (an id vanishing in the same run new
# ids are assigned) rather than letting it pass silently.
import sys, importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("assign_aa_ids", REPO / "wiki-sync" / "assign_aa_ids.py")
aid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aid)

# --- A genuine removal (no corresponding addition) - vanished lists it,
# same as a rename would at this stage, but main() only warns when
# something was ALSO added in the same run. ---
existing = {"general::adamant-will": 0, "general::combat-fury": 1}
current = {"general::combat-fury"}
result = aid.compute_vanished(existing, current)
print("pure removal case:", result)
assert result == ["general::adamant-will"]
print("PASS: a removed AA's id shows up as vanished")

# --- Nothing vanished - the common, steady-state run. ---
result2 = aid.compute_vanished(existing, {"general::adamant-will", "general::combat-fury"})
print("steady-state case (nothing vanished):", result2)
assert result2 == []
print("PASS: an unchanged table reports nothing vanished")

# --- The rename shape: the old slug is gone, a new one exists that isn't
# in `existing` yet - compute_vanished only reports the "gone" half;
# main() cross-references this against `added` to decide whether to warn,
# but this function's own job is just correctly identifying "gone". ---
existing2 = {"general::innate-regeneration": 5, "general::combat-fury": 1}
current2 = {"general::regeneration", "general::combat-fury"}  # renamed, same AA
result3 = aid.compute_vanished(existing2, current2)
print("rename case (old slug vanished, new slug not yet in the table):", result3)
assert result3 == ["general::innate-regeneration"]
print("PASS: a renamed AA's old id shows up as vanished, same signature a removal has")

# --- Multiple vanished ids, sorted for stable/readable output. ---
existing3 = {"general::z-aa": 2, "general::a-aa": 0, "general::m-aa": 1}
result4 = aid.compute_vanished(existing3, set())
print("multiple-vanished case (sorted):", result4)
assert result4 == ["general::a-aa", "general::m-aa", "general::z-aa"]
print("PASS: vanished keys come back sorted, not in dict-iteration order")

print("ALL PASS")
