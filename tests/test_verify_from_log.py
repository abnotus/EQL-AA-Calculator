# -*- coding: utf-8 -*-
# Direct, data-independent test of wiki-sync/verify_from_log.py's
# classify_cost - the core comparison verify_from_log.py's main() uses
# per (name, rank) found in a character's log. Same philosophy as this
# project's other wiki-sync unit tests: synthetic costs tables rather
# than depending on a real log file being available to run against.
import sys, importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("verify_from_log", REPO / "wiki-sync" / "verify_from_log.py")
vfl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vfl)

COSTS = ["2", "4", "6"]

assert vfl.classify_cost(1, 2, COSTS) == ("matched", 2)
assert vfl.classify_cost(2, 4, COSTS) == ("matched", 4)
print("PASS: a rank whose logged cost agrees with data.src.js is matched")

assert vfl.classify_cost(2, 5, COSTS) == ("mismatched", 4)
print("PASS: a rank whose logged cost disagrees is mismatched, with the real cost for the caller to report")

assert vfl.classify_cost(4, 99, COSTS) == ("no-data", None)
print("PASS: a rank past the end of the current costs table is no-data")

assert vfl.classify_cost(2, 99, ["2", "?", "6"]) == ("no-data", None)
print("PASS: a rank whose current cost is still '?' is no-data")

# --- Regression: rank 0 (or negative) must be no-data, not silently read
# costs[-1] via Python's negative indexing - a malformed/unexpected log
# line reporting rank 0 would otherwise get compared against the LAST
# rank's cost instead of correctly finding nothing to compare. ---
assert vfl.classify_cost(0, 6, COSTS) == ("no-data", None), \
    "FAIL: rank 0 must be no-data, not silently wrap to costs[-1] (the last rank)"
assert vfl.classify_cost(-1, 6, COSTS) == ("no-data", None), \
    "FAIL: a negative rank must be no-data too"
print("PASS: rank 0 and negative ranks are no-data, not a silent wraparound match against the last rank")

print("ALL PASS")
