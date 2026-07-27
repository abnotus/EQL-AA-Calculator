# -*- coding: utf-8 -*-
# The "Move To" popover (a "..." button per Progression row, opening a
# small anchored menu - the first lightweight popover in the app, see
# moveMenuHtml/wireProgressionDropZone's outside-click listener in
# render.js) - a community suggestion (drew_atx) for reordering very long
# lists without dragging: jump a row to the top/bottom of the list, the
# top/bottom of any waypoint section (not just the one it's currently in),
# or a specific numeric position.
#
# Scoping this out surfaced a real, separate bug worth its own coverage
# here: step-num (the row number shown per row) used to render the
# absolute state.purchaseOrder index (s.index + 1), which can show gaps
# once an inactive class's entries can sit between active ones without
# being wiped (v1.8.0) - "1, 3" with no visible "2". Fixed by introducing
# s.visiblePos (1-indexed among the rows actually rendered), which both
# step-num and every Move To target are now defined against.
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

    # --- Buy 5 general AAs (click order determines the initial sequence). ---
    page.click('button[data-tab="general"]')
    nodes = page.locator(".node")
    for i in range(5):
        nodes.nth(i).click()
        page.click("#incBtn")
        page.wait_for_timeout(60)

    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(150)
    rows = page.locator(".progression-row")
    names0 = [rows.nth(i).locator(".step-name").inner_text() for i in range(rows.count())]
    print("initial order:", names0)
    assert rows.count() == 5

    # --- No waypoints yet: the menu should only offer Top/Bottom of list,
    # no section group. ---
    rows.first.locator(".step-move").click()
    page.wait_for_timeout(80)
    items0 = rows.first.locator(".move-menu-item").all_text_contents()
    print("menu items with no waypoints:", items0)
    assert items0 == ["Top of list", "Bottom of list"], "FAIL: section options must be absent entirely when there are no waypoints"
    page.keyboard.press("Escape")
    page.wait_for_timeout(80)
    print("PASS: no waypoints -> no section group in the menu")

    # --- Bottom of list: move the first row to the end. ---
    first_name = names0[0]
    rows_a = page.locator(".progression-row")
    rows_a.first.locator(".step-move").click()
    page.wait_for_timeout(80)
    rows_a.first.locator(".move-menu-item", has_text="Bottom of list").click()
    page.wait_for_timeout(100)
    rows_b = page.locator(".progression-row")
    names_b = [rows_b.nth(i).locator(".step-name").inner_text() for i in range(rows_b.count())]
    print("order after 'Bottom of list' on the original first row:", names_b)
    assert names_b[-1] == first_name, "FAIL: expected the row to land at the very end"
    assert names_b[:-1] == names0[1:], "FAIL: the rest of the order should just shift up, undisturbed"
    print("PASS: Bottom of list")

    # --- Top of list: move it right back. ---
    rows_c = page.locator(".progression-row")
    last_row = rows_c.last
    last_row.locator(".step-move").click()
    page.wait_for_timeout(80)
    last_row.locator(".move-menu-item", has_text="Top of list").click()
    page.wait_for_timeout(100)
    rows_d = page.locator(".progression-row")
    names_d = [rows_d.nth(i).locator(".step-name").inner_text() for i in range(rows_d.count())]
    print("order after 'Top of list':", names_d)
    assert names_d == names0, "FAIL: expected Top of list to exactly reverse the earlier Bottom of list move"
    print("PASS: Top of list")

    # --- Position field: valid entry, plus over/under-max clamping. ---
    rows_e = page.locator(".progression-row")
    row0 = rows_e.first
    row0.locator(".step-move").click()
    page.wait_for_timeout(80)
    row0.locator(".move-menu-position-input").fill("3")
    row0.locator(".move-menu-go").click()
    page.wait_for_timeout(100)
    rows_f = page.locator(".progression-row")
    names_f = [rows_f.nth(i).locator(".step-name").inner_text() for i in range(rows_f.count())]
    print("order after moving the original first row to position 3:", names_f)
    assert names_f[2] == first_name, "FAIL: expected the row at position 3 (1-indexed)"
    print("PASS: position field, valid entry")

    rows_g = page.locator(".progression-row")
    target_name = names_f[0]
    rows_g.first.locator(".step-move").click()
    page.wait_for_timeout(80)
    rows_g.first.locator(".move-menu-position-input").fill("999")
    rows_g.first.locator(".move-menu-go").click()
    page.wait_for_timeout(100)
    rows_h = page.locator(".progression-row")
    names_h = [rows_h.nth(i).locator(".step-name").inner_text() for i in range(rows_h.count())]
    print("order after an over-max position (999):", names_h)
    assert names_h[-1] == target_name, "FAIL: an over-max position should clamp to the very end"
    print("PASS: position field, over-max clamp")

    rows_i = page.locator(".progression-row")
    target_name2 = names_h[-1]
    rows_i.last.locator(".step-move").click()
    page.wait_for_timeout(80)
    rows_i.last.locator(".move-menu-position-input").fill("0")
    rows_i.last.locator(".move-menu-go").click()
    page.wait_for_timeout(100)
    rows_j = page.locator(".progression-row")
    names_j = [rows_j.nth(i).locator(".step-name").inner_text() for i in range(rows_j.count())]
    print("order after an under-min position (0):", names_j)
    assert names_j[0] == target_name2, "FAIL: an under-min position should clamp to the very top"
    print("PASS: position field, under-min clamp")

    print("ERRORS so far:", errors)
    assert not errors

    # --- Fresh page: waypoint sections, including moving INTO a section
    # the row didn't start in (not just its current one). ---
    page2 = browser.new_page(viewport={"width": 1400, "height": 900})
    errors2 = []
    page2.on("pageerror", lambda exc: errors2.append(str(exc)))
    page2.on("dialog", lambda d: d.accept())
    page2.goto(BASE)
    page2.wait_for_selector("#treeWrap .node")
    page2.click('button[data-tab="general"]')
    nodes2 = page2.locator(".node")
    for i in range(6):
        nodes2.nth(i).click()
        page2.click("#incBtn")
        page2.wait_for_timeout(60)

    page2.click('button[data-tab="progression"]')
    page2.wait_for_timeout(150)
    rows2_ = page2.locator(".progression-row")
    total_pts = int(rows2_.last.locator(".cost-total").inner_text().split()[0].lstrip("~"))
    third = max(1, total_pts // 3)

    def add_waypoint(pts, label):
        page2.click("#addWaypointBtn")
        page2.wait_for_timeout(80)
        page2.fill("#waypointPtsInput", str(pts))
        page2.fill("#waypointLabelInput", label)
        page2.click("#saveWaypointBtn")
        page2.wait_for_timeout(150)

    add_waypoint(third, "Early")
    add_waypoint(third * 2, "Late")

    rows2_names0 = [page2.locator(".progression-row").nth(i).locator(".step-name").inner_text() for i in range(6)]
    print("6-row order with 2 waypoints set:", rows2_names0)

    # Move the very last row (currently in/after "Late") into "Early"'s
    # section instead - a section it did NOT start in. Early's own first
    # step isn't necessarily position 1 overall (AA costs vary, so its
    # pts threshold may already be crossed by more than one step) - the
    # real invariant to check is "lands immediately before whatever was
    # Early's first step before the move", not "becomes step 1".
    early_first_name = page2.evaluate("""
        () => {
            const dividers = Array.from(document.querySelectorAll('.progression-divider'));
            const earlyDivider = dividers.find((d) => d.textContent.includes('Early'));
            const nextRow = earlyDivider.nextElementSibling;
            return nextRow ? nextRow.querySelector('.step-name').textContent : null;
        }
    """)
    print("Early section's first step before the move:", early_first_name)

    last_row2 = page2.locator(".progression-row").last
    last_name2 = last_row2.locator(".step-name").inner_text()
    last_row2.locator(".step-move").click()
    page2.wait_for_timeout(80)
    menu_items2 = last_row2.locator(".move-menu-item").all_text_contents()
    print("menu items with 2 waypoints:", menu_items2)
    assert menu_items2 == ["Top of list", "Bottom of list", "Early — top", "Early — bottom", "Late — top", "Late — bottom"]
    last_row2.locator(".move-menu-item", has_text="Early — top").click()
    page2.wait_for_timeout(100)

    rows2_names1 = [page2.locator(".progression-row").nth(i).locator(".step-name").inner_text() for i in range(6)]
    print("order after moving the last row into 'Early — top':", rows2_names1)
    moved_idx = rows2_names1.index(last_name2)
    assert rows2_names1[moved_idx + 1] == early_first_name, \
        "FAIL: expected the row to land immediately before Early section's previous first step"
    print("PASS: moving into a non-current waypoint section works")

    print("ERRORS:", errors2)
    assert not errors2
    page2.close()

    # --- Fresh page: an inactive class's entry sitting between two visible
    # rows - step-num must read as a clean sequence (no gaps), and Move To
    # must skip the inactive entry the same way the up/down arrows already
    # do (see moveProgressionEntry's own neighbor-skip). ---
    page3 = browser.new_page(viewport={"width": 1400, "height": 900})
    errors3 = []
    page3.on("pageerror", lambda exc: errors3.append(str(exc)))
    page3.on("dialog", lambda d: d.accept())
    page3.goto(BASE)
    page3.wait_for_selector("#treeWrap .node")

    page3.click('button[data-tab="general"]')
    gen_nodes = page3.locator(".node")
    gen_nodes.nth(0).click(); page3.click("#incBtn"); page3.wait_for_timeout(60)
    page3.click('button[data-tab="classSlot0"]')
    page3.wait_for_timeout(80)
    page3.locator(".node").first.click(); page3.click("#incBtn"); page3.wait_for_timeout(60)
    page3.click('button[data-tab="general"]')
    page3.wait_for_timeout(80)
    gen_nodes.nth(1).click(); page3.click("#incBtn"); page3.wait_for_timeout(60)

    select = page3.locator("#classSelect0")
    old_class = select.input_value()
    opts = select.locator("option").all_text_contents()
    others = [page3.locator("#classSelect1").input_value(), page3.locator("#classSelect2").input_value()]
    new_class = next(o for o in opts if o != old_class and o not in others)
    select.select_option(new_class)
    page3.wait_for_timeout(150)

    page3.click('button[data-tab="progression"]')
    page3.wait_for_timeout(150)
    rows3_ = page3.locator(".progression-row")
    print("visible row count with one inactive entry in between:", rows3_.count())
    assert rows3_.count() == 2
    step_nums = [rows3_.nth(i).locator(".step-num").inner_text() for i in range(2)]
    print("step-num sequence:", step_nums)
    assert step_nums == ["1", "2"], f"FAIL: step-num should read as a clean 1..N sequence, got {step_nums}"
    print("PASS: step-num shows no gap despite an inactive entry sitting between the two visible rows")

    # Move the first visible row to "Bottom of list" - must skip the
    # invisible inactive entry and land after the second visible row, not
    # get lost swapping with something nothing shows for.
    row0_name = rows3_.nth(0).locator(".step-name").inner_text()
    row1_name = rows3_.nth(1).locator(".step-name").inner_text()
    rows3_.nth(0).locator(".step-move").click()
    page3.wait_for_timeout(80)
    rows3_.nth(0).locator(".move-menu-item", has_text="Bottom of list").click()
    page3.wait_for_timeout(100)
    rows3_after = page3.locator(".progression-row")
    names3_after = [rows3_after.nth(i).locator(".step-name").inner_text() for i in range(2)]
    print("order after Bottom of list, with an inactive entry to skip:", names3_after)
    assert names3_after == [row1_name, row0_name], "FAIL: Move To must skip the invisible inactive entry, not swap with it"
    print("PASS: Move To correctly skips an inactive entry sitting between visible rows")

    print("ERRORS:", errors3)
    assert not errors3
    page3.close()

    # --- Waypoints are anchored to cumulative points crossed, not list
    # position - a step's own cost, added on top of whatever's already
    # accumulated at wherever it lands, can push its resulting cumulative
    # past the very section boundary it's being placed into. "top"/
    # "bottom" of a section must account for this: find the best-fitting
    # slot for the requested preference rather than just the section's
    # literal first/last slot, and disable the option outright if the
    # step doesn't fit anywhere in the section at all.
    #
    # Costs are read live rather than hardcoded to a specific AA, then
    # used to independently compute the expected fitting slot in Python -
    # this verifies the real algorithm's behavior against real numbers,
    # not just a hand-picked scenario assumed to work out. Each of
    # top/bottom gets its own fresh page (rather than chaining both moves
    # on the same build) so a moved step's cumulative recalculating after
    # the first move never muddies what the second move is actually
    # testing.
    def setup_fit_scenario(pg):
        pg.goto(BASE)
        pg.wait_for_selector("#treeWrap .node")
        pg.click('button[data-tab="general"]')
        gnodes = pg.locator(".node")
        # step1, step2 form the section's own content; step3 (bought as a
        # later, unrelated purchase - its cumulative already lands well
        # past the section by the time it's bought, same as any normal
        # purchase) is the one moved INTO that section afterward.
        for i in range(3):
            gnodes.nth(i).click()
            pg.click("#incBtn")
            pg.wait_for_timeout(60)
        pg.click('button[data-tab="progression"]')
        pg.wait_for_timeout(150)
        rows = pg.locator(".progression-row")
        c1 = int(rows.nth(0).locator(".cost-total").inner_text().split()[0].lstrip("~"))
        c2 = int(rows.nth(1).locator(".cost-total").inner_text().split()[0].lstrip("~"))
        moving_name = rows.nth(2).locator(".step-name").inner_text()
        moving_cost = int(rows.nth(2).locator(".cost-this").inner_text().split()[0].lstrip("+~"))
        # Section [0, c2]: step1 (slot0, baseline 0) and step2 (slot1,
        # baseline c1) are its members; slot2 (baseline c2) is the
        # literal bottom, past step2. Same formula the app itself uses
        # (waypointSections, render.js): baseline + moving_cost <= c2.
        pg.click("#addWaypointBtn")
        pg.wait_for_timeout(80)
        pg.fill("#waypointPtsInput", "0")
        pg.fill("#waypointLabelInput", "Section")
        pg.click("#saveWaypointBtn")
        pg.wait_for_timeout(150)
        pg.click("#addWaypointBtn")
        pg.wait_for_timeout(80)
        pg.fill("#waypointPtsInput", str(c2))
        pg.fill("#waypointLabelInput", "After")
        pg.click("#saveWaypointBtn")
        pg.wait_for_timeout(150)
        baselines = [0, c1, c2]
        fits = [b + moving_cost <= c2 for b in baselines]
        print(f"c1={c1} c2={c2} moving_cost={moving_cost} fits={list(zip(baselines, fits))}")
        return moving_name, fits

    # --- "Section — top": always resolves to slot0 (baseline 0, before
    # step1 - the section's true first slot) when it fits at all. ---
    page4 = browser.new_page(viewport={"width": 1400, "height": 900})
    errors4 = []
    page4.on("pageerror", lambda exc: errors4.append(str(exc)))
    page4.on("dialog", lambda d: d.accept())
    moving_name, fits = setup_fit_scenario(page4)

    moving_row = page4.locator(".progression-row").filter(has=page4.locator(".step-name", has_text=moving_name)).last
    moving_row.locator(".step-move").click()
    page4.wait_for_timeout(80)
    section_top = moving_row.locator(".move-menu-item", has_text="Section — top")
    section_bottom = moving_row.locator(".move-menu-item", has_text="Section — bottom")
    top_disabled = section_top.get_attribute("disabled") is not None
    bottom_disabled = section_bottom.get_attribute("disabled") is not None
    print("Section — top disabled:", top_disabled, "| Section — bottom disabled:", bottom_disabled)
    assert top_disabled == (not fits[0]), "FAIL: 'top' availability should match whether the step fits at the section's own top slot"
    assert bottom_disabled == (not fits[0]), "FAIL: bottom's availability is governed by the same top-slot fit (monotonicity - see waypointSections)"

    if fits[0]:
        section_top.click()
        page4.wait_for_timeout(100)
        rows4b = page4.locator(".progression-row")
        names4b = [rows4b.nth(i).locator(".step-name").inner_text() for i in range(3)]
        print("order after 'Section — top':", names4b)
        assert names4b[0] == moving_name, "FAIL: expected the moved step to become the section's (and list's) very first item - slot0 is BEFORE step1, not after it"
        print("PASS: 'Section — top' resolves to slot0")
    else:
        print("PASS: the step doesn't fit anywhere in the section - both options correctly disabled")

    print("ERRORS:", errors4)
    assert not errors4
    page4.close()

    # --- "Section — bottom": resolves to the LATEST fitting slot, not
    # necessarily the literal last one - degrades toward slot0 (same
    # result "top" would give) if even slot1 doesn't fit. ---
    page5 = browser.new_page(viewport={"width": 1400, "height": 900})
    errors5 = []
    page5.on("pageerror", lambda exc: errors5.append(str(exc)))
    page5.on("dialog", lambda d: d.accept())
    moving_name5, fits5 = setup_fit_scenario(page5)

    if fits5[0]:
        moving_row5 = page5.locator(".progression-row").filter(has=page5.locator(".step-name", has_text=moving_name5)).last
        moving_row5.locator(".step-move").click()
        page5.wait_for_timeout(80)
        page5.locator(".move-menu-item", has_text="Section — bottom").click()
        page5.wait_for_timeout(100)
        rows5 = page5.locator(".progression-row")
        names5 = [rows5.nth(i).locator(".step-name").inner_text() for i in range(3)]
        print(f"order after 'Section — bottom' (fits[1]={fits5[1]}):", names5)
        moved_idx = names5.index(moving_name5)
        if fits5[1]:
            # Slot1 (baseline c1, before step2) fits - lands right after
            # step1, pushing step2 (and nothing else) one later.
            assert moved_idx == 1, f"FAIL: expected the moved step at slot1 (right after step1), got index {moved_idx}"
        else:
            # Even slot1 overflows - degrades all the way back to slot0,
            # identical to what 'top' would give.
            assert moved_idx == 0, f"FAIL: expected 'bottom' to degrade to slot0 same as 'top', got index {moved_idx}"
        print("PASS: 'Section — bottom' resolves to the correct best-fitting slot")
    else:
        print("PASS: the step doesn't fit anywhere in the section - both options correctly disabled (covered above)")

    print("ERRORS:", errors5)
    assert not errors5
    page5.close()

    # --- "Doesn't fit anywhere": deterministic regardless of live AA cost
    # data (unlike the two scenarios above, where whether the interesting
    # partial-fit case actually triggers depends on which real costs get
    # read) - read the moving step's own cost first, then set the
    # section's upper bound one point below it, guaranteeing slot0 alone
    # already overflows (0 + moving_cost > moving_cost - 1) for any real,
    # positive-cost AA. ---
    page6 = browser.new_page(viewport={"width": 1400, "height": 900})
    errors6 = []
    page6.on("pageerror", lambda exc: errors6.append(str(exc)))
    page6.on("dialog", lambda d: d.accept())
    page6.goto(BASE)
    page6.wait_for_selector("#treeWrap .node")
    page6.click('button[data-tab="general"]')
    page6.locator(".node").first.click()
    page6.click("#incBtn")
    page6.wait_for_timeout(80)

    page6.click('button[data-tab="progression"]')
    page6.wait_for_timeout(150)
    moving_row6 = page6.locator(".progression-row").first
    moving_name6 = moving_row6.locator(".step-name").inner_text()
    moving_cost6 = int(moving_row6.locator(".cost-this").inner_text().split()[0].lstrip("+~"))
    print("moving_cost6:", moving_cost6)
    assert moving_cost6 >= 1, "FAIL: test assumes a real AA rank always costs at least 1 point"

    page6.click("#addWaypointBtn")
    page6.wait_for_timeout(80)
    page6.fill("#waypointPtsInput", "0")
    page6.fill("#waypointLabelInput", "Tiny")
    page6.click("#saveWaypointBtn")
    page6.wait_for_timeout(150)
    page6.click("#addWaypointBtn")
    page6.wait_for_timeout(80)
    page6.fill("#waypointPtsInput", str(moving_cost6 - 1))
    page6.fill("#waypointLabelInput", "TooSoon")
    page6.click("#saveWaypointBtn")
    page6.wait_for_timeout(150)

    moving_row6b = page6.locator(".progression-row").filter(has=page6.locator(".step-name", has_text=moving_name6)).last
    moving_row6b.locator(".step-move").click()
    page6.wait_for_timeout(80)
    top6 = moving_row6b.locator(".move-menu-item", has_text="Tiny — top")
    bottom6 = moving_row6b.locator(".move-menu-item", has_text="Tiny — bottom")
    print("Tiny — top disabled:", top6.get_attribute("disabled") is not None)
    print("Tiny — bottom disabled:", bottom6.get_attribute("disabled") is not None)
    assert top6.get_attribute("disabled") is not None, "FAIL: expected 'top' disabled - the step's own cost alone exceeds this section's entire span"
    assert bottom6.get_attribute("disabled") is not None, "FAIL: expected 'bottom' disabled for the same reason"
    print("PASS: a step that doesn't fit anywhere in a section gets both options disabled")

    print("ERRORS:", errors6)
    assert not errors6
    page6.close()

    browser.close()
    print("ALL PASS")
