# -*- coding: utf-8 -*-
# Manual/curator guesses (guess_costs.py's MANUAL_GUESSES, lowest-priority
# fallback for a slot neither sibling-matching nor bounded interpolation
# could reach): must render as a distinct "very-low" confidence tier, with
# manual-specific tooltip wording, and must never affect real point math -
# same guarantees as the algorithmic tiers, just a different evidence
# source and a strictly lower confidence label.
#
# As of this writing there is no live AA with a manual cost guess at all -
# every MANUAL_GUESSES entry that used to apply (Crafting Mastery, First
# Aid, Innate Metabolism, Spell Casting Subtlety, Reaching Notes,
# Conjurer's Efficiency) has since been fully confirmed by the wiki. The one
# AA still carrying an unguessed cost (Thief's Intuition, archetype, ranks
# 3-4) has no matching sibling for the algorithm to reach - a genuine hand-
# curated MANUAL_GUESSES entry for it would need real cross-referencing
# evidence this test has no basis to invent, so rather than fabricate one in
# the shipped data just to have a live example, this seeds a synthetic
# COST_GUESS_TABLE entry for it at the browser level instead: real app.js is
# a minified bundle whose identifiers (including COST_GUESS_TABLE itself)
# don't survive esbuild's mangling, so this intercepts the app.js request
# and serves app.src.js (the unminified, readable, otherwise-identical
# generated artifact) with one entry patched in. Thief's Intuition's own
# real costs/data are untouched - only the synthetic guess is injected, and
# only for this test's own page.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
APP_SRC_PATH = os.path.join(os.path.dirname(__file__), "..", "app.src.js")


def patched_app_src():
    with open(APP_SRC_PATH, "r", encoding="utf-8") as f:
        src = f.read()
    injected = (
        'const COST_GUESS_TABLE = {\n'
        '  "archetype::thiefs-intuition": { "2": { value: 9, confidence: "very-low", basedOn: [], manual: true } },'
    )
    patched = src.replace("const COST_GUESS_TABLE = {", injected, 1)
    assert patched != src, "FAIL: could not find COST_GUESS_TABLE in app.src.js to patch - has its declaration changed shape?"
    return patched


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.route("**/app.js*", lambda route: route.fulfill(body=patched_app_src(), content_type="application/javascript; charset=utf-8"))

    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # --- Thief's Intuition: costs = [3, 6, ?, ?], ranks 1-2 known. The
    # synthetic entry above gives rank 3 (index 2) a manual, very-low-
    # confidence value of 9. It's archetype-scoped with eligibleClasses
    # Bard/Rogue - Bard is CLASS_LIST[0], already in slot 0 by default, so
    # no class selection step is needed. ---
    page.click('button[data-tab="archetype"]')
    ti = page.locator(".node", has=page.locator(".name", has_text="Thief's Intuition"))
    ti.click()
    for _ in range(2):
        page.click("#incBtn")  # buy ranks 1-2, real costs 3+6 = 9
        page.wait_for_timeout(20)

    spent_before = page.locator("#spentValue").inner_text()
    print("points spent after ranks 1-2 (real cost 9):", spent_before)
    assert spent_before == "0 / 9"

    tag = ti.locator(".costtag")
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
    # must never leak into real point math, same structural guarantee as
    # algorithmic guesses. The topbar's "spent" side blends in the guess
    # for display; Progression's own running total blends the same way too
    # (~18, matching the topbar) instead of staying frozen at the real 9. ---
    page.click("#incBtn")  # buy rank3 (real cost "?", math treats as 0)
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
