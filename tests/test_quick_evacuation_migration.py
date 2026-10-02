# -*- coding: utf-8 -*-
# Quick Evacuation's rank/owned state always reads and writes through
# Druid's own copy now (logic.js's sharedCanonical - see
# test_quick_evacuation_shared_rank.py), but a save made before that
# redirect existed could have the value under EITHER class's own store,
# since each was tracked completely independently back then. state.js's
# migrateSharedQuickEvacuation moves a value found under Wizard's store
# into Druid's before deserialization runs. Without it, the value becomes
# invisible (sharedCanonical only ever reads Druid's slot) while still
# being summed by code that walks a class's own raw store directly
# (spentForClass/spentPoints in logic.js) - the topbar total silently
# counts points nothing on screen shows as spent, and gets WORSE (not just
# wrong) the moment the player buys another rank from Druid's tab, since
# now both the real purchase and the orphaned leftover both count.
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

WIZARD_ONLY_SAVE = {
    "v": 4,
    "selectedClasses": ["Druid", "Wizard", "Cleric"],
    "charLevel": 50,
    "ranks": {"general": {}, "archetype": {}, "special": {}, "classes": {"Wizard": {"quick-evacuation": 2}}},
    "purchaseOrder": [
        {"scope": "class", "className": "Wizard", "key": "quick-evacuation"},
        {"scope": "class", "className": "Wizard", "key": "quick-evacuation"},
    ],
    "waypoints": [],
}

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())

    page.add_init_script(f"""
        localStorage.setItem('eql_aa_builder_v1', {json.dumps(json.dumps(WIZARD_ONLY_SAVE))});
    """)
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)

    toast = page.locator("#toast").text_content()
    print("toast after boot:", repr(toast))
    assert not toast or "no longer exist" not in toast, f"FAIL: migrated rank was reported as dropped: {toast!r}"

    # --- The rank shows up on Druid's own tab (the canonical copy), even
    # though the save only ever had it under Wizard's store. ---
    page.click('button[data-tab="classSlot0"]')  # Druid
    page.wait_for_timeout(100)
    druid_html = page.locator(".node", has=page.locator(".name", has_text="Quick Evacuation")).inner_html()
    print("Druid tab node after boot:", druid_html)
    assert "2 / 3" in druid_html, f"FAIL: expected the migrated rank 2/3 on Druid's own tab, got: {druid_html}"

    # --- The topbar total reflects exactly the one real rank-2 investment
    # (9 points: 3+6), not a double-counted 18 from an orphaned Wizard
    # store sitting alongside it. ---
    spent = page.locator("#spentValue").text_content()
    print("spentValue (topbar) after boot:", repr(spent))
    assert "9" in spent and "18" not in spent, f"FAIL: expected spent total of 9 (not double-counted), got: {spent!r}"

    # --- Buying the 3rd rank from Druid's tab brings the real total to 18
    # (3+6+9) - still just once, not stacked on top of a leftover 9. ---
    page.locator(".node", has=page.locator(".name", has_text="Quick Evacuation")).click()
    page.click("#incBtn")
    page.wait_for_timeout(100)
    spent_after = page.locator("#spentValue").text_content()
    print("spentValue (topbar) after buying rank 3:", repr(spent_after))
    assert "18" in spent_after, f"FAIL: expected spent total of 18 after maxing it out, got: {spent_after!r}"
    assert "27" not in spent_after, f"FAIL: total still shows signs of double-counting: {spent_after!r}"

    print("ERRORS:", errors)
    assert not errors, f"FAIL: page errors {errors}"
    browser.close()
    print("ALL PASS")
