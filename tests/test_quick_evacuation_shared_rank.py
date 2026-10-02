# -*- coding: utf-8 -*-
# Quick Evacuation is one shared investment that the game itself still
# displays on both Druid's and Wizard's own AA page - confirmed by a real
# character's own log, which only ever shows one set of purchases for it
# regardless of which of the two classes was active. data.src.js keeps two
# ordinary class-scoped entries (one per class, so each displays exactly
# where the game shows it, each with its own id for the share-code format),
# but Wizard's copy carries a `sharedWithClass: "Druid"` field - logic.js's
# sharedCanonical redirects every rank/owned/hidden read and write for it to
# Druid's own copy, so the two always agree no matter which tab is used to
# train it. An AA was briefly modeled as a single shared "archetype" entry
# instead (trading the real in-game display for a simpler storage model);
# that showed it under a dedicated Archetype tab the game never uses for it,
# which is exactly what this test's tab-selector assertions below guard
# against regressing back to.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())

    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.select_option("#classSelect0", "Druid")
    page.select_option("#classSelect1", "Wizard")
    page.wait_for_timeout(120)

    # --- No "Archetype" tab regression: Quick Evacuation shows on Druid's
    # own tab, not a shared category tab. ---
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(80)
    druid_qe = page.locator(".node", has=page.locator(".name", has_text="Quick Evacuation"))
    assert druid_qe.count() == 1, "FAIL: expected exactly one Quick Evacuation node on Druid's own tab"
    print("PASS: Quick Evacuation shows on Druid's own class tab")

    # --- Buy two ranks from Druid's tab. ---
    druid_qe.click()
    page.click("#incBtn")
    page.click("#incBtn")
    page.wait_for_timeout(80)
    druid_html = druid_qe.inner_html()
    print("Druid tab node after buying 2 ranks:", druid_html)
    assert "2 / 3" in druid_html, f"FAIL: expected Druid's own node to show rank 2/3, got: {druid_html}"

    # --- Switch to Wizard's tab - same shared investment, same rank, no
    # Archetype tab involved. ---
    page.click('button[data-tab="classSlot1"]')
    page.wait_for_timeout(80)
    wizard_qe = page.locator(".node", has=page.locator(".name", has_text="Quick Evacuation"))
    assert wizard_qe.count() == 1, "FAIL: expected exactly one Quick Evacuation node on Wizard's own tab"
    wizard_html = wizard_qe.inner_html()
    print("Wizard tab node (should already show rank 2):", wizard_html)
    assert "2 / 3" in wizard_html, f"FAIL: Wizard's copy should already show the shared rank bought from Druid's tab, got: {wizard_html}"
    print("PASS: buying from Druid's tab immediately shows up on Wizard's tab too")

    # --- Buy the 3rd rank from Wizard's tab this time. ---
    wizard_qe.click()
    page.click("#incBtn")
    page.wait_for_timeout(80)
    wizard_html = wizard_qe.inner_html()
    assert "3 / 3" in wizard_html, f"FAIL: expected rank 3/3 after buying from Wizard's tab, got: {wizard_html}"

    # --- Druid's tab reflects the rank bought from Wizard's tab too. ---
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(80)
    druid_html = druid_qe.inner_html()
    print("Druid tab node after buying rank 3 from Wizard's tab:", druid_html)
    assert "3 / 3" in druid_html, f"FAIL: expected Druid's copy to reflect the rank bought from Wizard's tab, got: {druid_html}"
    print("PASS: buying from Wizard's tab immediately shows up on Druid's tab too")

    # --- Progression shows exactly 3 rows total for it, one per real
    # purchase - not 6 (a split identity would double them), not showing
    # under an "Archetype" grouping. ---
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(100)
    rows = page.locator(".progression-row", has=page.locator(".step-name", has_text="Quick Evacuation"))
    print("Quick Evacuation progression rows:", rows.count())
    assert rows.count() == 3, f"FAIL: expected 3 progression rows (one shared investment, 3 ranks), got {rows.count()}"

    # --- Decrementing from whichever tab is active removes a rank from the
    # one shared pool - buying from Wizard's tab, refunding from Druid's,
    # must not desync the two copies. ---
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(80)
    druid_qe.click()
    page.click("#decBtn")
    page.wait_for_timeout(80)
    druid_html = druid_qe.inner_html()
    assert "2 / 3" in druid_html, f"FAIL: expected rank 2/3 after refunding from Druid's tab, got: {druid_html}"
    page.click('button[data-tab="classSlot1"]')
    page.wait_for_timeout(80)
    wizard_html = wizard_qe.inner_html()
    print("Wizard tab node after refunding from Druid's tab:", wizard_html)
    assert "2 / 3" in wizard_html, f"FAIL: expected Wizard's copy to follow the refund made from Druid's tab, got: {wizard_html}"
    print("PASS: a refund from either tab keeps both copies in sync")

    print("ERRORS:", errors)
    assert not errors, f"FAIL: page errors {errors}"
    browser.close()
    print("ALL PASS")
