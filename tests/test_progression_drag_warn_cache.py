# -*- coding: utf-8 -*-
# dragWouldIntroduceWarn (render.js) caches its answer per insertion point
# (toIndex) to avoid re-running computeProgressionSteps on every dragover
# event while the cursor sits over the same spot. The cache is keyed only on
# toIndex, which is safe *within* one drag - dragSrcIndex is fixed for the
# whole session - but a NEW drag can revisit the same toIndex with a
# different dragSrcIndex (or after real state has changed) and needs a
# different answer, which is why the dragstart handler resets the cache.
#
# No existing test performed two separate drags in one page session, so a
# missing reset here would pass every other test silently: the correct
# answer for toIndex=0 with one dragged AA is TRUE, and with a different one
# it's FALSE, and without the reset the second drag would just keep
# serving the first drag's cached TRUE.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"


def dispatch_dragstart(page, row_handle, dt_name):
    page.evaluate(
        f"""
        (rowEl) => {{
            window['{dt_name}'] = new DataTransfer();
            const dragstart = new DragEvent('dragstart', {{ bubbles: true, cancelable: true, dataTransfer: window['{dt_name}'] }});
            rowEl.dispatchEvent(dragstart);
        }}
        """,
        row_handle,
    )


def dispatch_dragover_top_half(page, row_handle, dt_name):
    page.evaluate(
        f"""
        (rowEl) => {{
            const rect = rowEl.getBoundingClientRect();
            const dragover = new DragEvent('dragover', {{ bubbles: true, cancelable: true, dataTransfer: window['{dt_name}'], clientX: rect.left + 10, clientY: rect.top + 2 }});
            rowEl.dispatchEvent(dragover);
        }}
        """,
        row_handle,
    )


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # --- Fear Resistance (general) to rank 3, then War Cry (Warrior,
    # "Requires Fear Resistance at level 3") to rank 1 - purchaseOrder ends
    # up [FR, FR, FR, War Cry], the same known-good prereq pair
    # test_cross_class_prereq_dependency.py already pins. ---
    page.select_option("#classSelect0", "Warrior")
    page.wait_for_timeout(100)
    page.click('button[data-tab="general"]')
    page.locator(".node", has=page.locator(".name", has_text="Fear Resistance")).click()
    for _ in range(3):
        page.click("#incBtn")
        page.wait_for_timeout(15)
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    page.locator(".node", has=page.locator(".name", has_text="War Cry")).click()
    page.click("#incBtn")
    page.wait_for_timeout(30)

    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(150)
    rows = page.locator(".progression-row")
    assert rows.count() == 4, f"FAIL: expected 4 Progression rows (3x Fear Resistance + War Cry), got {rows.count()}"
    row0 = rows.nth(0).element_handle()  # first Fear Resistance step
    row1 = rows.nth(1).element_handle()  # second Fear Resistance step
    row3 = rows.nth(3).element_handle()  # War Cry

    # --- Drag 1: drag War Cry (the AA with the prereq) to the very front
    # (toIndex 0) - it would then sit before any Fear Resistance rank is
    # trained, so this must warn. ---
    dispatch_dragstart(page, row3, "__aaDT1")
    dispatch_dragover_top_half(page, row0, "__aaDT1")
    page.wait_for_timeout(30)
    warned_1 = "drag-warn" in (rows.nth(0).get_attribute("class") or "")
    print("row0 drag-warn after dragging War Cry to the front (toIndex 0):", warned_1)
    assert warned_1, "FAIL: dragging War Cry ahead of its own Fear Resistance prereq should warn - can't test cache staleness if this baseline isn't even true"

    page.evaluate("(rowEl) => rowEl.dispatchEvent(new DragEvent('dragend', { bubbles: true }))", row3)
    page.wait_for_timeout(30)

    # --- Drag 2: a brand-new drag, dragging a plain Fear Resistance step
    # (no prereq of its own) to the SAME toIndex 0 - reordering which Fear
    # Resistance copy comes first never breaks War Cry's prereq (all 3 are
    # still trained), so this must NOT warn. If dragWarnCacheToIndex wasn't
    # reset at this dragstart, toIndex 0's answer from drag 1 (True) would
    # still be sitting in the cache and this would wrongly warn too. ---
    dispatch_dragstart(page, row1, "__aaDT2")
    dispatch_dragover_top_half(page, row0, "__aaDT2")
    page.wait_for_timeout(30)
    warned_2 = "drag-warn" in (rows.nth(0).get_attribute("class") or "")
    print("row0 drag-warn after a new drag of a plain Fear Resistance step to the same toIndex 0:", warned_2)
    assert not warned_2, "FAIL: a stale drag-warn cache from the previous drag leaked into this new drag at the same insertion point"
    print("PASS: a new drag recomputes its own answer instead of reusing the previous drag's cached one")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
