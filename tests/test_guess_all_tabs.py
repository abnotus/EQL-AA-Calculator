# -*- coding: utf-8 -*-
# Cost estimates were only wired into the tree/side-panel originally -
# Browse's per-rank cost list and the Progression tab's per-step cost pill
# and next-rank preview still showed the raw "?" (or, worse, the Progression
# pill showed a literal "0", since its real math correctly treats "?" as 0
# for the running total but that same number was also being used as the
# *display* for an unpurchased/purchased step, which reads as "this costs
# nothing" rather than "this is unknown"). This test covers those two
# previously-missed spots so a guess shows up consistently everywhere a
# real cost would.
#
# The final scenario covers an inactive-class pick - one whose class is no
# longer in the active 3. Progression renders it inline, muted and
# read-only, rather than hiding it, so the scenario checks the row is
# present and its controls disabled. costGuessScoped/effectGuessScoped,
# the scoped lookups such a row depends on, are also covered by the Browse
# scenarios above.
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

    # --- Browse view: Turn Summoned's rank 2 (high-confidence guess, value
    # 6) should show as an estimate in the per-rank cost list, not a plain
    # "?". Use the global search box to find it quickly - Browse lists
    # every class regardless of the active 3 slots (see the Conjurer's
    # Efficiency scenario just below), so no class selection is needed
    # here. (This used to be Alchemy Mastery's rank 2, before that Combat
    # Stability's rank 3, before that Adamant Will's rank 4 - each got
    # confirmed by a wiki scrape in turn since this test was first written.
    # Every remaining high-confidence guess now lives on a per-class AA
    # rather than a general one - Turn Summoned is Magician-only and its
    # name isn't shared with any other AA, unlike e.g. "Quick Evacuation"
    # which exists for both Druid and Wizard.) ---
    page.click("#browseToggle")
    page.fill("#globalSearch", "Turn Summoned")
    page.wait_for_timeout(100)
    card = page.locator(".browse-card", has=page.locator(".name", has_text="Turn Summoned"))
    info_html = card.locator(".info").inner_html()
    print("Turn Summoned browse info html:", info_html)
    assert "~6" in info_html
    assert 'class="is-estimate tier-high"' in info_html
    print("PASS: Browse shows Turn Summoned's rank-2 estimate, not a bare '?'")

    # --- Browse view: a second class outside the active 3, to show the
    # scoped guess lookup isn't specific to one class. Default
    # selectedClasses is Bard/Beastlord/Berserker (CLASS_LIST[0..2]), so
    # Wizard's Quick Evacuation qualifies, as Magician's Turn Summoned
    # above does. (This was Conjurer's Efficiency until a wiki scrape
    # confirmed all five of its costs, leaving it with no guess to show.
    # Every remaining cost guess is either high or manual very-low - there
    # is no medium-confidence one left to pin here.) ---
    page.fill("#globalSearch", "Quick Evacuation")
    page.wait_for_timeout(100)
    # Druid has an identically-named AA whose costs are all confirmed, so
    # pin the Wizard card by its own class rather than by list position.
    ce_card = page.locator('.browse-card:has(button[data-classname="Wizard"])',
                           has=page.locator(".name", has_text="Quick Evacuation"))
    ce_html = ce_card.locator(".info").inner_html()
    print("Quick Evacuation (Wizard) browse info html:", ce_html)
    assert "~6" in ce_html and "tier-high" in ce_html
    print("PASS: Browse shows a guess even for a class outside the active 3 slots")

    page.fill("#globalSearch", "")
    page.click("#browseToggle")

    # --- Progression tab: buy Turn Summoned up through the guessed rank 2
    # and confirm the per-step cost pill shows the estimate (not '0'), the
    # running total blends it in like the topbar, and the next-rank preview
    # also shows the estimate + confidence chip. Turn Summoned is a
    # per-class (Magician) AA, so it needs a slot. ---
    page.select_option("#classSelect0", "Magician")
    page.click('button[data-tab="classSlot0"]')
    am = page.locator(".node", has=page.locator(".name", has_text="Turn Summoned"))
    am.click()
    for _ in range(2):
        page.click("#incBtn")
        page.wait_for_timeout(20)

    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(100)
    row2 = page.locator(".progression-row").nth(1)
    cost_this = row2.locator(".cost-this")
    print("Progression row2 cost-this:", cost_this.inner_text(), cost_this.get_attribute("class"))
    assert cost_this.inner_text().strip() == "+~6 pt(s)"
    cls2 = cost_this.get_attribute("class")
    assert "is-estimate" in cls2 and "tier-high" in cls2
    # Class alone isn't proof of anything on screen - .step-cost .cost-this
    # and the generic .is-estimate.tier-* rule are equal CSS specificity, so
    # without an explicit compound override the red "spent" color silently
    # wins on source order even though the class list is completely correct.
    # Check the actually-rendered color, not just the class attribute.
    color2 = cost_this.evaluate("el => getComputedStyle(el).color")
    print("Progression row2 cost-this computed color:", color2)
    assert color2 == "rgb(90, 169, 230)", f"FAIL: guessed step still rendering in the real 'spent' red, got {color2}"
    print("PASS: the guessed step's cost pill actually renders in its tier color, not red")
    cost_total = row2.locator(".cost-total")
    print("Progression row2 cost-total (blends the guess in, like the topbar):", cost_total.inner_text(), cost_total.get_attribute("title"))
    assert cost_total.inner_text().strip() == "~9 total", "FAIL: expected the running total to blend real 3 + guessed 6"
    assert "is-estimate" in cost_total.get_attribute("class")
    assert cost_total.get_attribute("title") == "3 confirmed + 6 estimated."
    print("PASS: Progression's per-step pill shows the estimate, and the running total blends it in the same way the topbar does")

    # --- A real, fully-known step (rank 1, cost 3) must NOT get estimate
    # styling on its cost pill. ---
    row1 = page.locator(".progression-row").nth(0)
    cost_this1 = row1.locator(".cost-this")
    print("Progression row1 cost-this (real cost):", cost_this1.inner_text(), cost_this1.get_attribute("class"))
    assert cost_this1.inner_text().strip() == "+3 pts"
    assert "is-estimate" not in cost_this1.get_attribute("class")
    color1 = cost_this1.evaluate("el => getComputedStyle(el).color")
    print("Progression row1 cost-this computed color (should stay real 'spent' red):", color1)
    assert color1 == "rgb(217, 76, 76)"
    print("PASS: a real known per-step cost never gets estimate styling")

    # --- An inactive-class purchaseOrder entry (its class isn't in the
    # current 3 slots) still renders as a Progression row - muted/read-only
    # (see .inactive, styles.css) - and also shows up in the Other Classes
    # tab (test_other_classes.py covers that tab's own content in depth).
    # Real share link from a live Paladin/Enchanter/Druid build with
    # Bard/Monk/Rogue/Shaman/Wizard history (see tests/test_real_world_build.py's
    # own header for the pinned-to-a-live-build caveat) - Cannibalization is
    # one of its Shaman picks, now inactive. ---
    inactive_build = "fZM_j9swDMW_SqH5DaJI6s_arUOnjoaHFAkOQdO7Q3A39NsXj459cZEr9LNhSbQtku9NhmnAYTM8Y5oyHBUNHZIhAlGIQzpkoAiKohhKRWkoHSrQAlWoQR1aoQ06YBkmsAJTmME6bPD7XuAKN7jDK7zBO3ygZlRBVUhRSDZIdkhuGIbhGA3VUStqQ-2oAy1DVCBiEGkzJoNBt0vgaMwqsoCgwyGxodtgIAf3lxcraszWOH6U8_2bjOEpl615xsS0CqvC5DZKFCnw_PFcWmSmssZltNvoLIRnloyF4KTyXlocraKjRxc29H-wCzmasnQk37VpRHMDFji4reflgGOFnVlhewNfRwl93DP2ZKdARCmBDQrqDjd29DPY-IB6WXCKYIE5LWl5qCSgxO4ZN5bfUZULslJuUHyl77HQ2jBqL9-G3GGd0t2gIwLvIdg9IrxsxjRtTntos_AYDfbQXRq--sxUq6NWG1FNOx_RQeGa1Qb_OKbfVP_hlUcuWXf2vpJMT0yWkb49n9_Oh0tCerkenp9OacbUM9L38_Hp8PuUkK6nIxe1C9KPX3--HF-eufz6fn29RLiLIn09XI8J6efl_ZTmef4L"
    # Fresh page (no unsaved-build prompt to fight through) rather than
    # reusing the one with Turn Summoned already bought above.
    inactive_page = browser.new_page(viewport={"width": 1400, "height": 900})
    inactive_page.on("dialog", lambda d: d.accept())
    inactive_page.goto(f"{BASE}?build={inactive_build}")
    inactive_page.wait_for_selector("#treeWrap .node")
    inactive_page.wait_for_timeout(200)
    inactive_page.click('button[data-tab="progression"]')
    inactive_page.wait_for_timeout(150)
    inactive_row = inactive_page.locator(".progression-row", has=inactive_page.locator(".step-name", has_text="Cannibalization"))
    print("Progression row count for the inactive-class pick (should be 1, muted):", inactive_row.count())
    assert inactive_row.count() == 1, "FAIL: an inactive-class pick should still render inline in Progression, muted"
    assert "inactive" in inactive_row.get_attribute("class")
    assert inactive_row.locator(".step-add").get_attribute("disabled") is not None
    assert inactive_row.locator(".step-remove").get_attribute("disabled") is not None

    inactive_page.click('button[data-tab="otherClasses"]')
    inactive_page.wait_for_timeout(150)
    other_classes_html = inactive_page.locator("#otherClassesContent").inner_html()
    print("Other Classes tab shows Cannibalization:", "Cannibalization" in other_classes_html)
    assert "Cannibalization" in other_classes_html
    print("PASS: an inactive-class pick renders muted in Progression and also shows up in Other Classes")
    inactive_page.close()

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
