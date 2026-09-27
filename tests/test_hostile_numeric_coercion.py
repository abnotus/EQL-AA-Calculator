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
# Hit three separate call sites, each through the path that actually
# reaches it unfiltered - a naive test routing all three through a single
# ?build= JSON payload would pass even against the broken pre-fix code,
# since a `v` field of 2 or higher always selects compact decoding
# (expandCompactPayload/exportImport.js) regardless of whether the payload
# actually uses compact field names, and compact ranks specifically get
# filtered by expandCompactRanks's own Number.isFinite check (a separate,
# earlier fix) before clampRankValue ever sees them - a hostile rank value
# sent that way never exercises safeParseInt at all.
#   - charLevel and a waypoint's pts pass through expandCompactPayload
#     completely unfiltered (`charLevel: l`, `waypoints: w || []` - see
#     that function's own comments), so a compact (v2 keyed-object) share
#     code's `l`/`w` fields reach applyLoaded/sanitizeWaypoints untouched -
#     exercises safeParseInt for real.
#   - A rank value's only unfiltered path is a v4+ localStorage build
#     payload: main.js's boot calls applyLoaded(loadLocal()) directly, with
#     no decodeBuildCode/expandCompactRanks step in between at all.
import os, sys, io, json, base64
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
STORAGE_KEY = "eql_aa_builder_v1"
HOSTILE = {"toString": None}


def compact_build_code(l=50, w=None):
    # v2 keyed-object compact shape (BUILD_CODE_VERSION, not SAVE_FORMAT_VERSION -
    # see exportImport.js's own header comment on the two being unrelated
    # numbers). columnar = v>=4, so v2's r/o are the pair-array shape; empty
    # here since ranks aren't what this payload is exercising.
    payload = {"v": 2, "c": [], "l": l, "r": [], "p": [], "o": None, "w": w or []}
    raw = json.dumps(payload).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())

    # --- charLevel: {"toString": null}, via a compact share code (l passes
    # straight through expandCompactPayload unfiltered) ---
    code = compact_build_code(l=HOSTILE)
    page.goto(f"{BASE}?build={code}")
    page.wait_for_timeout(500)
    tree_count = page.locator("#treeWrap .node").count()
    level_value = page.locator("#levelInput").input_value()
    print(f"charLevel case: tree node count={tree_count}, #levelInput value={level_value!r}, errors={errors}")
    assert not errors, f"FAIL: a hostile charLevel threw instead of degrading gracefully: {errors}"
    assert tree_count > 0, "FAIL: tree never rendered - startup froze on a hostile charLevel"
    assert level_value == "50", f"FAIL: an unparseable charLevel should leave the default (50) untouched, got {level_value!r}"
    print("PASS: a hostile charLevel value no longer crashes startup, and falls back to the default level")

    # --- A waypoint's pts: {"toString": null}, via a compact share code's
    # `w` field (also unfiltered - sanitizeWaypoints is the only guard) ---
    errors.clear()
    code = compact_build_code(w=[[HOSTILE, "test", None]])
    page.goto(f"{BASE}?build={code}")
    page.wait_for_timeout(500)
    tree_count = page.locator("#treeWrap .node").count()
    chip_count = page.locator(".waypoint-chip").count()
    print(f"waypoint case: tree node count={tree_count}, waypoint chips={chip_count}, errors={errors}")
    assert not errors, f"FAIL: a hostile waypoint pts threw instead of degrading gracefully: {errors}"
    assert tree_count > 0, "FAIL: tree never rendered - startup froze on a hostile waypoint pts"
    assert chip_count == 0, f"FAIL: a waypoint with an unparseable pts should be dropped entirely, got {chip_count} chip(s)"
    print("PASS: a hostile waypoint pts value no longer crashes startup, and the waypoint is dropped")

    # --- A rank value: {"toString": null}, via a v4 localStorage build
    # payload - the one path a hostile rank reaches clampRankValue
    # unfiltered (a ?build= share code's compact ranks get pre-filtered by
    # expandCompactRanks's own guard before this point, see header comment). ---
    errors.clear()
    local_payload = {
        "v": 4,
        "selectedClasses": ["Bard", "Beastlord", "Berserker"],
        "charLevel": 50,
        "ranks": {"general": {"adamant-will": HOSTILE}, "archetype": {}, "special": {}, "classes": {}},
        "purchaseOrder": [],
        "waypoints": []
    }
    page.goto(BASE)  # establish the origin so localStorage.setItem below has somewhere to land
    page.evaluate(
        "(kv) => localStorage.setItem(kv[0], JSON.stringify(kv[1]))",
        [STORAGE_KEY, local_payload]
    )
    page.reload()
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

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
