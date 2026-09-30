# EQL AA Calculator

A talent-calculator-style planner for [EverQuest Legends](https://eqlwiki.com/Alternate_Advancement) Alternate Advancement (AA) builds. Unofficial fan-made tool, not affiliated with the game.

**Live:** https://aacalc.abnotus.com

## Features

- Pick up to 3 classes (EQL's tri-class combo system) and spend points across General, Archetype, Class, and Special AAs
- Swap classes freely — picks for a class you're not currently using stay right where they were in **Progression** (just muted and read-only) and still count toward your total Points Planned, with a dedicated **Other Classes** tab for a filtered look at just those. Switch back and everything's exactly as you left it
- Prerequisite, level, class-based rank-cap, and class-eligibility checks before you can spend a point (some Archetype AAs are only trainable by certain classes), with no artificial point cap of its own. A rank that a later class swap puts out of reach is never stripped — it stays flagged until a qualifying class comes back
- Locked AAs show *why* — a missing prerequisite, a class-eligibility restriction, and a plain level gate all look different from each other, in both the tree and Browse All AAs
- Next-rank preview — see what the next rank upgrades to before you buy it
- Global search, with match-count badges on every tab
- **Browse All AAs** — a searchable reference independent of your current build, with an Unowned Only filter and owned/unowned styling on every card once you're tracking owned progress
- **Build Summary** — everything you've picked, grouped by category, including picks for a class you've swapped away from (also on their own Other Classes tab)
- **Progression** tab — the order you picked things in, drag-and-drop or arrow-key reorderable, with per-step and running-total cost. A "Move To" button quick-jumps a step to the top/bottom of the list or of any waypoint, or to a specific position — handy once a build gets long
- **Waypoints** — mark a point total worth returning to (e.g. "Level 20"), and it shows up as a colored divider right where your training order crosses it. Anchored to the point total, not a list position, so reordering and Reset Build never break one
- Mark AAs as **owned** to track what you've actually trained in-game, separate from what's just planned — the topbar shows a running owned/planned total at a glance, and the Progression tab breaks it down further into "points owned / to go". Each Build tracks its own owned progress by default; **Manage tracking…** on the Progression tab lets you Link two builds to share the same live progress, Merge in progress from another build without disturbing it, or Split one back off onto its own copy
- **Builds** — save named snapshots of your build and switch between them, for comparing class combos or planning alternate paths
- Export a build as text or a shareable link; import by pasting text, a link, or loading a saved file
- Undocumented costs and effect values can show a pattern-inferred estimate instead of a bare `?`, color-coded by confidence. Purely a display hint — never counted in real point totals, and automatically replaced the moment the wiki confirms the real value
- Auto-granted AAs are applied automatically, no points needed
- Responsive layout, keyboard-accessible
- Saved builds stay correct even when the underlying AA data changes — you'll see a notice if a pick disappeared or a prerequisite stopped being met
- **Hide** AAs you don't care about to declutter the tree and Browse All AAs, with a toggle to bring them back. An AA you've already picked always stays visible regardless

Player-facing version history is in the app itself — click the version tag in the bottom-right corner. For everything else, `git log` is the changelog.

Each version in that history has a matching annotated git tag (`vX.Y.Z`), so a reported issue can be pinned to a specific version.

## Data source

All AA data (costs, effects, ranks, prerequisites) lives in `data.src.js`, sourced from [eqlwiki.com/Alternate_Advancement](https://eqlwiki.com/Alternate_Advancement) and cross-checked against in-game logs/screenshots where the wiki is silent or wrong. Values marked `?` are undocumented anywhere and treated as 0 until confirmed.

Most descriptions state one effect that scales, written as a slash progression (`"by 2/4/6%"`) so the value for the rank you hold can be picked out. An AA whose ranks each do something *different* is written as consecutive `"Rank N: ..."` clauses instead, and renders one line per rank with your current one marked (`splitPerRankLines` in `logic.js`). A progression can't express that shape: its slots are positional, so one covering only ranks 2-4 would line up against ranks 1-3, and a rank doing something unrelated has no slot at all. Splitting only starts at the very beginning of a description, which is what keeps a passing mention like `"Rank 2 requires level 30"` inline.

### Checking for wiki changes

```
python wiki-sync/scrape_wiki.py
```

Fetches the AA page's current wikitext from eqlwiki's MediaWiki API and compares it against `wiki-sync/snapshot.json` (the state as of the last run). Prints what's new, gone, or changed, then overwrites the snapshot.

It's a diagnostic, not an auto-updater — it never touches `data.src.js`. Run it, review what changed, cross-check those entries against `data.src.js` by hand, apply any confirmed fixes, then rebuild. Run manually whenever we want to check in on the wiki; never on a schedule.

### Checking costs against a game log

```
python wiki-sync/verify_from_log.py path/to/eqlog_CharName_Zone.txt
```

A second, independent check on the costs `data.src.js` marks as confirmed. It reads the "gained the ability ... at a cost of N ability points" and "improved ... at a cost of N" lines from a player's own EverQuest Legends log and compares each against the data. Like the scrape, it's a diagnostic: it never reads the wiki and never touches `data.src.js`. Matches are recorded in `wiki-sync/log_verified.json`; a mismatch, a name the data doesn't have, or a rank the current data lacks is reported for you to look at. A log only covers what that character trained while logging, so it confirms a subset. `wiki-sync/total_verified.json` lists the owned ranks the log doesn't cover, taken from a build export whose total matched the in-game total; those are verified by that total match alone, one tier below a log match.

### Estimating undocumented costs

```
python wiki-sync/guess_costs.py
```

Regenerates `src/costGuesses.js`: estimates for per-rank costs the wiki hasn't documented (`?` in `data.src.js`). It cross-references other fully known AAs with the same rank count and matching known costs rather than trusting one AA's own progression (`2/4/6/?` looks like doubling, but a sibling known at `2/4/6/9` proves otherwise). Confidence scales with how many siblings agree (tiers in the script's docstring); a gap between two of the AA's own known costs can still get a lower-confidence interpolated guess.

The file is rewritten from scratch each run, so a confirmed guess simply disappears. Run it after any `data.src.js` change. A small hand-maintained `MANUAL_GUESSES` dict covers slots nothing else can reach, tagged with its own `"very-low"` tier; a real cross-AA match always wins over it.

### Estimating undocumented effect values

```
python wiki-sync/guess_effects.py
```

The same for numeric values inside effect descriptions, such as the `?` in `"Increases your critical hit chance by 1/?/5/10%."`. Regenerates `src/effectGuesses.js`, keyed one level deeper than costs because one description can hold several progressions (Adamant Will has two). Siblings are compared only within hand-declared groups (`EFFECT_SIBLING_GROUPS`): cost curves recur across AAs because the game reuses templates, but a recurring effect magnitude is coincidence. Interpolation and the manual fallback work as for costs.

### Keeping share-link ids in sync

```
python wiki-sync/assign_aa_ids.py
```

Maintains `src/aaIds.js`, the append-only numeric id table the share/export format addresses AAs by (`keys.js`'s `idForKey`/`entryForId`). Existing AAs keep their id and new ones get the next unused integer. An id is never reused, even for a removed AA, so an old link resolves to "gone" rather than to a different AA.

Run it after any `data.src.js` change that adds, removes or **renames** an AA. Identity comes from the slugified name, so a rename looks like a removal plus an addition, and existing links would silently drop that AA's picks. The script warns whenever an id vanishes in the same run new ones are assigned; if it was a rename (check the wiki's history), hand-edit `aaIds.js` to give the new key the *old* id.

## Running locally

No build tools, no server — just open `index.html` in a browser.

## Development

The app logic is authored as real ES modules under `src/` (`aaIds.js`, `costGuesses.js`, `effectGuesses.js`, `keys.js`, `changelogData.js`, `state.js`, `logic.js`, `builds.js`, `dom.js`, `render.js`, `exportImport.js`, `events.js`, `main.js`). Native ES modules don't work over `file://` in Chrome, and this app is deliberately built to run by just double-clicking `index.html` with no local server — so `build_minify.py` assembles the `src/` modules back into a single classic script and minifies it (via [esbuild](https://esbuild.github.io/), a build-time-only dependency — see Prerequisites below), which is what `index.html` actually loads.

`build_minify.py` also runs two data-integrity checks before building and fails with an explanation if either is violated, rather than shipping something broken: `check_prereq_disambiguation_invariant` (a repeated AA name needs exactly one non-auto occurrence for prereq resolution to stay deterministic) and `check_aa_ids_current` (every AA in `data.src.js` needs a matching entry in `src/aaIds.js`, or it silently drops out of every share link/export that includes it — run `wiki-sync/assign_aa_ids.py` to fix). If a build fails on either, the error message says what to do.

**Prerequisites:** `npm install` once, to pull in [esbuild](https://esbuild.github.io/) (the only dependency, and build-time only — the shipped app itself still has none, no server, works from `file://`).

To make a change:

1. Edit files under `src/` (app logic), `data.src.js` (AA data), or `styles.src.css`.
2. Run `python build_minify.py`. This regenerates `app.src.js` (assembled, readable — generated, don't edit directly), `app.js`/`data.js`/`styles.css` (minified, what ships), and re-stamps `index.html` with a cache-busting version hash.
3. Open `index.html` to test.

### Saved builds are keyed by AA name, not array position

At runtime, `state.ranks` and `purchaseOrder` address AAs by index into `AA_DATA` — simple, and every render/logic function already works that way. But that index is *not* what gets persisted to localStorage, exported text, or share links: `src/keys.js` derives a stable key from each AA's name instead, so a save survives `data.src.js` being reordered or regenerated by a wiki scrape. Without this, reordering an AA would silently shift every index-based save onto the wrong ability.

`keys.js` also carries a frozen snapshot of `AA_DATA`'s ordering as of 2026-07-09 (`LEGACY_AA_ORDER`), used only to migrate saves made before this existed. Never update it — it's a historical record of what old saves meant, not current data.

### Share codes are packed bits, format-sniffed on decode

A share link/export's `BUILD_CODE` is a compact, numeric-id-keyed payload, base64-encoded. As of `BUILD_CODE_VERSION` 5 it's packed bits rather than JSON (`src/exportImport.js`'s `packV5`/`expandBinaryPayload`): every field is sized to its own real enforced ceiling — a rank needs 5 bits, an AA id 9, a purchase-order entry only 6 (it indexes into *this build's* own AA list, not the global id space) — and the AA set rides as a bitmap when that beats listing ids outright, which the encoder decides per build by packing both and keeping the smaller. Owned progress is stored as one bit per planned AA meaning "owned at the planned rank", plus an explicit delta only where the two disagree, which on a real build is 1 entry in 43. Measured 41-67% smaller than the JSON format across build sizes (~45% on a 180-pick build: 604 characters down to 332), with nothing dropped or approximated.

v5 is deliberately **not** compressed: packed bits are near-maximum entropy, so DEFLATE made them bigger. It carries a CRC-16 instead of DEFLATE's incidental integrity check, so a mangled or truncated link reports "looks invalid" rather than decoding into a plausible but wrong build.

`decodeBuildCode` recognizes every format the app has emitted, sniffed from the bytes: v5's magic byte first (binary can be valid deflate-raw input that inflates into garbage), then gzip's 2-byte magic, then a deflate-raw attempt, then uncompressed JSON. On the JSON side `expandCompactPayload` accepts the v3+ positional array or the v2 keyed object, and `expandCompactRanks` the columnar `r`/`o` shape (v4+) or the older pair array, so every era of link keeps working. A decoded value that isn't a recognizable build is rejected. `compress`/`decompress` pipe through a `Blob`'s stream so a rejection surfaces in the awaited call a `try`/`catch` guards.

### purchaseOrder has a hard length ceiling

Rank values are clamped per entry on load (`clampRankValue`), and numeric fields from untrusted input go through `safeParseInt`, which accepts only numbers and strings. `purchaseOrder` needs its own ceiling: `reconcilePurchaseOrderCounts` (`logic.js`) costs far worse than linear time in its length, so a share link inflated to tens of thousands of entries (cheap to make, since it compresses well) would freeze the tab of whoever opens it. `MAX_PURCHASE_ORDER` (2000, in `state.js`'s `deserializePurchaseOrder`) truncates it first; a fully maxed roster is a few hundred entries. `MAX_WAYPOINTS` bounds waypoints the same way.

### Named builds don't replace the always-autosaving current build

`state.js`'s `STORAGE_KEY` is whatever build you're currently looking at — autosaved on every change, loaded unconditionally on boot. `src/builds.js` adds named snapshots on top as a separate concern: saving copies the current state into its own key, loading overwrites the current state with a saved copy. Which slot a loaded/saved build is "active" is tracked only for UI display, and cleared on Reset/Import/a share link so a later save can't mistake unrelated content for an update to a slot it no longer matches.

### Owned progress is tracked per build, through swappable "profiles"

`state.owned` (the Progression tab's "actually trained in-game" watermark) persists to a `localStorage` key scoped to an owned *profile* id (`ownedStorageKeyFor`, `state.js`), not a single fixed key. `state.ownedProfileId` says which profile the current session is showing; each saved Build slot carries its own `ownedProfileId` field pointing at one too. Two builds pointing at the same profile id read/write the same storage entry — that's what "linked" tracking means concretely, and it's how the old single-global-owned behavior is still available, just opt-in now instead of the only option.

A brand-new saved build gets its own fresh profile, seeded with a copy of whatever's showing at save time — independent from that point on. The Progression tab's **Manage tracking…** control (`render.js`'s owned-tracking modal, backed by `linkOwnedToBuild`/`mergeOwnedFromBuild`/`splitOwnedFromCurrent` in `builds.js`) can Link two builds onto the same profile, Merge another build's marks in as a one-directional non-destructive union, or Split a linked build back onto its own copy, at any time — not just when it's first saved. Owned data rides every export/share link unconditionally now (no opt-in checkbox — since owned is scoped to one specific build, it's no different in kind from the plan itself); importing one always creates its own fresh profile silently, with just a toast — nothing existing is ever at risk of being overwritten, so there's nothing to confirm.

Every existing user's builds are backfilled to a well-known shared `LEGACY_OWNED_PROFILE_ID` profile the first time they're seen post-upgrade (`migrateLegacyOwnedProfile`/`migrateStaleBuildSlots`) — a self-healing sweep that re-checks on every boot rather than a one-time flag, so a build that reaches a given browser later (a restored backup, a synced device) still gets caught. The original `eql_aa_owned_v1` key is left in place, never deleted.

Minting a profile has no matching cleanup on its own — deleting a build only removes its index entry and slot key, not whatever profile it pointed at, since another build might still be linked to it. `builds.js`'s `cleanupOrphanedOwnedProfiles()`, called once per boot, sweeps any profile with no build slot's `ownedProfileId` and no live session pointing at it (via `state.js`'s `listOwnedProfileIds`/`removeOwnedProfile`), leaving the legacy profile untouched regardless.

### A cost or effect estimate can never outrank a real one

`src/costGuesses.js` is only ever consulted through `keys.js`'s `costGuessFor`, and only when the real `costs[rankIdx]` is exactly `"?"` — `logic.js`'s `costNum()`/`spentPoints()` never look at it, so an estimate can't affect real point totals. The moment a real number replaces `"?"` in `data.src.js`, that slot's guess (if one still exists) is simply never read again.

`src/effectGuesses.js` has the same guarantee: `logic.js`'s `highlightRankValue` only substitutes a guess where the description text is literally `"?"` — search, export text, and everywhere else a description is read still see the real, unmodified string.

## Testing

`tests/` has data-independent Python unit tests for `wiki-sync/guess_costs.py`'s, `wiki-sync/guess_effects.py`'s, `wiki-sync/assign_aa_ids.py`'s, and `wiki-sync/common.py`'s core logic, plus 33 Playwright browser tests that drive the actual app — cost/effect estimates, class-based rank caps, Archetype class-eligibility gating, hiding AAs, Progression's drag/auto-scroll/reorder, cross-class prereq dependencies, per-build owned-tracking profiles (Link/Merge/Split, migration, orphaned-profile cleanup), share-code encoding backward-compatibility, and the Other Classes tab, among others. See `tests/README.md` for the full list, prerequisites, and how to run them (`python tests/run_all.py` runs everything in one pass). There's no CI: every push to `main` deploys the site, so the tests are run by hand before pushing.

## Deployment

Hosted on GitHub Pages, served from `main` on every push.

## License

[PolyForm Noncommercial 1.0.0](LICENSE) — free to use, share, and modify for any noncommercial purpose.
