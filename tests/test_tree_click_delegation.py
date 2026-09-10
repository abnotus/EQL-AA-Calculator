# -*- coding: utf-8 -*-
# renderTree no longer attaches a click/keydown listener to every AA node -
# events.js binds one delegated listener on the never-recreated #treeWrap
# instead, resolving the clicked node's category from state.activeTab at
# click time (the tree only ever renders state.activeTab's own list). Every
# existing test that clicks a tree node happens to do it on the General tab
# (the default active one), so a delegated handler that resolved the wrong
# category - e.g. hardcoding "general" - would still pass every one of them:
# General is state.activeTab there too, so the (wrong) hardcoded value and
# the (right) dynamic one agree by coincidence. This clicks a node on a
# non-general tab instead, where a wrong-category bug would show the wrong
# AA (or the wrong category label) in the side panel.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # --- Archetype tab: click its first node, and confirm both the AA name
    # AND the side panel's category label ("Archetype AA") match - a
    # wrong-category resolution would show a different AA's name entirely
    # (or, if idx happened to be in range, General's category label instead
    # of Archetype's). ---
    page.click('button[data-tab="archetype"]')
    page.wait_for_timeout(100)
    first_node_name = page.locator("#treeWrap .node .name").first.inner_text()
    page.locator("#treeWrap .node").first.click()
    page.wait_for_timeout(50)
    header_name = page.locator("#sidePanel .sidepanel-header h2").inner_text()
    meta_text = page.locator("#sidePanel .meta").inner_text()
    print(f"clicked Archetype node '{first_node_name}' -> side panel shows '{header_name}' ({meta_text})")
    assert header_name == first_node_name, f"FAIL: clicked '{first_node_name}' on the Archetype tab but the side panel shows '{header_name}'"
    assert meta_text.lower().startswith("archetype aa"), f"FAIL: expected the side panel's category label to read 'Archetype AA', got '{meta_text}'"
    print("PASS: clicking a node on the Archetype tab resolves to the Archetype category, not a hardcoded default")

    # --- A class tab too (classSlot0), same check against that class's own
    # name rather than "Archetype" or "General". ---
    class_name = page.locator("#classSelect0").input_value()
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(100)
    class_node_name = page.locator("#treeWrap .node .name").first.inner_text()
    page.locator("#treeWrap .node").first.click()
    page.wait_for_timeout(50)
    class_header_name = page.locator("#sidePanel .sidepanel-header h2").inner_text()
    class_meta_text = page.locator("#sidePanel .meta").inner_text()
    print(f"clicked {class_name} node '{class_node_name}' -> side panel shows '{class_header_name}' ({class_meta_text})")
    assert class_header_name == class_node_name, f"FAIL: clicked '{class_node_name}' on the {class_name} tab but the side panel shows '{class_header_name}'"
    assert class_meta_text.lower().startswith(f"{class_name.lower()} aa"), f"FAIL: expected the side panel's category label to read '{class_name} AA', got '{class_meta_text}'"
    print(f"PASS: clicking a node on the {class_name} class tab resolves to that class's category")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
