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

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
