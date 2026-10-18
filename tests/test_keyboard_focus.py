# -*- coding: utf-8 -*-
# Keyboard focus survives Progression re-renders and stays inside modals.
# Progression rebuilt its rows with innerHTML and dropped focus to <body>
# after every action (167 Tabs back on a 30-step plan); Reset Build and
# Manage tracking neither took nor trapped focus; no modal was marked as a
# dialog.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"


def active_info(page):
    return page.evaluate("""() => {
        const a = document.activeElement;
        const row = a && a.closest('.progression-row');
        const modal = a && a.closest('.modal-overlay');
        return { tag: a ? a.tagName : null, id: a ? a.id : null, move: a ? a.getAttribute('data-move') : null,
                 rowKey: row ? row.getAttribute('data-key') : null, rowIndex: row ? row.getAttribute('data-index') : null,
                 modal: modal ? modal.id : null };
    }""")


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    for name in ("Adamant Will", "Combat Agility", "Fear Resistance", "Packrat", "Foraging"):
        page.locator("#treeWrap .node", has=page.locator(".name", has_text=name)).click()
        page.click("#incBtn")
    page.click('button[data-tab="progression"]')
    page.wait_for_selector(".progression-row")

    last = page.locator(".progression-row").last
    key = last.get_attribute("data-key")
    last.locator('.step-btn[data-move="up"]').focus()
    page.keyboard.press("Enter")
    page.wait_for_timeout(60)
    info = active_info(page)
    print("focus after moving the last row up:", info)
    assert info["rowKey"] == key and info["move"] == "up", f"FAIL: focus should stay on the moved row's up arrow: {info}"
    page.keyboard.press("Enter")
    page.wait_for_timeout(60)
    info = active_info(page)
    assert info["rowKey"] == key and info["rowIndex"] == "2", f"FAIL: a second Enter should move the same row again: {info}"
    print("PASS: focus follows the moved row, so repeated Enter keeps moving it")

    page.focus("#resetBtn")
    page.keyboard.press("Enter")
    page.wait_for_timeout(60)
    assert active_info(page)["modal"] == "resetModal", f"FAIL: Reset Build should take focus: {active_info(page)}"
    for _ in range(8):
        page.keyboard.press("Tab")
        assert active_info(page)["modal"] == "resetModal", f"FAIL: Tab left the open modal: {active_info(page)}"
    page.keyboard.press("Shift+Tab")
    assert active_info(page)["modal"] == "resetModal", "FAIL: Shift+Tab left the open modal"
    page.keyboard.press("Escape")
    page.wait_for_timeout(60)
    assert active_info(page)["id"] == "resetBtn", f"FAIL: closing should return focus to Reset Build: {active_info(page)}"
    print("PASS: a modal takes focus, keeps Tab inside, and returns focus on close")

    page.click('button[data-tab="progression"]')
    page.focus("#manageOwnedTrackingBtn")
    page.keyboard.press("Enter")
    page.wait_for_timeout(60)
    assert active_info(page)["modal"] == "ownedTrackingModal", f"FAIL: Manage tracking should take focus: {active_info(page)}"
    page.keyboard.press("Escape")

    unlabelled = page.evaluate("""() => Array.from(document.querySelectorAll('.modal-overlay > .modal'))
        .filter((m) => m.getAttribute('role') !== 'dialog' || m.getAttribute('aria-modal') !== 'true'
                       || !document.getElementById(m.getAttribute('aria-labelledby') || '_'))
        .map((m) => m.parentElement.id)""")
    assert not unlabelled, f"FAIL: modals without a labelled dialog role: {unlabelled}"
    print("PASS: every modal is a labelled aria-modal dialog")

    assert not errors, errors
    browser.close()
    print("ALL PASS")
