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

    # --- A malformed classes.Wizard store (not an object at all) must not
    # crash - the `in` operator (used to check for a "quick-evacuation"
    # entry before migrating it) throws on a non-object right-hand side. ---
    browser2 = p.chromium.launch(channel="chrome", headless=True)
    page2 = browser2.new_page(viewport={"width": 1400, "height": 900})
    errors2 = []
    page2.on("pageerror", lambda exc: errors2.append(str(exc)))
    page2.on("dialog", lambda d: d.accept())
    bad_wizard_store = {"v": 4, "owned": {"general": {}, "archetype": {}, "special": {}, "classes": {"Wizard": "bad"}}}
    page2.add_init_script(f"""
        localStorage.setItem('eql_aa_owned_legacy', {json.dumps(json.dumps(bad_wizard_store))});
    """)
    page2.goto(BASE)
    page2.wait_for_timeout(300)
    tree_count = page2.locator("#treeWrap .node").count()
    print(f"malformed Wizard store case: tree node count={tree_count}, errors={errors2}")
    assert not errors2, f"FAIL: a malformed classes.Wizard store threw instead of degrading gracefully: {errors2}"
    assert tree_count > 0, "FAIL: tree never rendered - boot froze on a malformed classes.Wizard store"
    print("PASS: a non-object classes.Wizard store no longer crashes startup")
    browser2.close()

    # --- A malformed classes.Druid store (not an object), alongside a
    # VALID Wizard entry, must not crash either - assigning a property to
    # a primitive (Druid: true) throws in strict mode - and the valid
    # Wizard rank should still survive via the recovered Druid store. ---
    browser3 = p.chromium.launch(channel="chrome", headless=True)
    page3 = browser3.new_page(viewport={"width": 1400, "height": 900})
    errors3 = []
    page3.on("pageerror", lambda exc: errors3.append(str(exc)))
    page3.on("dialog", lambda d: d.accept())
    bad_druid_store = {
        "v": 4,
        "owned": {"general": {}, "archetype": {}, "special": {}, "classes": {"Druid": True, "Wizard": {"quick-evacuation": 2}}}
    }
    page3.add_init_script(f"""
        localStorage.setItem('eql_aa_owned_legacy', {json.dumps(json.dumps(bad_druid_store))});
    """)
    page3.goto(BASE)
    page3.wait_for_timeout(300)
    tree_count3 = page3.locator("#treeWrap .node").count()
    print(f"malformed Druid store case: tree node count={tree_count3}, errors={errors3}")
    assert not errors3, f"FAIL: a malformed classes.Druid store threw instead of degrading gracefully: {errors3}"
    assert tree_count3 > 0, "FAIL: tree never rendered - boot froze on a malformed classes.Druid store"
    page3.click('button[data-tab="progression"]')
    page3.wait_for_timeout(100)
    owned_summary = page3.locator("#ownedSummary").inner_text()
    print("owned summary after recovering from a malformed Druid store:", owned_summary)
    assert owned_summary.startswith("9 "), \
        f"FAIL: expected the valid Wizard rank 2 (9 pts) to still migrate into a recovered Druid store, got {owned_summary!r}"
    print("PASS: a non-object classes.Druid store is replaced rather than crashing, and a valid Wizard entry alongside it still migrates")
    browser3.close()
    print("ALL PASS")
