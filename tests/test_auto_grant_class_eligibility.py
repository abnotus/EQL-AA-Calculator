# -*- coding: utf-8 -*-
# An archetype/general AA that's both auto: true AND has eligibleClasses
# (e.g. Intimidation: Bard/Berserker/Monk/Rogue) used to skip class
# eligibility entirely in the free-grant path - effectiveRankScoped only
# gated on level, so an ineligible class combo still showed it as granted
# (rank N/N, "AUTO" tag, "always active" side panel text) and it counted
# toward Summary/exports as owned. A class-scoped auto AA never had this
# problem (classActive already gates it), so it went unnoticed until a
# second archetype auto AA (Point Blank Fire) got added and a review
# caught it. Intimidation is the regression subject here since it's a
# permanent part of the dataset, unlike Point Blank Fire which turned out
# to need manual purchase despite its 0 cost and isn't auto at all.
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
    page.click('button[data-tab="archetype"]')

    node = page.locator(".node", has=page.locator(".name", has_text="Intimidation"))

    # --- Default classes (Bard/Beastlord/Berserker) - Bard and Berserker
    # both qualify, so the free grant is active. ---
    print("node class list, default (eligible) combo:", node.get_attribute("class"))
    assert "auto" in node.get_attribute("class")
    assert "locked-classlock" not in node.get_attribute("class")
    assert node.locator(".ranktext").inner_text() == "1 / 1"
    assert node.locator(".costtag.auto-tag").count() == 1
    print("PASS: eligible combo shows the free grant as active, AUTO tag, rank 1/1")

    # --- Swap all 3 slots to a combo with none of Intimidation's eligible
    # classes - the free grant must NOT apply. ---
    page.select_option("#classSelect0", "Cleric")
    page.select_option("#classSelect1", "Druid")
    page.select_option("#classSelect2", "Wizard")
    page.wait_for_timeout(150)
    node_classes = node.get_attribute("class")
    print("node class list, ineligible combo:", node_classes)
    assert "auto" not in node_classes.split()
    assert "locked-classlock" in node_classes
    assert node.locator(".ranktext").inner_text() == "0 / 1", \
        "FAIL: an ineligible class combo must not receive an auto-granted rank"
    assert node.locator(".costtag.classlock-tag").count() == 1
    assert node.locator(".costtag.classlock-tag").inner_text() == "CLASS"
    assert node.locator(".costtag.auto-tag").count() == 0
    print("PASS: ineligible combo shows 0/1, a CLASS tag, no AUTO tag")

    node.click()
    block_line = page.locator("#sidePanel .req-line.warn").first
    print("side panel line, ineligible combo:", block_line.inner_text())
    assert block_line.inner_text() == "Requires one of: Bard, Berserker, Monk, Rogue."
    assert "always active" not in page.locator("#sidePanel").inner_text()
    print("PASS: side panel states the class requirement instead of claiming it's already active")

    # --- Must not count toward Summary/exports while ineligible. ---
    page.click('button[data-tab="summary"]')
    page.wait_for_timeout(150)
    summary_card = page.locator("#summaryContent .browse-card", has=page.locator(".name", has_text="Intimidation"))
    print("Summary card count while ineligible:", summary_card.count())
    assert summary_card.count() == 0, "FAIL: an ungranted auto AA must not appear in Summary as owned"
    print("PASS: Summary excludes it while the combo is ineligible")

    # --- Swap a qualifying class back in - the free grant returns. ---
    page.click('button[data-tab="archetype"]')
    page.select_option("#classSelect0", "Bard")
    page.wait_for_timeout(150)
    node_classes2 = node.get_attribute("class")
    print("node class list, class swapped back to eligible:", node_classes2)
    assert "auto" in node_classes2.split()
    assert "locked-classlock" not in node_classes2
    assert node.locator(".ranktext").inner_text() == "1 / 1"
    print("PASS: swapping a qualifying class back in restores the free grant")

    print("ERRORS:", errors)
    assert not errors

    browser.close()
    print("ALL PASS")
