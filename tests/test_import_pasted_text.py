# -*- coding: utf-8 -*-
# Text import accepts what mail and chat do to a code or link: a code line
# wrapped at 76 columns, a reply quoting it with "> ", a link ending a
# sentence, a link inside <...> (wrapped or not) or a Markdown link, a
# percent-encoded link, and a code or link followed directly by a one-word
# line or a sentence. The readable export also lists the picks of classes not currently
# selected.
import os, sys, io, json, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
EMPTY = {"general": {}, "archetype": {}, "special": {}, "classes": {}}
GEN = {"scope": "general", "className": None}
# Enough picks for a code longer than one 76-column line, plus a Cleric pick
# while Cleric isn't selected.
SLUGS = ["adamant-will", "alchemy-mastery", "baking-mastery", "blacksmithing-mastery", "brewing-mastery",
         "circular-breathing", "combat-agility", "combat-fury", "combat-stability", "fear-resistance",
         "first-aid", "fletching-mastery", "foraging", "innate-lung-capacity", "innate-metabolism"]
PAYLOAD = {"v": 4, "selectedClasses": ["Bard", "Beastlord", "Berserker"], "charLevel": 50,
           "ranks": {**EMPTY, "general": {s: 1 for s in SLUGS}, "classes": {"Cleric": {"turn-undead": 1}}},
           "purchaseOrder": [{**GEN, "key": s} for s in SLUGS] + [{"scope": "class", "className": "Cleric", "key": "turn-undead"}],
           "waypoints": [{"pts": 20, "label": "a waypoint label to lengthen the code", "color": "red"}]}

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    errors = []
    src = browser.new_page()
    src.on("pageerror", lambda exc: errors.append(str(exc)))
    src.add_init_script(f"localStorage.setItem('eql_aa_builder_v1', {json.dumps(json.dumps(PAYLOAD))});")
    src.goto(BASE)
    src.wait_for_selector("#treeWrap .node")
    src.click("#exportBtn")
    src.wait_for_function("document.querySelector('#shareLinkInput').value.includes('build=')")
    export_text = src.locator("#exportText").input_value()
    url = src.locator("#shareLinkInput").input_value()
    src.close()
    code = next(l.split("BUILD_CODE:")[1] for l in export_text.splitlines() if l.startswith("BUILD_CODE:"))
    print(f"code: {len(code)} chars")
    assert len(code) > 80, "FAIL: setup needs a code longer than one wrapped line"
    assert "== Cleric AA (not one of your current 3 classes) ==" in export_text and "Turn Undead: rank 1/" in export_text, \
        "FAIL: the readable export should list picks for classes not currently selected"
    print("PASS: the readable export lists other classes' picks")

    line = "BUILD_CODE:" + code
    wrapped = "\n".join(line[i:i + 76] for i in range(0, len(line), 76))
    std_code = code + "=" * (-len(code) % 4)
    bracketed = f"see <{url}>"
    wrapped_link = "\n".join(bracketed[i:i + 76] for i in range(0, len(bracketed), 76))
    assert len(wrapped_link.splitlines()[-1]) > 1, "FAIL: setup needs code on the wrapped link's last line"
    variants = {
        "wrapped at 76 columns": wrapped + "\nThanks",
        "code line then a one-word line": line + "\nthanks",
        "link then a name": url + "\nBob",
        "wrapped link in angle brackets": wrapped_link,
        "quoted reply": "\n".join("> " + l for l in (wrapped + "\nThanks").splitlines()),
        "link ending a sentence": f"Try my build: {url}.",
        "link in angle brackets": f"see <{url}>",
        "markdown link": f"[my build]({url}) for the raid",
        "percent-encoded link": BASE + "?build=" + urllib.parse.quote(std_code, safe=""),
        "bare code with a full stop": code + ".",
        "bare code then a one-word line": code + "\nthanks",
        "bare code then a sentence": code + "\nThanks for the raid!",
    }
    for label, text in variants.items():
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("dialog", lambda d: d.accept())
        page.goto(BASE)
        page.wait_for_selector("#treeWrap .node")
        page.click("#importBtn")
        page.fill("#importText", text)
        page.click("#doImportBtn")
        page.wait_for_selector("#toast.show")
        toast = page.locator("#toast").inner_text()
        print(f"{label}: {toast[:40]!r}")
        assert toast.startswith("Build imported"), f"FAIL: {label} was rejected: {toast!r}"
        page.close()
    print("PASS: wrapped, quoted, punctuated and percent-encoded pastes all import")

    assert not errors, errors
    browser.close()
    print("ALL PASS")
