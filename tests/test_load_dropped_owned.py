# -*- coding: utf-8 -*-
# Loading a saved build, or linking to one, reports owned picks that no
# longer exist in the data, the same way dropped planned picks already
# were. Both used to discard loadAndApplyOwned's dropped count, so such a
# pick disappeared without a notice.
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
EMPTY = {"general": {}, "archetype": {}, "special": {}, "classes": {}}
SLOT = {"v": 4, "selectedClasses": ["Bard", "Beastlord", "Berserker"], "charLevel": 50,
        "ranks": EMPTY, "purchaseOrder": [], "waypoints": [], "ownedProfileId": "gone"}
GONE_PROFILE = {"v": 4, "owned": {**EMPTY, "general": {"an-aa-that-no-longer-exists": 2, "combat-agility": 1}}}
SETUP = (
    f"localStorage.setItem('eql_aa_builds_index_v1', {json.dumps(json.dumps([{'id': 'old', 'name': 'Old Build', 'updatedAt': 1}]))});"
    f"localStorage.setItem('eql_aa_build_old', {json.dumps(json.dumps(SLOT))});"
    f"localStorage.setItem('eql_aa_owned_gone', {json.dumps(json.dumps(GONE_PROFILE))});"
)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    errors = []

    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.add_init_script(SETUP)
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.click("#buildsBtn")
    page.locator(".build-row", has=page.locator(".build-name", has_text="Old Build")).locator('[data-action="load"]').click()
    page.wait_for_selector("#toast.show")
    toast = page.locator("#toast").inner_text()
    print("toast after Load:", toast)
    assert "1 pick no longer exists" in toast, f"FAIL: Load should report the owned pick that no longer exists: {toast!r}"
    page.close()

    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.add_init_script(SETUP)
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    page.click('button[data-tab="progression"]')
    page.click("#manageOwnedTrackingBtn")
    page.select_option("#ownedTrackingBuildSelect", label="Old Build")
    page.click("#ownedTrackingLinkBtn")
    page.wait_for_selector("#toast.show")
    toast = page.locator("#toast").inner_text()
    print("toast after Link:", toast)
    assert "1 pick no longer exists" in toast, f"FAIL: Link should report the owned pick that no longer exists: {toast!r}"
    page.close()

    print("PASS: Load and Link report owned picks that no longer exist")
    assert not errors, errors
    browser.close()
    print("ALL PASS")
