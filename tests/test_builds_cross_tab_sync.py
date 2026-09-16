# -*- coding: utf-8 -*-
# cachedIndex (builds.js) only stayed in sync with THIS tab's own writes.
# Before this fix, a tab that had cached the index once would never learn
# about another tab's save no matter how much later it happened - even
# minutes afterward, its next save would still clobber the other tab's
# addition. Fixed by listening for the "storage" event (which only ever
# fires in OTHER tabs) and dropping cachedIndex so the next read picks up
# the fresh value instead of overwriting it.
#
# What this does NOT fix: two tabs saving within the same short window,
# before either one's "storage" event has been delivered, can still race
# and clobber each other - the event only invalidates the cache once it
# arrives, which is asynchronous and not instantaneous. This test proves
# event-driven invalidation itself works (dispatch the event, then confirm
# a subsequent save doesn't overwrite what it announced), not that true
# concurrent writes are now impossible - that would need real cross-tab
# mutual exclusion (e.g. the Web Locks API), which this doesn't attempt.
# The permanently-stale-cache bug above is fixed; the inherent last-write-
# wins race for genuinely simultaneous writes is a smaller, separate,
# still-open gap.
#
# Playwright runs everything in one tab, so this simulates a second tab's
# write directly (bypassing the app's own JS, the way an actual other tab's
# independent page would) and manually dispatches the "storage" event this
# tab's own write never would - a same-tab localStorage.setItem never fires
# "storage" in the tab that made it, only in others, which is exactly why
# this needed simulating rather than just triggering a second real save
# from this same page.
import os, sys, io, json
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

    # An external ("other tab") write to BUILDS_INDEX_KEY, signaled the way
    # a real other tab's write would be - must not get clobbered by a save
    # made afterward in this tab.
    external_entry = {"id": "external-tab-build", "name": "From Other Tab", "updatedAt": 1}
    page.evaluate(
        """([key, entry]) => {
            localStorage.setItem(key, JSON.stringify([entry]));
            window.dispatchEvent(new StorageEvent('storage', { key, newValue: JSON.stringify([entry]) }));
        }""",
        [BUILDS_INDEX_KEY, external_entry]
    )

    page.click("#buildsBtn")
    page.wait_for_timeout(100)
    page.fill("#buildSaveName", "From This Tab")
    page.click("#buildSaveBtn")
    page.wait_for_timeout(150)
    toast_text = page.locator("#toast").inner_text()
    print("toast after saving in this tab following the simulated external write:", toast_text)
    assert "saved" in toast_text.lower(), f"FAIL: expected a normal success toast, got: {toast_text!r}"

    final_raw = page.evaluate("(key) => localStorage.getItem(key)", BUILDS_INDEX_KEY)
    final_index = json.loads(final_raw)
    names = sorted(b["name"] for b in final_index)
    print("BUILDS_INDEX_KEY after both writes:", names)
    assert "From Other Tab" in names, \
        f"FAIL: the external tab's build was clobbered by this tab's save - got {names}"
    assert "From This Tab" in names, f"FAIL: this tab's own save didn't persist - got {names}"
    print("PASS: a storage-event-signaled external write survives a subsequent save from this tab")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
