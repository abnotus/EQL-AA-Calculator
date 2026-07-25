# -*- coding: utf-8 -*-
# Owned progress (state.owned) is character-global, independent of the plan
# and independent of which classes are currently active - that was already
# true before this session's Other Classes feature (see OWNED_STORAGE_KEY's
# own comment, state.js), but a class swap no longer wiping ranks/
# purchaseOrder (events.js) means owned marks on an inactive class are now
# a routine, reachable case instead of a rare one. Three things this covers,
# each pinned against raw localStorage as well as the UI so a display-only
# bug (correct data, wrong render) can't slip past an assertion that only
# checks the DOM:
#   1. Owned status and the Progression toolbar's "N owned, M to go" summary
#      both survive a class swap untouched (ownedPoints(), logic.js, is a
#      lifetime total for exactly this reason - see its own comment).
#   2. Clear Owned wipes owned globally (including an inactive class) without
#      touching the plan itself - the AA's held rank survives.
#   3. Reset Build's default (keep owned) trims an INACTIVE class's plan down
#      to its owned watermark too, not just the active 3 - performReset
#      (logic.js) already iterated every class in state.ranks.classes before
#      this feature existed, so this is confirming existing generic behavior
#      still holds now that inactive-class data is actually reachable in
#      practice, not verifying something newly built.
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8743/index.html"


