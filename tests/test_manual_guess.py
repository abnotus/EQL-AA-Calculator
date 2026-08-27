# -*- coding: utf-8 -*-
# Manual/curator guesses (guess_costs.py's MANUAL_GUESSES, lowest-priority
# fallback for a slot neither sibling-matching nor bounded interpolation
# could reach): must render as a distinct "very-low" confidence tier, with
# manual-specific tooltip wording, and must never affect real point math -
# same guarantees as the algorithmic tiers, just a different evidence
# source and a strictly lower confidence label.
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
    page.click('button[data-tab="general"]')

    # --- First Aid: costs = [1, 1, 1, 3, ?, ?], MANUAL_GUESSES gives rank5
    # (index 4) a value of 5, tagged very-low/manual. (This used to be
    # Crafting Mastery's rank 2 - a wiki scrape confirmed its whole
    # progression since this test was first written, so it no longer has
    # any "?" cost left at all; swapped to a currently-live example. First
    # Aid's first unconfirmed rank is its 5th, not its 2nd, so getting there
    # takes 4 real purchases instead of 1.) ---
    cm = page.locator(".node", has=page.locator(".name", has_text="First Aid"))
    cm.click()
    for _ in range(4):
        page.click("#incBtn")  # buy ranks 1-4, real costs 1+1+1+3 = 6
        page.wait_for_timeout(20)

    spent_before = page.locator("#spentValue").inner_text()
    print("points spent after ranks 1-4 (real cost 6):", spent_before)
    assert spent_before == "0 / 6"

    tag = cm.locator(".costtag")
    print("tree costtag text:", tag.inner_text(), "class:", tag.get_attribute("class"))
    assert tag.inner_text() == "~5"
    cls = tag.get_attribute("class")
    assert "is-estimate" in cls and "tier-very-low" in cls
    title = tag.get_attribute("title")
    print("tooltip:", title)
    assert "hand-picked" in title and "not derived from other AAs" in title
    print("PASS: manual guess renders very-low tier with manual-specific tooltip wording in the tree")

    # Side panel next-rank box + confidence chip + pip strip.
    next_cost_b = page.locator("#sidePanel .next-rank-title b")
    print("next-rank cost text:", next_cost_b.inner_text(), "class:", next_cost_b.get_attribute("class"))
    assert next_cost_b.inner_text() == "~5"
    chip = page.locator("#sidePanel .confidence-chip")
    print("confidence chip:", chip.inner_text(), chip.get_attribute("class"))
    assert chip.inner_text().strip().lower() == "very-low"
    assert "tier-very-low" in chip.get_attribute("class")

    pip5 = page.locator("#sidePanel .rank-costs .pip").nth(4)
    print("pip5:", pip5.inner_text(), pip5.get_attribute("class"))
    assert pip5.inner_text() == "R5: ~5"
    assert "is-estimate" in pip5.get_attribute("class") and "tier-very-low" in pip5.get_attribute("class")
    print("PASS: side panel next-rank box, confidence chip, and rank-costs pip all show very-low consistently")

    # --- Buying the manually-guessed rank must cost costNum('?') == 0 in
    # spentPoints()/affordability terms, not the guessed 5 - manual guesses
    # must never leak into real point math, same structural guarantee as
    # algorithmic guesses. The topbar's "spent" side blends in the guess
    # for display (test_estimated_total.py); Progression's own running
    # total blends the same way now (~11, matching the topbar) instead of
    # staying frozen at the real 6 - see test_estimated_total.py and
    # logic.js's computeProgressionSteps (blendedCumulative) for why. ---
    page.click("#incBtn")  # buy rank5 (real cost "?", math treats as 0)
    page.wait_for_timeout(50)
    spent_after = page.locator("#spentValue").inner_text()
    print("spentValue after buying the manually-guessed rank (blends in the guess for display):", spent_after)
    assert spent_after == "0 / ~11", "FAIL: expected the headline to blend real 6 + guessed 5"
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(50)
    total_el = page.locator(".progression-row .cost-total").last
    blended_total = total_el.inner_text()
    print("Progression's blended running total after buying the manually-guessed rank:", blended_total)
    assert blended_total == "~11 total", f"FAIL: expected Progression's total to blend to ~11 like the topbar, got {blended_total}"
    assert total_el.get_attribute("title") == "6 confirmed + 5 estimated.", f"FAIL: unexpected breakdown tooltip: {total_el.get_attribute('title')}"
    print("PASS: Progression's running total blends the manual guess in too, same as the topbar - spentPoints() itself stays real (6 confirmed, tracked separately)")
    page.click('button[data-tab="general"]')

    # --- Reaching Notes: costs = [2, 4, 6, ?, ?, ?], ranks 1-3 known -
    # MANUAL_GUESSES gives rank4 (index 3) a value of 8, very-low/manual.
    # (This used to be Spell Casting Subtlety - a wiki scrape confirmed its
    # whole progression since this test was first written, so it no longer
    # has any "?" cost left at all; swapped to a currently-live example.
    # Reaching Notes is a Bard class AA rather than an archetype one, so
    # instead of a qualifying class in any slot, it specifically needs Bard
    # in a slot - which happens to already be true by default (slot 0), so
    # no class selection step is needed here.) ---
    page.click('button[data-tab="classSlot0"]')
    rn = page.locator(".node", has=page.locator(".name", has_text="Reaching Notes"))
    rn.click()
    for _ in range(3):
        page.click("#incBtn")  # ranks 1-3, real costs 2/4/6
        page.wait_for_timeout(20)
    rn_tag = rn.locator(".costtag")
    print("Reaching Notes rank4 tag:", rn_tag.inner_text(), rn_tag.get_attribute("class"))
    assert rn_tag.inner_text() == "~8"
    rn_cls = rn_tag.get_attribute("class")
    assert "is-estimate" in rn_cls and "tier-very-low" in rn_cls
    print("PASS: Reaching Notes' manual guess renders as very-low, same as any other manual entry")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
