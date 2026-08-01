# -*- coding: utf-8 -*-
# Swapping a class slot to a genuinely different class used to wipe that
# class's ranks/purchaseOrder entirely (clearClassData, after a confirm()
# dialog if any points were spent) - it no longer does. The old class's
# picks simply stop being "active" (resolveEntryCategory/isEntryActive,
# logic.js): invisible in the tree/Progression, but still fully intact,
# still counted in spentPoints()'s now-lifetime total, still part of the
# build payload, and visible instead in the new Other Classes tab
# (renderOtherClasses, render.js) - grouped by class with its own subtotal.
#
# Two totals are DELIBERATELY allowed to diverge once any inactive-class
# spending exists: the topbar's Points Spent (a genuine lifetime total
# across every class ever picked) vs. Progression's own running total
# (scoped to just the current 3 classes' click history, computed the same
# way it always was - see computeProgressionSteps' active-gated stepCost).
# Both sides get a note pointing at the split (renderTopbar's tooltip,
# Progression's own toolbar note) rather than leaving it implicit.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    dialogs = []
    page.on("dialog", lambda d: (dialogs.append(d.message), d.accept()))
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # --- Spend on class slot 0's first two AAs, in a specific order/rank
    # so "reappears exactly as left" is actually checkable later. ---
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    class0_nodes = page.locator(".node")
    node_a = class0_nodes.nth(0)
    node_a_name = node_a.locator(".name").inner_text()
    node_a.click()
    page.click("#incBtn")
    page.wait_for_timeout(60)
    page.click("#incBtn")
    page.wait_for_timeout(60)  # node A at rank 2
    node_b = class0_nodes.nth(1)
    node_b_name = node_b.locator(".name").inner_text()
    node_b.click()
    page.click("#incBtn")
    page.wait_for_timeout(60)  # node B at rank 1

    spent_before = page.locator("#spentValue").inner_text()
    print("spentValue before swap:", spent_before)

    old_class = page.locator("#classSelect0").input_value()
    class0_select = page.locator("#classSelect0")
    options = class0_select.locator("option").all_text_contents()
    other_slots = [page.locator("#classSelect1").input_value(), page.locator("#classSelect2").input_value()]
    new_class = next(o for o in options if o != old_class and o not in other_slots)

    # --- Swap: no confirm dialog anymore, no data loss. ---
    class0_select.select_option(new_class)
    page.wait_for_timeout(150)
    print("dialogs fired during swap (should be none):", dialogs)
    assert not dialogs, "FAIL: swapping a class with spent points should no longer prompt a confirm dialog"

    spent_after_swap = page.locator("#spentValue").inner_text()
    print("spentValue after swap (lifetime total - should be UNCHANGED):", spent_after_swap)
    assert spent_after_swap == spent_before, "FAIL: spentPoints() is a lifetime total now, swapping must not change it"

    # --- Tree: the swapped-out class's picks are gone from the (now
    # different) class-slot-0 tree - nothing to assert about node_a/node_b
    # by name here since the tree now shows an entirely different class's
    # AAs, but the slot itself should show 0 selected/maxed nodes matching
    # the old names. ---
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    stale_nodes = page.locator(".node", has=page.locator(".name", has_text=node_a_name))
    print("old class's node A still present under the new class's tree:", stale_nodes.count())
    assert stale_nodes.count() == 0

    # --- Progression: nothing from the old class shows up inline anymore. ---
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(150)
    prog_a = page.locator(".progression-row", has=page.locator(".step-name", has_text=node_a_name))
    prog_b = page.locator(".progression-row", has=page.locator(".step-name", has_text=node_b_name))
    print("Progression rows for the swapped-out class's picks (should be 0):", prog_a.count(), prog_b.count())
    assert prog_a.count() == 0 and prog_b.count() == 0

    # Progression's own toolbar note should point at the divergence.
    note = page.locator("#otherClassesNote")
    print("Progression's other-classes note:", note.is_visible(), note.inner_text())
    assert note.is_visible()
    assert "Other Classes" in note.inner_text()

    # --- Other Classes tab: both picks show up, grouped under the old
    # class's name, with the right subtotal. ---
    page.click('button[data-tab="otherClasses"]')
    page.wait_for_timeout(150)
    section_title = page.locator("#otherClassesContent .summary-section-title", has_text=old_class)
    print("Other Classes section for the old class:", section_title.count())
    assert section_title.count() == 1
    oc_card_a = page.locator("#otherClassesContent .browse-card", has=page.locator(".name", has_text=node_a_name))
    oc_card_b = page.locator("#otherClassesContent .browse-card", has=page.locator(".name", has_text=node_b_name))
    print("Other Classes cards present:", oc_card_a.count(), oc_card_b.count())
    assert oc_card_a.count() == 1 and oc_card_b.count() == 1
    a_rank_text = oc_card_a.locator(".cat").inner_text()
    print("node A's rank shown in Other Classes:", a_rank_text)
    # inner_text() reflects rendered CSS (text-transform: uppercase on
    # .browse-card .top .cat), not the raw textContent set in render.js.
    assert a_rank_text.startswith("RANK 2/")
    subtotal_text = page.locator("#otherClassesContent .other-classes-subtotal").first.inner_text()
    print("Other Classes subtotal line:", subtotal_text)
    assert str(int(spent_after_swap)) + " point" in subtotal_text or spent_after_swap in subtotal_text

    # Tab badge count reflects the picks.
    other_classes_tab = page.locator('button[data-tab="otherClasses"]')
    badge_count_text = other_classes_tab.locator(".count").inner_text()
    print("Other Classes tab badge:", badge_count_text)
    assert badge_count_text == "(2)"

    # --- Export: the inactive class's data round-trips (always included,
    # no opt-in checkbox needed - it's just more of the same ranks/
    # purchaseOrder payload every build already carries). ---
    page.click("#exportBtn")
    page.wait_for_timeout(100)
    export_text = page.locator("#exportText").input_value()
    print("export text mentions the old class's picks:", node_a_name in export_text or "BUILD_CODE" in export_text)
    # The export text embeds a compact code rather than raw names, but the
    # share link (built from the exact same payload) round-trips through a
    # fresh page to prove the data survives - more meaningful than grepping
    # the opaque code string.
    share_link = page.locator("#shareLinkInput").input_value()
    print("share link:", share_link)
    page.click("#closeExportBtn")
    page.wait_for_timeout(80)

    page2 = browser.new_page(viewport={"width": 1400, "height": 900})
    page2.on("dialog", lambda d: d.accept())
    page2.goto(share_link)
    page2.wait_for_selector("#treeWrap .node")
    page2.wait_for_timeout(200)
    page2.click('button[data-tab="otherClasses"]')
    page2.wait_for_timeout(150)
    reloaded_a = page2.locator("#otherClassesContent .browse-card", has=page2.locator(".name", has_text=node_a_name))
    reloaded_b = page2.locator("#otherClassesContent .browse-card", has=page2.locator(".name", has_text=node_b_name))
    print("reloaded-from-share-link Other Classes cards present:", reloaded_a.count(), reloaded_b.count())
    assert reloaded_a.count() == 1 and reloaded_b.count() == 1
    print("PASS: the inactive class's picks round-trip through a share link")
    page2.close()

    # --- Swap back: picks reappear in the tree/Progression exactly as
    # left (rank 2 for A, rank 1 for B). ---
    page.click('button[data-tab="classSlot0"]')
    class0_select.select_option(old_class)
    page.wait_for_timeout(150)
    restored_a = page.locator(".node", has=page.locator(".name", has_text=node_a_name))
    restored_b = page.locator(".node", has=page.locator(".name", has_text=node_b_name))
    rank_a = restored_a.locator(".ranktext").inner_text()
    rank_b = restored_b.locator(".ranktext").inner_text()
    print("ranks after swapping back:", rank_a, "|", rank_b)
    assert rank_a.strip().startswith("2 /")
    assert rank_b.strip().startswith("1 /")

    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(150)
    prog_a2 = page.locator(".progression-row", has=page.locator(".step-name", has_text=node_a_name))
    prog_b2 = page.locator(".progression-row", has=page.locator(".step-name", has_text=node_b_name))
    print("Progression rows restored after swapping back:", prog_a2.count(), prog_b2.count())
    assert prog_a2.count() == 2  # rank 1 and rank 2 of node A
    assert prog_b2.count() == 1
    note_after = page.locator("#otherClassesNote")
    print("other-classes note hidden again once nothing's inactive:", note_after.is_visible())
    assert not note_after.is_visible()

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
