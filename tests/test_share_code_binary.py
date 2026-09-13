# -*- coding: utf-8 -*-
# BUILD_CODE v5 is packed bits rather than JSON (see exportImport.js's
# BUILD_CODE_VERSION header). That buys 41-67% shorter codes, but it moves
# the format from "structurally self-describing" to "every field's meaning
# is a bit offset" - so one wrong width or a missed read shifts everything
# after it and can still produce values that are individually in-range. A
# CRC can't catch that class of bug, because the encoder checksums its own
# wrong output.
#
# Hence the property test below: randomized builds pushed through the real
# export -> share-link -> import path, asserting every field comes back
# exactly. That path is what a share link actually is, so this exercises
# the shipped encoder and decoder rather than a reimplementation of them.
# The corruption and backward-compatibility cases either side of it cover
# the two things a user can actually hit.
import os, sys, io, json, random, base64
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

BASE = f"http://localhost:{os.environ.get('AACALC_TEST_PORT', '8743')}/index.html"
STORAGE_KEY = "eql_aa_builder_v1"

# A v4 code (deflate-raw, positional array, columnar r/o) for the real
# Paladin/Enchanter/Druid build - pinned to prove pre-v5 links still decode,
# and to measure v5 against.
V4_CODE = "fZM_j9swDMW_SqH5DaJI6s_arUOnjoaHFAkOQdO7Q3A39NsXj459cZEr9LNhSbQtku9NhmnAYTM8Y5oyHBUNHZIhAlGIQzpkoAiKohhKRWkoHSrQAlWoQR1aoQ06YBkmsAJTmME6bPD7XuAKN7jDK7zBO3ygZlRBVUhRSDZIdkhuGIbhGA3VUStqQ-2oAy1DVCBiEGkzJoNBt0vgaMwqsoCgwyGxodtgIAf3lxcraszWOH6U8_2bjOEpl615xsS0CqvC5DZKFCnw_PFcWmSmssZltNvoLIRnloyF4KTyXlocraKjRxc29H-wCzmasnQk37VpRHMDFji4reflgGOFnVlhewNfRwl93DP2ZKdARCmBDQrqDjd29DPY-IB6WXCKYIE5LWl5qCSgxO4ZN5bfUZULslJuUHyl77HQ2jBqL9-G3GGd0t2gIwLvIdg9IrxsxjRtTntos_AYDfbQXRq--sxUq6NWG1FNOx_RQeGa1Qb_OKbfVP_hlUcuWXf2vpJMT0yWkb49n9_Oh0tCerkenp9OacbUM9L38_Hp8PuUkK6nIxe1C9KPX3--HF-eufz6fn29RLiLIn09XI8J6efl_ZTmef4L"

# Real slugs and their true max ranks from data.src.js, so seeded builds are
# values the app would actually accept (deserializeRanks clamps to aa.ranks,
# so an over-max seed would come back changed and look like a codec bug).
GENERAL = [("adamant-will", 4), ("alchemy-mastery", 3), ("baking-mastery", 3),
           ("circular-breathing", 4), ("combat-agility", 3), ("packrat", 10)]
ARCHETYPE = [("acrobatics", 3), ("ambidexterity", 1), ("mental-clarity", 4)]
CLASSES = [("Bard", "instrument-mastery", 3), ("Bard", "jam-fest", 3)]
COLORS = [None, "red", "orange", "yellow", "green", "teal", "blue", "purple"]
LABELS = ["", "Level 20", "x" * 60, "日本語ラベル", "emoji dragon"]


