# -*- coding: utf-8 -*-
# changeRank always records a sharedWithClass purchase under its canonical
# identity (Druid, for Quick Evacuation) in purchaseOrder/lastMutation,
# even when bought from Wizard's own tab - see
# test_quick_evacuation_shared_rank.py. Progression's own row-active check
# and Undo Last both used to resolve that identity's class directly
# (Druid), so buying it with Wizard active and Druid NOT one of the 3
# selected classes showed the row as locked ("swap Druid back in to keep
# training this", add/remove/expand all disabled) and made Undo Last fail
# with "that class isn't currently selected" - both wrong, since the
# player can plainly see and edit it live on Wizard's own tab right there.
# logic.js's activeEntryTarget resolves through whichever linked class is
# actually active instead of only the canonical one.
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
    # Druid is NOT one of the 3 active classes.
    page.select_option("#classSelect0", "Wizard")
    page.select_option("#classSelect1", "Bard")
    page.select_option("#classSelect2", "Cleric")
    page.wait_for_timeout(120)

    page.click('button[data-tab="classSlot0"]')  # Wizard
    page.wait_for_timeout(80)
    qe = page.locator(".node", has=page.locator(".name", has_text="Quick Evacuation"))
    qe.click()
    page.click("#incBtn")
    page.wait_for_timeout(80)
    assert "1 / 3" in qe.inner_html(), "FAIL: buying from Wizard's tab should still work with Druid inactive"

    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(100)
    row = page.locator(".progression-row", has=page.locator(".step-name", has_text="Quick Evacuation"))
    row_classes = row.get_attribute("class")
    print("progression row classes:", row_classes)
    assert "inactive" not in row_classes, f"FAIL: row should be active (editable via Wizard's tab), got classes: {row_classes}"

    add_btn = row.locator(".step-add")
    remove_btn = row.locator(".step-remove")
    print("step-add disabled:", add_btn.get_attribute("disabled"))
    print("step-remove disabled:", remove_btn.get_attribute("disabled"))
    assert add_btn.get_attribute("disabled") is None, "FAIL: step-add should be enabled with Wizard active"
    assert remove_btn.get_attribute("disabled") is None, "FAIL: step-remove should be enabled with Wizard active"
    print("PASS: the Progression row is active and editable via Wizard's tab even with Druid inactive")

    # --- The +/- controls actually work (not just enabled). ---
    add_btn.click()
    page.wait_for_timeout(80)
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(80)
    assert "2 / 3" in qe.inner_html(), "FAIL: Progression's own + button should have bought another rank"
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(80)
    rows = page.locator(".progression-row", has=page.locator(".step-name", has_text="Quick Evacuation"))
    last_remove = rows.last.locator(".step-remove")
    last_remove.click()
    page.wait_for_timeout(80)
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(80)
    assert "1 / 3" in qe.inner_html(), "FAIL: Progression's own - button should have refunded a rank"
    print("PASS: Progression's +/- controls actually change the shared rank with Druid inactive")

    # --- Undo Last works too. ---
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(80)
    qe.click()
    page.click("#incBtn")
    page.wait_for_timeout(80)
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(100)
    undo_btn = page.locator("#undoLastBtn")
    assert undo_btn.get_attribute("disabled") is None, "FAIL: Undo Last should be enabled"
    undo_btn.click()
    page.wait_for_timeout(100)
    toast = page.locator("#toast").text_content()
    print("toast after Undo Last:", repr(toast))
    assert not toast or "n't undo" not in toast, f"FAIL: Undo Last should succeed, got: {toast!r}"
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(80)
    print("Wizard tab node after Undo Last:", qe.inner_html())
    assert "1 / 3" in qe.inner_html(), "FAIL: Undo Last should have reverted the rank back to 1/3"
    print("PASS: Undo Last works for a sharedWithClass AA bought while its canonical class is inactive")

    print("ERRORS:", errors)
    assert not errors, f"FAIL: page errors {errors}"
    browser.close()
    print("ALL PASS")
