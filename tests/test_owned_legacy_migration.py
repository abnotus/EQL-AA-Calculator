# -*- coding: utf-8 -*-
# state.js's migrateLegacyOwnedProfile() copies the old single-global
# eql_aa_owned_v1 key's content into the well-known "legacy" owned profile
# (eql_aa_owned_legacy) on boot, and builds.js's migrateStaleBuildSlots()
# backfills every existing build slot's missing ownedProfileId to that same
# profile - together, the "don't break anything old" half of the per-build
# owned-progress-tracking feature. This seeds a realistic pre-migration
# localStorage shape (the legacy owned key populated, an existing build
# slot with no ownedProfileId field at all, no current-session save yet)
# and confirms every existing build still shows exactly the same owned
# data after boot, with zero visible change from before per-build tracking
# existed.
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

LEGACY_OWNED = {"v": 4, "owned": {"general": {"adamant-will": 2}, "archetype": {}, "special": {}, "classes": {}}}
OLD_SLOT_PAYLOAD = {
    "v": 4,
    "selectedClasses": ["Bard", "Beastlord", "Berserker"],
    "charLevel": 42,
    "ranks": {"general": {"adamant-will": 2}, "archetype": {}, "special": {}, "classes": {}},
    "purchaseOrder": [
        {"scope": "general", "className": None, "key": "adamant-will"},
        {"scope": "general", "className": None, "key": "adamant-will"},
    ],
    "waypoints": [],
}
INDEX_PAYLOAD = [{"id": "premigslot", "name": "Pre-Migration Build", "updatedAt": 1000}]

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())

    page.add_init_script(f"""
        localStorage.setItem('eql_aa_owned_v1', {json.dumps(json.dumps(LEGACY_OWNED))});
        localStorage.setItem('eql_aa_builds_index_v1', {json.dumps(json.dumps(INDEX_PAYLOAD))});
        localStorage.setItem('eql_aa_build_premigslot', {json.dumps(json.dumps(OLD_SLOT_PAYLOAD))});
    """)
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)

    # --- The legacy key's content is now also reachable under the
    # well-known "legacy" profile id. ---
    legacy_profile = page.evaluate("localStorage.getItem('eql_aa_owned_legacy')")
    print("eql_aa_owned_legacy after boot:", legacy_profile)
    assert legacy_profile is not None
    assert json.loads(legacy_profile) == LEGACY_OWNED
    print("PASS: the legacy owned key's content was copied to the shared legacy profile")

    # --- The old legacy key itself is untouched, not deleted. ---
    still_there = page.evaluate("localStorage.getItem('eql_aa_owned_v1')")
    assert still_there is not None and json.loads(still_there) == LEGACY_OWNED
    print("PASS: the legacy owned key itself was left in place, not deleted")

    # --- The current session (no local save existed before this boot)
    # shows the migrated owned data immediately - checked via Clear Owned's
    # enabled state (hasAnyOwned()), since nothing was purchased on this
    # session's own (empty) plan to look at in Progression directly. ---
    clear_owned_btn = page.locator("#clearOwnedBtn")
    print("Clear Owned enabled (legacy owned data present):", clear_owned_btn.get_attribute("disabled") is None)
    assert clear_owned_btn.get_attribute("disabled") is None, "FAIL: migrated legacy owned data should make Clear Owned active"
    print("PASS: the current session shows the migrated owned data")

    # Force a save of the current session (an unrelated field change) so its
    # own ownedProfileId can be inspected directly in storage.
    page.fill("#levelInput", "45")
    page.locator("#levelInput").press("Tab")
    page.wait_for_timeout(100)
    build_storage = json.loads(page.evaluate("localStorage.getItem('eql_aa_builder_v1')"))
    print("current session ownedProfileId after boot:", build_storage.get("ownedProfileId"))
    assert build_storage.get("ownedProfileId") == "legacy"
    print("PASS: the current session defaulted to the shared legacy profile")

    # --- The pre-existing build slot was backfilled to point at the same
    # legacy profile - loading it later will show the identical owned data,
    # no visible change from how it behaved before per-build tracking. ---
    slot_after = json.loads(page.evaluate("localStorage.getItem('eql_aa_build_premigslot')"))
    print("pre-migration slot after boot:", slot_after)
    assert slot_after.get("ownedProfileId") == "legacy"
    print("PASS: the pre-existing build slot was backfilled to the shared legacy profile")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
