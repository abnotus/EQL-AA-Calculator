#!/usr/bin/env python3
"""
Cross-references a live EverQuest Legends log file's own "gained the
ability .../improved ... at a cost of N ability points" lines against
data.src.js's confirmed costs - a second, independent verification
channel beyond the wiki scrape itself (a player's own log is ground truth
for whatever it covers, no transcription in between). Never reads the
wiki and never touches data.src.js - purely a diagnostic, run by hand
against whatever log file is available:

    python wiki-sync/verify_from_log.py path/to/eqlog_CharName_Zone.txt

A log rarely covers every AA a character has (some were trained before
logging started, some belong to a class no longer active), so this only
ever confirms a subset - see log_verified.json below for how that's
tracked across however many log files get checked over time.

Keeps the LATEST logged cost per (AA name, rank) if a line repeats -
mostly relevant for a rank retrained after a patch changed the AA (e.g.
Master of All's September rework: an old "gained ... at a cost of 5"
followed weeks later by a new "gained ... at a cost of 10" for the same
rank 1, after the in-game refund) - the later entry is closer to what the
AA actually costs today, which is what this is checking against anyway.

Four outcomes per (name, rank) found in the log:
    matched      the log's cost agrees with data.src.js - written to
                 log_verified.json
    mismatched   the log's cost DISAGREES with data.src.js - a real
                 finding worth investigating, never silently ignored
    unrecognized the name isn't in data.src.js at all (retired AA-toggle
                 naming like "Symphonic Aura: Enabled", a genuinely new
                 AA the wiki scrape hasn't picked up yet, or an ambiguous
                 name shared by more than one class - can't safely
                 compare without knowing which)
    no-data      the name matches, but this rank doesn't exist in the
                 CURRENT data (an old rank from before a patch reworked
                 the AA and reduced its rank count, or the wiki still has
                 "?" there)
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DATA_SRC, DATA_ENTRY_NAME, iter_data_entries  # noqa: E402

HERE = Path(__file__).resolve().parent
VERIFIED_FILE = HERE / "log_verified.json"

COSTS_RE = re.compile(r'\bcosts:\s*\[([^\]]*)\]')
FILL_RE = re.compile(r'\bcosts:\s*Array\((\d+)\)\.fill\("0"\)')
GAIN_RE = re.compile(r'You have gained the ability "([^"]+)" at a cost of (\d+) ability points?\.')
IMPROVE_RE = re.compile(r'You have improved (.+?) (\d+) at a cost of (\d+) ability points?\.')


def parse_costs(raw):
    return [c.strip().strip('"') for c in raw.split(",") if c.strip()]


def load_data_src():
    """name -> list of (scope, className, costs) - more than one entry
    means the name is ambiguous across classes (e.g. Quick Evacuation),
    which this treats the same as "not found" rather than guessing."""
    by_name = {}
    for scope, className, s in iter_data_entries(DATA_SRC):
        nm = DATA_ENTRY_NAME.search(s)
        if not nm:
            continue
        name = nm.group(1)
        ct = COSTS_RE.search(s)
        if ct:
            costs = parse_costs(ct.group(1))
        else:
            fm = FILL_RE.search(s)
            costs = ["0"] * int(fm.group(1)) if fm else []
        by_name.setdefault(name, []).append((scope, className, costs))
    return by_name


def parse_log(log_path):
    events = []
    unparsed = []
    with open(log_path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            if "at a cost of" not in line:
                continue
            m = GAIN_RE.search(line)
            if m:
                events.append((i, m.group(1), 1, int(m.group(2))))
                continue
            m = IMPROVE_RE.search(line)
            if m:
                events.append((i, m.group(1), int(m.group(2)), int(m.group(3))))
                continue
            unparsed.append((i, line.strip()))
    return events, unparsed


def main():
    if len(sys.argv) != 2:
        print("usage: python wiki-sync/verify_from_log.py path/to/eqlog_file.txt")
        return 1
    log_path = Path(sys.argv[1])
    if not log_path.exists():
        print(f"ERROR: {log_path} not found")
        return 1

    by_name = load_data_src()
    events, unparsed = parse_log(log_path)
    print(f"Parsed {len(events)} 'at a cost of' line(s) from {log_path.name}"
          + (f", {len(unparsed)} unparsed" if unparsed else ""))
    for i, line in unparsed:
        print(f"  UNPARSED line {i}: {line}")

    latest = {}
    for line_no, name, rank, cost in events:
        latest[(name, rank)] = (line_no, cost)

    matched, mismatched, unmatched_name, no_data = [], [], [], []
    for (name, rank), (line_no, cost) in latest.items():
        entries = by_name.get(name)
        if not entries or len(entries) > 1:
            unmatched_name.append((line_no, name, rank, cost))
            continue
        _, _, costs = entries[0]
        if rank > len(costs) or costs[rank - 1] == "?":
            no_data.append((line_no, name, rank, cost))
            continue
        if int(costs[rank - 1]) == cost:
            matched.append((name, rank, cost))
        else:
            mismatched.append((line_no, name, rank, cost, costs[rank - 1]))

    print(f"\nMatched: {len(matched)}  Mismatched: {len(mismatched)}  "
          f"Unrecognized name: {len(unmatched_name)}  No current data for that rank: {len(no_data)}")

    if mismatched:
        print("\n=== MISMATCHED (real game cost disagrees with data.src.js - investigate) ===")
        for line_no, name, rank, cost, real in mismatched:
            print(f"  line {line_no}: {name} rank {rank} - log says {cost}, data.src.js says {real}")

    if unmatched_name:
        print("\n=== UNRECOGNIZED NAME (not in data.src.js, ambiguous across classes, or a retired AA/naming scheme) ===")
        for line_no, name, rank, cost in unmatched_name:
            print(f'  line {line_no}: "{name}" rank {rank} (cost {cost})')

    if no_data:
        print("\n=== NO CURRENT DATA FOR THAT RANK (an old/retired rank - e.g. before a patch reworked the AA) ===")
        for line_no, name, rank, cost in no_data:
            print(f"  line {line_no}: {name} rank {rank} (cost {cost} in the log)")

    # Running record: never removes an existing entry (a name absent from
    # THIS run's log isn't unverified, just not re-checked this time) or
    # lowers maxRankVerified; only adds new AAs or raises the rank.
    existing = {}
    if VERIFIED_FILE.exists():
        existing = json.loads(VERIFIED_FILE.read_text(encoding="utf-8"))
    today = date.today().isoformat()
    for name, rank, cost in matched:
        entry = existing.get(name, {"maxRankVerified": 0, "verifiedAt": today})
        if rank > entry["maxRankVerified"]:
            entry["maxRankVerified"] = rank
            entry["verifiedAt"] = today
        existing[name] = entry
    VERIFIED_FILE.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\nUpdated {VERIFIED_FILE.name}: {len(existing)} AA(s) with at least one log-verified rank")

    return 1 if mismatched else 0


if __name__ == "__main__":
    sys.exit(main())
