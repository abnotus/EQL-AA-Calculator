# -*- coding: utf-8 -*-
# Effect-value guessing (the cost-guessing feature ported to the numeric
# values embedded in AA effect descriptions, e.g. the "?" in "1/?/5/10%"):
# a guessed value must render inline in the description, styled and
# tooltipped like every other guess in the app, wherever a description
# shows up (side panel, Browse, Summary, Progression's next-rank preview) -
# and must never affect anything else (search, export text, real math,
# which never looked at description text for spending purposes anyway).
#
# special::banestrike is the live example: real confirmed values for ranks
# 1-2 (2/4), with ranks 3-4 each a "?" ("...by 2/4/?/?%.") - no sibling AA
# shares its name, so each "?" only ever gets a hand-picked manual guess
# (very-low confidence), not a sibling-matched one. It has been Baking
# Mastery, Combat Fury, Spell Casting Subtlety, Packrat and (briefly)
# Druid/Wizard's Quick Evacuation before now - each of the first four
# resolved on the wiki in turn, and Quick Evacuation stopped being a
# sibling pair when its two per-class entries turned out to be one shared
# archetype AA in disguise and were merged into a single data.src.js entry
# - each the expected way this test breaks. Regenerate effectGuesses.js,
# then pick whatever still has a "?" left.
#
# One thing to know when picking the next one: prefer an AA a player
# actually spends points on. Unbound Companion is the only other AA with
# an unresolved "?" at the time of writing, but it's auto-granted
# (`auto: true`) rather than purchased, so driving it with #incBtn tests a
# purchase that cannot happen in game - same reasoning that ruled out
# Banestrike before it became the only option. Banestrike itself is
# nominally unlocked by Slayer achievements rather than bought, but
# data.src.js carries no `auto`/`autoRanks` flag for it, so the app already
# treats it as an ordinary purchasable entry everywhere else - this test
# just goes along with that existing simplification rather than inventing
# a new one.
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
    page.click('button[data-tab="special"]')

    bs = page.locator(".node", has=page.locator(".name", has_text="Banestrike"))
    bs.click()
    page.click("#incBtn")  # rank1, real value 2
    page.wait_for_timeout(30)

    # --- Side panel: rank1 is real (bolded, no estimate); ranks 3 and 4's
    # "?"s each show their own guess, styled and tooltipped independently,
    # neither bolded (neither is the current rank yet). Rank 2 (also real,
    # not yet current) renders as plain unstyled text. ---
    desc = page.locator("#sidePanel .desc").first
    html = desc.inner_html()
    print("side panel desc (rank1 current):", html)
    assert '<span class="rank-highlight">2</span>' in html, "FAIL: the real current-rank value should still be bolded"
    assert html.count('class="is-estimate tier-very-low" title="Estimated (very low confidence)') == 2, "FAIL: expected two independently-styled guessed ranks"
    assert "~6" in html and "~8" in html
    assert "hand-picked pending wiki confirmation" in html, "FAIL: expected the manual-guess tooltip wording"
    assert html.rstrip().endswith("Complete Slayer achievements to progress this ability."), "FAIL: trailing prose after the progression should be untouched"
    print("PASS: side panel shows the real current rank bolded and both guessed ranks estimate-styled, independently")

    # --- Buy rank2 (also real) so the next-rank preview lands on rank3,
    # the first guessed slot. ---
    page.click("#incBtn")
    page.wait_for_timeout(30)

    # --- Progression tab: the next-rank preview (rank3, the first guessed
    # one) shows the same estimate. Being the next rank it is also
    # rank-highlighted, so this is the combined case in situ. ---
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(100)
    # Each rank purchased is its own progression row (one per
    # purchaseOrder entry), so two rows named "Banestrike" exist here
    # (ranks 1 and 2) - the one just bought (rank2, the later row) is the
    # one whose "next rank" preview is rank3.
    row = page.locator(".progression-row", has=page.locator(".step-name", has_text="Banestrike")).last
    row.locator(".step-expand").click()
    page.wait_for_timeout(100)
    prog_desc = page.locator(".progression-next-rank .desc").inner_html()
    print("Progression next-rank desc:", prog_desc)
    assert "~6" in prog_desc and "is-estimate" in prog_desc and "tier-very-low" in prog_desc
    print("PASS: Progression's next-rank preview shows the same guess")

    # --- Buy rank3 - now the guessed slot IS the current rank too. Combined
    # rank-highlight + is-estimate case: color/background must resolve to
    # the tier color, not the default red rank-highlight background (the
    # exact CSS-cascade pitfall the Progression cost pill hit earlier). ---
    page.click('button[data-tab="special"]')
    bs.click()
    page.click("#incBtn")
    page.wait_for_timeout(30)
    span = page.locator("#sidePanel .desc .is-estimate.rank-highlight").first
    cls = span.get_attribute("class")
    print("combined rank-highlight + is-estimate class:", cls)
    assert "is-estimate" in cls and "tier-very-low" in cls and "rank-highlight" in cls
    color = span.evaluate("el => getComputedStyle(el).color")
    bg = span.evaluate("el => getComputedStyle(el).backgroundColor")
    print("combined span color/background:", color, bg)
    assert color == "rgb(107, 100, 89)", f"FAIL: expected the very-low-tier color to win, got {color}"
    assert bg == "rgba(107, 100, 89, 0.12)", f"FAIL: expected the very-low-tier background, not the default red rank-highlight one, got {bg}"
    print("PASS: a slot that's both the current rank and a guess resolves to the tier's own color and background")

    # --- Browse: rank-agnostic reference view - the guess still shows, but
    # with no rank-highlight class at all (there's no "current rank" here). ---
    page.click("#browseToggle")
    page.fill("#globalSearch", "Banestrike")
    page.wait_for_timeout(100)
    card = page.locator("#browseGrid .browse-card", has=page.locator(".name", has_text="Banestrike")).first
    browse_html = card.locator(".desc").inner_html()
    print("Browse desc html:", browse_html)
    assert "~6" in browse_html and "~8" in browse_html and "is-estimate" in browse_html
    assert "rank-highlight" not in browse_html, "FAIL: Browse has no current rank, nothing should be bolded"
    page.fill("#globalSearch", "")
    page.click("#browseToggle")
    print("PASS: Browse shows the guess with no rank-highlighting (no current rank concept there)")

    # --- Summary tab: picked AAs show their description at the rank you
    # hold, same guess/bold treatment as the side panel. Current rank (3)
    # happens to be a guessed slot too, same combined case as above. ---
    page.click('button[data-tab="summary"]')
    page.wait_for_timeout(100)
    summary_card = page.locator("#summaryContent .browse-card", has=page.locator(".name", has_text="Banestrike"))
    summary_html = summary_card.locator(".desc").inner_html()
    print("Summary desc html:", summary_html)
    assert "~6" in summary_html and "is-estimate" in summary_html and "rank-highlight" in summary_html
    print("PASS: Summary shows the guess, bolded (it's the currently-held rank there)")

    print("ERRORS:", errors)
    assert not errors, f"FAIL: page errors {errors}"
    browser.close()
    print("ALL PASS")
