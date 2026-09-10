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
- **Browse All AAs** — a searchable reference independent of your current build
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

Each entry added to `USER_CHANGELOG` (`src/changelogData.js`) gets a matching annotated git tag (`vX.Y.Z`, e.g. `git tag -a v1.1.0 -m "..."`) on the commit that bumped it, then `git push origin vX.Y.Z`. Lets a reported issue be pinned to a specific version.

## Data source

All AA data (costs, effects, ranks, prerequisites) lives in `data.src.js`, sourced from [eqlwiki.com/Alternate_Advancement](https://eqlwiki.com/Alternate_Advancement) and cross-checked against in-game logs/screenshots where the wiki is silent or wrong. Values marked `?` are undocumented anywhere and treated as 0 until confirmed.

Most descriptions state one effect that scales, written as a slash progression (`"by 2/4/6%"`) so the value for the rank you hold can be picked out. An AA whose ranks each do something *different* is written as consecutive `"Rank N: ..."` clauses instead, and renders one line per rank with your current one marked (`splitPerRankLines` in `logic.js`). A progression can't express that shape: its slots are positional, so one covering only ranks 2-4 would line up against ranks 1-3, and a rank doing something unrelated has no slot at all. Splitting only starts at the very beginning of a description, which is what keeps a passing mention like `"Rank 2 requires level 30"` inline.

### Checking for wiki changes

```
python wiki-sync/scrape_wiki.py
```

Fetches the AA page's current wikitext from eqlwiki's MediaWiki API and compares it against `wiki-sync/snapshot.json` (the state as of the last run). Prints what's new, gone, or changed, then overwrites the snapshot.

It's a diagnostic, not an auto-updater — it never touches `data.src.js`. Run it, review what changed, cross-check those entries against `data.src.js` by hand, apply any confirmed fixes, then rebuild. Run manually whenever we want to check in on the wiki; never on a schedule.

### Estimating undocumented costs

```
python wiki-sync/guess_costs.py
```

Regenerates `src/costGuesses.js` — pattern-inferred estimates for per-rank costs the wiki hasn't documented yet (`?` in `data.src.js`). Cross-references *other* fully-known AAs with the same rank count and matching known costs, rather than trusting one AA's own progression alone — a `2/4/6/?` pattern might look like a clean doubling sequence (implying 12), but a same-shaped sibling fully known at `2/4/6/9` proves the doubling read wrong. Confidence scales with how many independent siblings agree (see the script's own docstring for the tiers); a gap bounded by two of the AA's own known costs can still get a lower-confidence interpolated guess, since the true value is provably between them either way.

Rewrites `costGuesses.js` from scratch every run, so a guess that's since been confirmed (or lost its supporting evidence) just stops appearing — nothing to clean up by hand. Run it after any `data.src.js` change that could move the picture.

For the handful of slots nothing else can reach, the script also has a small hand-maintained `MANUAL_GUESSES` dict — curator judgment calls, used only as a last resort and tagged with their own `"very-low"` tier so they never read as the same kind of evidence as the algorithmic ones. A real cross-AA match always wins over a manual entry automatically, the moment one exists.

### Estimating undocumented effect values

```
python wiki-sync/guess_effects.py
```

Same idea, applied to the numeric values inside AA effect descriptions instead of per-rank costs — the `?` in something like `"Increases your critical hit chance by 1/?/5/10%."`. Regenerates `src/effectGuesses.js`, keyed one level deeper than costs since a single description can hold more than one independent progression (Adamant Will's resist-charm and resist-mesmerization percentages are two separate ones in the same sentence).

The one real difference: sibling matching only compares AAs within an explicitly hand-declared group (`EFFECT_SIBLING_GROUPS` in the script) — a human confirming two AAs share the same formula, not a text-similarity guess. A cost curve recurring across AAs is a real pattern (the game reuses cost templates); an effect *magnitude* recurring is just coincidence. Interpolation and the manual fallback otherwise work the same as the cost version.

### Keeping share-link ids in sync

```
python wiki-sync/assign_aa_ids.py
```

Maintains `src/aaIds.js`, the append-only numeric id table the compact share/export wire format addresses AAs by (see `keys.js`'s `idForKey`/`entryForId`). Every AA currently in `data.src.js` keeps its existing id if it already has one; anything new gets the next unused integer appended at the end. An id is never reassigned or reused, even for an AA since removed — its old entry stays in the table, so an old share link for it resolves to "gone" rather than a different AA someday inheriting the same number.

Run this after any `data.src.js` change that adds, removes, or **renames** an AA. A rename is the one case worth real care: the script computes identity from the AA's (slugified) name, so a rename looks exactly like "the old AA was removed and a new one was added" — the old id is orphaned, and every share link already encoding it silently drops that AA's picks from then on (reported as "N picks no longer exist," indistinguishable from a genuine deletion). The script can't tell a rename apart from a coincidental removal-and-unrelated-addition on its own, so it doesn't try — it prints a warning whenever an id vanishes in the same run new ones are assigned, prompting a manual check against the wiki's edit history. If it really was a rename, hand-edit `aaIds.js` to point the new key at the *old* id instead of leaving the freshly-appended one in place, so existing links keep resolving.

## Running locally

No build tools, no server — just open `index.html` in a browser.

## Development

The app logic is authored as real ES modules under `src/` (`aaIds.js`, `costGuesses.js`, `effectGuesses.js`, `keys.js`, `changelogData.js`, `state.js`, `logic.js`, `builds.js`, `dom.js`, `render.js`, `exportImport.js`, `events.js`, `main.js`). Native ES modules don't work over `file://` in Chrome, and this app is deliberately built to run by just double-clicking `index.html` with no local server — so `build_minify.py` assembles the `src/` modules back into a single classic script and minifies it (via [esbuild](https://esbuild.github.io/), a build-time-only dependency — see Prerequisites below), which is what `index.html` actually loads.

`build_minify.py` also runs two data-integrity checks before building and fails with an explanation if either is violated, rather than shipping something broken: `check_prereq_disambiguation_invariant` (a repeated AA name needs exactly one non-auto occurrence for prereq resolution to stay deterministic) and `check_aa_ids_current` (every AA in `data.src.js` needs a matching entry in `src/aaIds.js`, or it silently drops out of every share link/export that includes it — run `wiki-sync/assign_aa_ids.py` to fix). If a build fails on either, the error message says what to do.

### Saved builds are keyed by AA name, not array position

At runtime, `state.ranks` and `purchaseOrder` address AAs by index into `AA_DATA` — simple, and every render/logic function already works that way. But that index is *not* what gets persisted to localStorage, exported text, or share links: `src/keys.js` derives a stable key from each AA's name instead, so a save survives `data.src.js` being reordered or regenerated by a wiki scrape. Without this, reordering an AA would silently shift every index-based save onto the wrong ability.

`keys.js` also carries a frozen snapshot of `AA_DATA`'s ordering as of 2026-07-09 (`LEGACY_AA_ORDER`), used only to migrate saves made before this existed. Never update it — it's a historical record of what old saves meant, not current data.

### Share codes are packed bits, format-sniffed on decode

A share link/export's `BUILD_CODE` is a compact, numeric-id-keyed payload, base64-encoded. As of `BUILD_CODE_VERSION` 5 it's packed bits rather than JSON (`src/exportImport.js`'s `packV5`/`expandBinaryPayload`): every field is sized to its own real enforced ceiling — a rank needs 5 bits, an AA id 9, a purchase-order entry only 6 (it indexes into *this build's* own AA list, not the global id space) — and the AA set rides as a bitmap when that beats listing ids outright, which the encoder decides per build by packing both and keeping the smaller. Owned progress is stored as one bit per planned AA meaning "owned at the planned rank", plus an explicit delta only where the two disagree, which on a real build is 1 entry in 43. Measured 41-67% smaller than the JSON format across build sizes (~43% on a 191-pick build: 604 characters down to 344), with nothing dropped or approximated.

That size came from profiling rather than guessing, and the profile redirected the work: the purchase order was 37% of the payload, waypoints 19%, and owned only 11% — already so well compressed by DEFLATE (owned ranks nearly always equal their planned rank) that restructuring it was worth just 8%. Run-length-encoding the purchase order made codes *bigger*. Packing everything was the only lever that paid.

v5 is deliberately **not** compressed: packed bits are near-maximum entropy, so DEFLATE added bytes rather than removing them. That gave up the integrity check DEFLATE had been providing incidentally — a truncated stream simply fails to inflate — so v5 carries a CRC-16 instead. A mangled or truncated link reports "looks invalid" rather than decoding into a plausible-but-wrong build, which matters more for a bit-packed format than a JSON one: there are no brackets left to fail to parse.

`decodeBuildCode` recognizes every format this app has ever emitted, sniffed from the bytes themselves rather than from any assumption about the sender's app version. v5's magic byte is checked first, before any decompression is attempted — binary can otherwise be valid deflate-raw input that inflates into garbage, and the JSON parse further down is unconditional. Then gzip's own fixed 2-byte magic number (the only other self-identifying format here), then a try-then-fall-back for deflate-raw, then no compression at all for a code predating compression entirely. On the JSON side, `expandCompactPayload` accepts the v3+ positional array or the older v2 keyed object, and `expandCompactRanks` accepts either the columnar `r`/`o` shape (v4+) or the older pair-array one. Every era of link keeps working. `compress`/`decompress` pipe through a `Blob`'s stream rather than manually driving a writer, since a manually-written stream's rejection can otherwise surface as an unhandled error independently of the awaited call a `try`/`catch` actually guards.

### purchaseOrder has a hard length ceiling

`state.ranks` (a build's real, small rank counts) is validated/clamped per entry on load (`clampRankValue`), but `purchaseOrder` itself — a flat, attacker-shaped array on the untrusted-input path (localStorage, a pasted build code, a share link) — had no ceiling of its own. `reconcilePurchaseOrderCounts` (`logic.js`), which trims it down to match the real rank counts on every load/import, costs far worse than linear time in `purchaseOrder`'s own length: one backward pass per distinct AA with excess entries, each scanning the *current* array from the end. A `purchaseOrder` inflated to tens of thousands of entries for one real, held AA turns opening a share link into a multi-second tab freeze for whoever opens it, not just whoever crafted it — and compresses extremely well, so it costs the sender very little to build. `MAX_PURCHASE_ORDER` (`state.js`'s `deserializePurchaseOrder`) truncates the raw array to a generous-but-bounded ceiling (2000 — the entire AA roster, every class, everything maxed, is a few hundred entries at most) before any of that reconciliation work runs, the same "generous enough that no real user approaches it, tight enough that a hostile input can't exploit it" spirit `MAX_WAYPOINTS` already uses.

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

**Prerequisites:** `npm install` once, to pull in [esbuild](https://esbuild.github.io/) (the only dependency, and build-time only — the shipped app itself still has none, no server, works from `file://`).

To make a change:

1. Edit files under `src/` (app logic), `data.src.js` (AA data), or `styles.src.css`.
2. Run `python build_minify.py`. This regenerates `app.src.js` (assembled, readable — generated, don't edit directly), `app.js`/`data.js`/`styles.css` (minified, what ships), and re-stamps `index.html` with a cache-busting version hash.
3. Open `index.html` to test.

## Testing

`tests/` has data-independent Python unit tests for `wiki-sync/guess_costs.py`'s, `wiki-sync/guess_effects.py`'s, and `wiki-sync/assign_aa_ids.py`'s core logic, plus 22 Playwright browser tests that drive the actual app — cost/effect estimates, class-based rank caps, Archetype class-eligibility gating, hiding AAs, Progression's drag/auto-scroll/reorder, cross-class prereq dependencies, per-build owned-tracking profiles (Link/Merge/Split, migration, orphaned-profile cleanup), share-code encoding backward-compatibility, and the Other Classes tab, among others. See `tests/README.md` for the full list, prerequisites, and how to run them. None are wired into CI — run the relevant ones by hand after touching whatever they cover.

## Deployment

Hosted on GitHub Pages, served from `main` on every push.