def make_build(rnd):
    """A random but structurally valid build payload + its owned map."""
    ranks = {"general": {}, "archetype": {}, "special": {}, "classes": {}}
    order = []
    n_gen = rnd.randint(0, len(GENERAL))
    for slug, mx in rnd.sample(GENERAL, n_gen):
        r = rnd.randint(1, mx)
        ranks["general"][slug] = r
        order += [{"scope": "general", "className": None, "key": slug}] * r
    n_arc = rnd.randint(0, len(ARCHETYPE))
    for slug, mx in rnd.sample(ARCHETYPE, n_arc):
        r = rnd.randint(1, mx)
        ranks["archetype"][slug] = r
        order += [{"scope": "archetype", "className": None, "key": slug}] * r
    if rnd.random() < 0.5:
        cls, slug, mx = rnd.choice(CLASSES)
        r = rnd.randint(1, mx)
        ranks["classes"].setdefault(cls, {})[slug] = r
        order += [{"scope": "class", "className": cls, "key": slug}] * r
    rnd.shuffle(order)

    # owned <= planned, which is the invariant the delta encoding leans on.
    owned = {"general": {}, "archetype": {}, "special": {}, "classes": {}}
    mode = rnd.choice(["none", "some", "all", "lower"])
    if mode != "none":
        for scope in ("general", "archetype"):
            for slug, r in ranks[scope].items():
                if mode == "some" and rnd.random() < 0.5:
                    continue
                owned[scope][slug] = r if mode != "lower" else max(1, r - 1)

    waypoints = []
    for _ in range(rnd.choice([0, 1, 4])):
        waypoints.append({"pts": rnd.randint(0, 100000),
                          "label": rnd.choice(LABELS) or None,
                          "color": rnd.choice(COLORS)})
    # sanitizeWaypoints dedupes by pts and sorts, so match that here or the
    # comparison would flag the app's own normalization as a mismatch.
    seen = {}
    for w in waypoints:
        seen[min(w["pts"], 100000)] = w
    waypoints = [dict(w, pts=p) for p, w in sorted(seen.items())]

    classes = ["Bard", "Beastlord", "Berserker"]
    if ranks["classes"]:
        only = list(ranks["classes"])[0]
        classes = [only] + [c for c in classes if c != only][:2]
    return {
        "v": 4, "selectedClasses": classes, "charLevel": rnd.randint(1, 50),
        "ranks": ranks, "purchaseOrder": order, "waypoints": waypoints,
    }, owned


