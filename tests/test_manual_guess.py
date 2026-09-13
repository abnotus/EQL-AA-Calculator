# -*- coding: utf-8 -*-
# Manual/curator guesses (guess_costs.py's MANUAL_GUESSES, lowest-priority
# fallback for a slot neither sibling-matching nor bounded interpolation
# could reach): must render as a distinct "very-low" confidence tier, with
# manual-specific tooltip wording, and must never affect real point math -
# same guarantees as the algorithmic tiers, just a different evidence
# source and a strictly lower confidence label.
#
# As of this writing there is no live AA with a manual cost guess at all -
# every MANUAL_GUESSES entry that used to apply has since been fully
# confirmed by the wiki. The one AA still carrying an unguessed cost (Turn
# Summoned, Magician, ranks 2-3) already has its own real, high-confidence
# algorithmic guess, so this seeds a synthetic COST_GUESS_TABLE entry for it
# at the browser level instead, overriding (not merely adding to) that real
# entry so the very-low/manual tier can be tested in isolation: real app.js
# is a minified bundle whose identifiers (including COST_GUESS_TABLE itself)
# don't survive esbuild's mangling, so this intercepts the app.js request
# and serves app.src.js (the unminified, readable, otherwise-identical
# generated artifact) with Turn Summoned's real table entry replaced outright
# - a plain string-prepend (as opposed to a full replace) would just get
# clobbered by the real entry declared later in the same object literal,
# since it shares Turn Summoned's key. Turn Summoned's own real cost/level
# data is untouched - only the synthetic guess is injected, and only for
# this test's own page.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
APP_SRC_PATH = os.path.join(os.path.dirname(__file__), "..", "app.src.js")
TARGET_KEY = '"class:Magician:turn-summoned": {'  # object-shaped - AA_ID_TABLE has the same key with a plain numeric value, need the COST_GUESS_TABLE occurrence specifically
SYNTHETIC_VALUE = '{ "1": { value: 9, confidence: "very-low", basedOn: [], manual: true } }'


def patched_app_src():
    with open(APP_SRC_PATH, "r", encoding="utf-8") as f:
        src = f.read()
    key_start = src.find(TARGET_KEY)
    assert key_start != -1, "FAIL: could not find class:Magician:turn-summoned's object-valued entry in app.src.js - has COST_GUESS_TABLE's declaration changed shape?"
    brace_start = key_start + len(TARGET_KEY) - 1
    depth = 0
    i = brace_start
    while True:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    value_end = i + 1
    return src[:brace_start] + SYNTHETIC_VALUE + src[value_end:]


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.route("**/app.js*", lambda route: route.fulfill(body=patched_app_src(), content_type="application/javascript; charset=utf-8"))

    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # --- Turn Summoned: costs = [3, ?, ?], only rank 1 is real. Magician
    # isn't one of the 3 default class slots, so it needs swapping in first.
    # The synthetic entry above gives rank 2 (index 1) a manual, very-low-
    # confidence value of 9, replacing its real high-confidence guess
    # entirely - rank 3 (index 2) is left with no guess at all, so this
    # scenario simply never buys that far. ---
    page.select_option("#classSelect0", "Magician")
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    ts = page.locator(".node", has=page.locator(".name", has_text="Turn Summoned"))
    ts.click()
    page.click("#incBtn")  # buy rank 1, real cost 3
    page.wait_for_timeout(20)

    spent_before = page.locator("#spentValue").inner_text()
    print("points spent after rank 1 (real cost 3):", spent_before)
    assert spent_before == "0 / 3"

    tag = ts.locator(".costtag")
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

    pip2 = page.locator("#sidePanel .rank-costs .pip").nth(1)
    print("pip2:", pip2.inner_text(), pip2.get_attribute("class"))
    assert pip2.inner_text() == "R2: ~9"
    assert "is-estimate" in pip2.get_attribute("class") and "tier-very-low" in pip2.get_attribute("class")
    print("PASS: side panel next-rank box, confidence chip, and rank-costs pip all show very-low consistently")

    # --- Buying the manually-guessed rank must cost costNum('?') == 0 in
    # spentPoints()/affordability terms, not the guessed 9 - manual guesses
    # must never leak into real point math, same structural guarantee as
    # algorithmic guesses. The topbar's "spent" side blends in the guess
    # for display; Progression's own running total blends the same way too
    # (~12, matching the topbar) instead of staying frozen at the real 3. ---
    page.click("#incBtn")  # buy rank 2 (real cost "?", math treats as 0)
    page.wait_for_timeout(50)
    spent_after = page.locator("#spentValue").inner_text()
    print("spentValue after buying the manually-guessed rank (blends in the guess for display):", spent_after)
    assert spent_after == "0 / ~12", "FAIL: expected the headline to blend real 3 + guessed 9"
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(50)
    total_el = page.locator(".progression-row .cost-total").last
    blended_total = total_el.inner_text()
    print("Progression's blended running total after buying the manually-guessed rank:", blended_total)
    assert blended_total == "~12 total", f"FAIL: expected Progression's total to blend to ~12 like the topbar, got {blended_total}"
    assert total_el.get_attribute("title") == "3 confirmed + 9 estimated.", f"FAIL: unexpected breakdown tooltip: {total_el.get_attribute('title')}"
    print("PASS: Progression's running total blends the manual guess in too, same as the topbar - spentPoints() itself stays real (3 confirmed, tracked separately)")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
