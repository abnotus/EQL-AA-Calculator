# -*- coding: utf-8 -*-
# A prereq on a sharedWithClass AA (Quick Evacuation, one investment listed
# under both Druid and Wizard) must hold whichever tab lowers it. The
# dependency check compared tab-relative identities, so a Druid AA
# requiring Quick Evacuation didn't stop it being lowered from Wizard's
# tab. No real AA requires Quick Evacuation yet, so this appends a
# synthetic Druid one to data.js.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wiki_guess_fixtures import read_data_js  # noqa: E402

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
SYNTHETIC = ('\nAA_DATA.classes.Druid.push({ name: "Synthetic Evac Dependent", ranks: 1, costs: ["1"], '
             'levelReq: "1", prereq: "Requires Quick Evacuation rank 1", description: "Test only." });\n')


def node(page, name):
    return page.locator("#treeWrap .node", has=page.locator(".name", has_text=name))


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.route("**/data.js*", lambda route: route.fulfill(body=read_data_js() + SYNTHETIC, content_type="application/javascript; charset=utf-8"))
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.select_option("#classSelect0", "Wizard")
    page.select_option("#classSelect1", "Druid")
    page.wait_for_timeout(80)

    page.click('button[data-tab="classSlot0"]')
    node(page, "Quick Evacuation").click()
    page.click("#incBtn")
    page.click('button[data-tab="classSlot1"]')
    node(page, "Synthetic Evac Dependent").click()
    page.click("#incBtn")
    assert "1 / 1" in node(page, "Synthetic Evac Dependent").inner_text(), "FAIL: setup should buy the dependent"

    page.click('button[data-tab="classSlot0"]')
    node(page, "Quick Evacuation").click()
    page.click("#decBtn")
    page.wait_for_timeout(60)
    rank = node(page, "Quick Evacuation").locator(".ranktext").inner_text()
    toast = page.locator("#toast").inner_text()
    print(f"Quick Evacuation after lowering it from Wizard's tab: {rank}, toast {toast!r}")
    assert rank == "1 / 3", "FAIL: a Druid AA requiring Quick Evacuation should stop it being lowered from Wizard's tab"
    assert "depends on" in toast, f"FAIL: unexpected toast {toast!r}"
    print("PASS: a prereq on a shared AA holds from either class's tab")

    assert not errors, errors
    browser.close()
    print("ALL PASS")
