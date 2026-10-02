# -*- coding: utf-8 -*-
# A plain wiki rename (the AA itself unchanged, just its name/slug) leaves
# a v4+ (name-keyed) save's old slug resolving to nothing - unlike
# aaIds.js's numeric ids (which keep a rename's id stable for the
# share-code format), there was nothing playing the same role for
# localStorage's own name-keyed ranks/purchaseOrder/owned, so a save made
# before Berserker's Tireless Spirit -> Tireless Sprint rename dropped its
# rank on next load, reported the same as a genuine removal. keys.js's
# RENAMED_KEYS/idxForKey fixes this generically - add an entry there in
# the same commit as any future rename, same append-only spirit as
# aaIds.js.
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

OLD_NAME_SAVE = {
    "v": 4,
    "selectedClasses": ["Berserker", "Bard", "Cleric"],
    "charLevel": 50,
    "ranks": {"general": {}, "archetype": {}, "special": {}, "classes": {"Berserker": {"tireless-spirit": 1}}},
    "purchaseOrder": [
        {"scope": "class", "className": "Berserker", "key": "tireless-spirit"},
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
        localStorage.setItem('eql_aa_builder_v1', {json.dumps(json.dumps(OLD_NAME_SAVE))});
    """)
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)

    toast = page.locator("#toast").text_content()
    print("toast after boot:", repr(toast))
    assert not toast or "no longer exist" not in toast, f"FAIL: renamed AA's rank was reported as dropped: {toast!r}"

    page.click('button[data-tab="classSlot0"]')  # Berserker
    page.wait_for_timeout(100)
    node = page.locator(".node", has=page.locator(".name", has_text="Tireless Sprint"))
    assert node.count() == 1, "FAIL: expected exactly one Tireless Sprint node"
    html = node.inner_html()
    print("Tireless Sprint node:", html)
    assert "1 / 1" in html, f"FAIL: expected the pre-rename save's rank 1/1 to survive under the new name, got: {html}"

    # --- Progression carries the purchase through too, not just the tree. ---
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(100)
    rows = page.locator(".progression-row", has=page.locator(".step-name", has_text="Tireless Sprint"))
    assert rows.count() == 1, f"FAIL: expected 1 Progression row for the migrated purchase, got {rows.count()}"

    print("ERRORS:", errors)
    assert not errors, f"FAIL: page errors {errors}"
    browser.close()
    print("ALL PASS")