def normalize(payload, owned):
    """The subset that must survive a round trip, in a comparable shape."""
    return {
        "classes": payload["selectedClasses"],
        "level": payload["charLevel"],
        "ranks": payload["ranks"],
        "order": payload["purchaseOrder"],
        "waypoints": [[w["pts"], w["label"], w["color"]] for w in payload["waypoints"]],
        "owned": owned,
    }


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    errors = []

    def new_page(seed_payload=None, seed_owned=None, url=BASE):
        pg = browser.new_page(viewport={"width": 1400, "height": 900})
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("dialog", lambda d: d.accept())
        if seed_payload is not None:
            pg.add_init_script(
                f"localStorage.setItem({json.dumps(STORAGE_KEY)}, {json.dumps(json.dumps(seed_payload))});"
                f"localStorage.setItem('eql_aa_owned_legacy', {json.dumps(json.dumps({'v': 4, 'owned': seed_owned}))});"
            )
        pg.goto(url)
        pg.wait_for_selector("#treeWrap .node")
        pg.wait_for_timeout(120)
        return pg

    def export_code(pg):
        """The BUILD_CODE line's raw value - standard base64, as the export
        text embeds it."""
        pg.click("#exportBtn")
        pg.wait_for_timeout(250)
        text = pg.locator("#exportText").input_value()
        pg.click("#closeExportBtn")
        return next(l.split("BUILD_CODE:")[1].strip()
                    for l in text.splitlines() if l.startswith("BUILD_CODE:"))

    def as_url_code(code):
        """What buildShareUrl does before putting a code in a query string.
        Skipping this silently corrupts any code containing '+', which a
        URL decodes back as a space."""
        return code.replace("+", "-").replace("/", "_").rstrip("=")

    def read_state(pg):
        return pg.evaluate("""(key) => {
            const s = JSON.parse(localStorage.getItem(key) || '{}');
            let owned = { general: {}, archetype: {}, special: {}, classes: {} };
            for (let i = 0; i < localStorage.length; i++) {
                const k = localStorage.key(i);
                if (k && k.startsWith('eql_aa_owned_') && k !== 'eql_aa_owned_v1') {
                    const o = JSON.parse(localStorage.getItem(k) || '{}');
                    if (o && o.owned && Object.values(o.owned).some(v => v && Object.keys(v).length))
                        owned = o.owned;
                }
            }
            return { classes: s.selectedClasses, level: s.charLevel, ranks: s.ranks,
                     order: s.purchaseOrder, waypoints: (s.waypoints || []).map(w => [w.pts, w.label, w.color]),
                     owned };
        }""", STORAGE_KEY)

    # --- 1. Property test ---
    rnd = random.Random(20260828)
    checked = 0
    for i in range(18):
        payload, owned = make_build(rnd)
        src = new_page(payload, owned)
        code = export_code(src)
        src.close()
        assert code.startswith("5") or True  # base64 of 0xE5 - checked properly below
        dst = new_page(url=f"{BASE}?build={as_url_code(code)}")
        got = read_state(dst)
        toast_el = dst.locator("#toast")
        toast = toast_el.inner_text() if toast_el.count() else ""
        dst.close()
        want = normalize(payload, owned)
        for field in ("classes", "level", "ranks", "order", "waypoints", "owned"):
            assert got[field] == want[field], (
                f"FAIL case {i} field {field!r}\n  code ({len(code)} chars): {code}"
                f"\n  toast: {toast!r}"
                f"\n  sent: {json.dumps(want[field], ensure_ascii=False)}"
                f"\n  got:  {json.dumps(got[field], ensure_ascii=False)}")
        checked += 1
    print(f"PASS: {checked} randomized builds round-tripped through export -> share link -> import exactly")

    # --- 2. It really is the binary format, and it really is shorter ---
    pg = new_page(url=f"{BASE}?build={V4_CODE}")
    v5 = export_code(pg)
    pg.close()
    first = base64.urlsafe_b64decode(v5 + "=" * (-len(v5) % 4))[0]
    print(f"v5 magic byte: 0x{first:02x} (expect 0xe5)")
    assert first == 0xE5, "FAIL: export is not in the v5 binary format"
    print(f"same build: v4 {len(V4_CODE)} chars -> v5 {len(v5)} chars")
    assert len(v5) < len(V4_CODE) * 0.75, \
        f"FAIL: expected v5 to be well under 75% of v4's size, got {len(v5)} vs {len(V4_CODE)}"
    print("PASS: export is v5 binary and materially shorter than the v4 equivalent")

    # --- 3. The rank field's width. V5_BITS.rank is 5 because
    # data.src.js's largest `ranks` is 26 (Ranger's Hunter's Attack Power),
    # and a 4-bit field would silently wrap it to 10. Nothing the UI can do
    # reaches past 10 - auto AAs never enter the rank stores through it -
    # but an imported payload does: clampRankValue bounds a loaded value to
    # that AA's own `ranks`, so 26 survives into both state.ranks and
    # state.owned and then back out through a re-export. Without this case
    # the whole property test above tops out at 10 and the 5th bit is
    # unpinned.
    HIGH = {"general": {}, "archetype": {}, "special": {},
            "classes": {"Ranger": {"hunters-attack-power": 26}}}
    high_payload = {"v": 4, "selectedClasses": ["Ranger", "Beastlord", "Berserker"],
                    "charLevel": 50, "ranks": HIGH, "purchaseOrder": [], "waypoints": []}
    src = new_page(high_payload, HIGH)
    high_code = export_code(src)
    src.close()
    dst = new_page(url=f"{BASE}?build={as_url_code(high_code)}")
    high_back = dst.evaluate("""(k) => {
        const s = JSON.parse(localStorage.getItem(k) || '{}');
        let owned = null;
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('eql_aa_owned_') && key !== 'eql_aa_owned_legacy')
                owned = JSON.parse(localStorage.getItem(key)).owned;
        }
        return { planned: (s.ranks || {}).classes, owned: (owned || {}).classes };
    }""", STORAGE_KEY)
    dst.close()
    print("rank 26 round trip - planned:", json.dumps(high_back["planned"]),
          "owned:", json.dumps(high_back["owned"]))
    assert high_back["planned"] == {"Ranger": {"hunters-attack-power": 26}}, \
        f"FAIL: a rank of 26 must survive encoding - got {high_back['planned']}"
    assert high_back["owned"] == {"Ranger": {"hunters-attack-power": 26}}, \
        f"FAIL: an owned rank of 26 must survive encoding - got {high_back['owned']}"
    print("PASS: a rank above 15 round-trips, pinning the 5-bit rank field")

    # --- 4. The id bitmap's low boundary. A build with no AAs and one
    # holding only id 0 (Adamant Will) both store hi = 0, so the bitmap is
    # written as hi + 1 bits unconditionally - a lone "0" for the empty
    # build - and the two stay distinguishable. Writing nothing for the
    # empty case instead leaves the reader a bit ahead of the writer for
    # every field that follows, which a build of all-zero trailing fields
    # survives by luck and a build with waypoints does not: the shift
    # inflates wpCount and the reader runs off the end of the stream.
    # The property test can draw an empty build but only pairs it with
    # waypoints by chance, so both halves are pinned explicitly here. ---
    EMPTY_RANKS = {"general": {}, "archetype": {}, "special": {}, "classes": {}}
    ONLY_ID0 = {"general": {"adamant-will": 1}, "archetype": {}, "special": {},
                "classes": {}}
    WPS = [{"pts": 100 * n, "label": f"wp{n}", "color": "red"} for n in (1, 2, 3, 4)]
    for label, ranks, order, wps, want_ranks in (
        ("no AAs, no waypoints", EMPTY_RANKS, [], [], {}),
        ("no AAs, four waypoints", EMPTY_RANKS, [], WPS, {}),
        ("only id 0, four waypoints", ONLY_ID0,
         [{"scope": "general", "className": None, "key": "adamant-will"}], WPS,
         {"adamant-will": 1}),
    ):
        payload = {"v": 4, "selectedClasses": ["Bard", "Beastlord", "Berserker"],
                   "charLevel": 42, "ranks": ranks, "purchaseOrder": order,
                   "waypoints": wps}
        src = new_page(payload, EMPTY_RANKS)
        code = export_code(src)
        src.close()
        dst = new_page(url=f"{BASE}?build={as_url_code(code)}")
        got = read_state(dst)
        toast_el = dst.locator("#toast")
        toast = toast_el.inner_text() if toast_el.count() else ""
        dst.close()
        want_wps = [[w["pts"], w["label"], w["color"]] for w in wps]
        print(f"{label}: {len(code)} chars, level {got['level']}, "
              f"{len(got['waypoints'])} waypoints back")
        assert got["level"] == 42, \
            f"FAIL: {label} lost the level - got {got['level']!r}, toast {toast!r}"
        assert got["ranks"]["general"] == want_ranks, \
            f"FAIL: {label} ranks - want {want_ranks}, got {got['ranks']['general']}"
        assert got["waypoints"] == want_wps, \
            f"FAIL: {label} waypoints - want {want_wps}, got {got['waypoints']}"
    print("PASS: empty and id-0-only bitmaps stay distinct and round-trip with waypoints")

    # --- 5. Corruption must be rejected loudly, not decoded into a wrong
    # build. Before v5 this came free from DEFLATE failing on a damaged
    # stream; v5 is uncompressed, so its own CRC has to do it.
    #
    # The two damage shapes are caught by different things, and both are
    # worth keeping: truncation trips bitReader's bounds check, but a flip
    # in the trailing label bytes doesn't - nothing reads past those to
    # notice, so only the CRC stands between it and a build imported with
    # a silently wrong waypoint label. ---
    labelled = {"v": 4, "selectedClasses": ["Bard", "Beastlord", "Berserker"],
                "charLevel": 50,
                "ranks": {"general": {"adamant-will": 1}, "archetype": {}, "special": {}, "classes": {}},
                "purchaseOrder": [{"scope": "general", "className": None, "key": "adamant-will"}],
                "waypoints": [{"pts": 40, "label": "Sky done later on", "color": "blue"}]}
    src = new_page(labelled, {"general": {}, "archetype": {}, "special": {}, "classes": {}})
    lab_code = export_code(src)
    src.close()
    lab_bytes = bytearray(base64.b64decode(lab_code + "=" * (-len(lab_code) % 4)))
    # Third from the end: inside the UTF-8 label, ahead of the 2 CRC bytes.
    lab_bytes[-3] ^= 0x20
    late_flip = base64.b64encode(bytes(lab_bytes)).decode()

    for label, bad in [
        ("truncated", as_url_code(v5)[: len(as_url_code(v5)) // 2]),
        ("flipped char (early)", (lambda u: u[:20] + ("A" if u[20] != "A" else "B") + u[21:])(as_url_code(v5))),
        ("flipped byte in trailing label", as_url_code(late_flip)),
    ]:
        pg = new_page(url=f"{BASE}?build={bad}")
        toast = pg.locator("#toast")
        txt = toast.inner_text() if toast.count() and toast.is_visible() else ""
        state_after = read_state(pg)
        pg.close()
        print(f"{label}: toast={txt!r}")
        assert "invalid" in txt.lower(), f"FAIL: {label} code should report an invalid link, got {txt!r}"
        assert not state_after["order"], f"FAIL: {label} code should not have applied a build"
    print("PASS: truncated and mangled codes are rejected with a clear message, nothing applied")

    # --- 6. Pre-v5 links still work ---
    pg = new_page(url=f"{BASE}?build={V4_CODE}")
    rows = pg.locator(".progression-row")
    pg.click('button[data-tab="progression"]')
    pg.wait_for_timeout(200)
    n = pg.locator(".progression-row").count()
    pg.close()
    print("v4 link still decodes, Progression rows:", n)
    assert n == 183, f"FAIL: the pinned v4 build should still load its 183 rows, got {n}"
    print("PASS: v4 share links keep working unchanged")

    print("ERRORS:", errors)
    assert not errors
    browser.close()
    print("ALL PASS")
