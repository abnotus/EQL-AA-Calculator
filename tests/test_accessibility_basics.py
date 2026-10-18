# -*- coding: utf-8 -*-
# Keyboard and screen-reader basics: a waypoint can be edited by keyboard
# from its chip or its Progression divider (neither was focusable), the
# toast is announced (no role or aria-live), Progression's row buttons have
# names rather than only glyphs, and Char Level shows the clamped level
# after Enter (it kept showing "99" while 50 was used).
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

    page.fill("#levelInput", "99")
    page.press("#levelInput", "Enter")
    shown = page.locator("#levelInput").input_value()
    print("Char Level shown after entering 99:", shown)
    assert shown == "50", f"FAIL: the field should show the clamped level, got {shown!r}"
    print("PASS: Char Level shows the clamped value after Enter")

    page.locator("#treeWrap .node", has=page.locator(".name", has_text="Combat Agility")).click()
    page.click("#incBtn")
    page.click('button[data-tab="progression"]')
    page.click("#addWaypointBtn")
    page.fill("#waypointPtsInput", "1")
    page.click("#saveWaypointBtn")

    page.locator(".waypoint-chip .chip-label").focus()
    page.keyboard.press("Enter")
    assert page.locator("#waypointModal").is_visible(), "FAIL: Enter on a waypoint chip should open its editor"
    page.keyboard.press("Escape")
    page.locator(".progression-divider").first.focus()
    assert page.evaluate("document.activeElement.classList.contains('progression-divider')"), "FAIL: a divider can't take focus"
    page.keyboard.press("Enter")
    assert page.locator("#waypointModal").is_visible(), "FAIL: Enter on a divider should open its editor"
    page.keyboard.press("Escape")
    print("PASS: a waypoint can be edited by keyboard from its chip and its divider")

    unnamed = page.evaluate("""() => Array.from(document.querySelectorAll('.progression-row .step-btn'))
        .filter((b) => !b.getAttribute('aria-label')).map((b) => b.outerHTML.slice(0, 60))""")
    assert not unnamed, f"FAIL: row buttons without a name: {unnamed}"
    toast = page.evaluate("[document.getElementById('toast').getAttribute('role'), document.getElementById('toast').getAttribute('aria-live')]")
    assert toast == ["status", "polite"], f"FAIL: the toast isn't announced: {toast}"
    print("PASS: row buttons are named and the toast is a polite status")

    assert not errors, errors
    browser.close()
    print("ALL PASS")
