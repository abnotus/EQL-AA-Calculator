# -*- coding: utf-8 -*-
# Every import gets its own fresh owned profile, empty when the code
# carries no owned data. Before, a link without owned data kept the live
# profile, which after an earlier link was that friend's: friend B's build
# showed friend A's marks, and un-owning one on B removed it from A.
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
EMPTY = {"general": {}, "archetype": {}, "special": {}, "classes": {}}
CA = {"scope": "general", "className": None, "key": "combat-agility"}
PAYLOAD = {"v": 4, "selectedClasses": ["Bard", "Beastlord", "Berserker"], "charLevel": 50,
           "ranks": {**EMPTY, "general": {"combat-agility": 2}}, "purchaseOrder": [CA, CA], "waypoints": []}


def share_code(browser, owned):
    page = browser.new_page()
    page.add_init_script(
        f"localStorage.setItem('eql_aa_builder_v1', {json.dumps(json.dumps(PAYLOAD))});"
        f"localStorage.setItem('eql_aa_owned_legacy', {json.dumps(json.dumps({'v': 4, 'owned': owned}))});"
    )
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.click("#exportBtn")
    page.wait_for_function("document.querySelector('#shareLinkInput').value.includes('build=')")
    url = page.locator("#shareLinkInput").input_value()
    page.close()
    return url.split("?build=")[1]


def owned_summary(page):
    page.click('button[data-tab="progression"]')
    page.wait_for_selector(".progression-row")
    return page.locator("#ownedSummary").inner_text()


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    code_a = share_code(browser, {**EMPTY, "general": {"combat-agility": 2}})
    code_b = share_code(browser, EMPTY)

    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept("Friend A") if d.type == "prompt" else d.accept())

    page.goto(f"{BASE}?build={code_a}")
    page.wait_for_selector("#treeWrap .node")
    print("after friend A's link:", owned_summary(page))
    assert owned_summary(page).startswith("6 pts owned"), "FAIL: friend A's owned marks should load"
    page.click("#buildsBtn")
    page.locator(".build-row", has=page.locator(".build-name", has_text="Imported Build")).locator('[data-action="rename"]').click()
    page.click("#closeBuildsBtn")

    page.goto(f"{BASE}?build={code_b}")
    page.wait_for_selector("#treeWrap .node")
    after_b = owned_summary(page)
    print("after friend B's link (no owned data):", after_b)
    assert after_b == "0 pts owned, 6 to go", f"FAIL: friend B's build should start with nothing owned, got {after_b!r}"

    page.click("#buildsBtn")
    page.locator(".build-row", has=page.locator(".build-name", has_text="Friend A")).locator('[data-action="load"]').click()
    page.wait_for_timeout(120)
    if page.locator("#buildsModal").is_visible():
        page.click("#closeBuildsBtn")
    back_a = owned_summary(page)
    print("Friend A loaded again:", back_a)
    assert back_a.startswith("6 pts owned"), f"FAIL: Friend A's owned progress should be untouched, got {back_a!r}"
    assert not errors, errors
    print("PASS: an import without owned data starts on its own empty profile")
    browser.close()
    print("ALL PASS")
