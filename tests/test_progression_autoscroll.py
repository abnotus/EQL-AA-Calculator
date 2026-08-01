# -*- coding: utf-8 -*-
# Progression's drag-to-reorder auto-scroll (dragging near the top/bottom
# edge of #progressionWrap scrolls it, faster near the edge - see
# updateAutoScroll/autoScrollStep in render.js) is driven by a self-
# sustaining requestAnimationFrame loop that normally stops via a
# document-level "dragend" listener. But dragend is known to not always
# fire on a detached source node - this codebase already special-cased that
# for dragSrcIndex (MIME-gating dragover/drop against a stale value) after
# hitting it for real. A successful drop mutates state and calls
# renderProgression(), which replaces progressionContent's innerHTML and
# detaches the very row dragstart fired on - exactly that case. Some
# browsers (Firefox historically) don't fire dragend on a source node
# that's already gone by the time the drag would end, so every drop handler
# also calls stopAutoScroll() directly rather than relying on dragend alone.
#
# Playwright can't drive a real OS-level HTML5 drag, so this simulates the
# lifecycle by dispatching dragstart/dragover/drop DragEvents directly (each
# carrying a real DataTransfer, matching what render.js reads) and
# deliberately never dispatches dragend - reproducing the exact detached-
# source gap. Without the drop-handler stopAutoScroll() calls, the wrap
# keeps scrolling after the drop using its last-known direction/speed
# forever; with them, scrollTop goes stable within a couple of frames.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
# Same live fixture as test_estimated_total.py (Paladin/Monk/Shaman,
# Packrat rank 10, 235 points across plenty of AAs plus a couple of
# waypoints) - reused here purely for its row count, not its guess/estimate
# content or waypoints.
BUILD = "H4sIAAAAAAAACn2QTWoDMQyF76L1W9iS_-IbZNETGC-GZAgDaRKG0C5K714kz5Csij_zJPMky_6hL6oMOlFtB2R46aAr1ehAK9XWEqSjZYSOVixmbwkLvFNN8CoZpaOJt0yCWSUOGU3kYBKc1YdgzujsMPIQQVIZPb3eoeoypHfQg6o6I4MTorzB4LwR3SvmDCv2u88hb6tookOwIKbdqTvZKijQUXf0EQb7F_qkQdiJGyz_0EHf-rvBgY635blMVwLd1-l2mUl_2oE-lvNl-pwJtM5n6v33D8iR4qKsAQAA"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    # Short viewport so this build's rows overflow #progressionWrap without
    # needing an even bigger fixture just for this test.
    page = browser.new_page(viewport={"width": 1400, "height": 500})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.goto(f"{BASE}?build={BUILD}")
    page.wait_for_selector("#treeWrap .node")
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(150)

    wrap = page.locator("#progressionWrap")
    wrap_handle = wrap.element_handle()
    scroll_height, client_height = wrap.evaluate("el => [el.scrollHeight, el.clientHeight]")
    print("progressionWrap scrollHeight/clientHeight:", scroll_height, client_height)
    assert scroll_height > client_height + 100, \
        "FAIL: fixture doesn't overflow the wrap enough for this test to mean anything"

    # Start scrolled to the middle so both up- and down-scroll have room to
    # move - a stuck-at-the-limit false pass is impossible either way.
    page.evaluate(
        "el => { el.scrollTop = Math.floor((el.scrollHeight - el.clientHeight) / 2); }",
        wrap_handle,
    )
    mid_scroll = wrap.evaluate("el => el.scrollTop")
    print("scrollTop after seeking to the middle:", mid_scroll)

    rows = page.locator(".progression-row")
    row_count = rows.count()
    assert row_count >= 5, "FAIL: fixture doesn't have enough rows for a meaningful drag"
    src_row = rows.nth(row_count - 1).element_handle()
    target_row = rows.nth(0).element_handle()

    # dragstart on a real row (sets dragSrcIndex + the PROGRESSION_DRAG_TYPE
    # MIME data), then dragover right at the wrap's own top edge (inside
    # AUTOSCROLL_EDGE_PX) to kick the auto-scroll loop off.
    page.evaluate(
        """
        ([srcRow, wrapEl]) => {
            window.__aaTestDT = new DataTransfer();
            const dragstart = new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: window.__aaTestDT });
            srcRow.dispatchEvent(dragstart);
            const rect = wrapEl.getBoundingClientRect();
            const dragover = new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: window.__aaTestDT, clientX: rect.left + 20, clientY: rect.top + 5 });
            wrapEl.dispatchEvent(dragover);
        }
        """,
        [src_row, wrap_handle],
    )
    page.wait_for_timeout(150)
    scrolling_scroll = wrap.evaluate("el => el.scrollTop")
    print("scrollTop after dragover at the top edge (should have scrolled up):", scrolling_scroll)
    assert scrolling_scroll < mid_scroll, \
        "FAIL: auto-scroll never kicked in - can't test its cleanup if it didn't start"

    # Drop directly on another row (a valid, MIME-gated drop target) WITHOUT
    # ever dispatching dragend - the exact detached-source gap. The drop
    # handler mutates state and re-renders, tearing the original row out
    # from under any pending dragend.
    page.evaluate(
        """
        ([targetRow]) => {
            const rect = targetRow.getBoundingClientRect();
            const drop = new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: window.__aaTestDT, clientX: rect.left + 20, clientY: rect.top + 5 });
            targetRow.dispatchEvent(drop);
        }
        """,
        [target_row],
    )
    page.wait_for_timeout(80)
    after_drop = wrap.evaluate("el => el.scrollTop")
    page.wait_for_timeout(300)
    settled = wrap.evaluate("el => el.scrollTop")
    print("scrollTop right after drop:", after_drop, "| after waiting another 300ms with no more dragover:", settled)
    assert settled == after_drop, (
        f"FAIL: auto-scroll kept running after a drop that never fired dragend "
        f"(scrollTop drifted from {after_drop} to {settled}) - stopAutoScroll() "
        f"is missing from (or not reached by) the drop handler"
    )
    print("PASS: dropping without a dragend still stops the auto-scroll loop (belt-and-braces stopAutoScroll() in the drop handlers)")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
