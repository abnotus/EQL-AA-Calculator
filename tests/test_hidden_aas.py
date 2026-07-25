# -*- coding: utf-8 -*-
# Hiding an AA (the Hide/Unhide toggle in the side panel and on each Browse
# card, plus the "Show Hidden" toggle next to the global search bar) is a
# personal decluttering display preference, not build state - see
# HIDDEN_STORAGE_KEY/isHidden/setHidden (state.js/logic.js). Three rules
# this covers:
#   1. A hidden AA is left out of the tree/Browse grids unless Show Hidden
#      is on - EXCEPT one you've actually spent points on, which always
#      stays visible (hiding only declutters what to look at, never
#      suppresses real build state). Summary/Progression never filter on
#      hidden at all - they're an accounting of what's picked, not a
#      browsing view.
#   2. It's stored under its own localStorage key, independent of the
#      build/share-link payload - never exported, never part of a share
#      link, and survives a reload on its own.
#   3. The "Show Hidden" toggle only shows up once there's something hidden
#      to reveal, and auto-resets to off once the last hidden AA is
#      unhidden (rather than staying silently "on" but invisible).
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

    toggle = page.locator("#showHiddenToggle")
    print("Show Hidden toggle visible with nothing hidden yet:", toggle.is_visible())
    assert not toggle.is_visible(), "FAIL: toggle shouldn't show up until something is actually hidden"

    # --- Hide an unranked AA from the side panel - disappears from the
    # tree, toggle appears. ---
    node = page.locator(".node", has=page.locator(".name", has_text="Packrat"))
    node.click()
    hide_btn = page.locator("#hideToggleBtn")
    print("side panel hide button label before hiding:", hide_btn.inner_text())
    # inner_text() reflects rendered CSS (text-transform: uppercase on
    # .hide-toggle-btn), not the raw textContent set in render.js.
    assert hide_btn.inner_text() == "HIDE"
    hide_btn.click()
    page.wait_for_timeout(80)
    print("Packrat node present right after hiding (rank 0):", node.count())
    assert node.count() == 0, "FAIL: a hidden, unranked AA should be gone from the tree"
    print("Show Hidden toggle visible once something is hidden:", toggle.is_visible())
    assert toggle.is_visible()
    print("PASS: hiding an unranked AA removes it from the tree and surfaces the Show Hidden toggle")

    # --- Deliberate decision (not an oversight - see the comment above the
    # hidden check in renderTree/renderBrowse): search does NOT bypass
    # hiding. Show Hidden is meant to be the one override switch. Covers
    # both the tree grid itself and the tab's own match-count badge
    # (countMatches - a hidden AA matching the query must not inflate the
    # badge while the grid shows nothing for it). ---
    page.fill("#globalSearch", "packrat")
    page.wait_for_timeout(150)
    print("Packrat node present while searching for it, hidden, Show Hidden off:", node.count())
    assert node.count() == 0, "FAIL: hidden AAs must stay hidden from search too, by design"
    general_tab = page.locator('button[data-tab="general"]')
    badge = general_tab.locator(".search-badge")
    print("General tab search-match badge while the only match is hidden:", badge.count(), badge.inner_text() if badge.count() else None)
    assert badge.count() == 0, "FAIL: tab badge counted a hidden match the grid isn't actually showing"
    page.fill("#globalSearch", "")
    page.wait_for_timeout(80)
    print("PASS: search doesn't surface a hidden AA, in the grid or the tab's match badge")

    # --- Show Hidden reveals it again, dimmed with a HIDDEN tag. ---
    toggle.click()
    page.wait_for_timeout(80)
    print("Packrat node present with Show Hidden on:", node.count())
    assert node.count() == 1
    print("node classes:", node.get_attribute("class"))
    assert "hidden-aa" in node.get_attribute("class")
    assert node.locator(".hidden-tag").count() == 1
    print("PASS: Show Hidden reveals a hidden AA, dimmed with its own tag")

    # Re-select it (tab-independent side panel selection was cleared by the
    # tree rebuild above) and confirm the button now reads Unhide.
    node.click()
    print("side panel hide button label while hidden:", hide_btn.inner_text())
    assert hide_btn.inner_text() == "UNHIDE"
    assert "active" in hide_btn.get_attribute("class")

    toggle.click()  # back off
    page.wait_for_timeout(80)
    print("Packrat gone again with Show Hidden off:", node.count())
    assert node.count() == 0
    print("PASS: Show Hidden off hides it again")

    # --- Browse tab: same AA, same hidden state (shared storage, not a
    # separate per-view flag) - hide/unhide from the card itself. ---
    page.click("#browseToggle")
    page.wait_for_timeout(150)
    browse_card = page.locator(".browse-card", has=page.locator(".name", has_text="Packrat"))
    print("Packrat card in Browse with Show Hidden off:", browse_card.count())
    assert browse_card.count() == 0
    toggle.click()
    page.wait_for_timeout(150)
    print("Packrat card visible with Show Hidden on:", browse_card.count())
    assert browse_card.count() == 1
    assert "hidden-aa" in browse_card.get_attribute("class")
    unhide_btn = browse_card.locator(".hide-toggle-btn")
    print("browse card button label:", unhide_btn.inner_text())
    assert unhide_btn.inner_text() == "UNHIDE"
    unhide_btn.click()
    page.wait_for_timeout(150)
    print("toggle auto-reset off once the last hidden AA was unhidden:", toggle.is_visible())
    assert not toggle.is_visible(), "FAIL: toggle should disappear (and showHidden reset) once nothing's hidden"
    print("PASS: unhiding from a Browse card works, and the toggle auto-resets once nothing's left hidden")

    # --- Ranked exception: a hidden AA you've spent points on always stays
    # visible, even with Show Hidden off. ---
    page.click('button[data-tab="general"]')
    node2 = page.locator(".node", has=page.locator(".name", has_text="Alchemy Mastery"))
    node2.click()
    page.locator("#hideToggleBtn").click()
    page.wait_for_timeout(80)
    print("Alchemy Mastery gone once hidden (rank 0):", node2.count())
    assert node2.count() == 0
    page.click("#incBtn")
    page.wait_for_timeout(80)
    print("Alchemy Mastery reappears once ranked, despite being hidden:", node2.count())
    assert node2.count() == 1, "FAIL: a hidden AA you've actually spent points on must never disappear"
    assert "hidden-aa" in node2.get_attribute("class"), "FAIL: still flagged as hidden even though shown as an exception"
    print("PASS: a ranked-but-hidden AA stays visible regardless of Show Hidden")

    # Summary/Progression never filter on hidden at all - they show the
    # actual picked state, not a browsing view.
    page.click('button[data-tab="summary"]')
    page.wait_for_timeout(150)
    summary_card = page.locator("#summaryContent .browse-card", has=page.locator(".name", has_text="Alchemy Mastery"))
    print("Alchemy Mastery shows in Summary despite being hidden:", summary_card.count())
    assert summary_card.count() == 1
    print("PASS: Summary shows a hidden-but-picked AA normally, no filtering there at all")

    # --- Persistence: hidden state survives a reload, on its own storage
    # key, and is never part of the exported build text. ---
    hidden_storage = page.evaluate("localStorage.getItem('eql_aa_hidden_v1')")
    print("hidden storage after hiding Alchemy Mastery:", hidden_storage)
    assert hidden_storage and "alchemy-mastery" in hidden_storage
    page.click("#exportBtn")
    page.wait_for_timeout(100)
    export_text = page.locator("#exportText").input_value()
    print("hidden info absent from export text:", "alchemy-mastery" not in export_text.lower() and "hidden" not in export_text.lower())
    assert "hidden" not in export_text.lower(), "FAIL: hidden state must never leak into the export payload"
    page.click("#closeExportBtn")
    page.wait_for_timeout(80)

    page.reload()
    page.wait_for_selector("#treeWrap .node")
    page.click('button[data-tab="general"]')
    node2b = page.locator(".node", has=page.locator(".name", has_text="Alchemy Mastery"))
    print("Alchemy Mastery still shown (ranked) and still flagged hidden after reload:", node2b.count(), "hidden-aa" in (node2b.get_attribute("class") or ""))
    assert node2b.count() == 1 and "hidden-aa" in node2b.get_attribute("class")
    print("PASS: hidden state persists across a reload on its own storage key, and never leaks into export text")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
