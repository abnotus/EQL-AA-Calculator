# -*- coding: utf-8 -*-
# A Progression row dragged in from another tab carries this app's custom
# drag type, but this tab never saw its dragstart, so dragSrcIndex is null.
# The drop handlers used to trust it anyway, and splice(null, 1) moved the
# first step. A drop now needs both the type and a drag started here.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    for name in ("Adamant Will", "Combat Agility", "Fear Resistance"):
        page.locator("#treeWrap .node", has=page.locator(".name", has_text=name)).click()
        page.click("#incBtn")
    page.click('button[data-tab="progression"]')
    page.wait_for_selector(".progression-row")
    before = page.locator(".progression-row .step-name").all_inner_texts()

    page.evaluate("""() => {
        const rows = document.querySelectorAll('.progression-row');
        const target = rows[rows.length - 1];
        const rect = target.getBoundingClientRect();
        const dt = new DataTransfer();
        dt.setData('application/x-aacalc-progression-step', '0');
        const opts = { bubbles: true, cancelable: true, dataTransfer: dt,
                       clientX: rect.left + 20, clientY: rect.bottom - 2 };
        target.dispatchEvent(new DragEvent('dragover', opts));
        target.dispatchEvent(new DragEvent('drop', opts));
    }""")
    page.wait_for_timeout(80)
    after = page.locator(".progression-row .step-name").all_inner_texts()
    print("before:", before)
    print("after a foreign drop:", after)
    assert after == before, "FAIL: a drop from another tab reordered the list"
    assert not errors, errors
    print("PASS: a drop with no drag started in this tab changes nothing")
    browser.close()
    print("ALL PASS")
