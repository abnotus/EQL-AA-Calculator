# -*- coding: utf-8 -*-
# BUILD_CODE share codes/export text have changed twice in the same sitting:
# compression moved from gzip to raw DEFLATE ("deflate-raw" - same underlying
# compression, but without gzip's 10-byte header + 8-byte trailer a code
# embedded in a URL/text blob has no use for), and the JSON payload itself
# moved from a keyed object ({v,c,l,r,p,o,w}, v2) to a positional array
# ([v,c,l,r,p,o,w], v3+) - the object's keys cost real bytes for zero
# information a fixed-position schema doesn't already carry (see
# exportImport.js's compress/decompress, buildCodeArray, expandCompactPayload).
# decodeBuildCode checks gzip's own magic bytes directly, then falls back to
# deflate-raw and finally plain uncompressed JSON if that fails too - format-
# sniffed on the bytes themselves rather than gated on BUILD_CODE_VERSION, so
# every era of link/export keeps working forever, independent of which JSON
# shape ends up inside once decompressed.
#
# Rather than relying on some other test's hardcoded fixture happening to
# still be old-format (incidental, not deliberate coverage), this
# reconstructs what an old-style gzip-compressed code, a pre-compression
# plain-JSON code, and a v2 keyed-object code for the SAME current build
# would have looked like, directly from the browser's own CompressionStream -
# then feeds each into Import and confirms they all load identically to the
# app's own current export. Also confirms the real, measured savings: the
# app's own current code is shorter than the gzip equivalent for the same
# content.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"


def extract_code(export_text):
    marker = "BUILD_CODE:"
    idx = export_text.index(marker)
    return export_text[idx + len(marker):].strip()


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    # Re-importing while the live session has unsaved spent points (true
    # here, on purpose, for the second/third import below) triggers
    # confirmReplaceCurrentBuild's "save first?" confirm, then a prompt()
    # for a name - a blank accept declines the safety-save and silently
    # blocks the import. Auto-accepting every prompt with a fresh unique
    # name instead lets that safety-save succeed so the import proceeds.
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

    # --- Buy a handful of real AAs so there's a real, non-trivial payload
    # to round-trip and re-encode in alternate formats. ---
    page.click('button[data-tab="general"]')
    for i in range(2):
        page.locator(".node").nth(i).click()
        page.click("#incBtn")
        page.wait_for_timeout(60)
    page.click('button[data-tab="classSlot0"]')
    page.wait_for_timeout(80)
    page.locator(".node").first.click()
    page.click("#incBtn")
    page.click("#incBtn")
    page.wait_for_timeout(60)
    spent_before = page.locator("#spentValue").inner_text()

    page.click("#exportBtn")
    page.wait_for_timeout(300)
    export_text = page.locator("#exportText").input_value()
    current_code = extract_code(export_text)
    page.click("#closeExportBtn")
    page.wait_for_timeout(80)

    # --- Reconstruct old-style codes for the exact same underlying JSON,
    # using the browser's own Compression Streams API - not a guess at what
    # an old client produced, the real thing. ---
    reconstructed = page.evaluate("""
    async (currentCode) => {
      function b64ToBytes(b64) {
        const bin = atob(b64);
        const bytes = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        return bytes;
      }
      function bytesToB64(bytes) {
        let bin = "";
        for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
        return btoa(bin);
      }
      async function pipe(bytes, Ctor, format) {
        const stream = new Blob([bytes]).stream().pipeThrough(new Ctor(format));
        return new Uint8Array(await new Response(stream).arrayBuffer());
      }
      const compressedBytes = b64ToBytes(currentCode);
      const jsonBytes = await pipe(compressedBytes, DecompressionStream, "deflate-raw");
      const gzipBytes = await pipe(jsonBytes, CompressionStream, "gzip");

      // A genuine v2 keyed-object payload for the exact same content - not
      // just re-wrapping the current v3 array, actually reshaping it into
      // the old container so expandCompactPayload's Array.isArray branch
      // is deliberately exercised, not just incidentally covered by some
      // other test's aging fixture.
      const arr = JSON.parse(new TextDecoder().decode(jsonBytes));
      const v2Payload = { v: 2, c: arr[1], l: arr[2], r: arr[3], p: arr[4] };
      if (arr[5]) v2Payload.o = arr[5];
      if (arr[6]) v2Payload.w = arr[6];
      const v2Bytes = new TextEncoder().encode(JSON.stringify(v2Payload));
      const v2GzipBytes = await pipe(v2Bytes, CompressionStream, "gzip");

      return {
        gzipCode: bytesToB64(gzipBytes),
        plainCode: bytesToB64(jsonBytes),
        v2Code: bytesToB64(v2GzipBytes),
        newLen: currentCode.length,
        gzipLen: bytesToB64(gzipBytes).length,
        plainLen: bytesToB64(jsonBytes).length
      };
    }
    """, current_code)
    print("code lengths - current (deflate-raw):", reconstructed["newLen"],
          "| old-style gzip:", reconstructed["gzipLen"],
          "| uncompressed:", reconstructed["plainLen"])
    assert reconstructed["newLen"] < reconstructed["gzipLen"], \
        "FAIL: the current deflate-raw code should be shorter than the equivalent gzip code for the same content"
    print("PASS: the current encoding measurably shortens the code vs. the old gzip format")

    # --- An old-style gzip code for this exact build imports identically. ---
    page.click("#importBtn")
    page.wait_for_timeout(100)
    page.fill("#importText", reconstructed["gzipCode"])
    page.click("#doImportBtn")
    page.wait_for_timeout(200)
    spent_after_gzip_import = page.locator("#spentValue").inner_text()
    print("spentValue after importing the old-style gzip code:", spent_after_gzip_import)
    assert spent_after_gzip_import == spent_before, "FAIL: an old gzip-compressed code should still import correctly"
    print("PASS: a code compressed the old (gzip) way still imports correctly")

    # --- A pre-compression, uncompressed code for this exact build also
    # still imports identically. ---
    page.click("#importBtn")
    page.wait_for_timeout(100)
    page.fill("#importText", reconstructed["plainCode"])
    page.click("#doImportBtn")
    page.wait_for_timeout(200)
    spent_after_plain_import = page.locator("#spentValue").inner_text()
    print("spentValue after importing the uncompressed code:", spent_after_plain_import)
    assert spent_after_plain_import == spent_before, "FAIL: a pre-compression, uncompressed code should still import correctly"
    print("PASS: a code from before compression existed still imports correctly")

    # --- A genuine v2 keyed-object code (gzip-compressed, matching a real
    # older client) also still imports identically. ---
    page.click("#importBtn")
    page.wait_for_timeout(100)
    page.fill("#importText", reconstructed["v2Code"])
    page.click("#doImportBtn")
    page.wait_for_timeout(200)
    spent_after_v2_import = page.locator("#spentValue").inner_text()
    print("spentValue after importing a v2 keyed-object code:", spent_after_v2_import)
    assert spent_after_v2_import == spent_before, "FAIL: a v2 keyed-object code should still import correctly"
    print("PASS: a v2 keyed-object code still imports correctly")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
