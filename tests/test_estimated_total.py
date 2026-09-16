# -*- coding: utf-8 -*-
# The topbar's #spentValue shows "owned / planned" (renderTopbar, render.js) -
# each side blends real + estimated costs independently (colored blue, ~9
# instead of 3, in its own <span class="is-estimate">) when it includes at
# least one purchased-but-unconfirmed rank with a guess. The ~ prefix and
# per-side color are the only visible cue; the confirmed/estimated
# breakdown lives in one combined title tooltip on the outer element
# ("Owned: ..." and/or "Planned: ..."), same hover-to-disclose pattern as
# every other estimate badge in the app. Progression's own running total
# blends the exact same way (it used to stay strictly real while the
# topbar blended, but a cumulative frozen through a step whose own pill
# shows a nonzero ~N estimate read as "the estimate isn't doing anything" -
# see logic.js's computeProgressionSteps for blendedCumulative). What's
# still guaranteed: spentPoints()/affordability math itself never reads a
# guess - "?" still costs exactly 0 there - proven here by the real/
# estimated split staying separately trackable rather than the two numbers
# ever being silently merged into one indistinguishable figure.
#
# This is the exact scenario the guessed-total-freezing bug was originally
# reported against. BUILD is the user's own real build (Paladin/Monk/Shaman,
# with waypoints and real owned progress) - kept as a live fixture for its
# scale and realism, but it no longer carries any unconfirmed-cost rank of
# its own (Packrat, its last live example, got fully confirmed by a wiki
# scrape - the eventual fate every guess on this page is built to have).
# So the guessed-cost scenario below buys Turn Summoned (a Magician class
# AA, level 45 - comfortably under BUILD's level 50 - real ranks 1-2 cost
# 3/6, a single guessed rank 3 after them: 9) live on top of the loaded
# build instead, reintroducing a real "guess blends into the running total,
# never freezing" case without needing a stale, hand-picked share code.
# (This used to be Reaching Notes, then Quick Evacuation - each in turn got
# fully confirmed by a wiki scrape since this scenario was last written, so
# it no longer has any "?" cost left; swapped to a currently-live example
# each time.)
#
# Turn Summoned itself used to carry two consecutive guessed ranks (2 and
# 3) - the same scrape that reworked Master of All confirmed rank 2's real
# cost, leaving only rank 3 unconfirmed. Turn Summoned is currently the
# only AA anywhere in the dataset with any unconfirmed cost at all, and
# it's a single trailing rank - there is no live example left of two
# differently-sized guesses in a row, or of a PARTIAL owned/to-go split
# (an interior guessed rank, with real ranks still unowned after it): a
# single trailing guess is atomic, only ever 0% or 100% owned, never
# split. The scenario below tests the 100%-owned case instead of a partial
# one for that reason - not a gap introduced here, just what's left
# testable against real data right now. The guessing feature itself is
# unaffected; this only concerns which live AA can demonstrate it.
# Refreshed periodically to the user's current build as they keep playing -
# BUILD_STALE is regenerated alongside it each time (decode BUILD, inject
# "t": 1000, re-encode gzip+base64url) so both stay in sync.
#
# A second, separate scenario partway through this file re-tests the same
# build with a stale "t" (totalPoints) field injected into its payload, to
# keep the backward-compatibility regression coverage that was lost when an
# older two-build version of this file was simplified down to one. A third,
# independent scenario at the end checks owned/to-go can't show a negative
# figure when owned exceeds the current plan.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
BUILD = "H4sIAAAAAAAACn2QS27DMAxE78L1LCRSv_gGXfQEghZGYwQG0qQwinZR9O4FKSvuKtAzRjRGFDU_9EUTg95oqidkeGmgK03RgTaaak2QhpoRGmqxPXsrWOCdaoJXySgNVbxVEswqsUtvIieT4Ox8COaMzn5G7iJIKr2n1ztUXYa0BvqgSZ2RwQlR_sHgvBPdsecMO-yHzyHvq2ihQ7AgpuHUL9kqKNBRB_oIg_2BPqkTBnGH5QkNdNd0R66W4CPIfAT5LCWb9xFTA31ry-BAL7f1c52vBLpv8-2ykF7iQK_r-TK_LwTaljO19vsHCmycbf8BAAA"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())

    # --- Fresh page, nothing purchased: plain real number, red, no note. ---
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    sv0 = page.locator("#spentValue")
    print("fresh spentValue text/class:", sv0.inner_text(), sv0.get_attribute("class"))
    assert sv0.inner_text() == "0 / 0"
    assert sv0.locator(".is-estimate").count() == 0
    color0 = sv0.evaluate("el => getComputedStyle(el).color")
    assert color0 == "rgb(217, 76, 76)", f"FAIL: expected real 'planned' red, got {color0}"
    assert sv0.get_attribute("title") is None
    print("PASS: no guesses purchased -> plain owned/planned, red, no tooltip")

    # --- Load the real build - fully confirmed now, so it's a plain real
    # number too, same as the fresh-page case above (just non-zero). ---
    page.goto(f"{BASE}?build={BUILD}")
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)

    sv = page.locator("#spentValue")
    print("spentValue with BUILD alone (now fully confirmed):", sv.inner_text(), sv.get_attribute("class"))
    assert sv.inner_text() == "95 / 235"
    assert sv.locator(".is-estimate").count() == 0, "FAIL: a fully-confirmed build shouldn't carry estimate styling"
    assert sv.get_attribute("title") is None

    # --- Buy Turn Summoned live on top of it: ranks 1-2 are real (costs
    # 3/6), rank 3 is guessed (9 - high confidence, cross-AA sibling
    # match). Real total climbs to 244 (235 + ranks 1-2's real 3+6); rank 3
    # adds nothing to spentPoints() itself but 9 to the blended headline
    # (244 + 9 = 253). Turn Summoned is a Magician class AA, so slot 3
    # (Shaman in BUILD) needs to swap to Magician first - done after the
    # "95 / 235" assertion above so it doesn't disturb BUILD's own
    # already-purchased Paladin/Monk/Shaman ranks, which are
    # lifetime-scoped and unaffected by a later class swap. ---
    page.select_option("#classSelect2", "Magician")
    page.click('button[data-tab="classSlot2"]')
    page.wait_for_timeout(100)
    ts_node = page.locator(".node", has=page.locator(".name", has_text="Turn Summoned"))
    ts_node.click()
    for _ in range(3):
        page.click("#incBtn")
        page.wait_for_timeout(15)
    print("spentValue after buying Turn Summoned to rank 3:", sv.inner_text(), sv.get_attribute("title"))
    # Owned (95) has no estimate contribution here - only the planned side
    # does, so exactly one of the two numbers gets the estimate span/color,
    # not the whole "owned / planned" pair.
    assert sv.inner_text() == "95 / ~253"
    assert sv.locator(".is-estimate").count() == 1
    planned_span = sv.locator(".is-estimate")
    assert planned_span.inner_text() == "~253"
    color = planned_span.evaluate("el => getComputedStyle(el).color")
    print("planned estimate span computed color:", color)
    assert color == "rgb(90, 169, 230)", f"FAIL: the blended planned side should render blue, got {color}"
    # Swapping slot 3 to Magician (above) made Shaman inactive - BUILD already
    # had 5 real points on Shaman, so the tooltip now also discloses that
    # slice, same as any other class-swap-with-existing-spend scenario.
    assert sv.get_attribute("title") == "Planned: 244 confirmed + 9 estimated. 5 pts from classes not currently selected (see the Other Classes tab)."
    print("PASS: planned side blends to ~253 in blue, full breakdown lives only in the tooltip")

    # --- Progression's own running total now blends the same way the
    # topbar does - the last row's total must match the headline exactly
    # (~253), with the same "244 confirmed + 9 estimated." breakdown in its
    # own tooltip, proving the two displays agree rather than showing two
    # different numbers for the same underlying build. ---
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(150)
    prog_total_el = page.locator(".progression-row .cost-total").last
    prog_total = prog_total_el.inner_text()
    prog_title = prog_total_el.get_attribute("title")
    print("Progression's blended running total (must match the topbar's ~253):", prog_total, "|", prog_title)
    assert prog_total == "~253 total", f"FAIL: expected Progression's total to blend to ~253 like the topbar, got {prog_total}"
    assert "is-estimate" in prog_total_el.get_attribute("class")
    assert prog_title == "244 confirmed + 9 estimated.", f"FAIL: unexpected breakdown tooltip: {prog_title}"
    print("PASS: Progression's running total blends in estimates exactly like the topbar headline does, agreeing on both the figure and its breakdown")

    # --- Turn Summoned rank-by-rank: ranks 1-2 are real (riding on top of
    # BUILD's own real 235, so they render as PLAIN numbers); rank 3 is
    # guessed - its own total must be exactly its own guess higher than the
    # row before it, never frozen. Before the blendedCumulative fix, a
    # guessed-rank row showed the SAME frozen total as the row before it
    # instead, even though its own pill showed a nonzero estimate. ---
    ts_rows = page.locator(".progression-row", has=page.locator(".step-name", has_text="Turn Summoned"))
    totals = [ts_rows.nth(i).locator(".cost-total").inner_text() for i in range(ts_rows.count())]
    print("Turn Summoned rank 1-3's running totals in order:", totals)
    expected = ["238 total", "244 total", "~253 total"]
    assert totals == expected, \
        f"FAIL: the running total must climb by exactly each rank's own real-or-guessed cost - got {totals}"
    print("PASS: the running total climbs through both real ranks and the guessed one, never freezing")

    # --- Owned/to-go (ownedSummary) must blend the same way, not silently
    # drop an owned rank's estimate from either side - see
    # estimatedExtraOwnedPoints in logic.js. BUILD's own preloaded owned
    # progress (95 real points, none of it Turn Summoned, which was only
    # just bought above) starts this real-only on the owned side, with ALL
    # 9 of Turn Summoned's estimate still on "to go". ---
    owned_summary = page.locator("#ownedSummary")
    print("owned summary before owning any of Turn Summoned:", owned_summary.inner_text())
    assert owned_summary.inner_text() == "95 pts owned, ~158 to go", \
        f"FAIL: preloaded owned progress should read as a real 95, with all 9 of Turn Summoned's estimate still on 'to go' - got {owned_summary.inner_text()!r}"
    togo_span0 = owned_summary.locator(".is-estimate")
    assert togo_span0.get_attribute("title") == "149 confirmed + 9 estimated.", \
        f"FAIL: unexpected 'to go' breakdown tooltip: {togo_span0.get_attribute('title')!r}"

    # --- Marking Turn Summoned fully owned (through its guessed rank 3)
    # pulls its entire estimate onto the owned side - there's no live AA
    # left with an INTERIOR unconfirmed rank to demonstrate a partial split
    # (see this file's own header comment), so this checks the all-owned
    # case instead: the owned side picks up the guess (9) on top of its
    # real 104 (95 + ranks 1-2's real 3+6), and the to-go side, with
    # nothing guessed left unowned, drops back to a PLAIN real number - no
    # "~", no estimate styling lingering once nothing's actually estimated
    # anymore. ---
    ts_rows.nth(2).locator(".step-own").click()
    page.wait_for_timeout(150)
    print("owned summary after marking Turn Summoned fully owned:", owned_summary.inner_text())
    assert owned_summary.inner_text() == "~113 pts owned, 140 to go", \
        f"FAIL: owned should blend in rank 3's guess (9) on top of the real 104 (95 + ranks 1-2's real 3+6), and to-go should drop to a plain real 140 - got {owned_summary.inner_text()!r}"
    assert owned_summary.locator(".is-estimate").count() == 1, \
        "FAIL: with nothing guessed left on the to-go side, only the owned side should carry estimate styling"
    owned_span = owned_summary.locator(".is-estimate")
    assert owned_span.get_attribute("title") == "104 confirmed + 9 estimated.", \
        f"FAIL: unexpected owned breakdown tooltip: {owned_span.get_attribute('title')!r}"
    print("PASS: owned/to-go blends in the guess when a guessed rank becomes owned, and to-go cleanly drops the estimate styling once nothing guessed remains unowned")

    print("ERRORS:", errors)
    assert not errors

    # --- Separate, independent scenario: the same build as above (before
    # Spell Casting Subtlety was bought into it), but with a stale "t"
    # (totalPoints) field re-injected into its decoded payload - simulating
    # a share link generated before the point-cap removal. BUILD_STALE was
    # derived by decoding BUILD above, adding "t": 1000, and re-encoding
    # (gzip + base64url, matching encodeBuildCode exactly) - see this
    # test's own git history for the one-off script that produced it, if it
    # ever needs regenerating against a different build. Loading it must
    # produce the exact same result as the clean BUILD - proving a stale
    # field an old link might still carry is truly inert, not just "doesn't
    # crash". Kept as its own page/scenario rather than folded into the one
    # above, so a failure here reads unambiguously as a backward-
    # compatibility regression, not a data-drift one. ---
    page2 = browser.new_page(viewport={"width": 1400, "height": 900})
    errors2 = []
    page2.on("pageerror", lambda exc: errors2.append(str(exc)))
    page2.on("dialog", lambda d: d.accept())
    BUILD_STALE = "H4sIAAAAAAAC_31QSQ7CMAz8i88-xE2alP6AAy-oOFS0QpXYVCE4IP7O2OkiDiBPO4lje2y_6EF1wXSgutlwYvF7phPVpWMa4Wsiw9MkDvhXdi7ELoVnccqRRSlxBfJiNx8s1JeZchG_MQrO8kOwSAipsywyeY5KuaaohrJLeEVjN3SESACqiF0BT5qAissZsGSZ4xxmzFbpRZuACPSmSP2iWQXTVmfoEAbMv0BHyggzygko-xuY5arbnfcqX4tM6yL_bcn6XdaEkk8tiVZpexnuQ3siqIzt5diTisC_G7pje-7hH_uONOVOtTjn3h86SJr-CAIAAA"
    page2.goto(f"{BASE}?build={BUILD_STALE}")
    page2.wait_for_selector("#treeWrap .node")
    page2.wait_for_timeout(200)
    assert not errors2, f"FAIL: loading a build with a stale 't' field threw: {errors2}"
    sv_stale = page2.locator("#spentValue")
    print("stale-field build spentValue:", sv_stale.inner_text(), sv_stale.get_attribute("title"))
    assert sv_stale.inner_text() == "95 / 235"
    assert sv_stale.locator(".is-estimate").count() == 0
    assert sv_stale.get_attribute("title") is None
    print("PASS: a share code carrying a stale 't' field loads without error and produces an identical result to the clean one")
    page2.close()

    # --- Third, independent scenario: owned/to-go must never show a
    # negative "to go", even though nothing stops owned from exceeding
    # what's currently planned. setOwnedRank deliberately doesn't clamp to
    # the planned rank (owned is real-world truth, untouched by a refund -
    # see its own comment in logic.js), so buying an AA, marking it owned,
    # then refunding it back below that watermark is a real, reachable way
    # for ownedPoints() to exceed spentPoints() for that AA. Combat
    # Agility's costs are fully confirmed, so this isolates the plain
    # real-number clamp from the estimate-blending logic above. ---
    page3 = browser.new_page(viewport={"width": 1400, "height": 900})
    errors3 = []
    page3.on("pageerror", lambda exc: errors3.append(str(exc)))
    page3.on("dialog", lambda d: d.accept())
    page3.goto(BASE)
    page3.wait_for_selector("#treeWrap .node")
    page3.click('button[data-tab="general"]')
    ca_node = page3.locator(".node", has=page3.locator(".name", has_text="Combat Agility"))
    ca_node.click()
    for _ in range(3):
        page3.click("#incBtn")
        page3.wait_for_timeout(15)
    page3.click('button[data-tab="progression"]')
    page3.wait_for_timeout(150)
    page3.locator(".progression-row", has=page3.locator(".step-name", has_text="Combat Agility")).nth(2).locator(".step-own").click()
    page3.wait_for_timeout(150)
    print("owned summary with Combat Agility bought and owned to rank 3:", page3.locator("#ownedSummary").inner_text())
    assert page3.locator("#ownedSummary").inner_text() == "12 pts owned, 0 to go"

    page3.click('button[data-tab="general"]')
    ca_node.click()
    for _ in range(2):
        page3.click("#decBtn")
        page3.wait_for_timeout(15)
    print("Combat Agility rank after refunding below its own owned watermark:", page3.locator("#sidePanel .current").inner_text())
    assert page3.locator("#sidePanel .current").inner_text() == "1 / 3"
    page3.click('button[data-tab="progression"]')
    page3.wait_for_timeout(150)
    owned_summary3 = page3.locator("#ownedSummary").inner_text()
    print("owned summary after refunding below owned (must not go negative):", owned_summary3)
    assert owned_summary3 == "12 pts owned, 0 to go", \
        f"FAIL: 'to go' must clamp to 0, not go negative, when owned exceeds the current plan - got {owned_summary3!r}"
    print("PASS: owned/to-go never shows a negative figure, even with owned exceeding the current plan")
    print("ERRORS:", errors3)
    assert not errors3
    page3.close()

    browser.close()
    print("ALL PASS")
