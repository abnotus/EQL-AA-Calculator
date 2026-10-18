# -*- coding: utf-8 -*-
# Core behavior of per-build owned-progress profiles (state.js/builds.js/
# exportImport.js): a newly saved build gets its own independent copy of
# owned progress rather than sharing the live session's, and the Manage
# Owned Tracking control's three actions - Link, Merge, Split - work as
# designed: Link repoints two builds at the same live data, Merge is a
# one-directional non-destructive union, and Split pulls a linked build
# back onto its own independent copy without disturbing the other side.
# A separate scenario covers importing a build that carries owned data:
# always silent (no confirm dialog), always its own fresh profile.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"


def buy_and_own(page, tab, label):
    page.click(f'button[data-tab="{tab}"]')
    node = page.locator(".node").first
    name = node.locator(".name").inner_text()
    node.click()
    page.click("#incBtn")
    page.click('button[data-tab="progression"]')
    row = page.locator(".progression-row", has=page.locator(".step-name", has_text=name))
    row.locator(".step-own").click()
    summary = page.locator("#ownedSummary").inner_text()
    print(f"{label} ({name}) owned, summary now:", summary)
    return name, summary


def owned_summary(page):
    return page.locator("#ownedSummary").inner_text()


def save_build_as(page, name):
    page.click("#buildsBtn")
    page.fill("#buildSaveName", name)
    page.click("#buildSaveBtn")
    page.click("#closeBuildsBtn")


def load_build(page, name):
    page.click("#buildsBtn")
    row = page.locator(".build-row", has=page.locator(".build-name", has_text=name))
    row.locator('[data-action="load"]').click()
    # A successful load closes the modal itself (render.js); only close it
    # here if something left it open (e.g. the load was declined/failed).
    if page.locator("#buildsModal").is_visible():
        page.click("#closeBuildsBtn")


def open_tracking_modal(page):
    page.click('button[data-tab="progression"]')
    page.click("#manageOwnedTrackingBtn")


