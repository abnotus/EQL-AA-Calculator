# -*- coding: utf-8 -*-
# builds.js's activeBuildMatchesCurrent() used to be a raw string/
# JSON.stringify comparison against the active slot's stored payload - it
# broke the instant buildPayload's shape ever changed (this happened for
# real: totalPoints's removal made every pre-existing slot read as
# "unsaved" against a live build that hadn't actually changed, in every
# menu that asks this question - the Builds menu's own Load button, a
# share link, a text import, since they all funnel through
# confirmReplaceCurrentBuild). Replaced with a structural comparison that
# only checks the keys today's buildPayload() actually defines, ignoring
# any extra/reordered legacy fields a stored slot might carry - immune to
# this whole class of bug permanently, not just healed for the one field
# that's been removed so far.
#
# This drives the actual bug report: an "active" slot whose stored JSON has
# fields in a different order than today's buildPayload AND still carries
# stale fields (totalPoints, plus a made-up long-gone field) - loading it
# via the Builds menu with nothing actually changed must not warn. A
# genuinely different build must still warn, proving the fix didn't also
# swallow real changes.
#
# Also covers the converse direction, found in review: a stored slot
# entirely MISSING a key current buildPayload() defines (any slot saved in
# 1.3.x-1.4.x, before waypoints shipped in 1.5.0, has no "waypoints" field
# at all - not present, not null, just absent). The first version of the
# structural fix only tolerated *extra* keys on the stored side, not
# *missing* ones - a slot like that would still have read as permanently
# "unsaved" until re-saved, not even self-healing. Fixed by treating a
# missing stored key as a match only when today's value for that key is an
# empty composite ([] or {}) - applyLoaded loading that exact slot produces
# exactly that empty default, so the two are provably equivalent content,
# not just "close enough". The converse guard (missing on the stored side,
# non-empty on the live side) must still warn, proving the tolerance only
# forgives genuine emptiness, not any missing key regardless of content.
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8743/index.html"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    dialogs = []
    page.on("dialog", lambda d: (dialogs.append(d.message), d.accept()))

    # --- An active slot whose stored payload has reordered fields, a stale
    # totalPoints value, AND a made-up field current buildPayload() has
    # never heard of - simulates real historical schema drift, not just
    # the one case a targeted migration already covers. Live state on a
    # fresh boot (default classes/level, nothing picked) matches this
    # slot's actual content exactly. ---
    weird_order_payload = {
        "waypoints": [],
        "totalPoints": 1000,
        "purchaseOrder": [],
        "someLongGoneField": "legacy junk from an even older schema version",
        "ranks": {"classes": {}, "special": {}, "archetype": {}, "general": {}},
        "charLevel": 50,
        "selectedClasses": ["Bard", "Beastlord", "Berserker"],
        "v": 4,
    }
    index_payload = [{"id": "weirdslot", "name": "Weird Order Build", "updatedAt": 1000}]
    page.add_init_script(f"""
        localStorage.setItem('eql_aa_builds_index_v1', {json.dumps(json.dumps(index_payload))});
        localStorage.setItem('eql_aa_build_weirdslot', {json.dumps(json.dumps(weird_order_payload))});
        localStorage.setItem('eql_aa_active_build_id', 'weirdslot');
    """)
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)

    page.click("#buildsBtn")
    page.wait_for_timeout(100)
    load_btn = page.locator(".build-row", has=page.locator(".build-name", has_text="Weird Order Build")).locator('button[data-action="load"]')
    load_btn.click()
    page.wait_for_timeout(100)
    print("dialogs loading a matching-but-differently-shaped active slot:", dialogs)
    assert dialogs == [], f"FAIL: a slot that matches content-wise (just shaped differently) should not warn, got {dialogs}"
    print("PASS: reordered fields + stale/unknown keys in the active slot don't cause a false 'unsaved' warning")
    # No warning means loadBuild() proceeded and the Load handler already
    # closed the modal itself (see render.js) - nothing left to close here.

    # --- A genuine change since the last save must still warn - the fix
    # must not have swallowed real-difference detection along with the
    # false positives. ---
    dialogs.clear()
    page.click('button[data-tab="general"]')
    aw = page.locator(".node", has=page.locator(".name", has_text="Adamant Will"))
    aw.click()
    page.click("#incBtn")  # a real, new pick - genuinely diverges from the slot
    page.wait_for_timeout(50)
    page.click("#buildsBtn")
    page.wait_for_timeout(100)
    load_btn2 = page.locator(".build-row", has=page.locator(".build-name", has_text="Weird Order Build")).locator('button[data-action="load"]')
    load_btn2.click()
    page.wait_for_timeout(100)
    print("dialogs after a real change then Load (must warn):", dialogs)
    assert len(dialogs) >= 1 and "isn't saved" in dialogs[0], f"FAIL: a genuinely different build should still warn, got {dialogs}"
    print("PASS: a real difference from the active slot still triggers the unsaved-changes warning")

    # --- A slot saved before waypoints existed (no "waypoints" key at all,
    # not just an empty one) - fresh boot's live state (no waypoints
    # either) must be considered a match, no warning. Fresh page/context so
    # nothing from the scenario above bleeds in. ---
    page2 = browser.new_page(viewport={"width": 1400, "height": 900})
    dialogs2 = []
    page2.on("dialog", lambda d: (dialogs2.append(d.message), d.accept()))
    pre_waypoint_payload = {
        "v": 4,
        "selectedClasses": ["Bard", "Beastlord", "Berserker"],
        "charLevel": 50,
        # A real purchase, not an empty build - confirmReplaceCurrentBuild
        # short-circuits to "nothing at risk, proceed silently" whenever
        # spentPoints() <= 0, regardless of activeBuildMatchesCurrent, so an
        # all-empty build could never reach the comparison this test is
        # actually about. This gives the converse case below real spent
        # points to make that gate irrelevant, isolating the waypoints
        # field as the only difference under test.
        "ranks": {"general": {"adamant-will": 1}, "archetype": {}, "special": {}, "classes": {}},
        "purchaseOrder": [{"scope": "general", "className": None, "key": "adamant-will"}],
        # deliberately no "waypoints" key at all
    }
    index2 = [{"id": "prewaypointslot", "name": "Pre-Waypoint Build", "updatedAt": 1000}]
    page2.add_init_script(f"""
        localStorage.setItem('eql_aa_builds_index_v1', {json.dumps(json.dumps(index2))});
        localStorage.setItem('eql_aa_build_prewaypointslot', {json.dumps(json.dumps(pre_waypoint_payload))});
        localStorage.setItem('eql_aa_active_build_id', 'prewaypointslot');
    """)
    page2.goto(BASE)
    page2.wait_for_selector("#treeWrap .node")
    page2.wait_for_timeout(200)
    page2.click("#buildsBtn")
    page2.wait_for_timeout(100)
    load_btn3 = page2.locator(".build-row", has=page2.locator(".build-name", has_text="Pre-Waypoint Build")).locator('button[data-action="load"]')
    load_btn3.click()
    page2.wait_for_timeout(100)
    print("dialogs loading an untouched pre-1.5.0 slot with no waypoints key at all:", dialogs2)
    assert dialogs2 == [], f"FAIL: a slot missing 'waypoints' entirely should match live state that also has none, got {dialogs2}"
    print("PASS: a stored slot missing a key entirely matches live state when today's value for that key is empty")

    # --- Converse: same missing-waypoints slot, but live state now HAS a
    # waypoint - the tolerance must only forgive genuine emptiness, not any
    # missing key regardless of content. ---
    dialogs2.clear()
    page2.click('button[data-tab="progression"]')
    page2.wait_for_timeout(50)
    page2.click("#addWaypointBtn")
    page2.wait_for_timeout(50)
    page2.fill("#waypointPtsInput", "40")
    page2.click("#saveWaypointBtn")
    page2.wait_for_timeout(50)
    page2.click("#buildsBtn")
    page2.wait_for_timeout(100)
    load_btn4 = page2.locator(".build-row", has=page2.locator(".build-name", has_text="Pre-Waypoint Build")).locator('button[data-action="load"]')
    load_btn4.click()
    page2.wait_for_timeout(100)
    print("dialogs after adding a waypoint then loading the waypoints-less slot (must warn):", dialogs2)
    assert len(dialogs2) >= 1 and "isn't saved" in dialogs2[0], f"FAIL: a real waypoint the stored slot can't have should still warn, got {dialogs2}"
    print("PASS: the missing-key tolerance only forgives emptiness - a real non-empty difference still warns")
    page2.close()

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
