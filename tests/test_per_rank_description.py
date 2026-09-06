# -*- coding: utf-8 -*-
# Some AAs do genuinely different things at each rank rather than scaling one
# number, and the wiki writes those as a "Rank N: ..." list. A slash
# progression can't express them: highlightRankValue maps slot i to rank
# i + 1, so a progression covering only ranks 2-4 would bold the wrong
# number, and a rank doing something unrelated has no slot at all.
#
# So a description made of consecutive "Rank N: " clauses renders one line
# per rank, with the line for the rank you hold marked. Splitting only ever
# starts at the very beginning of a description, which is what keeps prose
# like "Rank 2 requires level 30" - present in 15 descriptions - inline;
# the last case here pins that. A clause also needs its colon, but no live
# description opens with "Rank N" without one, so that guard is defensive
# and nothing below exercises it.
#
# Conjurer's Efficiency (Magician) is the live example - 5 ranks, costs
# 3/5/6/6/6, each rank its own effect.
import os, sys, io, re
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
    page.select_option("#classSelect0", "Magician")
    page.wait_for_timeout(120)
    page.click('button[data-tab="classSlot0"]')
    ce = page.locator(".node", has=page.locator(".name", has_text="Conjurer's Efficiency"))
    ce.click()
    page.wait_for_timeout(60)
    desc = page.locator("#sidePanel .desc").first

    # --- Unbought: every rank is listed, none is current. ---
    html = desc.inner_html()
    print("rank 0 line count:", html.count('class="rank-line'))
    assert html.count('class="rank-line') == 5, "FAIL: expected one line per rank"
    assert "is-current-rank" not in html, "FAIL: nothing is the current rank at rank 0"

    # --- Each rank in turn marks its own line, and only its own. ---
    for rank in range(1, 6):
        page.click("#incBtn")
        page.wait_for_timeout(40)
        html = desc.inner_html()
        marked = re.findall(r'rank-line is-current-rank">Rank (\d+):', html)
        print(f"rank {rank}: marked line(s) = {marked}")
        assert marked == [str(rank)], f"FAIL: rank {rank} should mark exactly its own line, got {marked}"
        assert html.count('class="rank-line') == 5, "FAIL: all 5 lines must stay listed"

    # --- The lines are real line breaks on screen, not run-on prose. ---
    lines = [l for l in desc.inner_text().split("\n") if l.strip()]
    print("rendered line count:", len(lines))
    assert len(lines) == 5, f"FAIL: expected 5 rendered lines, got {len(lines)}"
    assert lines[0].startswith("Rank 1:") and lines[4].startswith("Rank 5:")

    # --- Browse is rank-agnostic: still one line per rank, none marked. ---
    page.click("#browseToggle")
    page.fill("#globalSearch", "Conjurer's Efficiency")
    page.wait_for_timeout(120)
    card = page.locator("#browseGrid .browse-card", has=page.locator(".name", has_text="Conjurer's Efficiency"))
    browse_html = card.locator(".desc").inner_html()
    print("browse line count:", browse_html.count('class="rank-line'))
    assert browse_html.count('class="rank-line') == 5
    assert "is-current-rank" not in browse_html, "FAIL: Browse has no current rank to mark"

    # --- An ordinary description mentioning a rank part-way through
    # ("Rank 2 requires level 30") must NOT be split: the clause list has
    # to start at the description's first character. ---
    page.fill("#globalSearch", "Unbound Life")
    page.wait_for_timeout(120)
    ul = page.locator("#browseGrid .browse-card", has=page.locator(".name", has_text="Unbound Life"))
    ul_html = ul.locator(".desc").inner_html()
    print("Unbound Life desc:", ul_html)
    assert "Rank 2 requires" in ul_html, "FAIL: expected the prose rank mention"
    assert "rank-line" not in ul_html, "FAIL: prose mentioning a rank must not be split into lines"
    print("PASS: per-rank clauses split into marked lines; prose rank mentions stay inline")

    print("ERRORS:", errors)
    assert not errors, f"FAIL: page errors {errors}"
    browser.close()
    print("ALL PASS")
