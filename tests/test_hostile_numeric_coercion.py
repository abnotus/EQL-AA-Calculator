# -*- coding: utf-8 -*-
# parseInt implicitly stringifies its argument via the ToPrimitive
# abstract operation - for most bad inputs (a plain object, an array) that
# just yields some string and parses to NaN like any other garbage, but for
# an object whose toString isn't callable and whose (inherited, default)
# valueOf doesn't return a primitive either - {"toString": null} is the
# simplest case - ToPrimitive itself throws a TypeError instead of ever
# reaching parseInt's own parsing. That's an uncaught, synchronous
# exception straight out of applyLoaded, which runs during page boot for a
# ?build= link: the tree never renders and every control stays dead, with
# no toast or error the player can act on - reported as a P2 (confirmed in
# Chrome).
#
# Hit three separate call sites the same way, all reachable from a share
# link or pasted import with no prior validation: applyLoaded's own
# charLevel field, a rank value (clampRankValue), and a waypoint's pts
# (sanitizeWaypoints). Fixed with a shared safeParseInt() that only calls
# parseInt for an input already a number or string, so each of these now
# degrades the same way any other malformed value already did (dropped /
# left at its default) instead of throwing.
import os, sys, io, json, base64
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
HOSTILE = {"toString": None}


def build_code(ranks=None, waypoints=None, char_level=50):
    payload = {
        "v": 4,
        "selectedClasses": ["Bard", "Beastlord", "Berserker"],
        "charLevel": char_level,
        "ranks": ranks or {"general": {}, "archetype": {}, "special": {}, "classes": {}},
        "purchaseOrder": [],
        "waypoints": waypoints or []
    }
    raw = json.dumps(payload).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())

    # --- charLevel: {"toString": null} - the exact reported case ---
    code = build_code(char_level=HOSTILE)
    page.goto(f"{BASE}?build={code}")
    page.wait_for_timeout(500)
    tree_count = page.locator("#treeWrap .node").count()
    level_value = page.locator("#levelInput").input_value()
    print(f"charLevel case: tree node count={tree_count}, #levelInput value={level_value!r}, errors={errors}")
    assert not errors, f"FAIL: a hostile charLevel threw instead of degrading gracefully: {errors}"
    assert tree_count > 0, "FAIL: tree never rendered - startup froze on a hostile charLevel"
    assert level_value == "50", f"FAIL: an unparseable charLevel should leave the default (50) untouched, got {level_value!r}"
    print("PASS: a hostile charLevel value no longer crashes startup, and falls back to the default level")

    # --- A rank value: {"toString": null} for a real, current AA key ---
    errors.clear()
    code = build_code(ranks={"general": {"adamant-will": HOSTILE}, "archetype": {}, "special": {}, "classes": {}})
    page.goto(f"{BASE}?build={code}")
    page.wait_for_timeout(500)
    tree_count = page.locator("#treeWrap .node").count()
    print(f"rank case: tree node count={tree_count}, errors={errors}")
    assert not errors, f"FAIL: a hostile rank value threw instead of degrading gracefully: {errors}"
    assert tree_count > 0, "FAIL: tree never rendered - startup froze on a hostile rank value"
    page.click('button[data-tab="general"]')
    page.locator(".node", has=page.locator(".name", has_text="Adamant Will")).first.click()
    current = page.locator("#sidePanel .current").inner_text()
    print("Adamant Will rank after a hostile stored value:", current)
    assert current == "0 / 4", f"FAIL: an unparseable rank should be dropped to 0, got {current!r}"
    print("PASS: a hostile rank value no longer crashes startup, and the rank is dropped rather than kept garbage")

    # --- A waypoint's pts: {"toString": null} ---
    errors.clear()
    code = build_code(waypoints=[{"pts": HOSTILE, "label": "test", "color": None}])
    page.goto(f"{BASE}?build={code}")
    page.wait_for_timeout(500)
    tree_count = page.locator("#treeWrap .node").count()
    chip_count = page.locator(".waypoint-chip").count()
    print(f"waypoint case: tree node count={tree_count}, waypoint chips={chip_count}, errors={errors}")
    assert not errors, f"FAIL: a hostile waypoint pts threw instead of degrading gracefully: {errors}"
    assert tree_count > 0, "FAIL: tree never rendered - startup froze on a hostile waypoint pts"
    assert chip_count == 0, f"FAIL: a waypoint with an unparseable pts should be dropped entirely, got {chip_count} chip(s)"
    print("PASS: a hostile waypoint pts value no longer crashes startup, and the waypoint is dropped")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
