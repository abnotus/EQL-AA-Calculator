# -*- coding: utf-8 -*-
# BUILD_CODE share codes/export text have changed several times: compression
# moved from gzip to raw DEFLATE ("deflate-raw" - same underlying
# compression, but without gzip's 10-byte header + 8-byte trailer a code
# embedded in a URL/text blob has no use for); the JSON payload moved from a
# keyed object ({v,c,l,r,p,o,w}, v2) to a positional array ([v,c,l,r,p,o,w],
# v3+); r/o's own inner shape moved from an array of [id,rank] pairs to
# columnar ([[ids...],[ranks...]], v4+); and v5 dropped JSON entirely for
# packed bits (see exportImport.js's packV5/expandBinaryPayload).
# decodeBuildCode checks v5's magic byte first, then gzip's, then falls back
# to deflate-raw and finally plain uncompressed JSON - format-sniffed on the
# bytes themselves rather than gated on BUILD_CODE_VERSION, so every era of
# link/export keeps working forever.
#
# Rather than relying on some other test's hardcoded fixture happening to
# still be old-format (incidental, not deliberate coverage), this builds one
# fixed v4 payload and re-encodes it four historical ways - gzip container,
# uncompressed plain JSON, a v2 keyed object, and a v3 positional-but-pair-
# shaped array - directly from the browser's own CompressionStream, then
# feeds each into Import and confirms they all load to the same build.
#
# It deliberately does NOT derive those from the app's own current export:
# that's v5 binary now, so there's no JSON to reshape. Comparing the four
# historical encodings against each other (and against a v4 baseline) is
# also the sharper invariant - it can't drift just because the current
# format changed again.
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"

# A fixed, real v4 payload: Adamant Will (id 0) rank 1, Alchemy Mastery
# (id 1) rank 1, and Bard's Instrument Mastery (id 65) rank 2, bought in
# that order. Ids are from src/aaIds.js; all three ranks are within each
# AA's own max, so nothing gets clamped on load and a mismatch below means
# a real decoding difference rather than normalization.
V4_PAYLOAD = [4, [0, 1, 2], 50, [[0, 1, 65], [1, 1, 2]], [0, 1, 65, 65], None, None]


def extract_code(export_text):
    marker = "BUILD_CODE:"
    idx = export_text.index(marker)
    return export_text[idx + len(marker):].strip()


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    autosave_counter = [0]

    def handle_dialog(d):
        # A blank prompt reads as "declined" to confirmReplaceCurrentBuild,
        # which would silently skip the import - so give the safety-save a
        # real name each time.
        if d.type == "prompt":
            autosave_counter[0] += 1
            d.accept(f"Autosave {autosave_counter[0]}")
        else:
            d.accept()
    page.on("dialog", handle_dialog)
    page.goto(BASE)
    page.wait_for_selector("#treeWrap .node")

    # --- Encode the same payload every way this app has ever emitted. ---
    codes = page.evaluate("""
    async (payload) => {
      function bytesToB64(bytes) {
        let bin = "";
        for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
        return btoa(bin);
      }
      async function pipe(bytes, Ctor, format) {
        const stream = new Blob([bytes]).stream().pipeThrough(new Ctor(format));
        return new Uint8Array(await new Response(stream).arrayBuffer());
      }
      const enc = (o) => new TextEncoder().encode(JSON.stringify(o));

      // v4: positional array, columnar r/o - the format immediately before v5.
      const v4Bytes = enc(payload);

      // The same content with r/o back in the older [[id,rank],...] shape.
      const toPairs = (col) => col ? col[0].map((id, i) => [id, col[1][i]]) : col;
      const rPairs = toPairs(payload[3]);
      const oPairs = toPairs(payload[5]);

      // v2: a genuine keyed object, exercising expandCompactPayload's
      // non-Array branch AND expandCompactRanks' non-columnar branch.
      const v2 = { v: 2, c: payload[1], l: payload[2], r: rPairs, p: payload[4] };
      if (oPairs) v2.o = oPairs;
      if (payload[6]) v2.w = payload[6];

      // v3: positional array container, but still pair-shaped r/o.
      const v3 = [3, payload[1], payload[2], rPairs, payload[4], oPairs, payload[6]];

      return {
        v4Deflate: bytesToB64(await pipe(v4Bytes, CompressionStream, "deflate-raw")),
        gzip:      bytesToB64(await pipe(v4Bytes, CompressionStream, "gzip")),
        plain:     bytesToB64(v4Bytes),
        v2Gzip:    bytesToB64(await pipe(enc(v2), CompressionStream, "gzip")),
        v3Gzip:    bytesToB64(await pipe(enc(v3), CompressionStream, "gzip")),
      };
    }
    """, V4_PAYLOAD)
    for k, v in codes.items():
        print(f"  {k}: {len(v)} chars")

    def import_and_read(code, label):
        page.click("#importBtn")
        page.wait_for_timeout(100)
        page.fill("#importText", code)
        page.click("#doImportBtn")
        page.wait_for_selector("#importModal", state="hidden", timeout=10000)
        page.wait_for_timeout(150)
        spent = page.locator("#spentValue").inner_text()
        print(f"  imported {label}: spentValue={spent}")
        return spent

    baseline = import_and_read(codes["v4Deflate"], "v4 (deflate-raw)")
    assert baseline != "0 / 0", "FAIL: the v4 baseline payload didn't import anything"

    for key, label in [("gzip", "gzip container"), ("plain", "uncompressed JSON"),
                       ("v2Gzip", "v2 keyed object"), ("v3Gzip", "v3 pair-shaped")]:
        got = import_and_read(codes[key], label)
        assert got == baseline, \
            f"FAIL: {label} should load identically to the v4 baseline - got {got}, expected {baseline}"
    print("PASS: every historical code format still imports to the same build")

    # --- The app's own current export is v5 binary, and shorter. Exported
    # from the state the imports above left behind, so it's the same build. ---
    page.click("#exportBtn")
    page.wait_for_timeout(300)
    current_code = extract_code(page.locator("#exportText").input_value())
    page.click("#closeExportBtn")
    page.wait_for_timeout(80)
    import base64
    first = base64.b64decode(current_code + "=" * (-len(current_code) % 4))[0]
    print(f"current export: {len(current_code)} chars, first byte 0x{first:02x}")
    assert first == 0xE5, "FAIL: the current export should be the v5 binary format"
    assert len(current_code) < len(codes["v4Deflate"]), (
        f"FAIL: v5 should be shorter than v4 for the same build - "
        f"got {len(current_code)} vs {len(codes['v4Deflate'])}")
    print("PASS: the current v5 encoding is shorter than the v4 equivalent for the same content")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
