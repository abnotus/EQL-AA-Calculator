# -*- coding: utf-8 -*-
# builds.js's migrateStaleBuildSlots() runs once at boot and strips the
# dead "totalPoints" field from every saved slot's stored JSON, left over
# from before the total-points cap was removed (buildPayload stopped
# emitting it, but existing slots on disk still have it baked in). Left
# alone, that mismatch makes activeBuildMatchesCurrent()'s string
# comparison read an untouched slot as "has unsaved changes" the first
# time it's compared post-upgrade - self-healing (a real save clears it)
# but a false "unsaved" reading in the one subsystem whose entire job is
# telling the user whether their work is backed up is worth actively
# fixing, not just tolerating. This seeds a slot with the exact shape an
# old buildPayload() would have produced (totalPoints included) and
# confirms: the field is gone after boot, every other field is preserved
# exactly (not just "some cleanup happened"), and nothing errors.
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8743/index.html"

OLD_PAYLOAD = {
    "v": 4,
    "selectedClasses": ["Bard", "Beastlord", "Berserker"],
    "charLevel": 42,
    "totalPoints": 1000,
    "ranks": {"general": {"adamant-will": 2}, "archetype": {}, "special": {}, "classes": {}},
    "purchaseOrder": [
        {"scope": "general", "className": None, "key": "adamant-will"},
        {"scope": "general", "className": None, "key": "adamant-will"},
    ],
    "waypoints": [[50, "Halfway", "blue"]],
}
NEW_PAYLOAD = {
    "v": 4,
    "selectedClasses": ["Cleric", "Druid", "Enchanter"],
    "charLevel": 10,
    "ranks": {"general": {}, "archetype": {}, "special": {}, "classes": {}},
    "purchaseOrder": [],
    "waypoints": [],
}
INDEX_PAYLOAD = [
    {"id": "testslot1", "name": "Old Build", "updatedAt": 1000},
    {"id": "testslot2", "name": "Already Current Build", "updatedAt": 2000},
]

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())

    new_payload_raw = json.dumps(NEW_PAYLOAD)
    page.add_init_script(f"""
        localStorage.setItem('eql_aa_builds_index_v1', {json.dumps(json.dumps(INDEX_PAYLOAD))});
        localStorage.setItem('eql_aa_build_testslot1', {json.dumps(json.dumps(OLD_PAYLOAD))});
        localStorage.setItem('eql_aa_build_testslot2', {json.dumps(new_payload_raw)});
    """)
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)

    raw_after = page.evaluate("localStorage.getItem('eql_aa_build_testslot1')")
    print("raw slot payload after boot:", raw_after)
    parsed = json.loads(raw_after)

    assert "totalPoints" not in parsed, "FAIL: the stale totalPoints field is still present after boot"
    print("PASS: the stale totalPoints field was stripped")

    expected_rest = {k: v for k, v in OLD_PAYLOAD.items() if k != "totalPoints"}
    assert parsed == expected_rest, f"FAIL: fields beyond totalPoints were touched - expected {expected_rest}, got {parsed}"
    print("PASS: every other field survived untouched (name, values, and structure all exactly preserved)")

    # The index itself (name/id/updatedAt) must be untouched too - the sweep
    # only ever rewrites slot payloads, never the index.
    index_after = json.loads(page.evaluate("localStorage.getItem('eql_aa_builds_index_v1')"))
    assert index_after == INDEX_PAYLOAD, f"FAIL: the builds index was modified, expected untouched: {index_after}"
    print("PASS: the builds index itself was left untouched")

    # --- A slot with no totalPoints field (already the current shape) must
    # be a true no-op - byte-identical raw string, not just "still parses
    # to the same thing" - proving the sweep doesn't rewrite what it
    # doesn't need to. ---
    raw_new_after = page.evaluate("localStorage.getItem('eql_aa_build_testslot2')")
    print("already-current slot raw payload after boot:", raw_new_after)
    assert raw_new_after == new_payload_raw, "FAIL: a slot with no stale field was rewritten anyway"
    print("PASS: a slot already in the current shape is left byte-identical, not rewritten")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
