# -*- coding: utf-8 -*-
# saveBuildAs (builds.js) used to report success (a truthy id) the moment
# the slot's own localStorage.setItem succeeded, even if a LATER write in
# the same call - the seeded owned-profile write for a brand-new slot, or
# the index write - failed (a full/unavailable quota crossed by that later,
# smaller write, not necessarily the slot's own larger one). The build
# would look saved this session but be gone after reload, with no error
# ever shown. Fixed by having saveIndex/saveOwnedProfileTo report their own
# success and saveBuildAs check both before returning a real id.
#
# A second, related scenario: deleteBuild used to remove the slot's own
# data unconditionally, even when the index write that was supposed to
# drop it from the list failed - producing a dangling index entry that
# points at a now-missing build (reproduced independently in review; not
# something saveBuildAs's own fix touched, since it's the opposite
# direction - deleteBuild destroying too much on failure, not reporting a
# false success). Fixed by only removing the slot's data once the index
# write actually succeeded, so a failed delete leaves both sides
# consistent (and safely retryable) instead of half-done.
#
# What this file does NOT cover: saveLocal/saveOwned (state.js) and the
# owned-tracking Link/Merge/Split primitives (builds.js) still swallow
# their own localStorage failures without reporting them to a caller -
# only saveBuildAs/renameBuild/deleteBuild's own write paths were brought
# in line with the "report partial failure" contract here. Broader
# persistence-reliability coverage remains an open, separate piece of work.
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
    page.fill("#buildSaveName", "Should Not Persist")
    page.click("#buildSaveBtn")
    toast_text = page.locator("#toast").inner_text()
    print("toast after a save whose index write fails:", toast_text)
    assert "couldn't save" in toast_text.lower(), \
        f"FAIL: expected a failure toast when the index write fails, got: {toast_text!r}"
    persisted_raw = page.evaluate("(key) => localStorage.getItem(key)", BUILDS_INDEX_KEY)
    print("BUILDS_INDEX_KEY after the failed save (must be untouched):", persisted_raw)
    assert not persisted_raw or "Should Not Persist" not in persisted_raw, \
        "FAIL: the index write failed but the build name still ended up persisted"
    print("PASS: a save whose index write fails reports failure, not a false success")

    # --- Deleting a build whose index write fails must not remove the
    # slot's own data either - a dangling index entry (pointing at nothing)
    # is worse than just leaving the delete not-yet-applied. Needs a fresh
    # page first: the patched Storage.prototype.setItem above is page-level
    # JS state, and this scenario needs a REAL save to succeed before
    # testing a failed delete against it. ---
    page.reload()
    page.wait_for_selector("#treeWrap .node")
    page.click("#buildsBtn")
    page.fill("#buildSaveName", "Delete Test")
    page.click("#buildSaveBtn")
    index_raw = page.evaluate("(key) => localStorage.getItem(key)", BUILDS_INDEX_KEY)
    build_id = next(b["id"] for b in json.loads(index_raw) if b["name"] == "Delete Test")
    slot_key = f"eql_aa_build_{build_id}"
    assert page.evaluate("(k) => localStorage.getItem(k)", slot_key) is not None, \
        "FAIL: test setup - the build didn't actually save"

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
    page.click(f'button[data-action="delete"][data-id="{build_id}"]')
    delete_toast = page.locator("#toast").inner_text()
    print("toast after a delete whose index write fails:", delete_toast)
    assert "couldn't save" in delete_toast.lower(), \
        f"FAIL: expected a failure toast when the delete's index write fails, got: {delete_toast!r}"

    index_after = json.loads(page.evaluate("(key) => localStorage.getItem(key)", BUILDS_INDEX_KEY))
    slot_after = page.evaluate("(k) => localStorage.getItem(k)", slot_key)
    print("index still lists the build:", any(b["id"] == build_id for b in index_after))
    print("slot data still present:", slot_after is not None)
    assert any(b["id"] == build_id for b in index_after), \
        "FAIL: the index write failed but the entry vanished from persisted storage anyway"
    assert slot_after is not None, \
        "FAIL: the slot's own data was deleted even though the index write (which was supposed to drop the reference) failed - dangling reference"
    print("PASS: a delete whose index write fails leaves the slot and index consistent, not a dangling reference")

    # --- Split whose new-profile write fails must not repoint the session
    # or the slot at a profile that was never written (the boot sweep would
    # then delete the old one). ---
    page2 = browser.new_page(viewport={"width": 1400, "height": 900})
    page2.on("pageerror", lambda exc: errors.append(str(exc)))
    page2.on("dialog", lambda d: d.accept())
    page2.goto(BASE)
    page2.wait_for_selector("#treeWrap .node")
    page2.locator("#treeWrap .node").first.click()
    page2.click("#incBtn")
    page2.click("#buildsBtn")
    page2.fill("#buildSaveName", "Split Me")
    page2.click("#buildSaveBtn")
    page2.click("#closeBuildsBtn")
    profile_before = page2.evaluate("JSON.parse(localStorage.getItem('eql_aa_builder_v1')).ownedProfileId")
    page2.evaluate("""() => {
        const real = Storage.prototype.setItem;
        const known = new Set(Object.keys(localStorage));
        Storage.prototype.setItem = function (k, v) {
            if (k.startsWith('eql_aa_owned_') && !known.has(k)) throw new DOMException('quota', 'QuotaExceededError');
            return real.call(this, k, v);
        };
    }""")
    page2.click('button[data-tab="progression"]')
    page2.click("#manageOwnedTrackingBtn")
    page2.click("#ownedTrackingSplitBtn")
    toast = page2.locator("#toast").inner_text()
    profile_after = page2.evaluate("JSON.parse(localStorage.getItem('eql_aa_builder_v1')).ownedProfileId")
    slot_profile = page2.evaluate("""() => {
        const id = JSON.parse(localStorage.getItem('eql_aa_builds_index_v1'))[0].id;
        return JSON.parse(localStorage.getItem('eql_aa_build_' + id)).ownedProfileId;
    }""")
    print(f"Split with a failing write: toast {toast!r}, session {profile_before} -> {profile_after}, slot {slot_profile}")
    assert profile_after == profile_before and slot_profile == profile_before, \
        "FAIL: a Split whose write failed repointed the session or slot at a profile that doesn't exist"
    assert "couldn't" in toast.lower(), f"FAIL: a failed Split should say so, got {toast!r}"
    print("PASS: a Split whose write fails leaves tracking where it was and says so")
    page2.close()

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
