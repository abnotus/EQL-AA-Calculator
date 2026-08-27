# -*- coding: utf-8 -*-
# Effect-value guessing (the cost-guessing feature ported to the numeric
# values embedded in AA effect descriptions, e.g. the "?" in "1/?/5/10%"):
# a guessed value must render inline in the description, styled and
# tooltipped like every other guess in the app, wherever a description
# shows up (side panel, Browse, Summary, Progression's next-rank preview) -
# and must never affect anything else (search, export text, real math,
# which never looked at description text for spending purposes anyway).
#
# Baking Mastery (general) is the one live example today: "Reduces the
# chance of failing Alchemy recipes by 10/?/?%." - ranks 2 and 3 each get a
# medium-confidence guess (25 and 50) once Jewel Craft Mastery (the same
# EFFECT_SIBLING_GROUPS crafting-Mastery family) became fully known. (This
# used to be Combat Fury's rank 2/3 - a wiki scrape confirmed both as real
# since this test was first written, so it no longer has any "?" effect
# value at all; swapped to a currently-live example. Combat Fury's own gap
# had no sibling group and a real rank *after* it, so it got a low-
# confidence interpolated guess instead - Baking Mastery's gap is
# trailing, so it's sibling-matched, not interpolated, and there's no
# rank 4 to check "stays untouched" against.)
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

    am = page.locator(".node", has=page.locator(".name", has_text="Baking Mastery"))
    am.click()
    page.click("#incBtn")  # rank1, real value 10
    page.wait_for_timeout(30)

    # --- Side panel: rank1 is real (bolded, no estimate); ranks 2 and 3's
    # "?"s each show their own sibling-matched guess, styled and
    # tooltipped, NOT bolded (neither is the current rank yet). No rank 4
    # here (only 3 ranks total) - the description just ends after rank 3's
    # guess. ---
    desc = page.locator("#sidePanel .desc").first
    html = desc.inner_html()
    print("side panel desc (rank1 current):", html)
    assert '<span class="rank-highlight">10</span>' in html, "FAIL: the real current-rank value should still be bolded"
    assert html.count('class="is-estimate tier-medium" title="Estimated (medium confidence) from Jewel Craft Mastery') == 2, "FAIL: expected two independently-styled guessed ranks"
    assert "~25" in html and "~50" in html
    assert html.rstrip().endswith("%."), "FAIL: description should end right after rank 3's guess"
    print("PASS: side panel shows the real current rank bolded and both guessed ranks estimate-styled, independently")

    # --- Progression tab: the next-rank preview (for rank2, the first
    # guessed one) shows the same estimate, with a confidence chip. ---
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(100)
    row = page.locator(".progression-row", has=page.locator(".step-name", has_text="Baking Mastery"))
    row.locator(".step-expand").click()
    page.wait_for_timeout(100)
    prog_desc = page.locator(".progression-next-rank .desc").inner_html()
    print("Progression next-rank desc:", prog_desc)
    assert "~25" in prog_desc and "is-estimate" in prog_desc and "tier-medium" in prog_desc
    print("PASS: Progression's next-rank preview shows the same guess")

    # --- Buy rank2 - now the guessed slot IS the current rank too. Combined
    # rank-highlight + is-estimate case: color/background must resolve to
    # the tier color, not the default red rank-highlight background (the
    # exact CSS-cascade pitfall the Progression cost pill hit earlier). ---
    page.click('button[data-tab="general"]')
    am.click()
    page.click("#incBtn")
    page.wait_for_timeout(30)
    desc2 = page.locator("#sidePanel .desc").first
    span = desc2.locator("span").first
    cls = span.get_attribute("class")
    print("combined rank-highlight + is-estimate class:", cls)
    assert "is-estimate" in cls and "tier-medium" in cls and "rank-highlight" in cls
    color = span.evaluate("el => getComputedStyle(el).color")
    bg = span.evaluate("el => getComputedStyle(el).backgroundColor")
    print("combined span color/background:", color, bg)
    assert color == "rgb(166, 124, 217)", f"FAIL: expected the medium-tier color to win, got {color}"
    assert bg == "rgba(166, 124, 217, 0.12)", f"FAIL: expected the medium-tier background, not the default red rank-highlight one, got {bg}"
    print("PASS: a slot that's both the current rank and a guess resolves to the tier's own color and background")

    # --- Browse: rank-agnostic reference view - the guess still shows, but
    # with no rank-highlight class at all (there's no "current rank" here). ---
    page.click("#browseToggle")
    page.fill("#globalSearch", "Baking Mastery")
    page.wait_for_timeout(100)
    card = page.locator("#browseGrid .browse-card", has=page.locator(".name", has_text="Baking Mastery"))
    browse_html = card.locator(".desc").inner_html()
    print("Browse desc html:", browse_html)
    assert "~25" in browse_html and "~50" in browse_html and "is-estimate" in browse_html
    assert "rank-highlight" not in browse_html, "FAIL: Browse has no current rank, nothing should be bolded"
    page.fill("#globalSearch", "")
    page.click("#browseToggle")
    print("PASS: Browse shows the guess with no rank-highlighting (no current rank concept there)")

    # --- Summary tab: picked AAs show their description at the rank you
    # hold, same guess/bold treatment as the side panel. ---
    page.click('button[data-tab="summary"]')
    page.wait_for_timeout(100)
    summary_card = page.locator("#summaryContent .browse-card", has=page.locator(".name", has_text="Baking Mastery"))
    summary_html = summary_card.locator(".desc").inner_html()
    print("Summary desc html:", summary_html)
    assert "~25" in summary_html and "is-estimate" in summary_html and "rank-highlight" in summary_html
    print("PASS: Summary shows the guess, bolded (it's the currently-held rank there)")

    # --- Quick Evacuation (Druid): MANUAL_EFFECT_GUESSES, very-low tier -
    # 2 guessed slots in a row (ranks 2-3), each independently styled/
    # tooltipped. Confirms the manual fallback (not just algorithmic
    # interpolation/sibling-matching) renders correctly for effects, same
    # as it does for costs. (This used to be Spell Casting Subtlety's 5
    # guessed ranks, before that Packrat's whole progression - each got
    # confirmed by a wiki scrape in turn since this test was first written,
    # same process as this file's own top comment describes for the Combat
    # Fury -> Baking Mastery swap. No live AA currently has more than 2
    # consecutive manual very-low effect guesses. Quick Evacuation is a
    # per-class AA (Druid here, though the identically-named Wizard version
    # would work too), so it needs a slot rather than the shared archetype
    # tab. ---
    page.select_option("#classSelect0", "Druid")
    page.click('button[data-tab="classSlot0"]')
    qe = page.locator(".node", has=page.locator(".name", has_text="Quick Evacuation"))
    qe.click()
    page.click("#incBtn")  # rank1, real value 10% - not part of what's being checked here
    page.wait_for_timeout(30)
    qe_desc = page.locator("#sidePanel .desc").first.inner_html()
    print("Quick Evacuation desc html:", qe_desc)
    for v in ("~20", "~30"):
        assert v in qe_desc, f"FAIL: expected {v} in Quick Evacuation's description"
    assert qe_desc.count('tier-very-low') == 2, "FAIL: expected both guessed slots tagged very-low"
    assert "hand-picked" in qe_desc
    print("PASS: Quick Evacuation's 2 manual very-low effect guesses all render correctly")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
