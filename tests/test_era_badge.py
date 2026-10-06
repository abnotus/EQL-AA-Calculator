# -*- coding: utf-8 -*-
# Expansion-era badge (Kunark/Velious): the optional `era` field (see
# logic.js's eraBadge) must render its small colored-letter marker
# everywhere a plain AA's own name/icon appears - the Tree node's icon
# corner, and the Browse/Summary card name line - and must render NOTHING
# for every ordinary AA that has no `era` field, which today is all 144 of
# them (Kunark/Velious don't exist yet).
#
# Fabricated on two already-established stable, player-log-verified hosts
# (Rapid Feign/Monk, Baking Mastery/general - see wiki_guess_fixtures.py
# and test_manual_guess.py's own header for the full rationale) rather
# than any real Kunark/Velious AA, since none exists yet to pin to. Only
# data.js needs patching here (just the `era` field, their real costs/
# description stay as-is) - no guess-table involved, so app.js is left
# untouched.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
from wiki_guess_fixtures import read_data_js, replace_object_literal

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

FROZEN_RAPID_FEIGN = '{name:"Rapid Feign",ranks:3,costs:["3","6","9"],levelReq:"17",description:"Reduces the reuse time of your Feign Death skill by 1/3/5 second(s).",era:"kunark"}'
FROZEN_BAKING_MASTERY = '{name:"Baking Mastery",ranks:3,costs:["2","4","6"],levelReq:"1",description:"Reduces the chance of failing Baking recipes by 10/25/50%.",era:"velious"}'


def patched_data_js():
    src = replace_object_literal(read_data_js(), '{name:"Rapid Feign"', FROZEN_RAPID_FEIGN)
    src = replace_object_literal(src, '{name:"Baking Mastery"', FROZEN_BAKING_MASTERY)
    return src


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.route("**/data.js*", lambda route: route.fulfill(body=patched_data_js(), content_type="application/javascript; charset=utf-8"))

    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # --- Tree: Baking Mastery (general, always visible regardless of
    # class selection) shows Velious's badge on its icon's own corner;
    # nothing else in that tab does. ---
    page.click('button[data-tab="general"]')
    bm_node = page.locator(".node", has=page.locator(".name", has_text="Baking Mastery"))
    bm_badge = bm_node.locator(".icon .era-badge")
    print("Baking Mastery tree badge:", bm_badge.inner_text(), bm_badge.get_attribute("class"))
    assert bm_badge.inner_text() == "V"
    assert "era-velious" in bm_badge.get_attribute("class")
    assert page.locator("#treeWrap .node .era-badge").count() == 1, "FAIL: expected exactly one era badge in the general tab"
    print("PASS: Tree node shows Velious's badge for Baking Mastery, nothing else in the tab")

    # --- Tree: Rapid Feign (Monk - not a default slot, selected
    # explicitly) shows Kunark's badge the same way. ---
    page.select_option("#classSelect0", "Monk")
    page.click('button[data-tab="classSlot0"]')
    rf_node = page.locator(".node", has=page.locator(".name", has_text="Rapid Feign"))
    rf_badge = rf_node.locator(".icon .era-badge")
    print("Rapid Feign tree badge:", rf_badge.inner_text(), rf_badge.get_attribute("class"))
    assert rf_badge.inner_text() == "K"
    assert "era-kunark" in rf_badge.get_attribute("class")
    assert page.locator("#treeWrap .node .era-badge").count() == 1, "FAIL: expected exactly one era badge in Monk's tab"
    print("PASS: Tree node shows Kunark's badge for Rapid Feign, nothing else in the tab")

    # --- Browse: same two badges, inline next to the name instead of on
    # an icon - and a plain real AA (Combat Fury - every AA today) shows
    # none at all. ---
    page.click("#browseToggle")
    page.fill("#globalSearch", "Rapid Feign")
    page.wait_for_timeout(250)
    rf_card = page.locator("#browseGrid .browse-card", has=page.locator(".name", has_text="Rapid Feign"))
    rf_card_badge = rf_card.locator(".name .era-badge")
    print("Rapid Feign browse badge:", rf_card_badge.inner_text(), rf_card_badge.get_attribute("class"))
    assert rf_card_badge.inner_text() == "K" and "era-kunark" in rf_card_badge.get_attribute("class")

    page.fill("#globalSearch", "Baking Mastery")
    page.wait_for_timeout(250)
    bm_card = page.locator("#browseGrid .browse-card", has=page.locator(".name", has_text="Baking Mastery"))
    bm_card_badge = bm_card.locator(".name .era-badge")
    print("Baking Mastery browse badge:", bm_card_badge.inner_text(), bm_card_badge.get_attribute("class"))
    assert bm_card_badge.inner_text() == "V" and "era-velious" in bm_card_badge.get_attribute("class")

    page.fill("#globalSearch", "Combat Fury")
    page.wait_for_timeout(250)
    cf_card = page.locator("#browseGrid .browse-card", has=page.locator(".name", has_text="Combat Fury"))
    assert cf_card.locator(".era-badge").count() == 0, "FAIL: a plain real AA must never show an era badge"
    page.fill("#globalSearch", "")
    page.click("#browseToggle")
    print("PASS: Browse cards show the same two badges inline, and a plain AA shows none")

    # --- Summary: a picked AA's card gets the same badge too (the exact
    # markup is shared with Browse's card - see render.js's renderSummary);
    # an ordinary picked AA with no era still shows none. Not separately
    # driven for Other Classes' own section here - that markup is
    # byte-identical to Summary's (render.js's otherClassesSectionsHtml),
    # added in the same edit as this one. ---
    page.click('button[data-tab="classSlot0"]')
    rf_node.click()
    page.click("#incBtn")
    page.wait_for_timeout(30)
    page.click('button[data-tab="general"]')
    cf_node = page.locator(".node", has=page.locator(".name", has_text="Combat Fury"))
    cf_node.click()
    page.click("#incBtn")
    page.wait_for_timeout(30)

    page.click('button[data-tab="summary"]')
    summary_rf_badge = page.locator("#summaryContent .browse-card .name .era-badge")
    print("Rapid Feign summary badge:", summary_rf_badge.inner_text(), summary_rf_badge.get_attribute("class"))
    assert summary_rf_badge.inner_text() == "K" and "era-kunark" in summary_rf_badge.get_attribute("class")
    summary_cf_card = page.locator("#summaryContent .browse-card", has=page.locator(".name", has_text="Combat Fury"))
    assert summary_cf_card.locator(".era-badge").count() == 0, "FAIL: a plain picked AA must never show an era badge in Summary either"
    print("PASS: Summary's card shows the same badge for a picked era AA, none for a plain one")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
