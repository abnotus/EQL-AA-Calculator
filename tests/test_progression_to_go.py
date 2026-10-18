# -*- coding: utf-8 -*-
# Progression's "X pts owned, Y to go": Y is the cost of the planned steps
# not yet owned. It used to be planned minus owned, so owned ranks outside
# the plan (a pre-1.9 user's builds all share one legacy profile) hid
# planned ranks that were still untrained.
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
EMPTY = {"general": {}, "archetype": {}, "special": {}, "classes": {}}
CA = {"scope": "general", "className": None, "key": "combat-agility"}

# Combat Agility costs 2/4/6, Fear Resistance 2/4/6/9.
CASES = [
    ("owned outside the plan", {"general": {"combat-agility": 2}}, {"general": {"fear-resistance": 4}}, "21 pts owned, 6 to go"),
    ("part of the plan owned", {"general": {"combat-agility": 3}}, {"general": {"combat-agility": 1}}, "2 pts owned, 10 to go"),
    ("owned above the plan", {"general": {"combat-agility": 1}}, {"general": {"combat-agility": 3}}, "12 pts owned, 0 to go"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    errors = []
    for label, ranks, owned, want in CASES:
        ranks = {**EMPTY, **ranks}
        owned = {**EMPTY, **owned}
        payload = {"v": 4, "selectedClasses": ["Bard", "Beastlord", "Berserker"], "charLevel": 50,
                   "ranks": ranks, "purchaseOrder": [CA] * ranks["general"]["combat-agility"], "waypoints": []}
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.add_init_script(
            f"localStorage.setItem('eql_aa_builder_v1', {json.dumps(json.dumps(payload))});"
            f"localStorage.setItem('eql_aa_owned_legacy', {json.dumps(json.dumps({'v': 4, 'owned': owned}))});"
        )
        page.goto(BASE)
        page.wait_for_selector("#treeWrap .node")
        page.click('button[data-tab="progression"]')
        page.wait_for_selector(".progression-row")
        got = page.locator("#ownedSummary").inner_text()
        print(f"{label}: {got!r}")
        assert got == want, f"FAIL: {label} - expected {want!r}, got {got!r}"
        page.close()
    assert not errors, errors
    print("PASS: 'to go' counts only the planned steps not yet owned")
    browser.close()
    print("ALL PASS")
