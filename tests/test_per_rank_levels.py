# -*- coding: utf-8 -*-
# Per-rank level requirements written into a description ("Rank 2 requires
# level 30, rank 3 requires level 50") gate each rank, for bought AAs and
# auto-granted ones alike. They used to be ignored: Turn Summoned's rank 2
# (level 59, above the cap) could be bought at 50, and the 15 auto
# "Unbound" AAs showed max rank from their first unlock level.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"


def set_level(page, level):
    page.fill("#levelInput", str(level))
    page.press("#levelInput", "Enter")
    page.locator("#levelInput").blur()
    page.wait_for_timeout(60)


def node(page, name):
    return page.locator("#treeWrap .node", has=page.locator(".name", has_text=name))


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.select_option("#classSelect0", "Magician")
    page.select_option("#classSelect1", "Berserker")
    page.wait_for_timeout(80)

    page.click('button[data-tab="classSlot1"]')
    for level, want in ((11, "0 / 3"), (20, "1 / 3"), (30, "2 / 3"), (50, "3 / 3")):
        set_level(page, level)
        got = node(page, "Unbound Fury").locator(".ranktext").inner_text()
        print(f"Unbound Fury at level {level}: {got}")
        assert got == want, f"FAIL: at level {level} expected {want}, got {got}"
    set_level(page, 20)
    node(page, "Unbound Fury").click()
    panel = page.locator("#sidePanel").inner_text()
    assert "Rank 2 comes at level 30" in panel, f"FAIL: side panel should name the next rank's level: {panel!r}"
    assert "doesn't document per-rank level" not in panel, "FAIL: the 'no breakpoints' note contradicts the description"
    print("PASS: an auto AA gains each rank at its own level")

    set_level(page, 50)
    page.click('button[data-tab="classSlot0"]')
    node(page, "Turn Summoned").click()
    page.click("#incBtn")
    page.click("#incBtn")
    page.wait_for_timeout(60)
    got = node(page, "Turn Summoned").locator(".ranktext").inner_text()
    toast = page.locator("#toast").inner_text()
    print(f"Turn Summoned after two clicks at level 50: {got}, toast {toast!r}")
    assert got == "1 / 3", f"FAIL: rank 2 needs level 59, so only rank 1 should be bought, got {got}"
    assert "Rank 2 requires character level 59" in toast, f"FAIL: unexpected toast {toast!r}"
    print("PASS: a bought AA's later rank is gated by its own level")

    assert not errors, errors
    browser.close()
    print("ALL PASS")
