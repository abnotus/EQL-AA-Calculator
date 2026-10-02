# -*- coding: utf-8 -*-
# "Merge In" (state.js's mergeOwnedProfileInto, the Manage Owned Tracking
# modal's union of another build's owned progress into the current one -
# see test_owned_profiles.py for the feature's own general coverage) reads
# the source profile's raw owned object straight into deserializeRanks
# without running it through migrateSharedQuickEvacuation first. A source
# profile saved before that redirect existed could hold Quick Evacuation's
# owned rank under Wizard's own store - merging it in without the
# migration lands it as a SEPARATE Wizard-keyed entry alongside whatever
# Druid's canonical copy already has, instead of raising Druid's own value
# the way every other AA's merge correctly does. The current profile's own
# display (which only ever reads Druid's slot) never reflects the merged-in
# rank, while ownedPoints() - which walks every class's raw store directly -
# still counts the orphaned entry, inflating the total.
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

CURRENT_SESSION = {
    "v": 4,
    "selectedClasses": ["Druid", "Wizard", "Cleric"],
    "charLevel": 50,
    "ranks": {"general": {}, "archetype": {}, "special": {}, "classes": {}},
    "purchaseOrder": [],
    "waypoints": [],
    "ownedProfileId": "legacy",
}
CURRENT_OWNED = {"v": 4, "owned": {"general": {}, "archetype": {}, "special": {}, "classes": {"Druid": {"quick-evacuation": 1}}}}
BUILD_B = {
    "v": 4, "selectedClasses": ["Druid", "Wizard", "Cleric"], "charLevel": 50,
    "ranks": {"general": {}, "archetype": {}, "special": {}, "classes": {}},
    "purchaseOrder": [], "waypoints": [], "ownedProfileId": "wizprofile",
}
WIZ_OWNED = {"v": 4, "owned": {"general": {}, "archetype": {}, "special": {}, "classes": {"Wizard": {"quick-evacuation": 2}}}}
BUILDS_INDEX = [{"id": "buildb", "name": "Build B", "updatedAt": 1000}]

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())

    page.add_init_script(f"""
        localStorage.setItem('eql_aa_builder_v1', {json.dumps(json.dumps(CURRENT_SESSION))});
        localStorage.setItem('eql_aa_owned_legacy', {json.dumps(json.dumps(CURRENT_OWNED))});
        localStorage.setItem('eql_aa_builds_index_v1', {json.dumps(json.dumps(BUILDS_INDEX))});
        localStorage.setItem('eql_aa_build_buildb', {json.dumps(json.dumps(BUILD_B))});
        localStorage.setItem('eql_aa_owned_wizprofile', {json.dumps(json.dumps(WIZ_OWNED))});
    """)
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)

    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(100)
    before = page.locator("#ownedSummary").inner_text()
    print("owned summary before merge:", before)
    assert before.startswith("3 "), f"FAIL: expected 3 pts owned (Druid's rank 1) before any merge, got {before!r}"

    # --- Merge Build B (Wizard-side owned rank 2) into the current profile. ---
    page.click("#manageOwnedTrackingBtn")
    page.wait_for_timeout(100)
    page.select_option("#ownedTrackingBuildSelect", label="Build B")
    page.click("#ownedTrackingMergeBtn")
    page.wait_for_timeout(150)
    page.click("#closeOwnedTrackingBtn")
    page.wait_for_timeout(80)

    after = page.locator("#ownedSummary").inner_text()
    print("owned summary after merge:", after)
    assert after.startswith("9 "), f"FAIL: expected 9 pts owned (rank 2, raised from Druid's rank 1) after merging in Wizard's rank 2, got {after!r}"

    # --- Druid's own tab (the canonical copy) reflects the raised rank. ---
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    node = page.locator(".node", has=page.locator(".name", has_text="Quick Evacuation"))
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(80)
    row = page.locator(".progression-row", has=page.locator(".step-name", has_text="Quick Evacuation"))
    # No row exists yet (nothing's been purchased, only owned) - check via
    # the raw merged storage instead, same as the live reproduction did.
    raw_owned = json.loads(page.evaluate("localStorage.getItem('eql_aa_owned_legacy')"))
    print("current profile's raw owned data after merge:", raw_owned)
    assert raw_owned["owned"]["classes"].get("Druid", {}).get("quick-evacuation") == 2, \
        f"FAIL: expected Druid's canonical owned rank raised to 2, got {raw_owned}"
    assert "quick-evacuation" not in raw_owned["owned"]["classes"].get("Wizard", {}), \
        f"FAIL: expected no orphaned Wizard entry after the merge, got {raw_owned}"
    print("PASS: merging a Wizard-side owned rank raises Druid's canonical copy instead of adding a separate entry")

    print("ERRORS:", errors)
    assert not errors, f"FAIL: page errors {errors}"
    browser.close()
    print("ALL PASS")
