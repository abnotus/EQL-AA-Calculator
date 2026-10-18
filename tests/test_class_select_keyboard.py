# -*- coding: utf-8 -*-
# ArrowDown on a closed class <select> fires change for every step. Each
# step used to be applied as a full duplicate-slot swap, so stepping Class 1
# from Bard past Beastlord and Berserker (held in slots 2 and 3) to Cleric
# ended at Cleric/Bard/Beastlord, swapping Berserker out. Swaps are now
# worked out against the selection from before the stepping began.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"


def classes(page):
    return [page.locator(f"#classSelect{i}").input_value() for i in range(3)]


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    assert classes(page) == ["Bard", "Beastlord", "Berserker"], classes(page)

    page.focus("#classSelect0")
    for _ in range(3):
        page.keyboard.press("ArrowDown")
        page.wait_for_timeout(40)
    print("after ArrowDown x3 on Class 1:", classes(page))
    assert page.locator("#classSelect0").input_value() == "Cleric", "FAIL: the keypresses didn't step the select"
    assert classes(page) == ["Cleric", "Beastlord", "Berserker"], f"FAIL: stepping cascaded swaps: {classes(page)}"
    print("PASS: stepping through classes swaps against the starting selection")

    # Once focus leaves, a new choice works against the current selection.
    page.locator("#classSelect0").blur()
    page.select_option("#classSelect0", "Beastlord")
    page.wait_for_timeout(60)
    print("after picking Beastlord for Class 1:", classes(page))
    assert classes(page) == ["Beastlord", "Cleric", "Berserker"], f"FAIL: a plain swap broke: {classes(page)}"
    print("PASS: a plain duplicate pick still swaps the two slots")

    assert not errors, errors
    browser.close()
    print("ALL PASS")
