# -*- coding: utf-8 -*-
# Cost estimates were only wired into the tree/side-panel originally -
# Browse's per-rank cost list and the Progression tab's per-step cost pill
# and next-rank preview still showed the raw "?" (or, worse, the Progression
# pill showed a literal "0", since its real math correctly treats "?" as 0
# for the running total but that same number was also being used as the
# *display* for an unpurchased/purchased step, which reads as "this costs
# nothing" rather than "this is unknown"). This test covers those two
# previously-missed spots so a guess shows up consistently everywhere a
# real cost would - plus an inactive-class Progression step, which needed
# its own fix (costDisplayScoped, not the catKey-based costDisplay) to get
# parity with Browse.
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

    # --- Browse view: Adamant Will's rank 4 (medium-confidence guess, value
    # 9) should show as an estimate in the per-rank cost list, not a plain
    # "?". Use the global search box to find it quickly. ---
    page.click("#browseToggle")
    page.fill("#globalSearch", "Adamant Will")
    page.wait_for_timeout(100)
    card = page.locator(".browse-card", has=page.locator(".name", has_text="Adamant Will"))
    info_html = card.locator(".info").inner_html()
    print("Adamant Will browse info html:", info_html)
    assert "~9" in info_html
    assert 'class="is-estimate tier-medium"' in info_html
    print("PASS: Browse shows Adamant Will's rank-4 estimate, not a bare '?'")

    # --- Browse view: a class NOT currently selected must still show its
    # guesses (Browse lists every class, not just the active 3). Default
    # selectedClasses is Bard/Beastlord/Berserker (CLASS_LIST[0..2]), so
    # Magician's Conjurer's Efficiency (a manual guess) is a real example
    # of a class outside the active 3. ---
    page.fill("#globalSearch", "Conjurer's Efficiency")
    page.wait_for_timeout(100)
    ce_card = page.locator(".browse-card", has=page.locator(".name", has_text="Conjurer's Efficiency"))
    ce_html = ce_card.locator(".info").inner_html()
    print("Conjurer's Efficiency browse info html:", ce_html)
    assert "~4" in ce_html and "tier-very-low" in ce_html
    print("PASS: Browse shows a manual guess even for a class outside the active 3 slots")

    page.fill("#globalSearch", "")
    page.click("#browseToggle")

    # --- Progression tab: buy Adamant Will up through the guessed rank 4
    # and confirm the per-step cost pill shows the estimate (not '0'), the
    # running total stays real, and the next-rank preview also shows the
    # estimate + confidence chip. ---
    page.click('button[data-tab="general"]')
    aw = page.locator(".node", has=page.locator(".name", has_text="Adamant Will"))
    aw.click()
    for _ in range(4):
        page.click("#incBtn")
        page.wait_for_timeout(20)

    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(100)
    row4 = page.locator(".progression-row").nth(3)
    cost_this = row4.locator(".cost-this")
    print("Progression row4 cost-this:", cost_this.inner_text(), cost_this.get_attribute("class"))
    assert cost_this.inner_text().strip() == "+~9 pt(s)"
    cls4 = cost_this.get_attribute("class")
    assert "is-estimate" in cls4 and "tier-medium" in cls4
    # Class alone isn't proof of anything on screen - .step-cost .cost-this
    # and the generic .is-estimate.tier-* rule are equal CSS specificity, so
    # without an explicit compound override the red "spent" color silently
    # wins on source order even though the class list is completely correct.
    # Check the actually-rendered color, not just the class attribute.
    color4 = cost_this.evaluate("el => getComputedStyle(el).color")
    print("Progression row4 cost-this computed color:", color4)
    assert color4 == "rgb(166, 124, 217)", f"FAIL: guessed step still rendering in the real 'spent' red, got {color4}"
    print("PASS: the guessed step's cost pill actually renders in its tier color, not red")
    cost_total = row4.locator(".cost-total")
    print("Progression row4 cost-total (blends the guess in, like the topbar):", cost_total.inner_text(), cost_total.get_attribute("title"))
    assert cost_total.inner_text().strip() == "~21 total", "FAIL: expected the running total to blend real 12 + guessed 9"
    assert "is-estimate" in cost_total.get_attribute("class")
    assert cost_total.get_attribute("title") == "12 confirmed + 9 estimated."
    print("PASS: Progression's per-step pill shows the estimate, and the running total blends it in the same way the topbar does")

    # --- A real, fully-known step (rank 1, cost 2) must NOT get estimate
    # styling on its cost pill. ---
    row1 = page.locator(".progression-row").nth(0)
    cost_this1 = row1.locator(".cost-this")
    print("Progression row1 cost-this (real cost):", cost_this1.inner_text(), cost_this1.get_attribute("class"))
    assert cost_this1.inner_text().strip() == "+2 pts"
    assert "is-estimate" not in cost_this1.get_attribute("class")
    color1 = cost_this1.evaluate("el => getComputedStyle(el).color")
    print("Progression row1 cost-this computed color (should stay real 'spent' red):", color1)
    assert color1 == "rgb(217, 76, 76)"
    print("PASS: a real known per-step cost never gets estimate styling")

    # --- An inactive-class Progression step (its class isn't in the
    # current 3 slots, e.g. from an imported build) should still show an
    # estimate in its next-rank preview, same as Browse does - costDisplay's
    # catKey lookup returns null off-slot, but costDisplayScoped (scope/
    # className directly) doesn't have that limitation. Hand-crafted build
    # code: selectedClasses = [Bard, Beastlord, Berserker] (the defaults),
    # but purchaseOrder references Magician's Conjurer's Efficiency (id 90)
    # anyway - simulates a build from before this app enforced the 3-slot
    # model, or one edited by hand. ---
    inactive_build = "H4sIAAAAAAAC_6tWKlOyUjDSUVBKBtLRBjoKhjoKRrFAfg6QbwrkK5UAGYYGBiBmEUhNtCVIVSxITQGIb2kQWwsAdrvsFEcAAAA"
    # Fresh page (no unsaved-build prompt to fight through) rather than
    # reusing the one with Adamant Will already bought above.
    inactive_page = browser.new_page(viewport={"width": 1400, "height": 900})
    inactive_page.on("dialog", lambda d: d.accept())
    inactive_page.goto(f"{BASE}?build={inactive_build}")
    inactive_page.wait_for_selector("#treeWrap .node")
    inactive_page.wait_for_timeout(200)
    inactive_page.click('button[data-tab="progression"]')
    inactive_page.wait_for_timeout(150)
    inactive_row = inactive_page.locator(".progression-row", has=inactive_page.locator(".step-name", has_text="Conjurer's Efficiency"))
    print("inactive row class:", inactive_row.get_attribute("class"))
    assert "inactive" in inactive_row.get_attribute("class")
    inactive_row.locator(".step-expand").click()
    inactive_page.wait_for_timeout(100)
    inactive_next = inactive_page.locator(".progression-next-rank .next-rank-title b")
    print("inactive step next-rank text/class:", inactive_next.inner_text(), inactive_next.get_attribute("class"))
    assert inactive_next.inner_text().strip() == "~4"
    assert "is-estimate" in inactive_next.get_attribute("class")
    print("PASS: an inactive-class step's next-rank preview still shows its estimate, matching Browse")
    inactive_page.close()

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
