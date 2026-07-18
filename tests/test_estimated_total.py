# -*- coding: utf-8 -*-
# The topbar's "Points Spent" headline number now blends real + estimated
# costs (colored blue, ~199 instead of 167) when the build includes at
# least one purchased-but-unconfirmed rank with a guess, with a small blue
# note spelling out how much of that came from estimates. Critically,
# "remaining" stays keyed to the REAL spent total always - that's the
# number that governs actual affordability everywhere else in the app, and
# must never imply a guess changes it, even though the headline spent
# number next to it now does include guesses. This is a real shared build
# with several purchased-but-unconfirmed ranks (Combat Stability, First
# Aid, Innate Eminence, Improved Mend), independently verified by hand:
# real total 167, guesses add 32, so the headline should read "~199".
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8743/index.html"
BUILD = "H4sIAAAAAAAACm2QwWrEMAxE_2XOc7DslZz4D3roFxgfQhuWQLotS2gPpf9eZAe2h-InxrY0c9A3PlEi8YJSZ2ZqI3YUDcSBIiEE4o5SqzE11sxLY536XWSIuqlG6a1oFJfMqbEm6S-NvaeJ5qLjc0xaGCkhd52VqTXiA8Vtg2jU9MCCk4Qx_4-HqfrQ6YlUY5QH-TwTJ1ovo8jJrCee00v_0ogv38glEE-37diWHcSxLjt8N4F43l6vy9sK4v2-3K4rWvv5BaiyIJppAQAA"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())

    # --- Fresh page, nothing purchased: plain real number, red, no note. ---
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")
    sv0 = page.locator("#spentValue")
    print("fresh spentValue text/class:", sv0.inner_text(), sv0.get_attribute("class"))
    assert sv0.inner_text() == "0"
    assert sv0.get_attribute("class") is None
    color0 = sv0.evaluate("el => getComputedStyle(el).color")
    assert color0 == "rgb(217, 76, 76)", f"FAIL: expected real 'spent' red, got {color0}"
    note0 = page.locator("#estimatedNote")
    assert "hidden" in note0.get_attribute("class")
    print("PASS: no guesses purchased -> plain real number, red, no note")

    # --- Load a build with several purchased-but-unconfirmed ranks. ---
    page.goto(f"{BASE}?build={BUILD}")
    page.wait_for_selector("#treeWrap .node")
    page.wait_for_timeout(200)

    sv = page.locator("#spentValue")
    print("spentValue text:", sv.inner_text())
    assert sv.inner_text() == "~199"
    assert "is-estimate" in sv.get_attribute("class")
    color = sv.evaluate("el => getComputedStyle(el).color")
    print("spentValue computed color:", color)
    assert color == "rgb(90, 169, 230)", f"FAIL: blended headline should render blue, got {color}"

    remaining = page.locator("#remainingValue").inner_text()
    print("remainingValue (must stay keyed to the REAL 167, not the blended 199):", remaining)
    assert remaining == "(833 remaining)", "FAIL: remaining must never be computed from the blended estimate total"

    note = page.locator("#estimatedNote")
    assert "hidden" not in note.get_attribute("class")
    note_text = note.inner_text()
    print("estimatedNote text:", note_text)
    assert note_text.strip() == "+32 from estimates"
    note_color = note.evaluate("el => getComputedStyle(el).color")
    print("estimatedNote computed color:", note_color)
    assert note_color == "rgb(90, 169, 230)"
    title = sv.get_attribute("title")
    print("spentValue title:", title)
    assert "167 confirmed + 32" in title
    print("PASS: headline blends to ~199 in blue, remaining stays real (833), note explains the +32 delta")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
