# -*- coding: utf-8 -*-
# Manual/curator guesses (guess_costs.py's MANUAL_GUESSES, lowest-priority
# fallback for a slot neither sibling-matching nor bounded interpolation
# could reach): must render as a distinct "very-low" confidence tier, with
# manual-specific tooltip wording, and must never affect real point math -
# same guarantees as the algorithmic tiers, just a different evidence
# source and a strictly lower confidence label.
#
# There's no live AA with a manual cost guess at all right now - every
# MANUAL_GUESSES entry that used to apply has since been fully confirmed by
# the wiki - so rather than pin to whichever real AA happens to have an
# unconfirmed cost today (and rewrite this test again the next time the
# wiki catches up, as has happened repeatedly to this file's siblings - see
# tests/README.md), this fabricates the whole scenario on a stable,
# player-log-verified host: Rapid Feign (Monk, wiki-sync/log_verified.json
# confirms rank 3 reached 2026-09-16), an otherwise perfectly ordinary AA
# with no auto/classRankCap/eligibleClasses/prereq quirks. Its real shape
# is already exactly ranks:3, costs:["3","6","9"] - data.js's route below
# only swaps rank 3's real "9" for a synthetic "?", and app.js's route
# (serving the unminified app.src.js, since COST_GUESS_TABLE's identifier
# doesn't survive esbuild's real bundling - see wiki_guess_fixtures.py)
# gives that same slot a synthetic very-low/manual guess. Neither Rapid
# Feign's real identity nor its real ranks 1-2 costs are otherwise touched -
# only the one slot this test needs is synthetic, and only for this test's
# own page.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
from wiki_guess_fixtures import read_app_src, read_data_js, replace_object_literal, insert_table_entry

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

FROZEN_AA = '{name:"Rapid Feign",ranks:3,costs:["3","6","?"],levelReq:"17",description:"Reduces the reuse time of your Feign Death skill by 1/3/5 second(s)."}'
SYNTHETIC_ENTRY = '"class:Monk:rapid-feign": { "2": { value: 9, confidence: "very-low", basedOn: [], manual: true } }'


def patched_data_js():
    return replace_object_literal(read_data_js(), '{name:"Rapid Feign"', FROZEN_AA)


def patched_app_src():
    return insert_table_entry(read_app_src(), "const COST_GUESS_TABLE = {", SYNTHETIC_ENTRY)


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.route("**/data.js*", lambda route: route.fulfill(body=patched_data_js(), content_type="application/javascript; charset=utf-8"))
    page.route("**/app.js*", lambda route: route.fulfill(body=patched_app_src(), content_type="application/javascript; charset=utf-8"))

    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # --- Rapid Feign: costs = [3, 6, ?], ranks 1-2 real. Monk isn't one of
    # the 3 default class slots, so it needs swapping in first. The
    # synthetic entry above gives rank 3 (index 2) a manual, very-low-
    # confidence value of 9, overriding what would otherwise be a real "?"
    # with no guess at all. ---
    page.select_option("#classSelect0", "Monk")
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    rf = page.locator(".node", has=page.locator(".name", has_text="Rapid Feign"))
    rf.click()
    for _ in range(2):
        page.click("#incBtn")  # buy ranks 1-2, real costs 3+6 = 9
        page.wait_for_timeout(20)

    spent_before = page.locator("#spentValue").inner_text()
    print("points spent after ranks 1-2 (real cost 9):", spent_before)
    assert spent_before == "0 / 9"

    tag = rf.locator(".costtag")
    print("tree costtag text:", tag.inner_text(), "class:", tag.get_attribute("class"))
    assert tag.inner_text() == "~9"
    cls = tag.get_attribute("class")
    assert "is-estimate" in cls and "tier-very-low" in cls
    title = tag.get_attribute("title")
    print("tooltip:", title)
    assert "hand-picked" in title and "not derived from other AAs" in title
    print("PASS: manual guess renders very-low tier with manual-specific tooltip wording in the tree")

    # Side panel next-rank box + confidence chip + pip strip.
    next_cost_b = page.locator("#sidePanel .next-rank-title b")
    print("next-rank cost text:", next_cost_b.inner_text(), "class:", next_cost_b.get_attribute("class"))
    assert next_cost_b.inner_text() == "~9"
    chip = page.locator("#sidePanel .confidence-chip")
    print("confidence chip:", chip.inner_text(), chip.get_attribute("class"))
    assert chip.inner_text().strip().lower() == "very-low"
    assert "tier-very-low" in chip.get_attribute("class")

    pip3 = page.locator("#sidePanel .rank-costs .pip").nth(2)
    print("pip3:", pip3.inner_text(), pip3.get_attribute("class"))
    assert pip3.inner_text() == "R3: ~9"
    assert "is-estimate" in pip3.get_attribute("class") and "tier-very-low" in pip3.get_attribute("class")
    print("PASS: side panel next-rank box, confidence chip, and rank-costs pip all show very-low consistently")

    # --- Buying the manually-guessed rank must cost costNum('?') == 0 in
    # spentPoints()/affordability terms, not the guessed 9 - manual guesses
    # must never leak into real point math. The topbar's "spent" side blends
    # in the guess for display; Progression's own running total blends the
    # same way too (~18, matching the topbar) instead of staying frozen at
    # the real 9. ---
    page.click("#incBtn")  # buy rank 3 (real cost "?", math treats as 0)
    page.wait_for_timeout(50)
    spent_after = page.locator("#spentValue").inner_text()
    print("spentValue after buying the manually-guessed rank (blends in the guess for display):", spent_after)
    assert spent_after == "0 / ~18", "FAIL: expected the headline to blend real 9 + guessed 9"
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(50)
    total_el = page.locator(".progression-row .cost-total").last
    blended_total = total_el.inner_text()
    print("Progression's blended running total after buying the manually-guessed rank:", blended_total)
    assert blended_total == "~18 total", f"FAIL: expected Progression's total to blend to ~18 like the topbar, got {blended_total}"
    assert total_el.get_attribute("title") == "9 confirmed + 9 estimated.", f"FAIL: unexpected breakdown tooltip: {total_el.get_attribute('title')}"
    print("PASS: Progression's running total blends the manual guess in too, same as the topbar - spentPoints() itself stays real (9 confirmed, tracked separately)")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
