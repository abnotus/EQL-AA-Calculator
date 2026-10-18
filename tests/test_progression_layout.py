# -*- coding: utf-8 -*-
# Progression layout: the Move To popover on a ⚠ row sits above later
# rows. The ⚠ dimming once put opacity on .step-controls, which made it a
# stacking context, so a click on the popover landed on the next row's
# buttons instead.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"


def buy(page, tab, name, times=1):
    page.click(f'button[data-tab="{tab}"]')
    page.locator("#treeWrap .node", has=page.locator(".name", has_text=name)).first.click()
    for _ in range(times):
        page.click("#incBtn")
    page.wait_for_timeout(60)


def step_names(page):
    return page.locator(".progression-row .step-name").all_inner_texts()


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)

    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # Thief's Intuition is Bard/Rogue only, so swapping Bard out warns its rows.
    buy(page, "archetype", "Thief's Intuition", 2)
    buy(page, "general", "Combat Agility")
    page.select_option("#classSelect0", "Cleric")
    page.wait_for_timeout(80)
    page.click('button[data-tab="progression"]')
    page.wait_for_selector(".progression-row")
    before = step_names(page)
    print("steps before:", before)
    assert page.locator(".progression-row").nth(0).get_attribute("class").count("prereq-warn-row") == 1, \
        "FAIL: setup should leave the first row warned"

    page.locator(".progression-row").nth(0).locator(".step-move").click()
    item = page.locator(".move-menu-item", has_text="Bottom of list")
    box = item.bounding_box()
    hit_in_menu = page.evaluate(
        "([x, y]) => !!document.elementFromPoint(x, y).closest('.move-menu')",
        [box["x"] + box["width"] / 2, box["y"] + box["height"] / 2],
    )
    assert hit_in_menu, "FAIL: the Move To item is covered by a later row's controls"
    item.click()
    page.wait_for_timeout(80)
    after = step_names(page)
    print("steps after Bottom of list:", after)
    assert len(after) == len(before), "FAIL: the click removed a rank instead of moving the row"
    assert after[1].startswith("Combat Agility"), f"FAIL: the row didn't move to the bottom: {after}"
    print("PASS: the Move To popover on a warned row receives its own clicks")
    page.close()

    assert not errors, errors
    browser.close()
    print("ALL PASS")
