# -*- coding: utf-8 -*-
# Link, Merge and Split change which owned profile is live without going
# through setOwnedRank, so they must clear the pending Undo Last. Otherwise
# Undo replays an owned edit made under the old profile into the newly
# linked one, rewriting another build's progress.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"


def progression(page):
    page.click('button[data-tab="progression"]')
    page.wait_for_selector(".progression-row")


def toggle_first_owned(page):
    progression(page)
    page.locator(".progression-row .step-own").first.click()
    page.wait_for_timeout(80)


def save_build_as(page, name):
    page.click("#buildsBtn")
    page.fill("#buildSaveName", name)
    page.click("#buildSaveBtn")
    page.wait_for_timeout(80)
    page.click("#closeBuildsBtn")


def load_build(page, name):
    page.click("#buildsBtn")
    row = page.locator(".build-row", has=page.locator(".build-name", has_text=name))
    row.locator('[data-action="load"]').click()
    page.wait_for_timeout(120)
    if page.locator("#buildsModal").is_visible():
        page.click("#closeBuildsBtn")


def tracking_action(page, build_name, button_id):
    progression(page)
    page.click("#manageOwnedTrackingBtn")
    page.select_option("#ownedTrackingBuildSelect", label=build_name)
    page.click(button_id)
    page.wait_for_timeout(100)
    page.click("#closeOwnedTrackingBtn")


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    for label, button_id in (("Link", "#ownedTrackingLinkBtn"), ("Merge", "#ownedTrackingMergeBtn")):
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("dialog", lambda d: d.accept())
        page.goto(BASE)
        page.wait_for_selector("#treeWrap .node")

        page.locator("#treeWrap .node").first.click()
        page.click("#incBtn")
        toggle_first_owned(page)
        save_build_as(page, "B")
        owned_b = page.locator("#ownedSummary").inner_text()

        # A forks B's profile, then unmarks and re-marks the AA, leaving an
        # owned edit (0 -> 1) as the pending Undo.
        save_build_as(page, "A")
        toggle_first_owned(page)
        toggle_first_owned(page)
        assert not page.locator("#undoLastBtn").is_disabled(), "FAIL: setup should leave an owned edit to undo"

        tracking_action(page, "B", button_id)
        assert page.locator("#undoLastBtn").is_disabled(), f"FAIL: {label} should clear the pending Undo"
        page.locator("#undoLastBtn").click(force=True)
        page.wait_for_timeout(80)

        load_build(page, "B")
        progression(page)
        owned_after = page.locator("#ownedSummary").inner_text()
        print(f"{label}: B owned before {owned_b!r}, after Undo {owned_after!r}")
        assert owned_after == owned_b, f"FAIL: Undo after {label} changed build B's owned progress"
        assert not errors, errors
        print(f"PASS: {label} clears Undo Last, so it can't rewrite the other build's progress")
        page.close()
    browser.close()
    print("ALL PASS")
