# -*- coding: utf-8 -*-
# Browse's "Unowned Only" toggle (#browseUnownedToggle, state.browseUnownedOnly)
# and the owned/unowned differentiation every Browse card gets regardless of
# that toggle (a green border/tint plus an "Owned: N/R" line once ownedRank
# is above 0) - added once a build's owned count got large enough that
# scanning Browse for what's still missing became worth a dedicated filter.
# Combines with the existing category filter/search rather than replacing
# them, same as any other Browse filter dimension.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # --- Own two General AAs (Adamant Will to rank 1 of 4, Alchemy Mastery
    # to rank 1 of 3) via Progression's own-toggle, leaving the rest of
    # General unowned. ---
    page.click('button[data-tab="general"]')
    for name in ["Adamant Will", "Alchemy Mastery"]:
        page.locator(".node", has=page.locator(".name", has_text=name)).first.click()
        page.click("#incBtn")
        page.wait_for_timeout(50)
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(150)
    for i in range(2):
        page.locator(".progression-row").nth(i).locator(".step-own").click()
        page.wait_for_timeout(50)

    page.click("#browseToggle")
    page.select_option("#browseFilter", "general")
    page.wait_for_timeout(150)

    # --- Default view: both owned cards are styled and labeled, unowned
    # ones aren't. ---
    total_general = page.locator(".browse-card").count()
    owned_cards = page.locator(".browse-card.owned")
    print("General cards total:", total_general, "owned:", owned_cards.count())
    assert owned_cards.count() == 2, f"FAIL: expected 2 owned cards, got {owned_cards.count()}"

    adamant_card = page.locator(".browse-card", has=page.locator(".name", has_text="Adamant Will"))
    alchemy_card = page.locator(".browse-card", has=page.locator(".name", has_text="Alchemy Mastery"))
    baking_card = page.locator(".browse-card", has=page.locator(".name", has_text="Baking Mastery"))
    assert "owned" in adamant_card.get_attribute("class")
    assert adamant_card.locator(".owned-info").inner_text() == "Owned: 1/4"
    assert "owned" in alchemy_card.get_attribute("class")
    assert alchemy_card.locator(".owned-info").inner_text() == "Owned: 1/3"
    assert "owned" not in (baking_card.get_attribute("class") or "").split()
    assert baking_card.locator(".owned-info").count() == 0
    print("PASS: owned cards are styled and show their exact owned rank; unowned cards show neither")

    # --- Unowned Only hides both owned cards, keeps the toggle visibly
    # active, and combines with the existing category filter (still just
    # General). ---
    toggle = page.locator("#browseUnownedToggle")
    toggle.click()
    page.wait_for_timeout(150)
    assert "active" in toggle.get_attribute("class")
    remaining = page.locator(".browse-card").count()
    print("General cards after Unowned Only:", remaining, "(was", total_general, ")")
    assert remaining == total_general - 2, \
        f"FAIL: expected exactly the 2 owned cards removed, got {total_general - remaining} fewer"
    assert page.locator(".browse-card.owned").count() == 0
    assert page.locator(".browse-card", has=page.locator(".name", has_text="Adamant Will")).count() == 0
    assert page.locator(".browse-card", has=page.locator(".name", has_text="Baking Mastery")).count() == 1
    print("PASS: Unowned Only hides every owned card and nothing else, staying scoped to the active category filter")

    # --- Toggling off restores exactly the owned cards that were hidden. ---
    toggle.click()
    page.wait_for_timeout(150)
    assert "active" not in (toggle.get_attribute("class") or "")
    restored = page.locator(".browse-card").count()
    print("General cards after toggling off:", restored)
    assert restored == total_general
    print("PASS: toggling off restores the owned cards")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
