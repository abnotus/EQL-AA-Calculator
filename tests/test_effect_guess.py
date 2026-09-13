# -*- coding: utf-8 -*-
# Effect-value guessing (the cost-guessing feature ported to the numeric
# values embedded in AA effect descriptions, e.g. the "?" in "1/?/5/10%"):
# a guessed value must render inline in the description, styled and
# tooltipped like every other guess in the app, wherever a description
# shows up (side panel, Browse, Summary, Progression's next-rank preview) -
# and must never affect anything else (search, export text, real math,
# which never looked at description text for spending purposes anyway).
#
# Druid's Quick Evacuation is the live example: real confirmed costs
# (3/6/9) with "...by 10/?/?%.", so ranks 2 and 3 each carry a guess (25
# and 50) - sibling-matched to Wizard's own Quick Evacuation (confirmed
# 10/25/50%) at medium confidence, once that was a manual very-low guess
# too. It has been Baking Mastery, Combat Fury, Spell Casting Subtlety and
# Packrat before now - each resolved on the wiki in turn, which is the
# expected way this test breaks. Regenerate effectGuesses.js, then pick
# whatever still has a "?" left.
#
# One thing to know when picking the next one: prefer an AA a player
# actually spends points on. Banestrike is the only other live candidate,
# but it is free and unlocked by Slayer achievements rather than bought,
# so driving it with #incBtn tests a purchase that cannot happen in game.
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
    page.select_option("#classSelect0", "Druid")
    page.wait_for_timeout(120)
    page.click('button[data-tab="classSlot0"]')

    qe = page.locator(".node", has=page.locator(".name", has_text="Quick Evacuation"))
    qe.click()
    page.click("#incBtn")  # rank1, real value 10
    page.wait_for_timeout(30)

    # --- Side panel: rank1 is real (bolded, no estimate); ranks 2 and 3's
    # "?"s each show their own guess, styled and tooltipped independently,
    # neither bolded (neither is the current rank yet). Only 3 ranks, so
    # the description ends right after rank 3's guess. ---
    desc = page.locator("#sidePanel .desc").first
    html = desc.inner_html()
    print("side panel desc (rank1 current):", html)
    assert '<span class="rank-highlight">10</span>' in html, "FAIL: the real current-rank value should still be bolded"
    assert html.count('class="is-estimate tier-medium" title="Estimated (medium confidence)') == 2, "FAIL: expected two independently-styled guessed ranks"
    assert "~25" in html and "~50" in html
    assert "from Quick Evacuation" in html, "FAIL: expected the sibling-matched guess tooltip wording"
    assert html.rstrip().endswith("%."), "FAIL: description should end right after rank 3's guess"
    print("PASS: side panel shows the real current rank bolded and both guessed ranks estimate-styled, independently")

    # --- Progression tab: the next-rank preview (rank2, the first guessed
    # one) shows the same estimate. Being the next rank it is also
    # rank-highlighted, so this is the combined case in situ. ---
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(100)
    row = page.locator(".progression-row", has=page.locator(".step-name", has_text="Quick Evacuation"))
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
    page.click('button[data-tab="classSlot0"]')
    qe.click()
    page.click("#incBtn")
    page.wait_for_timeout(30)
    desc2 = page.locator("#sidePanel .desc").first
    span = desc2.locator("span.rank-highlight").first
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
    # with no rank-highlight class at all (there's no "current rank" here).
    # Wizard has an identically-named AA, so both cards match; they carry
    # the same description and the same guesses, and the first is Druid's. ---
    page.click("#browseToggle")
    page.fill("#globalSearch", "Quick Evacuation")
    page.wait_for_timeout(100)
    card = page.locator("#browseGrid .browse-card", has=page.locator(".name", has_text="Quick Evacuation")).first
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
    summary_card = page.locator("#summaryContent .browse-card", has=page.locator(".name", has_text="Quick Evacuation"))
    summary_html = summary_card.locator(".desc").inner_html()
    print("Summary desc html:", summary_html)
    assert "~25" in summary_html and "is-estimate" in summary_html and "rank-highlight" in summary_html
    print("PASS: Summary shows the guess, bolded (it's the currently-held rank there)")

    print("ERRORS:", errors)
    assert not errors, f"FAIL: page errors {errors}"
    browser.close()
    print("ALL PASS")
