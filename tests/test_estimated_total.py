# -*- coding: utf-8 -*-
# The topbar's "Points Spent" headline number blends real + estimated costs
# (colored blue, ~9 instead of 3) when the build includes at least one
# purchased-but-unconfirmed rank with a guess - the ~ prefix and color are
# the only visible cue; the confirmed/estimated breakdown lives in the
# title tooltip only, same hover-to-disclose pattern as every other
# estimate badge in the app (no separate visible note element anymore -
# topbar is glanceable-density territory). Progression's own running total
# blends the exact same way now (it used to stay strictly real while the
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
# So the guessed-cost scenarios below buy Spell Casting Subtlety (archetype,
# real rank 1 cost 2, five manually-guessed ranks after it: 3/4/5/6/7) live
# on top of the loaded build instead, reintroducing a real "several
# different-sized guesses in a row" case without needing a stale, hand-
# picked share code. Refreshed periodically to the user's current build as
# they keep playing - BUILD_STALE is regenerated alongside it each time
# (decode BUILD, inject "t": 1000, re-encode gzip+base64url) so both stay
# in sync.
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
    assert sv0.inner_text() == "0"
    assert sv0.get_attribute("class") is None
    color0 = sv0.evaluate("el => getComputedStyle(el).color")
    assert color0 == "rgb(217, 76, 76)", f"FAIL: expected real 'spent' red, got {color0}"
    assert sv0.get_attribute("title") is None
    print("PASS: no guesses purchased -> plain real number, red, no tooltip")

    # --- Load the real build - fully confirmed now, so it's a plain real
    # number too, same as the fresh-page case above (just non-zero). ---
    page.goto(f"{BASE}?build={BUILD}")
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)

    sv = page.locator("#spentValue")
    print("spentValue with BUILD alone (now fully confirmed):", sv.inner_text(), sv.get_attribute("class"))
    assert sv.inner_text() == "235"
    assert sv.get_attribute("class") is None, "FAIL: a fully-confirmed build shouldn't carry estimate styling"
    assert sv.get_attribute("title") is None

    # --- Buy Spell Casting Subtlety live on top of it: rank 1 is real (cost
    # 2), ranks 2-6 are each independently guessed (3/4/5/6/7 - manual,
    # very-low confidence, chosen for having several guessed ranks in a row
    # like Packrat used to). Real total climbs to 237 (235 + rank 1's real
    # 2); ranks 2-6 add nothing to spentPoints() itself but 25 combined to
    # the blended headline (237 + 25 = 262). ---
    page.click('button[data-tab="archetype"]')
    page.wait_for_timeout(100)
    scs_node = page.locator(".node", has=page.locator(".name", has_text="Spell Casting Subtlety"))
    scs_node.click()
    for _ in range(6):
        page.click("#incBtn")
        page.wait_for_timeout(15)
    print("spentValue after buying Spell Casting Subtlety to rank 6:", sv.inner_text(), sv.get_attribute("title"))
    assert sv.inner_text() == "~262"
    assert "is-estimate" in sv.get_attribute("class")
    color = sv.evaluate("el => getComputedStyle(el).color")
    print("spentValue computed color:", color)
    assert color == "rgb(90, 169, 230)", f"FAIL: blended headline should render blue, got {color}"
    assert sv.get_attribute("title") == "237 confirmed + 25 estimated."
    print("PASS: headline blends to ~262 in blue, full breakdown lives only in the tooltip")

    # --- Progression's own running total now blends the same way the
    # topbar does - the last row's total must match the headline exactly
    # (~262), with the same "237 confirmed + 25 estimated." breakdown in its
    # own tooltip, proving the two displays agree rather than showing two
    # different numbers for the same underlying build. ---
    page.click('button[data-tab="progression"]')
    page.wait_for_timeout(150)
    prog_total_el = page.locator(".progression-row .cost-total").last
    prog_total = prog_total_el.inner_text()
    prog_title = prog_total_el.get_attribute("title")
    print("Progression's blended running total (must match the topbar's ~262):", prog_total, "|", prog_title)
    assert prog_total == "~262 total", f"FAIL: expected Progression's total to blend to ~262 like the topbar, got {prog_total}"
    assert "is-estimate" in prog_total_el.get_attribute("class")
    assert prog_title == "237 confirmed + 25 estimated.", f"FAIL: unexpected breakdown tooltip: {prog_title}"
    print("PASS: Progression's running total blends in estimates exactly like the topbar headline does, agreeing on both the figure and its breakdown")

    # --- Spell Casting Subtlety rank-by-rank: rank 1 is real (riding on top
    # of BUILD's own real 235, so it renders as a PLAIN number); ranks 2-6
    # are each independently guessed, by a DIFFERENT amount each time
    # (3/4/5/6/7, not a flat +1) - every one must still show a total that's
    # exactly its own guess higher than the row before it, never frozen.
    # Before the blendedCumulative fix, every guessed-rank row showed the
    # SAME frozen total instead, even though each row's own pill showed a
    # nonzero estimate. ---
    scs_rows = page.locator(".progression-row", has=page.locator(".step-name", has_text="Spell Casting Subtlety"))
    totals = [scs_rows.nth(i).locator(".cost-total").inner_text() for i in range(scs_rows.count())]
    print("Spell Casting Subtlety rank 1-6's running totals in order:", totals)
    expected = ["237 total", "~240 total", "~244 total", "~249 total", "~255 total", "~262 total"]
    assert totals == expected, \
        f"FAIL: the running total must climb by exactly each rank's own real-or-guessed cost - got {totals}"
    print("PASS: the running total climbs through both the real rank and every differently-sized guessed rank, never freezing")

    # --- Owned/to-go (ownedSummary) must blend the same way, not silently
    # drop an owned rank's estimate from either side - see
    # estimatedExtraOwnedPoints in logic.js. BUILD's own preloaded owned
    # progress (95 real points, none of it Spell Casting Subtlety, which was
    # only just bought above) starts this real-only on the owned side, with
    # ALL 25 of Spell Casting Subtlety's estimate still on "to go". ---
    owned_summary = page.locator("#ownedSummary")
    print("owned summary before owning any of Spell Casting Subtlety:", owned_summary.inner_text())
    assert owned_summary.inner_text() == "95 pts owned, ~167 to go", \
        f"FAIL: preloaded owned progress should read as a real 95, with all 25 of Spell Casting Subtlety's estimate still on 'to go' - got {owned_summary.inner_text()!r}"
    togo_span0 = owned_summary.locator(".is-estimate")
    assert togo_span0.get_attribute("title") == "142 confirmed + 25 estimated.", \
        f"FAIL: unexpected 'to go' breakdown tooltip: {togo_span0.get_attribute('title')!r}"

    # --- Marking Spell Casting Subtlety owned through rank 3 (its real
    # rank 1 plus two of its guessed ranks) pulls part - not all - of its
    # estimate onto the owned side, so both "owned" and "to go" carry an
    # estimate at once, proving the blend isn't just an all-or-nothing
    # move of the whole AA's estimate from one side to the other. ---
    scs_rows.nth(2).locator(".step-own").click()
    page.wait_for_timeout(150)
    print("owned summary after marking Spell Casting Subtlety owned through rank 3:", owned_summary.inner_text())
    assert owned_summary.inner_text() == "~104 pts owned, ~158 to go", \
        f"FAIL: owned should blend in ranks 2-3's guesses (7) on top of the real 97 (95 + rank 1's real 2) - got {owned_summary.inner_text()!r}"
    owned_span = owned_summary.locator(".is-estimate").first
    assert owned_span.get_attribute("title") == "97 confirmed + 7 estimated.", \
        f"FAIL: unexpected owned breakdown tooltip: {owned_span.get_attribute('title')!r}"
    togo_span = owned_summary.locator(".is-estimate").last
    assert togo_span.get_attribute("title") == "140 confirmed + 18 estimated.", \
        f"FAIL: unexpected 'to go' breakdown tooltip: {togo_span.get_attribute('title')!r}"
    print("PASS: owned/to-go blends estimates on both sides at once when only part of a guessed AA is owned, and both still sum to the blended headline")

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
    assert sv_stale.inner_text() == "235"
    assert sv_stale.get_attribute("class") is None
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
