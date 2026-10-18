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

# --- parse_log reads only the game's own purchase lines, not a chat line
# quoting one. ---
import tempfile, os
LOG = (
    '[Tue Sep 16 20:41:12 2026] You have gained the ability "Combat Agility" at a cost of 2 ability points.\r\n'
    '[Tue Sep 16 20:41:20 2026] You have improved Combat Agility 2 at a cost of 4 ability points.\r\n'
    "[Tue Sep 16 20:42:01 2026] Bob tells you, 'You have improved Combat Agility 3 at a cost of 6 ability points.'\r\n"
    '[Tue Sep 16 20:43:00 2026] You say, \'You have gained the ability "Fear Resistance" at a cost of 2 ability points.\'\r\n'
)
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "eqlog_test.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(LOG)
    events, unparsed = vfl.parse_log(path)
print("parsed events:", events)
assert [(name, rank, cost) for _, name, rank, cost in events] == [("Combat Agility", 1, 2), ("Combat Agility", 2, 4)], \
    f"FAIL: only the game's own purchase lines should count, got {events}"
assert len(unparsed) == 2, f"FAIL: the quoted chat lines should be reported as unparsed, got {unparsed}"
print("PASS: chat lines quoting a purchase message aren't counted as purchases")

# --- merge_verified: maxRankVerified only covers ranks that were all
# matched, from rank 1 up. ---
record = vfl.merge_verified({}, [("Adamant Will", 1, 2), ("Adamant Will", 3, 6)], "2026-10-18")
assert record["Adamant Will"]["ranksVerified"] == [1, 3], record
assert record["Adamant Will"]["maxRankVerified"] == 1, f"FAIL: rank 2 was never matched, so the max is 1: {record}"
record = vfl.merge_verified(record, [("Adamant Will", 2, 4)], "2026-10-19")
assert record["Adamant Will"]["maxRankVerified"] == 3, f"FAIL: once rank 2 matches, 1-3 are all verified: {record}"
legacy = vfl.merge_verified({"Packrat": {"maxRankVerified": 5, "verifiedAt": "2026-09-01"}}, [("Packrat", 1, 1)], "2026-10-18")
assert legacy["Packrat"]["maxRankVerified"] == 5, f"FAIL: an older entry's recorded max must not drop: {legacy}"
print("PASS: maxRankVerified counts only ranks verified contiguously from rank 1")

print("ALL PASS")
