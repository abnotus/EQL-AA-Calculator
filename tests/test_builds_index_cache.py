# -*- coding: utf-8 -*-
# builds.js caches the parsed builds index in memory (cachedIndex) to avoid
# a localStorage.getItem + JSON.parse on every listBuilds() call, which runs
# on every renderTopbar (i.e. every renderAll). saveIndex is the only write
# path, and must keep cachedIndex in lockstep with what's persisted.
#
# saveBuildAs and renameBuild both do loadIndex() -> mutate the returned
# array in place -> saveIndex(index): since loadIndex returns the cached
# array by reference once loaded, that mutation is already visible through
# the cache before saveIndex ever runs, so those two paths would keep
# "working" even if saveIndex forgot to update cachedIndex - the mutation is
# masked. deleteBuild is the one path that builds a genuinely NEW array
# (loadIndex().filter(...)), so it's the only one that actually depends on
# saveIndex reassigning cachedIndex - remove that line and the Builds modal
# keeps showing a just-deleted build until the next full page load, even
# though localStorage itself is already correct. Pins that specific path.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    dialogs = []
    page.on("dialog", lambda d: (dialogs.append(d.message), d.accept()))

    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # The modal doesn't close after a save (handleBuildSave just refreshes
    # its own list), so it's opened once - reclicking #buildsBtn while
    # already open would hit the modal-overlay backdrop sitting on top of it
    # instead of the button underneath.
    page.click("#buildsBtn")
    page.wait_for_timeout(50)

    def save_build(name):
        page.fill("#buildSaveName", name)
        page.click("#buildSaveBtn")
        page.wait_for_timeout(50)

    save_build("Build One")
    save_build("Build Two")
    page.wait_for_timeout(50)

    rows = page.locator("#buildsList .build-row")
    assert rows.count() == 2, f"FAIL: expected 2 saved builds listed, got {rows.count()}"
    print("PASS: both saved builds appear in the Builds modal")

    # Delete one without closing/reopening the modal or reloading the page -
    # renderBuildsList() runs immediately after deleteBuild() and must read
    # the same in-memory list deleteBuild() just wrote to.
    dialogs.clear()
    delete_btn = page.locator(".build-row", has=page.locator(".build-name", has_text="Build One")).locator('button[data-action="delete"]')
    delete_btn.click()
    page.wait_for_timeout(50)
    assert len(dialogs) == 1 and "can't be undone" in dialogs[0], f"FAIL: expected a delete confirmation, got {dialogs}"

    rows_after = page.locator("#buildsList .build-row")
    print("build rows still shown in the modal right after delete (no reload):", rows_after.count())
    assert rows_after.count() == 1, f"FAIL: the modal should immediately drop to 1 build, got {rows_after.count()}"
    assert page.locator(".build-row .build-name", has_text="Build Two").count() == 1, "FAIL: the wrong build was removed from the list"
    print("PASS: deleting a build updates the Builds modal immediately, without a reload")

    # localStorage must agree with what the modal now shows - the bug this
    # pins is exactly a DOM/storage split (a stale in-memory cache serving
    # renderBuildsList while localStorage itself is already correct).
    stored_count = page.evaluate("JSON.parse(localStorage.getItem('eql_aa_builds_index_v1') || '[]').length")
    print("builds index entries in localStorage after delete:", stored_count)
    assert stored_count == 1, f"FAIL: localStorage should also hold exactly 1 build, got {stored_count}"
    print("PASS: the in-memory list and localStorage agree after a delete")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
