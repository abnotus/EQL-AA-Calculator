# -*- coding: utf-8 -*-
# purchaseOrder had no length limit of its own on the untrusted-input path
# (a pasted build code, a share link) - state.ranks is validated/clamped
# per entry, but purchaseOrder itself wasn't. reconcilePurchaseOrderCounts
# (logic.js), which trims it down to match the real rank counts on every
# import, costs far worse than linear time in purchaseOrder's own length:
# a purchaseOrder inflated to a million entries for one real, held AA
# turns opening a share link into a multi-second tab freeze for whoever
# opens it - and it compresses extremely well (a million repeats of one
# id is a ~2.6KB code), so it costs the sender very little to build.
#
# MAX_PURCHASE_ORDER (state.js's deserializePurchaseOrder) truncates the
# raw array to a generous-but-bounded ceiling before any of that
# reconciliation work runs. This drives the malicious payload through the
# Import textarea - a real compact BUILD_CODE, compressed the same way an
# actual share link would be - rather than seeding localStorage directly.
# That distinction matters: on a localStorage-seeded boot, JSON.parse of
# the raw stored array dominates and happens before the cap ever runs, so
# a test on that path can't tell a capped build from an uncapped one (it
# doesn't, measured: ~4.7s either way at a size that's actually slow to
# parse) - and it isn't the real threat model either, since localStorage
# can only hold a hostile array if something already wrote it there. The
# import path is where the fix actually does its job: decoding a compact
# numeric-id array is cheap even at a million entries, so the cap landing
# before reconcilePurchaseOrderCounts is the entire difference between
# fast and multi-second. Measured directly against this exact test
# (temporarily reverting the cap, same machine): 5.50s uncapped vs 0.10s
# capped for the same 1,000,000-entry payload - the assertion below sits
# with wide margin on both sides of that gap, not tuned to a borderline
# fixture size.
import os, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
MALICIOUS_ENTRY_COUNT = 1000000


def extract_code(export_text):
    marker = "BUILD_CODE:"
    idx = export_text.index(marker)
    return export_text[idx + len(marker):].strip()


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    # Importing over an unsaved, non-empty build triggers
    # confirmReplaceCurrentBuild's "save first?" confirm, then a prompt()
    # for a name - a blank accept declines the safety-save and silently
    # blocks the import (it never reaches the code being measured at all).
    # Auto-accepting every prompt with a fresh unique name instead lets
    # that safety-save succeed so the import proceeds.
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

    # --- Buy one real AA so there's a genuine numeric id and a real held
    # rank to build the malicious payload around. ---
    page.click('button[data-tab="general"]')
    node = page.locator(".node").first
    node.click()
    page.click("#incBtn")
    page.wait_for_timeout(60)

    page.click("#exportBtn")
    page.wait_for_timeout(300)
    base_code = extract_code(page.locator("#exportText").input_value())
    page.click("#closeExportBtn")
    page.wait_for_timeout(80)

    # --- Build a malicious compact code for the SAME AA: a real held rank
    # of 1, but a purchaseOrder inflated to a million entries - using the
    # browser's own Compression Streams API, the real encoding, not a
    # hand-rolled approximation. ---
    malicious = page.evaluate("""
    async ({ baseCode, count }) => {
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
      const bytes = b64ToBytes(baseCode);
      const jsonBytes = await pipe(bytes, DecompressionStream, "deflate-raw");
      const arr = JSON.parse(new TextDecoder().decode(jsonBytes));
      const id = arr[3][0][0]; // the bought AA's id (columnar r: [[ids],[ranks]])
      const payload = [arr[0], arr[1], arr[2], [[id], [1]], new Array(count).fill(id), null, null];
      const payloadBytes = new TextEncoder().encode(JSON.stringify(payload));
      const compressed = await pipe(payloadBytes, CompressionStream, "deflate-raw");
      return { code: bytesToB64(compressed), codeLen: bytesToB64(compressed).length };
    }
    """, {"baseCode": base_code, "count": MALICIOUS_ENTRY_COUNT})
    print(f"malicious code for {MALICIOUS_ENTRY_COUNT} purchaseOrder entries: {malicious['codeLen']} chars")

    # --- Import it through the real UI path - the actual attack surface,
    # not a localStorage shortcut. ---
    page.click("#importBtn")
    page.wait_for_timeout(100)
    page.fill("#importText", malicious["code"])
    start = time.time()
    page.click("#doImportBtn")
    page.wait_for_selector("#importModal", state="hidden", timeout=20000)
    elapsed = time.time() - start
    print(f"import of a {MALICIOUS_ENTRY_COUNT}-entry purchaseOrder took {elapsed:.2f}s")
    # Wide margin on both sides of the measured 0.10s (capped) / 5.50s
    # (uncapped) gap - not a threshold picked independently of a baseline.
    assert elapsed < 2.0, f"FAIL: import took {elapsed:.2f}s - the purchaseOrder cap should keep this well under a second"
    print("PASS: import of a massively inflated purchaseOrder stayed fast")

    stored = page.evaluate("localStorage.getItem('eql_aa_builder_v1')")
    import json as _json
    parsed_stored = _json.loads(stored)
    print("purchaseOrder length after import-time reconciliation:", len(parsed_stored["purchaseOrder"]))
    assert len(parsed_stored["purchaseOrder"]) == 1, \
        f"FAIL: expected purchaseOrder reconciled down to 1 entry (the real held rank), got {len(parsed_stored['purchaseOrder'])}"
    print("PASS: purchaseOrder was capped and correctly reconciled to the real held rank")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
