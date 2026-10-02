# -*- coding: utf-8 -*-
# Effect-value guessing (the cost-guessing feature ported to the numeric
# values embedded in AA effect descriptions, e.g. the "?" in "1/?/5/10%"):
# a guessed value must render inline in the description, styled and
# tooltipped like every other guess in the app, wherever a description
# shows up (side panel, Browse, Summary, Progression's next-rank preview) -
# and must never affect anything else (search, export text, real math,
# which never looked at description text for spending purposes anyway).
#
# Pinning this to whichever real AA currently has an unconfirmed effect
# value has been expensive: this test has been rewritten to a new live
# example six times (Baking Mastery, Combat Fury, Spell Casting Subtlety,
# Packrat, Druid/Wizard's Quick Evacuation, Banestrike) as each prior one
# got confirmed by the wiki (or, for Quick Evacuation, turned out to be a
# shared AA and got merged away) in turn. Rather than keep re-pinning, the
# "?" and its guess are fabricated here on a stable, player-log-verified
# host: Baking Mastery (general, wiki-sync/log_verified.json confirms rank
# 3 reached 2026-09-21 - see wiki_guess_fixtures.py and
# test_manual_guess.py's own header comment for the full mechanism). Its
# real description is already "Reduces the chance of failing Baking
# recipes by 10/25/50%." - rank 1 (10) stays real; ranks 2-3 (25/50) become
# the fabricated "?"s.
#
# This also restores coverage the Banestrike/Packrat-era pins had lost:
# those AAs have no sibling, so their guesses could only ever be the
# manual/very-low tier (see test_guess_effects.py for that algorithm's own
# data-independent coverage). Baking Mastery's real sibling group (the
# other crafting masteries - test_guess_effects.py's own
# group_for_name("Baking Mastery") == group_for_name("Alchemy Mastery")
# assertion confirms this is a real, not fabricated, pairing) lets this
# test exercise a medium-confidence, sibling-matched guess and its "from
# Alchemy Mastery" tooltip wording instead - the richer case Quick
# Evacuation used to cover before it stopped being two separate AAs.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright
from wiki_guess_fixtures import read_app_src, read_data_js, replace_object_literal, insert_table_entry

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

FROZEN_AA = '{name:"Baking Mastery",ranks:3,costs:["2","4","6"],levelReq:"1",description:"Reduces the chance of failing Baking recipes by 10/?/?%."}'
SYNTHETIC_ENTRY = '"general::baking-mastery": { "0": { "1": { value: 25, confidence: "medium", basedOn: ["Alchemy Mastery"] }, "2": { value: 50, confidence: "medium", basedOn: ["Alchemy Mastery"] } } }'


def patched_data_js():
    return replace_object_literal(read_data_js(), '{name:"Baking Mastery"', FROZEN_AA)


def patched_app_src():
    return insert_table_entry(read_app_src(), "const EFFECT_GUESS_TABLE = {", SYNTHETIC_ENTRY)


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
    page.click('button[data-tab="general"]')

    bm = page.locator(".node", has=page.locator(".name", has_text="Baking Mastery"))
    bm.click()
    page.click("#incBtn")  # rank1, real value 10
    page.wait_for_timeout(30)

    # --- Side panel: rank1 is real (bolded, no estimate); ranks 2 and 3's
    # "?"s each show their own guess, styled and tooltipped independently,
    # neither bolded (neither is the current rank yet). ---
    desc = page.locator("#sidePanel .desc").first
    html = desc.inner_html()
    print("side panel desc (rank1 current):", html)
    assert '<span class="rank-highlight">10</span>' in html, "FAIL: the real current-rank value should still be bolded"
    assert html.count('class="is-estimate tier-medium" title="Estimated (medium confidence)') == 2, "FAIL: expected two independently-styled guessed ranks"
    assert "~25" in html and "~50" in html
    assert "from Alchemy Mastery" in html, "FAIL: expected the sibling-match tooltip wording"
    assert html.rstrip().endswith("%."), "FAIL: description should end right after rank 3's guess"
    print("PASS: side panel shows the real current rank bolded and both guessed ranks estimate-styled, independently")

    # --- Progression tab: the next-rank preview (rank2, the first guessed
    # one, immediately after the one real rank) shows the same estimate.
    # Being the next rank it is also rank-highlighted, so this is the
    # combined case in situ. ---
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
    bm.click()
    page.click("#incBtn")
    page.wait_for_timeout(30)
    span = page.locator("#sidePanel .desc .is-estimate.rank-highlight").first
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
    card = page.locator("#browseGrid .browse-card", has=page.locator(".name", has_text="Baking Mastery")).first
    browse_html = card.locator(".desc").inner_html()
    print("Browse desc html:", browse_html)
    assert "~25" in browse_html and "~50" in browse_html and "is-estimate" in browse_html
    assert "rank-highlight" not in browse_html, "FAIL: Browse has no current rank, nothing should be bolded"
    page.fill("#globalSearch", "")
    page.click("#browseToggle")
    print("PASS: Browse shows the guess with no rank-highlighting (no current rank concept there)")

    # --- Summary tab: picked AAs show their description at the rank you
    # hold, same guess/bold treatment as the side panel. Current rank (2)
    # happens to be a guessed slot too, same combined case as above. ---
    page.click('button[data-tab="summary"]')
    page.wait_for_timeout(100)
    summary_card = page.locator("#summaryContent .browse-card", has=page.locator(".name", has_text="Baking Mastery"))
    summary_html = summary_card.locator(".desc").inner_html()
    print("Summary desc html:", summary_html)
    assert "~25" in summary_html and "is-estimate" in summary_html and "rank-highlight" in summary_html
    print("PASS: Summary shows the guess, bolded (it's the currently-held rank there)")

    print("ERRORS:", errors)
    assert not errors, f"FAIL: page errors {errors}"
    browser.close()
    print("ALL PASS")