def swap_class0_to_something_else(page):
    select = page.locator("#classSelect0")
    old = select.input_value()
    options = select.locator("option").all_text_contents()
    others = [page.locator("#classSelect1").input_value(), page.locator("#classSelect2").input_value()]
    new = next(o for o in options if o != old and o not in others)
    select.select_option(new)
    page.wait_for_timeout(150)
    return old, new


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # --- Buy class-slot-0's first AA to rank 1, mark it owned. ---
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    node = page.locator(".node").first
    node_name = node.locator(".name").inner_text()
    node.click()
    page.click("#incBtn")
    page.wait_for_timeout(80)

    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(150)
    page.locator(".progression-row").first.locator(".step-own").click()
    page.wait_for_timeout(80)
    owned_before = page.locator("#ownedSummary").inner_text()
    print("owned summary before swap:", owned_before)
    assert owned_before == "3 pts owned, 0 to go" or owned_before.endswith("owned, 0 to go")

    # --- Swap the class away - owned status/summary must survive
    # untouched (it's global, and now a lifetime figure - see logic.js's
    # ownedPoints). ---
    old_class, _ = swap_class0_to_something_else(page)
    owned_after_swap = page.locator("#ownedSummary").inner_text()
    print("owned summary after swap (should be unchanged):", owned_after_swap)
    assert owned_after_swap == owned_before, "FAIL: owned/to-go must be a lifetime figure, unaffected by which classes are active"

    clear_owned_btn = page.locator("#clearOwnedBtn")
    print("Clear Owned enabled after swap (something is owned):", clear_owned_btn.get_attribute("disabled") is None)
    assert clear_owned_btn.get_attribute("disabled") is None
    print("PASS: owned status and its summary survive a class swap")

    # --- Clear Owned: wipes owned globally, including the now-inactive
    # class, without touching the plan itself. ---
    clear_owned_btn.click()
    page.wait_for_timeout(150)
    owned_after_clear = page.locator("#ownedSummary").inner_text()
    print("owned summary after Clear Owned:", owned_after_clear)
    assert owned_after_clear.startswith("0 pt"), f"FAIL: expected owned to zero out, got {owned_after_clear!r}"
    print("Clear Owned disabled again once nothing's owned:", clear_owned_btn.get_attribute("disabled") is not None)
    assert clear_owned_btn.get_attribute("disabled") is not None

    owned_storage = page.evaluate("localStorage.getItem('eql_aa_owned_v1')")
    print("raw owned storage after Clear Owned:", owned_storage)
    owned_parsed = json.loads(owned_storage)
    assert owned_parsed["owned"]["classes"] == {}, "FAIL: Clear Owned should wipe every class's owned watermark, including inactive ones"

    build_storage = page.evaluate("localStorage.getItem('eql_aa_builder_v1')")
    print("raw build storage after Clear Owned (plan must survive):", build_storage)
    build_parsed = json.loads(build_storage)
    assert build_parsed["ranks"]["classes"].get(old_class, {}), "FAIL: Clear Owned must never touch the plan itself"
    print("PASS: Clear Owned wipes owned globally (including the inactive class) without touching the plan")

    # Swap back and confirm the plan (not owned) survived, via the actual
    # rendered tree - not just raw storage - so a display-only bug can't
    # slip past.
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    page.locator("#classSelect0").select_option(old_class)
    page.wait_for_timeout(200)
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    restored = page.locator(".node", has=page.locator(".name", has_text=node_name))
    rank_text = restored.locator(".ranktext").inner_text()
    print("rank after Clear Owned + swap back:", rank_text)
    assert rank_text.strip().startswith("1 /")

    print("ERRORS so far:", errors)
    assert not errors

    # --- Fresh page: Reset Build's default (keep owned) trims an INACTIVE
    # class's plan down to its owned watermark, same as it already does for
    # an active one - performReset iterates every class in
    # state.ranks.classes, not just the active 3, and always has. ---
    page2 = browser.new_page(viewport={"width": 1400, "height": 900})
    errors2 = []
    page2.on("pageerror", lambda exc: errors2.append(str(exc)))
    page2.on("dialog", lambda d: d.accept())
    page2.goto(BASE)
    page2.wait_for_selector("#treeWrap .node")

    page2.click('button[data-tab="classSlot0"]')
    page2.wait_for_timeout(100)
    n2 = page2.locator(".node").first
    n2_name = n2.locator(".name").inner_text()
    n2.click()
    page2.click("#incBtn")
    page2.wait_for_timeout(60)
    page2.click("#incBtn")
    page2.wait_for_timeout(60)  # rank 2

    page2.click('button[data-tab="progression"]')
    page2.wait_for_timeout(150)
    page2.locator(".progression-row").nth(0).locator(".step-own").click()  # own rank 1 only
    page2.wait_for_timeout(80)

    old_class2, _ = swap_class0_to_something_else(page2)

    page2.click("#resetBtn")
    page2.wait_for_timeout(100)
    assert not page2.locator("#resetClearOwnedCheckbox").is_checked()
    page2.click("#confirmResetBtn")
    page2.wait_for_timeout(150)

    build_after_reset = json.loads(page2.evaluate("localStorage.getItem('eql_aa_builder_v1')"))
    print("ranks.classes after Reset Build (keep owned), inactive class trimmed to 1:", build_after_reset["ranks"]["classes"])
    assert build_after_reset["ranks"]["classes"][old_class2][list(build_after_reset["ranks"]["classes"][old_class2].keys())[0]] == 1, \
        "FAIL: Reset Build (keep owned) should trim an inactive class's plan to its owned watermark too"

    page2.click('button[data-tab="classSlot0"]')
    page2.wait_for_timeout(100)
    page2.locator("#classSelect0").select_option(old_class2)
    page2.wait_for_timeout(200)
    page2.click('button[data-tab="classSlot0"]')
    page2.wait_for_timeout(100)
    restored2 = page2.locator(".node", has=page2.locator(".name", has_text=n2_name))
    rank_after_reset = restored2.locator(".ranktext").inner_text()
    print("rendered rank after Reset Build (keep owned) + swap back:", rank_after_reset)
    assert rank_after_reset.strip().startswith("1 /"), f"FAIL: expected the tree to show the trimmed rank (1), got {rank_after_reset}"
    print("PASS: Reset Build (keep owned) trims an inactive class's plan to its owned watermark, same as an active one")

    print("ERRORS:", errors2)
    assert not errors2

    # --- Fresh page: Reset Build with "clear owned too" wipes an inactive
    # class's plan AND owned down to nothing. ---
    page3 = browser.new_page(viewport={"width": 1400, "height": 900})
    errors3 = []
    page3.on("pageerror", lambda exc: errors3.append(str(exc)))
    page3.on("dialog", lambda d: d.accept())
    page3.goto(BASE)
    page3.wait_for_selector("#treeWrap .node")

    page3.click('button[data-tab="classSlot0"]')
    page3.wait_for_timeout(100)
    n3 = page3.locator(".node").first
    n3.click()
    page3.click("#incBtn")
    page3.wait_for_timeout(60)

    page3.click('button[data-tab="progression"]')
    page3.wait_for_timeout(150)
    page3.locator(".progression-row").first.locator(".step-own").click()
    page3.wait_for_timeout(80)

    old_class3, _ = swap_class0_to_something_else(page3)

    page3.click("#resetBtn")
    page3.wait_for_timeout(100)
    page3.locator("#resetClearOwnedCheckbox").check()
    page3.click("#confirmResetBtn")
    page3.wait_for_timeout(150)

    build_after_full_reset = json.loads(page3.evaluate("localStorage.getItem('eql_aa_builder_v1')"))
    owned_after_full_reset = json.loads(page3.evaluate("localStorage.getItem('eql_aa_owned_v1')"))
    print("ranks.classes after full Reset Build:", build_after_full_reset["ranks"]["classes"])
    print("owned.classes after full Reset Build:", owned_after_full_reset["owned"]["classes"])
    assert old_class3 not in build_after_full_reset["ranks"]["classes"] or not build_after_full_reset["ranks"]["classes"][old_class3]
    assert owned_after_full_reset["owned"]["classes"] == {}
    print("PASS: Reset Build with 'clear owned too' wipes an inactive class's plan and owned status alike")

    print("ERRORS:", errors3)
    assert not errors3

    browser.close()
    print("ALL PASS")
