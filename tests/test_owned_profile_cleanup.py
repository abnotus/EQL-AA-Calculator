# -*- coding: utf-8 -*-
# Owned profiles are minted freely - every brand-new Save As, every Split,
# every owned-carrying import mints its own (state.js) - but nothing ever
# un-mints one when the build(s) pointing at it are deleted or re-linked
# elsewhere, so they'd otherwise accumulate in localStorage forever.
# builds.js's cleanupOrphanedOwnedProfiles(), called once per boot from
# main.js alongside cleanupStaleStorageKeys, sweeps any eql_aa_owned_<id>
# profile that nothing references anymore: not the live session's own
# state.ownedProfileId, and not any saved build slot's own ownedProfileId -
# including a slot that isn't currently loaded, since it's still reachable
# via Load. The permanent legacy profile is never swept even if nothing
# currently references it (removeOwnedProfile, state.js, refuses on its
# own regardless of what a caller passes it).
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

EMPTY_OWNED = {"v": 4, "owned": {"general": {}, "archetype": {}, "special": {}, "classes": {}}}

CURRENT_SESSION_PAYLOAD = {
    "v": 4,
    "selectedClasses": ["Bard", "Beastlord", "Berserker"],
    "charLevel": 50,
    "ranks": {"general": {}, "archetype": {}, "special": {}, "classes": {}},
    "purchaseOrder": [],
    "waypoints": [],
    "ownedProfileId": "profileA",
}
SLOT_A_PAYLOAD = dict(CURRENT_SESSION_PAYLOAD)  # same profile as the live session
SLOT_B_PAYLOAD = {**CURRENT_SESSION_PAYLOAD, "ownedProfileId": "profileB"}  # a DIFFERENT, not-currently-loaded profile
INDEX_PAYLOAD = [
    {"id": "slotA", "name": "Slot A", "updatedAt": 1000},
    {"id": "slotB", "name": "Slot B", "updatedAt": 2000},
]

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())

    page.add_init_script(f"""
        localStorage.setItem('eql_aa_builder_v1', {json.dumps(json.dumps(CURRENT_SESSION_PAYLOAD))});
        localStorage.setItem('eql_aa_builds_index_v1', {json.dumps(json.dumps(INDEX_PAYLOAD))});
        localStorage.setItem('eql_aa_build_slotA', {json.dumps(json.dumps(SLOT_A_PAYLOAD))});
        localStorage.setItem('eql_aa_build_slotB', {json.dumps(json.dumps(SLOT_B_PAYLOAD))});
        localStorage.setItem('eql_aa_owned_profileA', {json.dumps(json.dumps(EMPTY_OWNED))});
        localStorage.setItem('eql_aa_owned_profileB', {json.dumps(json.dumps(EMPTY_OWNED))});
        localStorage.setItem('eql_aa_owned_legacy', {json.dumps(json.dumps(EMPTY_OWNED))});
        localStorage.setItem('eql_aa_owned_orphan123', {json.dumps(json.dumps(EMPTY_OWNED))});
    """)
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)

    orphan_after = page.evaluate("localStorage.getItem('eql_aa_owned_orphan123')")
    print("orphaned profile after boot (should be gone):", orphan_after)
    assert orphan_after is None, "FAIL: a profile with no build slot or live session pointing at it should be swept"
    print("PASS: a genuinely unreferenced profile was removed")

    profile_a_after = page.evaluate("localStorage.getItem('eql_aa_owned_profileA')")
    print("profileA after boot (referenced by the live session and Slot A):", profile_a_after is not None)
    assert profile_a_after is not None, "FAIL: a profile referenced by the live session must survive"

    profile_b_after = page.evaluate("localStorage.getItem('eql_aa_owned_profileB')")
    print("profileB after boot (referenced only by Slot B, not currently loaded):", profile_b_after is not None)
    assert profile_b_after is not None, \
        "FAIL: a profile referenced only by a saved-but-not-loaded build slot must survive - it's still reachable via Load"
    print("PASS: profiles referenced by any build slot survive, loaded or not")

    legacy_after = page.evaluate("localStorage.getItem('eql_aa_owned_legacy')")
    print("legacy profile after boot (unreferenced by anything, must still survive):", legacy_after is not None)
    assert legacy_after is not None, "FAIL: the permanent legacy profile must never be swept, referenced or not"
    print("PASS: the legacy profile is protected even when nothing currently references it")

    # --- The original source key itself must never be mistaken for an
    # orphaned profile either, even though its "_v1" suffix sits under the
    # same eql_aa_owned_ prefix every real profile id does. ---
    page.evaluate("localStorage.setItem('eql_aa_owned_v1', JSON.stringify(" + json.dumps(json.dumps(EMPTY_OWNED)) + "))")
    page.reload()
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)
    legacy_source_after = page.evaluate("localStorage.getItem('eql_aa_owned_v1')")
    print("legacy source key (eql_aa_owned_v1) after a second boot:", legacy_source_after is not None)
    assert legacy_source_after is not None, "FAIL: the raw legacy source key must never be swept as if its '_v1' suffix were a profile id"
    print("PASS: the legacy source key survives a sweep too")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
