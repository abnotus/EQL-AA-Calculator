# -*- coding: utf-8 -*-
# Cost-guessing feature: guessed costs must never affect real cost math
# (spentPoints/affordability), must render with the right confidence tier
# in the tree node badge, the side panel's next-rank box, and the
# rank-costs pip strip, and must never appear for a real known cost.
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

    # --- Combat Stability: high-confidence guess (6) for rank 3. (This used
    # to be Adamant Will's rank 4, medium-confidence - a wiki scrape
    # confirmed that one as a real 9 since this test was first written, the
    # same "guess resolves away" story Combat Fury's own section below
    # already tells. Swapped to a currently-live example rather than just
    # updating the numbers, since Adamant Will has no "?" cost left at
    # all.) ---
    cs = page.locator(".node", has=page.locator(".name", has_text="Combat Stability"))
    cs.click()
    for _ in range(2):
        page.click("#incBtn")  # ranks 1,2 (costs 2,4 - both real)
        page.wait_for_timeout(20)

    spent_before = page.locator("#spentValue").inner_text()
    print("points spent after 2 real ranks (2+4=6):", spent_before)
    assert spent_before == "6"

    # Tree node badge shows the high-tier guess.
    tag = cs.locator(".costtag")
    print("tree costtag text:", tag.inner_text(), "class:", tag.get_attribute("class"))
    assert tag.inner_text() == "~6"
    assert "is-estimate" in tag.get_attribute("class") and "tier-high" in tag.get_attribute("class")
    print("PASS: tree node shows the high-confidence guess for Combat Stability's unknown rank 3")

    # Side panel next-rank box + pip strip.
    next_cost_b = page.locator("#sidePanel .next-rank-title b")
    print("next-rank cost text:", next_cost_b.inner_text(), "class:", next_cost_b.get_attribute("class"))
    assert next_cost_b.inner_text() == "~6"
    assert "is-estimate" in next_cost_b.get_attribute("class")
    chip = page.locator("#sidePanel .confidence-chip")
    print("confidence chip:", chip.inner_text(), chip.get_attribute("class"))
    assert chip.inner_text().strip().lower() == "high"
    assert "tier-high" in chip.get_attribute("class")

    pip3 = page.locator("#sidePanel .rank-costs .pip").nth(2)
    print("pip3:", pip3.inner_text(), pip3.get_attribute("class"))
    assert pip3.inner_text() == "R3: ~6"
    assert "is-estimate" in pip3.get_attribute("class") and "tier-high" in pip3.get_attribute("class")
    print("PASS: side panel next-rank box and rank-costs pip both show the guess consistently")

    # --- Real cost (rank 1, known = 2) must NEVER show an estimate treatment. ---
    pip1 = page.locator("#sidePanel .rank-costs .pip").nth(0)
    print("pip1 (real, known cost):", pip1.inner_text(), pip1.get_attribute("class"))
    assert pip1.inner_text() == "R1: 2"
    assert "is-estimate" not in pip1.get_attribute("class")
    print("PASS: a real known cost never gets estimate styling")

    # --- Buying the guessed rank must cost exactly costNum('?') == 0 in
    # spentPoints()/affordability terms, not the guessed 6 - guesses must
    # never leak into real point math. The topbar's headline number blends
    # in the guess for display (see test_estimated_total.py); Progression's
    # own per-step running total blends the same way (~12, matching the
    # topbar) instead of freezing at the real 6 - the earlier design kept
    # it strictly real, but a cumulative that never moves through a step
    # whose own pill shows a nonzero ~6 read as "the estimate isn't doing
    # anything", so it now blends everywhere the topbar already does. What's
    # still guaranteed or math-affecting: the real/estimated split stays
    # separately tracked (the tooltip's "6 confirmed" - never silently
    # merged into one indistinguishable number), and spentPoints() itself
    # (which drives everything affordability-related) is untouched -
    # verified by that same "6 confirmed" figure being exactly the real
    # total from before this purchase's guess was added. ---
    page.click("#incBtn")  # buy rank 3 (real cost "?", math treats as 0)
    page.wait_for_timeout(50)
    spent_after = page.locator("#spentValue").inner_text()
    print("spentValue after buying the guessed rank (blends in the guess for display):", spent_after)
    assert spent_after == "~12", "FAIL: expected the headline to blend real 6 + guessed 6"
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(50)
    total_el = page.locator(".progression-row .cost-total").last
    blended_total = total_el.inner_text()
    total_title = total_el.get_attribute("title")
    print("Progression's blended running total after buying the guessed rank:", blended_total, "|", total_title)
    assert blended_total == "~12 total", f"FAIL: expected Progression's total to blend to ~12 like the topbar, got {blended_total}"
    assert total_title == "6 confirmed + 6 estimated.", f"FAIL: unexpected breakdown tooltip: {total_title}"
    print("PASS: Progression's running total now blends the guess in the same way the topbar does, with the real/estimated split still tracked separately (spentPoints() itself untouched)")

    # --- The plain-text export's "Progression (click order)" listing must
    # show the same "~6" per-step estimate AND the same "~12" blended
    # running total the Progression tab itself now shows - buildExportText
    # used to print the raw real stepCost/cumulative regardless of whether a
    # guess existed, a real bug reported directly against Packrat's flat
    # "~1" manual guesses reading as "0 pt(s), (frozen) total" in an
    # exported build. ---
    page.click("#exportBtn")
    page.wait_for_timeout(300)
    export_text = page.locator("#exportText").input_value()
    line = next(l for l in export_text.split("\n") if "Combat Stability rank 3" in l)
    print("export text line for the guessed rank 3:", line)
    assert "~6 pt(s)" in line, f"FAIL: expected the export to show the ~6 guess, got: {line}"
    assert "~12 total" in line, f"FAIL: expected the export's running total to blend to ~12 like Progression's own, got: {line}"
    page.click("#closeExportBtn")
    print("PASS: the plain-text export shows the same guessed per-step estimate and blended running total the Progression tab does")

    # --- Combat Fury: this WAS the live example of a low-confidence,
    # interpolated guess (rank 2 boxed in by known ranks 1 and 3) - a fresh
    # wiki scrape confirmed the real value (2, matching the interpolation
    # exactly) since this test was first written, so it's now fully known
    # real data instead. That's the feature working end to end: a guess
    # resolving away the moment the wiki catches up, automatically, with
    # nothing to clean up by hand. See test_guess_costs_interpolation.py
    # for a live, data-independent test of the interpolation math itself. ---
    page.click('button[data-tab="general"]')
    cf = page.locator(".node", has=page.locator(".name", has_text="Combat Fury"))
    cf.click()
    page.click("#incBtn")  # rank1, cost 1 (real)
    page.wait_for_timeout(30)
    cf_tag = cf.locator(".costtag")
    print("Combat Fury tree costtag (rank2, now confirmed real data):", cf_tag.inner_text(), cf_tag.get_attribute("class"))
    assert cf_tag.inner_text() == "2"
    assert "is-estimate" not in cf_tag.get_attribute("class")
    print("PASS: a rank the wiki has since confirmed shows the real number, no leftover guess styling")

    # Note: as of the latest guess_costs.py run, every AA that has an
    # undocumented ("?") cost has at least a manual or algorithmic guess -
    # there's currently no live example of an AA with a totally empty
    # guess (no sibling, no bounded gap, no manual entry). That code path
    # is still covered directly: see test_guess_costs_interpolation.py's
    # exact-tie case, which asserts guess_for_entry produces nothing when
    # no evidence clears the bar and no manual fallback exists.

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
