# -*- coding: utf-8 -*-
# Manual/curator guesses (guess_costs.py's MANUAL_GUESSES, lowest-priority
# fallback for a slot neither sibling-matching nor bounded interpolation
# could reach): must render as a distinct "very-low" confidence tier, with
# manual-specific tooltip wording, and must never affect real point math -
# same guarantees as the algorithmic tiers, just a different evidence
# source and a strictly lower confidence label.
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8743/index.html"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())

    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.click('button[data-tab="general"]')

    # --- Crafting Mastery: costs = [3, ?, ?, ?, ?, ?], MANUAL_GUESSES gives
    # rank2 (index 1) a value of 4, tagged very-low/manual. ---
    cm = page.locator(".node", has=page.locator(".name", has_text="Crafting Mastery"))
    cm.click()
    page.click("#incBtn")  # buy rank1, real cost 3
    page.wait_for_timeout(30)

    spent_before = page.locator("#spentValue").inner_text()
    print("points spent after rank1 (real cost 3):", spent_before)
    assert spent_before == "3"

    tag = cm.locator(".costtag")
    print("tree costtag text:", tag.inner_text(), "class:", tag.get_attribute("class"))
    assert tag.inner_text() == "~4"
    cls = tag.get_attribute("class")
    assert "is-estimate" in cls and "tier-very-low" in cls
    title = tag.get_attribute("title")
    print("tooltip:", title)
    assert "hand-picked" in title and "not derived from other AAs" in title
    print("PASS: manual guess renders very-low tier with manual-specific tooltip wording in the tree")

    # Side panel next-rank box + confidence chip + pip strip.
    next_cost_b = page.locator("#sidePanel .next-rank-title b")
    print("next-rank cost text:", next_cost_b.inner_text(), "class:", next_cost_b.get_attribute("class"))
    assert next_cost_b.inner_text() == "~4"
    chip = page.locator("#sidePanel .confidence-chip")
    print("confidence chip:", chip.inner_text(), chip.get_attribute("class"))
    assert chip.inner_text().strip().lower() == "very-low"
    assert "tier-very-low" in chip.get_attribute("class")

    pip2 = page.locator("#sidePanel .rank-costs .pip").nth(1)
    print("pip2:", pip2.inner_text(), pip2.get_attribute("class"))
    assert pip2.inner_text() == "R2: ~4"
    assert "is-estimate" in pip2.get_attribute("class") and "tier-very-low" in pip2.get_attribute("class")
    print("PASS: side panel next-rank box, confidence chip, and rank-costs pip all show very-low consistently")

    # --- Buying the manually-guessed rank must cost costNum('?') == 0 in
    # spentPoints()/affordability terms, not the guessed 4 - manual guesses
    # must never leak into real point math, same structural guarantee as
    # algorithmic guesses. The headline spentValue blends in the guess for
    # display (test_estimated_total.py); Progression's own running total
    # blends the same way now (~7, matching the headline) instead of
    # staying frozen at the real 3 - see test_estimated_total.py and
    # logic.js's computeProgressionSteps (blendedCumulative) for why. ---
    page.click("#incBtn")  # buy rank2 (real cost "?", math treats as 0)
    page.wait_for_timeout(50)
    spent_after = page.locator("#spentValue").inner_text()
    print("spentValue after buying the manually-guessed rank (blends in the guess for display):", spent_after)
    assert spent_after == "~7", "FAIL: expected the headline to blend real 3 + guessed 4"
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(50)
    total_el = page.locator(".progression-row .cost-total").last
    blended_total = total_el.inner_text()
    print("Progression's blended running total after buying the manually-guessed rank:", blended_total)
    assert blended_total == "~7 total", f"FAIL: expected Progression's total to blend to ~7 like the topbar, got {blended_total}"
    assert total_el.get_attribute("title") == "3 confirmed + 4 estimated.", f"FAIL: unexpected breakdown tooltip: {total_el.get_attribute('title')}"
    print("PASS: Progression's running total blends the manual guess in too, same as the topbar - spentPoints() itself stays real (3 confirmed, tracked separately)")
    page.click('button[data-tab="general"]')

    # --- Spell Casting Subtlety: costs = [2, ?, ?, ?, ?, ?], only rank1
    # known - MANUAL_GUESSES gives rank2 (index 1) a flat +1/rank
    # continuation, value 3, very-low/manual. (This used to be Innate Spell
    # Resistance - a wiki scrape confirmed ranks 2-4 as real since this test
    # was first written, and its one remaining guess (rank 5) upgraded from
    # a manual very-low fallback to an algorithmic medium guess once
    # Stoicism became fully known, so it no longer demonstrates
    # MANUAL_GUESSES at all. Swapped to a currently-live example with the
    # identical shape - same rank1 cost, same rank2 guess value.) ---
    page.click('button[data-tab="archetype"]')
    scs = page.locator(".node", has=page.locator(".name", has_text="Spell Casting Subtlety"))
    scs.click()
    page.click("#incBtn")  # rank1, real cost 2
    page.wait_for_timeout(30)
    scs_tag = scs.locator(".costtag")
    print("Spell Casting Subtlety rank2 tag:", scs_tag.inner_text(), scs_tag.get_attribute("class"))
    assert scs_tag.inner_text() == "~3"
    scs_cls = scs_tag.get_attribute("class")
    assert "is-estimate" in scs_cls and "tier-very-low" in scs_cls
    print("PASS: Spell Casting Subtlety's manual guess renders as very-low, same as any other manual entry")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
