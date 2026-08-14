# -*- coding: utf-8 -*-
# builds.js's migrateStaleBuildSlots() runs on every boot and self-heals two
# independent things in every saved slot's stored JSON:
#   1. Strips the dead "totalPoints" field, left over from before the
#      total-points cap was removed (buildPayload stopped emitting it, but
#      existing slots on disk still have it baked in). Left alone, that
#      mismatch makes activeBuildMatchesCurrent()'s comparison read an
#      untouched slot as "has unsaved changes" the first time it's compared
#      post-upgrade - self-healing (a real save clears it) but a false
#      "unsaved" reading in the one subsystem whose entire job is telling
#      the user whether their work is backed up is worth actively fixing.
#   2. Backfills a missing "ownedProfileId" to the shared legacy profile
#      (LEGACY_OWNED_PROFILE_ID, state.js) - a slot saved before per-build
#      owned tracking existed always meant "the one global pool", so this
#      keeps it behaving exactly that way until something deliberately
#      diverges it. A slot that already HAS its own ownedProfileId (real
#      per-build data, not a pre-migration slot) must never have that
#      overwritten - only ever filled in when genuinely missing.
# Seeds three slots - stale+no-profile, already-current, and stale-but-
# already-profiled - to pin all of the above independently, plus confirms
# a slot needing no fix at all stays byte-identical (not rewritten).
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

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
    "ownedProfileId": "legacy",
}
# Stale totalPoints AND already has its own real owned profile (not a
# pre-migration slot missing the field entirely) - the backfill must strip
# totalPoints without touching this.
PROFILED_STALE_PAYLOAD = {
    "v": 4,
    "selectedClasses": ["Monk", "Ranger", "Rogue"],
    "charLevel": 30,
    "totalPoints": 500,
    "ranks": {"general": {}, "archetype": {}, "special": {}, "classes": {}},
    "purchaseOrder": [],
    "waypoints": [],
    "ownedProfileId": "customprofile123",
}
INDEX_PAYLOAD = [
    {"id": "testslot1", "name": "Old Build", "updatedAt": 1000},
    {"id": "testslot2", "name": "Already Current Build", "updatedAt": 2000},
    {"id": "testslot3", "name": "Stale But Already-Profiled Build", "updatedAt": 3000},
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
        localStorage.setItem('eql_aa_build_testslot3', {json.dumps(json.dumps(PROFILED_STALE_PAYLOAD))});
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
    expected_rest["ownedProfileId"] = "legacy"
    assert parsed == expected_rest, f"FAIL: fields beyond totalPoints were touched - expected {expected_rest}, got {parsed}"
    print("PASS: every other field survived untouched, and the missing ownedProfileId was backfilled to the shared legacy profile")

    # The index itself (name/id/updatedAt) must be untouched too - the sweep
    # only ever rewrites slot payloads, never the index.
    index_after = json.loads(page.evaluate("localStorage.getItem('eql_aa_builds_index_v1')"))
    assert index_after == INDEX_PAYLOAD, f"FAIL: the builds index was modified, expected untouched: {index_after}"
    print("PASS: the builds index itself was left untouched")

    # --- A slot needing neither fix (no totalPoints, already has its own
    # ownedProfileId) must be a true no-op - byte-identical raw string, not
    # just "still parses to the same thing" - proving the sweep doesn't
    # rewrite what it doesn't need to. ---
    raw_new_after = page.evaluate("localStorage.getItem('eql_aa_build_testslot2')")
    print("already-current slot raw payload after boot:", raw_new_after)
    assert raw_new_after == new_payload_raw, "FAIL: a slot needing no fix was rewritten anyway"
    print("PASS: a slot already in the current shape is left byte-identical, not rewritten")

    # --- A slot that's stale on totalPoints but already has its OWN real
    # owned profile must get totalPoints stripped without its
    # ownedProfileId being clobbered back to the shared legacy one. ---
    raw_profiled_after = page.evaluate("localStorage.getItem('eql_aa_build_testslot3')")
    print("stale-but-already-profiled slot raw payload after boot:", raw_profiled_after)
    parsed_profiled = json.loads(raw_profiled_after)
    assert "totalPoints" not in parsed_profiled, "FAIL: totalPoints wasn't stripped from the already-profiled slot"
    assert parsed_profiled["ownedProfileId"] == "customprofile123", \
        f"FAIL: an existing ownedProfileId must never be overwritten by the backfill, got {parsed_profiled.get('ownedProfileId')!r}"
    print("PASS: totalPoints was stripped without touching an already-present ownedProfileId")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
