# -*- coding: utf-8 -*-
# purchaseOrder has no length limit of its own on the untrusted-input path
# (localStorage, a pasted build code, a share link) - state.ranks (the
# real, small rank counts) is what's actually validated/clamped
# (clampRankValue), but reconcilePurchaseOrderCounts (logic.js), which
# trims purchaseOrder down to match those counts, costs far worse than
# linear time in purchaseOrder's own length: it makes one backward pass
# per distinct AA with excess entries, and each pass scans the *current*
# state.purchaseOrder from the end. A purchaseOrder inflated to tens of
# thousands of entries for a real, held AA turns "one small build" into a
# multi-second tab freeze on load - a crafted share link doing that to
# whoever opens it, not just its author.
#
# MAX_PURCHASE_ORDER (state.js's deserializePurchaseOrder) truncates the
# raw untrusted array to a generous-but-bounded ceiling before any of that
# reconciliation work runs. This seeds a build slot with a real held rank
# (adamant-will, rank 2) and a purchaseOrder inflated to 50,000 entries
# for that same AA, then confirms the page still loads promptly and the
# in-memory purchaseOrder ends up correctly bounded and reconciled, not
# just "eventually correct after a long freeze."
import os, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

MALICIOUS_ENTRY_COUNT = 50000

BUILD_PAYLOAD = {
    "v": 4,
    "selectedClasses": ["Bard", "Beastlord", "Berserker"],
    "charLevel": 50,
    "ranks": {"general": {"adamant-will": 2}, "archetype": {}, "special": {}, "classes": {}},
    "purchaseOrder": [{"scope": "general", "className": None, "key": "adamant-will"}] * MALICIOUS_ENTRY_COUNT,
    "waypoints": [],
}

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())

    page.add_init_script(f"""
        localStorage.setItem('eql_aa_builder_v1', {json.dumps(json.dumps(BUILD_PAYLOAD))});
    """)

    start = time.time()
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)
    elapsed = time.time() - start
    print(f"page load with a {MALICIOUS_ENTRY_COUNT}-entry purchaseOrder took {elapsed:.2f}s")
    assert elapsed < 5, f"FAIL: load took {elapsed:.2f}s - the purchaseOrder cap should keep this fast regardless of input size"
    print("PASS: load stayed fast despite a massively inflated purchaseOrder")

    stored = json.loads(page.evaluate("localStorage.getItem('eql_aa_builder_v1')"))
    print("purchaseOrder length after boot-time reconciliation:", len(stored["purchaseOrder"]))
    # Reconciled against the real held rank (2), not the malicious count -
    # exactly 2 entries once repaired, well under the truncation ceiling.
    assert len(stored["purchaseOrder"]) == 2, \
        f"FAIL: expected purchaseOrder reconciled down to 2 entries (the real held rank), got {len(stored['purchaseOrder'])}"
    print("PASS: purchaseOrder was capped and correctly reconciled to the real held rank")

    rank_text = page.locator(".node", has=page.locator(".name", has_text="Adamant Will")).locator(".ranktext").inner_text()
    print("Adamant Will's rendered rank:", rank_text)
    assert rank_text.strip().startswith("2 /"), f"FAIL: expected the real rank (2) to still render correctly, got {rank_text}"
    print("PASS: the real rank still renders correctly after the truncation/reconciliation")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
