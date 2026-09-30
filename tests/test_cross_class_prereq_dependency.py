# -*- coding: utf-8 -*-
# isDependedOn (logic.js) blocks lowering a rank if some other held AA's
# prereq depends on it - but it used to only check the 3 currently active
# class slots (AA_CATEGORY_KEYS), not every class ever picked. Since a
# class swap no longer wipes an inactive class's picks, a class AA whose
# prereq targets a general/archetype/special AA (e.g. Warrior's War Cry
# needing Fear Resistance rank 3) could have its dependency silently
# refunded out from under it the moment that class was swapped out -
# nothing blocked the refund, and nothing warned until the class was
# reselected and heldRankInvalidReason caught it after the fact. Fixed by
# generalizing isDependedOn to also check every class in
# state.ranks.classes, not just the active 3, via the new
# resolvePrereqTargetScoped (scope/className-addressed, so it still
# resolves a same-class prereq target like Valiant Steed -> Holy Steed
# correctly for an inactive class too).
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

    page.select_option("#classSelect0", "Warrior")
    page.wait_for_timeout(100)

    # --- Train Fear Resistance (general) to rank 3, then War Cry (Warrior
    # class AA, "Requires Fear Resistance at level 3") to rank 1. ---
    page.click('button[data-tab="general"]')
    fr = page.locator(".node", has=page.locator(".name", has_text="Fear Resistance"))
    fr.click()
    for _ in range(3):
        page.click("#incBtn")
        page.wait_for_timeout(15)
    print("Fear Resistance rank:", page.locator("#sidePanel .current").inner_text())
    assert page.locator("#sidePanel .current").inner_text() == "3 / 4"

    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    wc = page.locator(".node", has=page.locator(".name", has_text="War Cry"))
    wc.click()
    page.click("#incBtn")
    page.wait_for_timeout(30)
    print("War Cry rank:", page.locator("#sidePanel .current").inner_text())
    assert page.locator("#sidePanel .current").inner_text() == "1 / 1"

    # --- Swap Warrior out - War Cry (and its dependency on Fear Resistance)
    # moves to the Other Classes tab, still fully intact. ---
    page.select_option("#classSelect0", "Bard")
    page.wait_for_timeout(150)

    # --- Attempting to refund Fear Resistance below rank 3 must be blocked,
    # even though War Cry - the AA that depends on it - isn't one of the 3
    # active classes right now. ---
    page.click('button[data-tab="general"]')
    fr.click()
    page.wait_for_timeout(100)
    page.click("#decBtn")
    page.wait_for_timeout(150)
    print("Fear Resistance rank after blocked decrement attempt:", page.locator("#sidePanel .current").inner_text())
    assert page.locator("#sidePanel .current").inner_text() == "3 / 4", \
        "FAIL: Fear Resistance should not have been refundable while an inactive class's War Cry depends on it"
    toast = page.locator("#toast")
    print("toast:", toast.inner_text() if toast.is_visible() else None)
    assert toast.is_visible() and "another AA depends" in toast.inner_text(), \
        "FAIL: expected the same 'another AA depends on the current rank' block an active dependent would get"
    print("PASS: refunding a general AA is blocked by a dependent held on a currently-inactive class")

    # --- Control: remove War Cry itself (swap Warrior back in, refund it to
    # 0), swap Warrior out again, and confirm Fear Resistance CAN now be
    # refunded - proving the block above was tied to War Cry's own
    # dependency, not just "something is inactive". ---
    page.select_option("#classSelect0", "Warrior")
    page.wait_for_timeout(150)
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    wc.click()
    page.click("#decBtn")
    page.wait_for_timeout(30)
    print("War Cry rank after refund:", page.locator("#sidePanel .current").inner_text())
    assert page.locator("#sidePanel .current").inner_text() == "0 / 1"

    page.select_option("#classSelect0", "Bard")
    page.wait_for_timeout(150)
    page.click('button[data-tab="general"]')
    fr.click()
    page.wait_for_timeout(100)
    page.click("#decBtn")
    page.wait_for_timeout(150)
    print("Fear Resistance rank after War Cry's own refund removed the dependency:", page.locator("#sidePanel .current").inner_text())
    assert page.locator("#sidePanel .current").inner_text() == "2 / 4", \
        "FAIL: with no dependent left anywhere, Fear Resistance should refund normally"
    print("PASS: once the dependency itself is gone, the block clears - this isn't just a blanket inactive-class lock")

    print("ERRORS:", errors)
    assert not errors

    # --- Regression: findInvalidatedPicks (the "N picks no longer meet
    # their requirements" notice on load) previously only walked the 3
    # active class slots, so a broken pick sitting in an inactive class
    # never counted toward it - the only signal the player gets for such a
    # break, since an inactive row's own invalidReason line is deliberately
    # not shown (see otherClassesSectionsHtml in render.js). Reuses War
    # Cry/Fear Resistance from above; the broken state itself (War Cry held
    # with Fear Resistance not held at all) isn't reachable through the UI -
    # isDependedOn blocks exactly that refund - so it's written directly to
    # localStorage, the same way a resync-broken prereq would actually
    # arrive (an import, a share link, or the data simply changing under an
    # existing save). ---
    page2 = browser.new_page(viewport={"width": 1400, "height": 900})
    errors2 = []
    page2.on("pageerror", lambda exc: errors2.append(str(exc)))
    page2.on("dialog", lambda d: d.accept())
    page2.goto(BASE)
    page2.wait_for_selector("#treeWrap .node")
    page2.select_option("#classSelect0", "Warrior")
    page2.wait_for_timeout(100)
    page2.click('button[data-tab="general"]')
    page2.locator(".node", has=page2.locator(".name", has_text="Fear Resistance")).click()
    for _ in range(3):
        page2.click("#incBtn")
        page2.wait_for_timeout(15)
    page2.click('button[data-tab="classSlot0"]')
    page2.wait_for_timeout(100)
    page2.locator(".node", has=page2.locator(".name", has_text="War Cry")).click()
    page2.click("#incBtn")
    page2.wait_for_timeout(60)
    print("War Cry rank before seeding the broken state:", page2.locator("#sidePanel .current").inner_text())
    war_cry_slug = page2.evaluate(
        "() => Object.keys(JSON.parse(localStorage.getItem('eql_aa_builder_v1')).ranks.classes.Warrior)[0]"
    )
    print("War Cry slug:", war_cry_slug)

    page2.evaluate("""(slug) => {
        const s = JSON.parse(localStorage.getItem('eql_aa_builder_v1'));
        s.selectedClasses = ['Bard', 'Beastlord', 'Berserker'];
        s.ranks.general = {};
        s.ranks.classes = { Warrior: { [slug]: 1 } };
        s.purchaseOrder = [{ scope: 'class', className: 'Warrior', key: slug }];
        localStorage.setItem('eql_aa_builder_v1', JSON.stringify(s));
    }""", war_cry_slug)
    page2.reload()
    page2.wait_for_selector("#treeWrap .node")
    page2.wait_for_timeout(250)

    toast = page2.locator("#toast")
    toast_text = toast.inner_text() if toast.count() and toast.is_visible() else ""
    print("load toast:", repr(toast_text))
    assert "1 pick" in toast_text and "no longer meet" in toast_text, \
        f"FAIL: expected the load notice to count War Cry's broken prereq even though Warrior isn't active, got {toast_text!r}"
    print("PASS: a broken pick in an inactive class is counted in the load-time notice")

    print("ERRORS:", errors2)
    assert not errors2
    page2.close()

    browser.close()
    print("ALL PASS")
