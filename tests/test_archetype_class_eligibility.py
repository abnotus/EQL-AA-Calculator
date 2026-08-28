# -*- coding: utf-8 -*-
# Archetype AAs are now gated by which classes can actually train them
# (data.src.js's eligibleClasses: ["ClassName", ...]) - eqlwiki confirms
# eligibility varies by class combo but documents no mapping table, so this
# was hand-compiled from raidloot.com's per-class Archetype listings and
# cross-checked 1:1 against eqlwiki's own 34-AA archetype list. Explicitly
# a first-pass "good enough for a framework" dataset, pending real in-game
# confirmation - if a class turns out wrong for a given AA, it's a one-line
# data.src.js fix, not a logic change.
#
# Mirrors test_class_rank_cap.py's structure closely: purchasing past the
# gate is blocked (structuralLockReason, same "+" button gating a prereq or
# level gate already uses), a rank already held that becomes ineligible
# after a class swap is NOT stripped - it persists, flagged with the exact
# same warning-sign machinery classRankCap's own held-rank invalidation
# already uses (heldRankInvalidReason -> .invalidated node class + the "No
# longer valid" side-panel line).
#
# Innate Camouflage (Druid, Ranger only; levelReq 40, already satisfied by
# the default charLevel of 50) is the test subject - not eligible under the
# app's default Bard/Beastlord/Berserker combo, giving a clean
# single-reason-locked starting state with no level gate to disentangle.
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

    node = page.locator(".node", has=page.locator(".name", has_text="Innate Camouflage"))
    node.click()

    # --- Default classes (Bard/Beastlord/Berserker) - none Druid or Ranger,
    # so the AA is locked outright, not just capped. ---
    print("node class list, default combo:", node.get_attribute("class"))
    assert "locked-classlock" in node.get_attribute("class")
    assert node.locator(".costtag.classlock-tag").count() == 1
    assert node.locator(".costtag.classlock-tag").inner_text() == "CLASS"
    block_line = page.locator("#sidePanel .req-line.warn").first
    print("block reason:", block_line.inner_text())
    assert block_line.inner_text() == "Requires one of: Druid, Ranger."
    # incBtn is only disabled at max rank/auto - a structural lock just adds
    # the .blocked class and no-ops the click (attemptIncrement's own
    # message is discarded by the click handler, not surfaced as a toast
    # here since applyAttempt only toasts on a truthy message from a
    # *changed: false* attempt with something to say - side panel already
    # shows the same text via block_line above).
    inc_btn = page.locator("#incBtn")
    assert "blocked" in inc_btn.get_attribute("class")
    page.click("#incBtn")
    page.wait_for_timeout(30)
    current = page.locator("#sidePanel .current")
    print("rank after blocked click:", current.inner_text())
    assert current.inner_text() == "0 / 1", "FAIL: purchase went through despite no qualifying class"
    print("PASS: locked outright under a non-qualifying default combo, with a clear class-specific reason")

    # --- Swap Class 3 to Ranger - a qualifying class unlocks it entirely. ---
    page.select_option("#classSelect2", "Ranger")
    page.wait_for_timeout(150)
    print("node class list with Ranger selected:", node.get_attribute("class"))
    assert "locked-classlock" not in node.get_attribute("class")
    assert node.locator(".costtag.classlock-tag").count() == 0
    page.click("#incBtn")
    page.wait_for_timeout(30)
    print("rank after buying with Ranger selected:", current.inner_text())
    assert current.inner_text() == "1 / 1"
    assert "maxed" in node.get_attribute("class")
    print("PASS: a qualifying class (Ranger) clears the lock entirely and the purchase goes through")

    # --- Swap Ranger back out for a non-qualifying class - the held rank
    # must persist (not get silently stripped), flagged the same way an
    # exceeded classRankCap already is. ---
    page.select_option("#classSelect2", "Cleric")
    page.wait_for_timeout(150)
    print("rank after swapping the qualifying class back out:", current.inner_text())
    assert current.inner_text() == "1 / 1", "FAIL: an owned/purchased rank must never be silently stripped by a class swap"
    node_classes = node.get_attribute("class")
    print("node class list:", node_classes)
    assert "invalidated" in node_classes
    assert "locked-classlock" not in node_classes, "FAIL: invalidated (held-rank) and locked-classlock (next-rank-blocked) are different states"
    invalid_line = page.locator("#sidePanel .req-line.warn").first
    print("invalid reason:", invalid_line.inner_text())
    assert invalid_line.inner_text() == "⚠ No longer valid: requires one of: Druid, Ranger, none of which are currently selected."
    print("PASS: the held rank persists across the class swap, flagged invalidated with a class-specific warning")

    # --- Both badges at once, on separate corners. Innate Camouflage can't
    # reach this state: it has only 1 rank, so once held it's maxed and
    # structuralLockReason is never consulted (renderTree only asks when
    # rank < aa.ranks). A multi-rank AA can be BOTH "next rank blocked by
    # class" (CLASS, top-left) and "held rank now ineligible" (⚠) at the
    # same time - they used to render stacked in the same corner. ---
    page.select_option("#classSelect2", "Warrior")
    page.wait_for_timeout(150)
    bop = page.locator(".node", has=page.locator(".name", has_text="Burst of Power"))
    bop.click()
    page.click("#incBtn")  # rank 1 of 3, legal while Warrior is slotted
    page.wait_for_timeout(60)
    page.select_option("#classSelect2", "Cleric")
    page.wait_for_timeout(200)
    bop_classes = bop.get_attribute("class")
    print("Burst of Power classes (held rank 1/3, no longer eligible):", bop_classes)
    assert "locked-classlock" in bop_classes and "invalidated" in bop_classes, \
        "FAIL: expected both the next-rank-blocked and held-rank-invalid states at once"
    tag_boxes = []
    for sel in (".costtag.classlock-tag", ".costtag.invalid-tag"):
        tag = bop.locator(sel)
        assert tag.count() == 1, f"FAIL: expected exactly one {sel}"
        tag_boxes.append((sel, tag.bounding_box()))
    (a_sel, a), (b_sel, b) = tag_boxes
    print(f"  {a_sel} box: {a}")
    print(f"  {b_sel} box: {b}")
    overlap = not (a["x"] + a["width"] <= b["x"] or b["x"] + b["width"] <= a["x"]
                   or a["y"] + a["height"] <= b["y"] or b["y"] + b["height"] <= a["y"])
    assert not overlap, "FAIL: the CLASS and ⚠ badges are rendering on top of each other - check their corner overrides in styles.css"
    print("PASS: the CLASS and ⚠ badges occupy separate corners when both apply")

    # Refund it so the rest of this file sees the state it did before. The
    # check-order section near the bottom uses Burst of Power too, and a
    # held-but-ineligible rank would put heldRankInvalidReason's "No longer
    # valid" line ahead of the block reason it asserts on.
    page.click("#decBtn")
    page.wait_for_timeout(60)
    assert page.locator("#sidePanel .current").inner_text() == "0 / 3"
    node.click()
    page.wait_for_timeout(60)

    # --- Progression tab: the row warns with the same shared machinery
    # prereqWarn/classCapWarn already use, wording distinct from
    # .step-inactive-warn (a different concept - a whole class swapped out
    # of a slot, not a specific AA's own restriction; archetype AAs are
    # never class-scoped, so they're always "active"). ---
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(150)
    prog_row = page.locator(".progression-row", has=page.locator(".step-name", has_text="Innate Camouflage"))
    assert prog_row.count() == 1
    print("Progression row classes:", prog_row.get_attribute("class"))
    assert "prereq-warn-row" in prog_row.get_attribute("class")
    step_warn = prog_row.locator(".step-warn")
    assert step_warn.count() == 1
    print("step-warn title:", step_warn.get_attribute("title"))
    assert step_warn.get_attribute("title") == "Requires one of: Druid, Ranger."
    assert prog_row.locator(".step-inactive-warn").count() == 0, "FAIL: this is the eligibility path, not the swapped-class-slot path"
    print("PASS: Progression flags the row with a class-specific warning, distinct from the inactive-class-slot warning")

    # --- Browse tab: always-visible reference info (Browse is "a searchable
    # reference independent of your current build"), warn-styled only when
    # the current combo doesn't qualify. ---
    page.click("#browseToggle")
    page.fill("#globalSearch", "Innate Camouflage")
    page.wait_for_timeout(150)
    browse_card = page.locator(".browse-card", has=page.locator(".name", has_text="Innate Camouflage"))
    assert browse_card.count() == 1
    eligible_info = browse_card.locator(".eligible-info")
    print("Browse eligible-info text/class (Cleric selected, not eligible):", eligible_info.inner_text(), eligible_info.get_attribute("class"))
    assert eligible_info.inner_text() == "Classes: Druid, Ranger"
    assert "warn" in eligible_info.get_attribute("class")

    page.select_option("#classSelect2", "Ranger")
    page.wait_for_timeout(150)
    eligible_info2 = browse_card.locator(".eligible-info")
    print("Browse eligible-info class (Ranger selected, eligible):", eligible_info2.get_attribute("class"))
    assert "warn" not in eligible_info2.get_attribute("class")
    print("PASS: Browse shows the eligible-classes reference text always, warn-styled only when the current combo doesn't qualify")
    page.fill("#globalSearch", "")
    page.click("#browseToggle")

    # --- Check-order invariant: classEligibility must be checked BEFORE
    # level, not after (structuralLockReason's own comment says exactly why -
    # a level-gated AA you also don't qualify for by class shouldn't
    # misleadingly read as "just wait"). Innate Camouflage can't exercise
    # this - its level-40 gate is already satisfied at the default charLevel
    # of 50, so there's no ordering to disentangle. Burst of Power
    # (Berserker/Warrior only, levelReq 46) can: drop below level 46 under a
    # combo that's also not Berserker/Warrior, and both gates apply at once. ---
    page.click('button[data-tab="archetype"]')
    page.fill("#levelInput", "30")
    page.locator("#levelInput").press("Tab")
    page.wait_for_timeout(100)
    # Slots are currently Bard/Beastlord/Ranger (Ranger from unlocking
    # Innate Camouflage above) - none Berserker or Warrior.
    bop_node = page.locator(".node", has=page.locator(".name", has_text="Burst of Power"))
    bop_node.click()
    bop_block = page.locator("#sidePanel .req-line.warn").first
    print("Burst of Power block reason, ineligible AND under level 46:", bop_block.inner_text())
    assert bop_block.inner_text() == "Requires one of: Berserker, Warrior.", \
        "FAIL: class-eligibility must be checked before level, not after - got the level message instead"
    assert "locked-classlock" in bop_node.get_attribute("class")
    print("PASS: class-eligibility wins over a simultaneous level gate, matching structuralLockReason's own stated check order")

    # --- Swap in a qualifying class while still under level 46 - the
    # eligibility check clears and the level gate takes over. Proves this is
    # a genuine ordered fallthrough (eligibility checked first, THEN level),
    # not a bug that happened to skip the level check entirely regardless of
    # class. ---
    page.select_option("#classSelect2", "Berserker")
    page.wait_for_timeout(150)
    bop_block2 = page.locator("#sidePanel .req-line.warn").first
    print("Burst of Power block reason, eligible but still under level 46:", bop_block2.inner_text())
    assert bop_block2.inner_text() == "Requires character level 46."
    assert "locked-classlock" not in bop_node.get_attribute("class")
    assert "locked" in bop_node.get_attribute("class")
    print("PASS: once eligible, the level gate correctly takes over - an ordered fallthrough, not eligibility masking every other gate")

    page.fill("#levelInput", "50")
    page.locator("#levelInput").press("Tab")
    page.wait_for_timeout(100)

    print("ERRORS:", errors)
    assert not errors

    # --- Boot-time toast: a saved build loaded with Innate Camouflage
    # already held and a non-qualifying combo selected must surface the
    # same invalidation notice a stale prerequisite or exceeded classRankCap
    # already gets on load (findInvalidatedPicks, main.js). ---
    page2 = browser.new_page(viewport={"width": 1400, "height": 900})
    errors2 = []
    page2.on("pageerror", lambda exc: errors2.append(str(exc)))
    dialogs2 = []
    page2.on("dialog", lambda d: (dialogs2.append(d.message), d.accept()))
    payload = {
        "v": 4,
        "selectedClasses": ["Bard", "Beastlord", "Berserker"],
        "charLevel": 50,
        "ranks": {"general": {}, "archetype": {"innate-camouflage": 1}, "special": {}, "classes": {}},
        "purchaseOrder": [{"scope": "archetype", "className": None, "key": "innate-camouflage"}],
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
    print("PASS: a saved build already ineligible for its class combo surfaces the same boot-time notice a stale prerequisite would")
    print("ERRORS2:", errors2)
    assert not errors2

    browser.close()
    print("ALL PASS")