def tracking_status(page):
    return page.locator("#ownedTrackingStatus").inner_text()


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)

    # =========================================================================
    # PART 1: independence at Save As, then Link / Merge / Split, all within
    # one browser context so the builds genuinely share localStorage.
    # =========================================================================
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    # Loading a build while the live session has diverged from every saved
    # slot (this test buys ranks incidentally while marking things owned,
    # so that happens often) triggers confirmReplaceCurrentBuild's "save
    # first?" confirm, then a prompt() for a name - a blank accept would
    # decline the safety-save and silently block the load. Auto-accepting
    # every prompt with a fresh unique name instead lets that safety-save
    # succeed so the load itself proceeds, same as a real user typing a name.
    autosave_counter = [0]
    def handle_dialog(d):
        if d.type == "prompt":
            autosave_counter[0] += 1
            d.accept(f"Autosave {autosave_counter[0]}")
        else:
            d.accept()
    page.on("dialog", handle_dialog)
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    name_x, owned_x_only = buy_and_own(page, "classSlot0", "AA_X")
    save_build_as(page, "Build A")

    # Save As moves the session onto the new slot's own profile, so a mark
    # made straight after saving belongs to the slot just saved, not to
    # whatever the session was tracking before.
    save_build_as(page, "Build B")
    name_y, owned_x_and_y = buy_and_own(page, "classSlot1", "AA_Y (into Build B)")
    assert owned_x_and_y != owned_x_only, "FAIL: marking a second AA owned should change the summary"
    owned_b_before_merge = owned_x_and_y

    load_build(page, "Build A")
    page.click('button[data-tab="progression"]')
    owned_after_load_a = owned_summary(page)
    print("owned summary after loading Build A back:", owned_after_load_a)
    assert owned_after_load_a == owned_x_only, \
        f"FAIL: Build A's own profile should still show only AA_X, expected {owned_x_only!r}, got {owned_after_load_a!r}"

    load_build(page, "Build B")
    owned_after_load_b = owned_summary(page)
    print("owned summary after loading Build B back:", owned_after_load_b)
    assert owned_after_load_b == owned_x_and_y, \
        f"FAIL: AA_Y was marked right after saving Build B, so B should show it, expected {owned_x_and_y!r}, got {owned_after_load_b!r}"
    print("PASS: each saved build has its own owned profile, and marks made after Save As land in the slot just saved")

    # --- Merge: B ends up {X, Y}, A stays {X}. Merging B into A must
    # produce the union {X, Y} without touching B. ---

    load_build(page, "Build A")
    open_tracking_modal(page)
    page.select_option("#ownedTrackingBuildSelect", label="Build B")
    page.click("#ownedTrackingMergeBtn")
    page.click("#closeOwnedTrackingBtn")
    owned_a_after_merge = owned_summary(page)
    print("Build A's owned summary after merging in Build B:", owned_a_after_merge)
    assert owned_a_after_merge == owned_x_and_y, \
        f"FAIL: merging B ({{X,Y}}) into A ({{X}}) should produce {{X,Y}}, expected {owned_x_and_y!r}, got {owned_a_after_merge!r}"

    load_build(page, "Build B")
    owned_b_after_merge = owned_summary(page)
    print("Build B's owned summary after being merged FROM (must be untouched):", owned_b_after_merge)
    assert owned_b_after_merge == owned_b_before_merge, "FAIL: merging FROM a build must never modify that build's own data"
    print("PASS: Merge produces a non-destructive union in the target, and never touches the source")

    # --- Link: A and B share the same live data from this point on. ---
    load_build(page, "Build A")
    open_tracking_modal(page)
    status_before_link = tracking_status(page)
    print("tracking status before Link:", status_before_link)
    page.select_option("#ownedTrackingBuildSelect", label="Build B")
    page.click("#ownedTrackingLinkBtn")
    status_after_link = tracking_status(page)
    print("tracking status after Link:", status_after_link)
    assert "Build B" in status_after_link, f"FAIL: status should mention sharing with Build B, got {status_after_link!r}"
    page.click("#closeOwnedTrackingBtn")

    name_z, owned_after_z = buy_and_own(page, "classSlot2", "AA_Z (while A is linked to B)")
    load_build(page, "Build B")
    owned_b_after_link = owned_summary(page)
    print("Build B's owned summary after A (linked) marked AA_Z:", owned_b_after_link)
    assert owned_b_after_link == owned_after_z, "FAIL: a Link should make the two builds show identical live owned data"
    print("PASS: Link makes two builds share the same live owned data")

    # --- Split: B pulls off onto its own independent copy again. Further
    # changes on A must no longer reach B. ---
    open_tracking_modal(page)
    page.click("#ownedTrackingSplitBtn")
    status_after_split = tracking_status(page)
    print("Build B's tracking status after Split:", status_after_split)
    assert "Build A" not in status_after_split and "sharing" not in status_after_split.lower(), \
        f"FAIL: expected an independent-tracking status after Split, got {status_after_split!r}"
    page.click("#closeOwnedTrackingBtn")
    owned_b_after_split = owned_summary(page)

    load_build(page, "Build A")
    buy_and_own(page, "general", "one more AA (on A, after B split off)")
    owned_a_after_more = owned_summary(page)
    assert owned_a_after_more != owned_b_after_split, "FAIL: A should have diverged further after B split off"

    load_build(page, "Build B")
    owned_b_final = owned_summary(page)
    print("Build B's owned summary after A kept changing post-split:", owned_b_final)
    assert owned_b_final == owned_b_after_split, "FAIL: Split should make B immune to further changes on A"
    print("PASS: Split gives a build back its own independent copy, unaffected by the build it used to share with")

    print("ERRORS:", errors)
    assert not errors

    # =========================================================================
    # PART 2: importing a build that carries owned data is always silent -
    # no confirm dialog, always its own fresh profile.
    # =========================================================================
    sender = browser.new_page(viewport={"width": 1400, "height": 900})
    sender.on("dialog", lambda d: d.accept())
    sender.goto(BASE)
    sender.wait_for_selector("#treeWrap .node")
    _, sender_owned = buy_and_own(sender, "general", "sender AA")

    sender.click("#exportBtn")
    sender.wait_for_function("document.querySelector('#shareLinkInput').value.includes('build=')")
    export_text = sender.locator("#exportText").input_value()
    sender.close()

    receiver = browser.new_page(viewport={"width": 1400, "height": 900})
    dialogs = []
    receiver.on("dialog", lambda d: (dialogs.append(d.message), d.accept()))
    receiver.goto(BASE)
    receiver.wait_for_selector("#treeWrap .node")

    receiver.click("#importBtn")
    receiver.fill("#importText", export_text)
    receiver.click("#doImportBtn")
    receiver.wait_for_selector("#importModal", state="hidden")

    print("dialogs during import-with-owned-data:", dialogs)
    assert dialogs == [], f"FAIL: importing owned data must never show a confirm dialog, got {dialogs}"

    toast = receiver.locator("#toast")
    toast_text = toast.inner_text() if toast.is_visible() else ""
    print("toast after import:", toast_text)
    assert "owned progress included" in toast_text and "separately" in toast_text, \
        f"FAIL: unexpected toast wording: {toast_text!r}"

    receiver.click('button[data-tab="progression"]')
    receiver_owned_after = owned_summary(receiver)
    print("receiver's owned summary after import:", receiver_owned_after)
    assert receiver_owned_after == sender_owned, \
        f"FAIL: expected the receiver to show exactly the imported owned data, expected {sender_owned!r}, got {receiver_owned_after!r}"
    print("PASS: importing owned data is silent (no dialog) and lands in its own fresh profile")

    receiver.close()
    browser.close()
    print("ALL PASS")
