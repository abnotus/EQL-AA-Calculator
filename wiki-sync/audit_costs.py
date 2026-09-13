#!/usr/bin/env python3
"""
One-off diagnostic: hunts for a confirmed cost that disagrees with strong
sibling consensus, as a way to localize the 13-point gap between this
dataset's max-AA total (1185) and a real max-level player's reported total
(1172) - see scrape_wiki.py's own docstring for that discrepancy's history.

Reuses guess_costs.py's own sibling-matching machinery (same reference
pool, same monotonic-only filter, same voting rules) but inverts its use:
instead of asking "what should this UNKNOWN rank cost", it asks "if this
KNOWN rank's real cost were hidden, would sibling-matching predict
something else" - a real cost that contradicts a high/medium-confidence
sibling consensus is exactly the shape a wiki transcription error would
take. A curator MANUAL_GUESSES fallback never counts here (only high/medium
sibling-matched predictions are compared against), since disagreeing with a
human guess proves nothing.

Also checks for a phantom extra rank: any AA whose cost ladder, with its
own final rank dropped, exactly matches another AA's complete (shorter)
ladder - suggesting the longer one may have one rank too many, and that
extra rank's own cost is the whole overcount.

Not part of the regular data.src.js -> costGuesses.js pipeline (it doesn't
write anything) - run by hand only when hunting a specific total-cost
discrepancy:

    python wiki-sync/audit_costs.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guess_costs  # noqa: E402 - reuse parse_data_src/guess_for_entry/is_monotonic as-is

GAP = 13  # the discrepancy this run is hunting - see the module docstring


def build_reference_pool(entries, exclude_idx):
    pool = []
    for i, e in enumerate(entries):
        if i == exclude_idx or e["auto"] or e["autoRanks"]:
            continue
        if any(c == "?" for c in e["costs"][:e["ranks"]]):
            continue
        values = [int(c) for c in e["costs"][:e["ranks"]]]
        pool.append({"name": e["name"], "ranks": e["ranks"], "values": values,
                     "monotonic": guess_costs.is_monotonic(values)})
    return pool


def find_cost_anomalies(entries):
    anomalies = []
    for i, e in enumerate(entries):
        if e["auto"] or e["autoRanks"]:
            continue
        if any(c == "?" for c in e["costs"][:e["ranks"]]):
            continue  # only a fully-known AA can be checked this way
        real_values = [int(c) for c in e["costs"][:e["ranks"]]]
        pool = build_reference_pool(entries, exclude_idx=i)
        for idx in range(e["ranks"]):
            hidden = dict(e)
            hidden_costs = list(e["costs"])
            hidden_costs[idx] = "?"
            hidden["costs"] = hidden_costs
            guesses = guess_costs.guess_for_entry(hidden, pool)
            g = guesses.get(idx)
            if not g or g["confidence"] not in ("high", "medium"):
                continue
            if g["value"] == real_values[idx]:
                continue
            anomalies.append((e, idx, real_values[idx], g))
    return anomalies


def find_phantom_ranks(entries):
    fully_known = [
        e for e in entries
        if not e["auto"] and not e["autoRanks"]
        and not any(c == "?" for c in e["costs"][:e["ranks"]])
    ]
    by_ladder = {}
    for e in fully_known:
        values = tuple(int(c) for c in e["costs"][:e["ranks"]])
        by_ladder.setdefault(values, []).append(e)

    found = []
    for e in fully_known:
        values = tuple(int(c) for c in e["costs"][:e["ranks"]])
        if len(values) < 2:
            continue
        shorter = values[:-1]
        matches = by_ladder.get(shorter, [])
        if matches:
            found.append((e, values, matches))
    return found


def main():
    entries = guess_costs.parse_data_src()
    guess_costs.check_parse_sanity(entries)

    print("=== Confirmed costs that disagree with high/medium sibling consensus ===")
    anomalies = find_cost_anomalies(entries)
    if not anomalies:
        print("(none found)")
    for e, idx, real, g in sorted(anomalies, key=lambda a: -abs(a[2] - a[3]["value"])):
        diff = real - g["value"]
        flag = "  <=== exactly the 13-point gap" if abs(diff) == GAP else ""
        print(f'{e["scope"]}:{e["className"] or ""}:{e["name"]}  rank {idx + 1}/{e["ranks"]}: '
              f'real={real}  sibling-predicted={g["value"]} ({g["confidence"]}, '
              f'based on {", ".join(g["basedOn"])})  diff={diff:+d}{flag}')

    print()
    print("=== Possible phantom extra rank (own ladder minus last rank == another AA's full ladder) ===")
    phantoms = find_phantom_ranks(entries)
    if not phantoms:
        print("(none found)")
    for e, values, matches in phantoms:
        last_cost = values[-1]
        flag = "  <=== exactly the 13-point gap" if last_cost == GAP else ""
        match_names = ", ".join(f'{m["name"]} ({m["scope"]}:{m["className"] or ""})' for m in matches)
        print(f'{e["scope"]}:{e["className"] or ""}:{e["name"]}  ranks={e["ranks"]}  '
              f'costs={list(values)}  last rank costs {last_cost}{flag}  '
              f'- matches the FULL ladder of: {match_names}')


if __name__ == "__main__":
    sys.exit(main())
