# -*- coding: utf-8 -*-
# Browse's "Unowned Only" toggle (#browseUnownedToggle, state.browseUnownedOnly)
# and the owned/unowned differentiation every Browse card gets regardless of
# that toggle (a green border/tint plus an "Owned: N/R" line once ownedRank
# is above 0) - added once a build's owned count got large enough that
# scanning Browse for what's still missing became worth a dedicated filter.
# Combines with the existing category filter/search rather than replacing
# them, same as any other Browse filter dimension.
#
# Auto-granted AAs (aa.auto) never go through owned-tracking - they're never
# a Progression step, so there's nothing to mark owned - which leaves
# ownedRank permanently 0 for them. Unowned Only excludes them too, or every
# auto AA would sit in that list forever despite needing no action at all.
#
# A partial-auto AA (aa.autoRanks, e.g. Symphonic Aura's free rank 1 of 5)
# needs the same floor respected on its owned watermark, not just its rank
# store: marking its one purchasable step owned then unmarking it must drop
# owned back to 0, not the free-rank floor, or it reads as "owned" here
# despite nothing purchased.
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
    # ones aren't. auto_count is read here (not hardcoded) since which/how
    # many General AAs are auto-granted is wiki data, not this test's concern. ---
    total_general = page.locator(".browse-card").count()
    owned_cards = page.locator(".browse-card.owned")
    auto_count = page.locator(".browse-card .auto-badge").count()
    print("General cards total:", total_general, "owned:", owned_cards.count(), "auto:", auto_count)
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
    expected = total_general - 2 - auto_count
    print("General cards after Unowned Only:", remaining, "(was", total_general, ", expected", expected, ")")
    assert remaining == expected, \
        f"FAIL: expected the 2 owned cards plus {auto_count} auto card(s) removed ({expected} left), got {remaining}"
    assert page.locator(".browse-card.owned").count() == 0
    assert page.locator(".browse-card", has=page.locator(".name", has_text="Adamant Will")).count() == 0
    assert page.locator(".browse-card", has=page.locator(".name", has_text="Baking Mastery")).count() == 1
    print("PASS: Unowned Only hides every owned card and nothing else, staying scoped to the active category filter")

    # --- Auto-granted General AAs (never owned-tracked - see header comment)
    # are excluded too, not left sitting in the list forever. ---
    for auto_name in ["Full Potential", "Gather Party", "Origin"]:
        count = page.locator(".browse-card", has=page.locator(".name", has_text=auto_name)).count()
        print(f"{auto_name} (auto) present under Unowned Only:", count)
        assert count == 0, f"FAIL: auto-granted {auto_name} should be excluded from Unowned Only, never just 'still unowned'"
    print("PASS: auto-granted AAs are excluded from Unowned Only")

    # --- Toggling off restores exactly the owned cards that were hidden. ---
    toggle.click()
    page.wait_for_timeout(150)
    assert "active" not in (toggle.get_attribute("class") or "")
    restored = page.locator(".browse-card").count()
    print("General cards after toggling off:", restored)
    assert restored == total_general
    print("PASS: toggling off restores the owned cards")

    # --- Regression: an autoRanks AA's free floor must not read as "owned".
    # Symphonic Aura (Bard, classSlot0) has 1 free rank plus 4 purchasable
    # ones. Plan rank 2, mark it owned, then unmark it - the owned watermark
    # must fall all the way back to 0, not get stuck at the free-rank floor
    # (1), or it would silently disappear from Unowned Only despite no
    # purchased rank being owned. ---
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    page.locator(".node", has=page.locator(".name", has_text="Symphonic Aura")).first.click()
    page.click("#incBtn")
    page.wait_for_timeout(80)
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(150)
    sa_row = page.locator(".progression-row", has=page.locator(".step-name", has_text="Symphonic Aura"))
    sa_row.locator(".step-own").click()
    page.wait_for_timeout(80)
    sa_row.locator(".step-own").click()
    page.wait_for_timeout(80)

    page.click("#browseToggle")
    page.select_option("#browseFilter", "Bard")
    page.wait_for_timeout(150)
    sa_card = page.locator(".browse-card", has=page.locator(".name", has_text="Symphonic Aura"))
    assert "owned" not in (sa_card.get_attribute("class") or "").split(), \
        "FAIL: Symphonic Aura still shows as owned after mark/unmark - owned watermark stuck at the free-rank floor"
    assert sa_card.locator(".owned-info").count() == 0, \
        "FAIL: Symphonic Aura still shows an Owned: N/R badge after mark/unmark"
    print("PASS: mark/unmark of an autoRanks AA's purchasable rank returns owned to 0, not the free-rank floor")

    if "active" not in toggle.get_attribute("class"):
        toggle.click()
        page.wait_for_timeout(150)
    assert page.locator(".browse-card", has=page.locator(".name", has_text="Symphonic Aura")).count() == 1, \
        "FAIL: Unowned Only hid Symphonic Aura despite no purchased rank being owned"
    print("PASS: Unowned Only still shows an autoRanks AA after a mark/unmark round trip on its purchasable rank")
    toggle.click()
    page.wait_for_timeout(150)

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
