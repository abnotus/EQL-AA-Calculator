# -*- coding: utf-8 -*-
# saveBuildAs (builds.js) used to report success (a truthy id) the moment
# the slot's own localStorage.setItem succeeded, even if a LATER write in
# the same call - the seeded owned-profile write for a brand-new slot, or
# the index write - failed (a full/unavailable quota crossed by that later,
# smaller write, not necessarily the slot's own larger one). The build
# would look saved this session but be gone after reload, with no error
# ever shown. Fixed by having saveIndex/saveOwnedProfileTo report their own
# success and saveBuildAs check both before returning a real id.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
BUILDS_INDEX_KEY = "eql_aa_builds_index_v1"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # The index write fails (simulating a quota boundary crossed by that
    # write specifically, not the slot write before it) - saving a
    # brand-new build must report failure, not silently succeed.
    page.evaluate(
        """(key) => {
            const real = Storage.prototype.setItem;
            Storage.prototype.setItem = function (k, v) {
                if (k === key) throw new DOMException('quota', 'QuotaExceededError');
                return real.call(this, k, v);
            };
        }""",
        BUILDS_INDEX_KEY
    )
    page.click("#buildsBtn")
    page.wait_for_timeout(100)
    page.fill("#buildSaveName", "Should Not Persist")
    page.click("#buildSaveBtn")
    page.wait_for_timeout(150)
    toast_text = page.locator("#toast").inner_text()
    print("toast after a save whose index write fails:", toast_text)
    assert "couldn't save" in toast_text.lower(), \
        f"FAIL: expected a failure toast when the index write fails, got: {toast_text!r}"
    persisted_raw = page.evaluate("(key) => localStorage.getItem(key)", BUILDS_INDEX_KEY)
    print("BUILDS_INDEX_KEY after the failed save (must be untouched):", persisted_raw)
    assert not persisted_raw or "Should Not Persist" not in persisted_raw, \
        "FAIL: the index write failed but the build name still ended up persisted"
    print("PASS: a save whose index write fails reports failure, not a false success")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
