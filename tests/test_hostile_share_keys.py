# -*- coding: utf-8 -*-
# Class and scope names in a share link are untrusted. "constructor" or
# "__proto__" used to resolve to Object built-ins in keys.js's lookups and
# throw inside applyLoaded, and nothing caught it at startup: the page
# never rendered, and since the ?build= param was never stripped, every
# reload repeated it. A null entry in the builds index (corrupt storage)
# broke boot the same way.
import os, sys, io, json, base64
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"


def link_code(payload):
    raw = base64.b64encode(json.dumps(payload).encode()).decode()
    return raw.replace("+", "-").replace("/", "_").rstrip("=")


PAYLOADS = [
    ("legacy constructor class", {"ranks": {"classes": {"constructor": {"0": 1}}}}),
    ("v4 __proto__ class", {"v": 4, "ranks": {"general": {}, "classes": {"__proto__": {"x": 1}}}}),
    ("v4 scope 'classes' in purchaseOrder", {"v": 4, "ranks": {}, "purchaseOrder": [{"scope": "classes", "key": "x"}]}),
    ("v2 compact with a prototype id", {"v": 2, "c": [0, 1, 2], "l": 50, "r": [["constructor", 1]], "p": ["__proto__"]}),
]

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    for label, payload in PAYLOADS:
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("dialog", lambda d: d.accept())
        page.goto(f"{BASE}?build={link_code(payload)}")
        page.wait_for_selector("#treeWrap .node", timeout=5000)
        assert "build=" not in page.url, f"FAIL: {label} - the ?build= param should be stripped, url {page.url}"
        assert not errors, f"FAIL: {label} - page errors: {errors}"
        print(f"PASS: {label} - page renders and the link param is stripped")
        page.close()

    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.add_init_script("localStorage.setItem('eql_aa_builds_index_v1', JSON.stringify([null, 5, {name: 'no id'}]));")
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node", timeout=5000)
    page.click("#buildsBtn")
    rows = page.locator(".build-row").count()
    assert rows == 0, f"FAIL: invalid index entries should be skipped, got {rows} rows"
    assert not errors, f"FAIL: corrupt builds index - page errors: {errors}"
    print("PASS: a corrupt builds index doesn't break boot")
    page.close()
    browser.close()
    print("ALL PASS")
