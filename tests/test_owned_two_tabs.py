# -*- coding: utf-8 -*-
# Two tabs open on the app share localStorage (two pages in one Playwright
# context do too, storage events included). Two ways that corrupted owned
# tracking:
# 1. The active build id was one shared value, so after tab 2 loaded or
#    saved another build, tab 1's Split repointed tab 2's slot instead of
#    its own.
# 2. Owned profiles were rewritten whole from memory, so a mark made in a
#    stale tab erased marks the other tab had made on the same profile.
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"


def open_tab(ctx, errors):
    page = ctx.new_page()
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    return page


def buy(page, name):
    page.click('button[data-tab="general"]')
    page.locator("#treeWrap .node", has=page.locator(".name", has_text=name)).click()
    page.click("#incBtn")
    page.wait_for_timeout(40)


def toggle_owned(page, name):
    page.click('button[data-tab="progression"]')
    row = page.locator(".progression-row", has=page.locator(".step-name", has_text=name))
    row.locator(".step-own").click()
    page.wait_for_timeout(60)


def save_build_as(page, name):
    page.click("#buildsBtn")
    page.fill("#buildSaveName", name)
    page.click("#buildSaveBtn")
    page.wait_for_timeout(60)
    page.click("#closeBuildsBtn")


def slot_profile(page, name):
    return page.evaluate("""(name) => {
        const index = JSON.parse(localStorage.getItem('eql_aa_builds_index_v1') || '[]');
        const entry = index.find((b) => b.name === name);
        return JSON.parse(localStorage.getItem('eql_aa_build_' + entry.id)).ownedProfileId;
    }""", name)


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    errors = []

    # --- 1. Split in tab 1 repoints tab 1's own slot. ---
    ctx = browser.new_context(viewport={"width": 1400, "height": 900})
    tab1 = open_tab(ctx, errors)
    buy(tab1, "Combat Agility")
    save_build_as(tab1, "Main")
    tab2 = open_tab(ctx, errors)
    save_build_as(tab2, "Other")
    other_before = slot_profile(tab1, "Other")
    main_before = slot_profile(tab1, "Main")

    tab1.click('button[data-tab="progression"]')
    tab1.click("#manageOwnedTrackingBtn")
    tab1.click("#ownedTrackingSplitBtn")
    tab1.wait_for_timeout(80)
    tab1.click("#closeOwnedTrackingBtn")
    other_after = slot_profile(tab1, "Other")
    main_after = slot_profile(tab1, "Main")
    print(f"Other: {other_before} -> {other_after}; Main: {main_before} -> {main_after}")
    assert other_after == other_before, "FAIL: tab 1's Split repointed the build tab 2 is on"
    assert main_after != main_before, "FAIL: tab 1's Split should repoint its own build, Main"
    print("PASS: each tab's Split repoints its own active build")
    ctx.close()

    # --- 2. Marks made in two tabs on the same profile both survive. ---
    ctx = browser.new_context(viewport={"width": 1400, "height": 900})
    tab1 = open_tab(ctx, errors)
    buy(tab1, "Combat Agility")
    buy(tab1, "Fear Resistance")
    tab2 = open_tab(ctx, errors)
    toggle_owned(tab1, "Combat Agility")
    toggle_owned(tab2, "Fear Resistance")
    tab3 = open_tab(ctx, errors)
    tab3.click('button[data-tab="progression"]')
    owned = tab3.locator(".progression-row .step-name.owned").all_inner_texts()
    print("owned after one mark in each tab:", owned)
    assert len(owned) == 2, f"FAIL: a mark from one tab was lost: {owned}"
    tab1.click('button[data-tab="progression"]')
    tab1.wait_for_timeout(60)
    assert tab1.locator(".progression-row .step-name.owned").count() == 2, \
        "FAIL: tab 1 should pick up tab 2's mark"
    print("PASS: marks made in two tabs on one profile are both kept, and both tabs show them")
    ctx.close()

    assert not errors, errors
    browser.close()
    print("ALL PASS")
