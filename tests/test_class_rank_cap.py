# -*- coding: utf-8 -*-
# Class-based rank caps (data.src.js's classRankCap: { default, byClass }) -
# Steadfast Will is the one live example: capped at rank 6 unless one of
# your 3 selected classes is Warrior/Paladin/Shadow Knight (rank 8) or
# Ranger (rank 7). Tri-class combines rather than switches, so ANY of the 3
# selected classes granting a higher cap applies (see classRankCapFor's own
# comment) - not some notion of one "active" class the tool doesn't track at
# all. Purchasing past the current cap is blocked (structuralLockReason,
# same "+" button gating as a prereq or level gate); a rank already held
# that exceeds the cap after a class swap is NOT stripped - it persists,
# flagged with the exact same warning-sign machinery already used for a
# prerequisite going stale (heldRankInvalidReason -> .invalidated node
# class + the "No longer valid" side-panel line), plus a dimmed hatched
# segment on the tree node's rank bar for the portion beyond the cap.
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

    node = page.locator(".node", has=page.locator(".name", has_text="Steadfast Will"))
    node.click()

    # --- Default classes (Bard/Beastlord/Berserker) - none tank or Ranger,
    # so the cap is the flat default of 6, even though the AA itself goes to
    # rank 8. ---
    for _ in range(6):
        page.click("#incBtn")
        page.wait_for_timeout(15)
    current = page.locator("#sidePanel .current")
    print("rank after 6 clicks:", current.inner_text())
    assert current.inner_text() == "6 / 8"

    page.click("#incBtn")  # 7th click - must be blocked
    page.wait_for_timeout(30)
    print("rank after blocked 7th click:", current.inner_text())
    assert current.inner_text() == "6 / 8", "FAIL: purchase went through past the class cap"
    block_line = page.locator("#sidePanel .req-line.warn").first
    print("block reason:", block_line.inner_text())
    assert block_line.inner_text() == "Capped at rank 6 for your currently selected classes."
    print("node class list at the cap:", node.get_attribute("class"))
    assert "locked" in node.get_attribute("class")
    assert "invalidated" not in node.get_attribute("class"), "FAIL: sitting exactly at the cap isn't a violation, shouldn't warn"
    assert node.locator(".fill-capped").count() == 0, "FAIL: no dimmed segment expected while rank == cap"
    print("PASS: purchasing is blocked exactly at the default cap (6), with a clear reason, no false warning")

    # --- Swap Class 3 to Warrior (a tank) - cap rises to 8, both remaining
    # ranks become purchasable. ---
    page.select_option("#classSelect2", "Warrior")
    page.wait_for_timeout(150)
    assert current.inner_text() == "6 / 8", "FAIL: rank should be untouched by the class swap itself"
    for _ in range(2):
        page.click("#incBtn")
        page.wait_for_timeout(15)
    print("rank after buying through to 8 with Warrior selected:", current.inner_text())
    assert current.inner_text() == "8 / 8"
    assert "maxed" in node.get_attribute("class") and "invalidated" not in node.get_attribute("class")
    print("PASS: a qualifying class (Warrior) raises the cap and rank 8 becomes purchasable")

    # --- Swap Warrior back out for a non-qualifying class - rank 8 must
    # persist (not get silently stripped), flagged as invalidated with the
    # same warning-sign machinery a stale prerequisite already uses, plus a
    # dimmed rank-bar segment for the 2 ranks (7-8) beyond the new cap of 6
    # (2 of 8 total ranks = 25% of the bar's width). ---
    page.select_option("#classSelect2", "Cleric")
    page.wait_for_timeout(150)
    print("rank after swapping the qualifying class back out:", current.inner_text())
    assert current.inner_text() == "8 / 8", "FAIL: an owned/purchased rank must never be silently stripped by a class swap"
    node_classes = node.get_attribute("class")
    print("node class list:", node_classes)
    assert "invalidated" in node_classes
    invalid_line = page.locator("#sidePanel .req-line.warn").first
    print("invalid reason:", invalid_line.inner_text())
    assert invalid_line.inner_text() == "⚠ No longer valid: exceeds the rank 6 cap for your currently selected classes."
    fill_capped = node.locator(".fill-capped")
    assert fill_capped.count() == 1
    style = fill_capped.get_attribute("style")
    print("fill-capped style:", style)
    assert "width:25%" in style, f"FAIL: expected the capped segment to cover 2/8 = 25% of the bar, got {style}"
    print("PASS: rank 8 persists across the class swap, flagged invalidated with the exact prereq-style warning, and the bar shows the excess dimmed")

    # --- Ranger gets its own distinct cap (7, not the tank classes' 8) -
    # confirms byClass isn't just a boolean tank/not-tank check. ---
    page.select_option("#classSelect2", "Ranger")
    page.wait_for_timeout(150)
    print("node class list with Ranger selected (rank 8 still exceeds Ranger's cap of 7):", node.get_attribute("class"))
    assert "invalidated" in node.get_attribute("class"), "FAIL: Ranger's cap is 7, not 8 - rank 8 should still be flagged"
    invalid_line2 = page.locator("#sidePanel .req-line.warn").first
    print("invalid reason with Ranger selected:", invalid_line2.inner_text())
    assert invalid_line2.inner_text() == "⚠ No longer valid: exceeds the rank 7 cap for your currently selected classes."
    print("PASS: Ranger's own cap (7) is distinct from the tank classes' cap (8), not just a flat tank/non-tank boolean")

    print("ERRORS:", errors)
    assert not errors

    # --- Boot-time toast: a saved build loaded with Steadfast Will already
    # at rank 8 and no qualifying class selected must surface the same
    # invalidation notice a stale prerequisite already gets on load
    # (findInvalidatedPicks, main.js). ---
    page2 = browser.new_page(viewport={"width": 1400, "height": 900})
    errors2 = []
    page2.on("pageerror", lambda exc: errors2.append(str(exc)))
    dialogs2 = []
    page2.on("dialog", lambda d: (dialogs2.append(d.message), d.accept()))
    payload = {
        "v": 4,
        "selectedClasses": ["Bard", "Beastlord", "Berserker"],
        "charLevel": 50,
        "ranks": {"general": {"steadfast-will": 8}, "archetype": {}, "special": {}, "classes": {}},
        "purchaseOrder": [{"scope": "general", "className": None, "key": "steadfast-will"}] * 8,
        "waypoints": [],
    }
    import json
    page2.add_init_script(f"""
        localStorage.setItem('eql_aa_builder_v1', {json.dumps(json.dumps(payload))});
    """)
    page2.goto(BASE)
    page2.wait_for_selector("#treeWrap .node")
    page2.wait_for_timeout(200)
    print("boot-time dialogs/toasts:", dialogs2)
    toast = page2.locator("#toast")
    toast_text = toast.inner_text() if toast.count() and toast.is_visible() else ""
    print("toast text:", toast_text)
    assert "1 pick" in toast_text and "no longer meets its requirements" in toast_text, \
        f"FAIL: expected the boot-time invalidation notice, got: {toast_text!r}"
    print("PASS: a saved build already exceeding the class cap surfaces the same boot-time notice a stale prerequisite would")

    print("ERRORS:", errors2)
    assert not errors2
    page2.close()

    browser.close()
    print("ALL PASS")
