# -*- coding: utf-8 -*-
# A real, in-use build shared by the app's own user (Paladin/Enchanter/Druid,
# 191 total picks, with Bard/Monk/Rogue/Shaman/Wizard history from before
# those classes were swapped out) - a scale/realism check the smaller
# synthetic fixtures in test_other_classes.py and test_progression_move_to.py
# don't cover: a genuinely large purchaseOrder, several ranks deep on some
# AAs, real blended estimates, and several different inactive classes at
# once rather than one hand-crafted scenario. Also a real-world check on
# Archetype class-eligibility gating specifically - this build holds Burst
# of Power and Rampage (Berserker/Warrior-only) from before the current
# combo, the exact "stuck behind a class I don't have anymore" case the
# feature exists for.
#
# Refreshed once already (originally a Paladin/Monk/Enchanter build) when
# the user's real character grew enough to exercise the archetype-
# eligibility feature specifically - swapping the fixture is worth the
# rework only when it buys new coverage like that, not just to track
# current progress; see the commit that did this swap for the reasoning.
#
# Pinned to this build's exact numbers (191 rows, 36 inactive, "537 / ~748"
# spent) the same way test_effect_guess.py etc. are pinned to specific live
# AAs - see tests/README.md's note on that. A future wiki scrape that
# resolves one of this build's unconfirmed costs, or a rename/removal
# affecting one of its AAs, would shift these numbers and need a fresh share
# link swapped in from a still-representative real build.
#
# This is the widest-coverage test in the suite and, because of the above,
# also the most likely to fail for a reason that isn't a code regression -
# every count assertion below carries a reminder to check a recent wiki
# scrape / data.src.js diff for this build's AAs BEFORE assuming something
# broke. The one exception is the last-row-vs-topbar total check near the
# bottom: it compares two independently-computed numbers against each
# other rather than against a hardcoded figure, so it stays meaningful
# regardless of what the wiki says on a given day - a failure there really
# is a code regression.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
BUILD_CODE = "fZM_j9swDMW_SqH5DaJI6s_arUOnjoaHFAkOQdO7Q3A39NsXj459cZEr9LNhSbQtku9NhmnAYTM8Y5oyHBUNHZIhAlGIQzpkoAiKohhKRWkoHSrQAlWoQR1aoQ06YBkmsAJTmME6bPD7XuAKN7jDK7zBO3ygZlRBVUhRSDZIdkhuGIbhGA3VUStqQ-2oAy1DVCBiEGkzJoNBt0vgaMwqsoCgwyGxodtgIAf3lxcraszWOH6U8_2bjOEpl615xsS0CqvC5DZKFCnw_PFcWmSmssZltNvoLIRnloyF4KTyXlocraKjRxc29H-wCzmasnQk37VpRHMDFji4reflgGOFnVlhewNfRwl93DP2ZKdARCmBDQrqDjd29DPY-IB6WXCKYIE5LWl5qCSgxO4ZN5bfUZULslJuUHyl77HQ2jBqL9-G3GGd0t2gIwLvIdg9IrxsxjRtTntos_AYDfbQXRq--sxUq6NWG1FNOx_RQeGa1Qb_OKbfVP_hlUcuWXf2vpJMT0yWkb49n9_Oh0tCerkenp9OacbUM9L38_Hp8PuUkK6nIxe1C9KPX3--HF-eufz6fn29RLiLIn09XI8J6efl_ZTmef4L"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("dialog", lambda d: d.accept())

    page.goto(f"{BASE}?build={BUILD_CODE}")
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(300)

    classes = [page.locator(f"#classSelect{i}").input_value() for i in range(3)]
    print("selected classes:", classes)
    assert classes == ["Paladin", "Enchanter", "Druid"], \
        "FAIL: check wiki-sync/snapshot.json's recent diff before assuming a code regression - a class rename would land here first"

    # --- Progression: every pick renders, active or not - none silently
    # dropped for a build this size. ---
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(250)
    rows = page.locator(".progression-row")
    row_count = rows.count()
    print("Progression row count:", row_count)
    assert row_count == 191, \
        "FAIL: check for a wiki rename/removal affecting one of this build's AAs before assuming a code regression - see this file's header comment"

    inactive_rows = page.locator(".progression-row.inactive")
    inactive_count = inactive_rows.count()
    print("inactive row count:", inactive_count)
    assert inactive_count == 36, \
        "FAIL: check for a wiki rename/removal affecting one of this build's inactive-class AAs before assuming a code regression - see this file's header comment"

    # Every inactive row stays read-only and full-opacity with just the
    # warning icon signaling its status (not dimmed - see the
    # "replace dimming with a warning icon" change), and still shows its
    # class badge - a neutral pill rather than a colored one (there's no
    # unique hue per class, only per active slot - see classBadgeClass,
    # render.js), but still a proper badge, not plain text.
    class_badges_seen = set()
    for i in range(inactive_count):
        row = inactive_rows.nth(i)
        assert row.locator(".step-add").get_attribute("disabled") is not None
        assert row.locator(".step-remove").get_attribute("disabled") is not None
        cat = row.locator(".step-cat")
        assert "step-cat-inactive" in cat.get_attribute("class")
        class_badges_seen.add(cat.inner_text())
        warn_title = row.locator(".step-inactive-warn").get_attribute("title")
        assert warn_title and "Not one of your current 3 classes" in warn_title
    print("class badges seen on inactive rows:", class_badges_seen)
    assert class_badges_seen == {"Bard AA", "Monk AA", "Rogue AA", "Shaman AA", "Wizard AA"}
    opacity_sample = inactive_rows.first.evaluate("el => getComputedStyle(el).opacity")
    print("sample inactive row opacity (should be full, not dimmed):", opacity_sample)
    assert opacity_sample == "1"
    print("PASS: every one of the 191 picks renders, inactive ones muted-free but read-only with a warning icon")

    # --- Other Classes: the same 13 inactive picks (Bard/Monk/Rogue/Shaman/
    # Wizard), grouped. ---
    page.click('button[data-tab="otherClasses"]')
    page.wait_for_timeout(200)
    section_titles = page.locator("#otherClassesContent .summary-section-title").all_inner_texts()
    print("Other Classes sections:", section_titles)
    assert sorted(section_titles) == ["BARD", "MONK", "ROGUE", "SHAMAN", "WIZARD"], \
        "FAIL: check for a wiki rename/removal before assuming a code regression - see this file's header comment"
    oc_badge = page.locator('button[data-tab="otherClasses"] .count').inner_text()
    print("Other Classes tab badge:", oc_badge)
    assert oc_badge == "(13)", \
        "FAIL: check for a wiki rename/removal affecting one of this build's inactive-class AAs before assuming a code regression - see this file's header comment"
    print("PASS: Other Classes groups the same inactive picks by class")

    # --- Progression's own running total must exactly match the topbar's
    # spent figure - no more silent divergence, even blended with real
    # estimates on a build this size. ---
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(200)
    last_total = page.locator(".progression-row").last.locator(".cost-total").inner_text().strip()
    spent_text = page.locator("#spentValue").inner_text()
    spent_only = spent_text.split("/")[-1].strip()
    print("last row cost-total:", last_total, "| topbar spentValue (spent side):", spent_only)
    assert last_total == f"{spent_only} total"
    print("PASS: Progression's final running total matches the topbar's spent figure exactly")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
