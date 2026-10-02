# -*- coding: utf-8 -*-
# Quick Evacuation used to be two separate per-class data.src.js entries
# (Druid, Wizard) that turned out to be the same shared investment in-game
# the whole time - confirmed by a real character's own log, which only
# ever shows one set of purchases for it regardless of which of the two
# classes is active. data.src.js now has a single archetype entry
# (eligibleClasses: Druid/Wizard) instead, same precedent as Exodus.
#
# A save made before that merge has its rank/purchaseOrder entries filed
# under classes.Druid or classes.Wizard's own "quick-evacuation" key, which
# no longer resolves to anything post-merge - state.js's
# migrateQuickEvacuationRanks/migrateQuickEvacuationPurchaseOrder rewrite
# that onto the new archetype key before deserialization ever runs, so nothing
# is silently dropped as "no longer exists". This seeds a realistic
# pre-merge save (Druid's quick-evacuation at rank 2, two matching
# purchaseOrder entries) and confirms it survives boot intact.
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

OLD_SHAPED_SAVE = {
    "v": 4,
    "selectedClasses": ["Druid", "Wizard", "Cleric"],
    "charLevel": 50,
    "ranks": {"general": {}, "archetype": {}, "special": {}, "classes": {"Druid": {"quick-evacuation": 2}}},
    "purchaseOrder": [
        {"scope": "class", "className": "Druid", "key": "quick-evacuation"},
        {"scope": "class", "className": "Druid", "key": "quick-evacuation"},
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
        localStorage.setItem('eql_aa_builder_v1', {json.dumps(json.dumps(OLD_SHAPED_SAVE))});
    """)
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)

    # --- No "no longer exist" load-time notice - the old class-scoped rank
    # was migrated, not dropped. ---
    toast_text = page.locator("#toast").text_content()
    print("toast after boot:", repr(toast_text))
    assert not toast_text or "no longer exist" not in toast_text, f"FAIL: migrated rank was reported as dropped: {toast_text!r}"
    print("PASS: no dropped-pick notice on boot")

    # --- Both purchases survived, now under the shared archetype slot - two
    # Progression rows, not zero. ---
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(100)
    rows = page.locator(".progression-row", has=page.locator(".step-name", has_text="Quick Evacuation"))
    print("Quick Evacuation progression rows:", rows.count())
    assert rows.count() == 2, f"FAIL: expected both purchases to survive as 2 rows, got {rows.count()}"
    print("PASS: both purchases survived the merge as Progression rows")

    # --- The Archetype tab (not Druid's own tab - there's no per-class
    # entry left to look at) shows it at rank 2. ---
    page.click('button[data-tab="archetype"]')
    page.wait_for_timeout(100)
    node = page.locator(".node", has=page.locator(".name", has_text="Quick Evacuation"))
    node_html = node.inner_html()
    print("Archetype tab node html:", node_html)
    assert "2/3" in node_html or "2 /" in node_html or ">2<" in node_html, f"FAIL: expected rank 2 to show on the Archetype tab's node, got: {node_html}"

    # --- Force a save (an unrelated field edit) and confirm the rewritten
    # shape is what actually lands in storage, not just in memory. ---
    page.fill("#levelInput", "49")
    page.locator("#levelInput").press("Tab")
    page.wait_for_timeout(100)
    saved = json.loads(page.evaluate("localStorage.getItem('eql_aa_builder_v1')"))
    print("saved ranks after boot+save:", saved.get("ranks"))
    print("saved purchaseOrder after boot+save:", saved.get("purchaseOrder"))
    assert saved["ranks"]["archetype"].get("quick-evacuation") == 2, "FAIL: expected the merged rank under archetype in storage"
    assert "quick-evacuation" not in saved["ranks"]["classes"].get("Druid", {}), "FAIL: the old per-class key should no longer be present"
    qe_entries = [e for e in saved["purchaseOrder"] if e.get("key") == "quick-evacuation"]
    assert len(qe_entries) == 2 and all(e.get("scope") == "archetype" for e in qe_entries), \
        f"FAIL: expected both purchaseOrder entries repointed at scope archetype, got {qe_entries}"
    print("PASS: the persisted save reflects the migrated archetype shape")

    print("ERRORS:", errors)
    assert not errors, f"FAIL: page errors {errors}"
    browser.close()
    print("ALL PASS")
