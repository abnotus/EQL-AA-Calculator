# -*- coding: utf-8 -*-
# decodeBuildCode/decompress (exportImport.js) used to have no size limit
# anywhere before fully materializing a share/import code's decoded/
# decompressed bytes: a huge base64 string went straight into atob(), and a
# compressed payload's output went straight into
# new Response(stream).arrayBuffer() with no cap on how large that output
# could be. A small, deliberately crafted compressed input (a
# "decompression bomb" - highly repetitive data compresses to almost
# nothing but expands back to its full size) could have hung or crashed
# the tab before any existing validation ran, since MAX_PURCHASE_ORDER
# (state.js) only bounds one field's array length AFTER a successful
# JSON.parse, not the decompression step itself.
#
# Fixed with two independent limits: MAX_ENCODED_CODE_LENGTH rejects an
# oversized encoded string before it even reaches atob, and
# MAX_DECOMPRESSED_BYTES is enforced while streaming DecompressionStream's
# output chunk-by-chunk, aborting the stream the moment the running total
# crosses it rather than ever fully materializing an oversized buffer.
#
# Both scenarios below build a payload that's otherwise completely valid -
# a real, importable (if minimal) build with one big benign padding field
# applyLoaded simply ignores - specifically so the test discriminates the
# fix from ordinary "that wasn't valid JSON anyway" rejection: without
# either limit this actually imports successfully (proving oversized input
# really would be processed, not just coincidentally fail some unrelated
# check), and with them it's rejected before ever finishing.
#
# Driven through the paste-import box (not a ?build= URL) - a code this
# size doesn't fit real-world URL/server line-length limits anyway, and
# pasting a hostile code from a chat/forum post is the more realistic
# vector for either of these regardless.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

VALID_MINIMAL_BUILD = """{
    "v": 1,
    "selectedClasses": ["Bard", "Beastlord", "Berserker"],
    "charLevel": 50,
    "ranks": {"general": {}, "archetype": {}, "special": {}, "classes": {}},
    "purchaseOrder": [],
    "waypoints": []
}"""

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda d: d.accept())
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    def to_base64url(page, text):
        return page.evaluate(
            """(json) => {
                const bytes = new TextEncoder().encode(json);
                let binary = '';
                for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
                return btoa(binary).replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, '');
            }""",
            text
        )

    # --- Sanity check: the minimal payload alone (base64url-encoded, like
    # a real legacy uncompressed code - extractBuildCode only recognizes a
    # bare code by that shape, not raw JSON text) really does import
    # successfully, so the rejections below are proven to be about size,
    # not about the payload shape being bogus to begin with. ---
    page.click("#importBtn")
    page.evaluate("(t) => { document.getElementById('importText').value = t; }", to_base64url(page, VALID_MINIMAL_BUILD))
    page.click("#doImportBtn")
    page.wait_for_timeout(200)
    baseline_toast = page.locator("#toast").inner_text()
    print("toast for the unpadded minimal build:", baseline_toast)
    assert "imported" in baseline_toast.lower(), \
        f"FAIL: the minimal payload should import cleanly on its own - got {baseline_toast!r}"

    # --- An otherwise-valid build, padded (via an ignored extra field)
    # well past MAX_ENCODED_CODE_LENGTH, sent uncompressed - rejected
    # before base64ToBytes/atob ever runs on it. ---
    padded_uncompressed = VALID_MINIMAL_BUILD[:-1] + f', "padding": "{"A" * 250000}"}}'
    encoded_uncompressed = to_base64url(page, padded_uncompressed)
    print("oversized-but-otherwise-valid code length:", len(encoded_uncompressed))
    page.click("#importBtn")  # the baseline import above succeeded, which closes the modal
    page.evaluate("(c) => { document.getElementById('importText').value = c; }", encoded_uncompressed)
    start1 = page.evaluate("() => performance.now()")
    page.click("#doImportBtn")
    page.wait_for_timeout(300)
    elapsed1_ms = page.evaluate("() => performance.now()") - start1
    print(f"settled {elapsed1_ms:.0f}ms after importing the oversized-but-valid code")
    toast1 = page.locator("#toast").inner_text()
    print("toast:", toast1)
    assert "failed to read" in toast1.lower(), \
        f"FAIL: an otherwise-valid build padded past the length cap must still be rejected - got {toast1!r}"
    print("PASS: an oversized encoded code is rejected before it's ever decoded, even though the payload underneath is valid")

    # --- The same otherwise-valid build, this time padded to just over
    # MAX_DECOMPRESSED_BYTES (4MB) and gzip-compressed - the padding's
    # repetition compresses the ENCODED size down small (well under the
    # length cap above), so only the decompressed-output cap can catch
    # this one. Without it, this payload would decompress fully and
    # import successfully (same as the sanity check above, just larger). ---
    padded_for_compression = VALID_MINIMAL_BUILD[:-1] + f', "padding": "{"A" * (5 * 1024 * 1024)}"}}'
    bomb_code = page.evaluate(
        """async (json) => {
            const bytes = new TextEncoder().encode(json);
            const stream = new Blob([bytes]).stream().pipeThrough(new CompressionStream('gzip'));
            const compressed = new Uint8Array(await new Response(stream).arrayBuffer());
            let binary = '';
            for (let i = 0; i < compressed.length; i++) binary += String.fromCharCode(compressed[i]);
            return btoa(binary).replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, '');
        }""",
        padded_for_compression
    )
    print("bomb payload encoded length (tiny relative to the 5MB it decompresses to):", len(bomb_code))
    assert len(bomb_code) < 50000, \
        f"FAIL: the compressed bomb should be tiny (highly repetitive padding) - got {len(bomb_code)} chars, test setup may be wrong"
    assert len(bomb_code) < len(encoded_uncompressed), \
        "FAIL: the compressed bomb must be smaller than the uncompressed scenario's code, or it isn't isolating the decompressed-bytes cap"

    # No re-click of #importBtn here - the previous scenario's import
    # failed, which leaves the modal open rather than closing it.
    page.evaluate("(c) => { document.getElementById('importText').value = c; }", bomb_code)
    start2 = page.evaluate("() => performance.now()")
    page.click("#doImportBtn")
    page.wait_for_timeout(300)
    elapsed2_ms = page.evaluate("() => performance.now()") - start2
    print(f"settled {elapsed2_ms:.0f}ms after importing the bomb code (must not hang)")
    toast2 = page.locator("#toast").inner_text()
    print("toast:", toast2)
    assert "failed to read" in toast2.lower(), \
        f"FAIL: a decompression bomb (otherwise-valid payload padded past the decompressed-size cap) must be rejected - got {toast2!r}"
    print("PASS: a decompression bomb is rejected before it ever fully decompresses, even though the payload underneath is valid")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
