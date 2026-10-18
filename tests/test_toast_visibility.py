# -*- coding: utf-8 -*-
# The toast is the only feedback for several modal actions (a failed
# Import, Save in Builds, Link/Merge/Split), but it sat under the modal
# overlay (z-index 50 against 100), was squeezed to half the screen, and
# vanished after a fixed 2.2 s however long the message was.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 740, "height": 360})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    page.click("#importBtn")
    page.fill("#importText", "this is not a build code at all")
    page.click("#doImportBtn")
    page.wait_for_selector("#toast.show")
    z = page.evaluate("""() => [getComputedStyle(document.getElementById('toast')).zIndex,
                                getComputedStyle(document.getElementById('importModal')).zIndex].map(Number)""")
    print("toast z-index vs modal overlay:", z)
    assert z[0] > z[1], f"FAIL: the toast renders under the open modal: {z}"
    print("PASS: the toast shows above an open modal")

    page.click("#closeImportBtn")
    page.evaluate("""() => document.getElementById('toast').textContent = ''""")
    long_msg = "x" * 200
    page.evaluate("""(m) => {
        const t = document.getElementById('toast');
        t.textContent = m;
    }""", long_msg)
    box = page.locator("#toast").bounding_box()
    print(f"long toast: {box['width']:.0f}px wide in a 740px viewport")
    assert box["width"] > 370, "FAIL: a long toast is squeezed to half the screen"
    assert box["x"] >= 0 and box["x"] + box["width"] <= 740, "FAIL: a long toast runs off screen"
    print("PASS: a long toast uses the screen width without overflowing it")

    page.click("#importBtn")
    page.fill("#importText", "still not a build code")
    page.click("#doImportBtn")
    page.wait_for_selector("#toast.show")
    page.wait_for_timeout(2600)
    assert page.locator("#toast.show").count() == 1, "FAIL: the toast vanished after the old fixed 2.2 s"
    print("PASS: a toast stays up longer than 2.2 s when it has more to say")

    assert not errors, errors
    browser.close()
    print("ALL PASS")
