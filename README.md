# EQL AA Calculator

A talent-calculator-style planner for [EverQuest Legends](https://eqlwiki.com/Alternate_Advancement) Alternate Advancement (AA) builds. Unofficial fan-made tool, not affiliated with the game.

**Live:** https://aacalc.abnotus.com

## Features

- Pick up to 3 classes (EQL's tri-class combo system) and spend points across General, Archetype, Class, and Special AAs
- Swap classes freely — picks for a class you're not currently using move to a new **Other Classes** tab instead of disappearing, and still count toward your total Points Spent. Switch back and everything's exactly as you left it
- Prerequisite, level, and class-based rank-cap checks before you can spend a point, with no artificial point cap of its own. A rank that a later class swap puts out of reach is never stripped — it stays flagged until a qualifying class comes back
- Locked AAs show *why* — a missing prerequisite looks different from a plain level gate, in both the tree and Browse All AAs
- Next-rank preview — see what the next rank upgrades to before you buy it
- Global search, with match-count badges on every tab
- **Browse All AAs** — a searchable reference independent of your current build
- **Build Summary** — everything you've picked, grouped by category
- **Progression** tab — the order you spent points in, drag-and-drop or arrow-key reorderable, with per-step and running-total cost. A "Move To" button quick-jumps a step to the top/bottom of the list or of any waypoint, or to a specific position — handy once a build gets long
- **Waypoints** — mark a point total worth returning to (e.g. "Level 20"), and it shows up as a colored divider right where your training order crosses it. Anchored to the point total, not a list position, so reordering and Reset Build never break one
- Mark AAs as **owned** to track what you've actually trained in-game, separate from what's just planned — with a running "points owned / to go" total. Owned status follows your character, not any one plan, so switching Builds never touches it
- **Builds** — save named snapshots of your build and switch between them, for comparing class combos or planning alternate paths
- Export a build as text or a shareable link; import by pasting text, a link, or loading a saved file
- Undocumented costs and effect values can show a pattern-inferred estimate instead of a bare `?`, color-coded by confidence. Purely a display hint — never counted in real point totals, and automatically replaced the moment the wiki confirms the real value
- Auto-granted AAs are applied automatically, no points needed
- Responsive layout, keyboard-accessible
- Saved builds stay correct even when the underlying AA data changes — you'll see a notice if a pick disappeared or a prerequisite stopped being met
- **Hide** AAs you don't care about to declutter the tree and Browse All AAs, with a toggle to bring them back. An AA you've already spent points on always stays visible regardless

Player-facing version history is in the app itself — click the version tag in the bottom-right corner. For everything else, `git log` is the changelog.

Each entry added to `USER_CHANGELOG` (`src/changelogData.js`) gets a matching annotated git tag (`vX.Y.Z`, e.g. `git tag -a v1.1.0 -m "..."`) on the commit that bumped it, then `git push origin vX.Y.Z`. Lets a reported issue be pinned to a specific version.

## Data source

All AA data (costs, effects, ranks, prerequisites) lives in `data.src.js`, sourced from [eqlwiki.com/Alternate_Advancement](https://eqlwiki.com/Alternate_Advancement) and cross-checked against in-game logs/screenshots where the wiki is silent or wrong. Values marked `?` are undocumented anywhere and treated as 0 until confirmed.

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

Regenerates `src/costGuesses.js` — pattern-inferred estimates for per-rank costs the wiki hasn't documented yet (`?` in `data.src.js`). Cross-references *other* fully-known AAs with the same rank count and matching known costs, rather than trusting one AA's own progression alone — Adamant Will's `2/4/6/?` looks like a clean doubling sequence, but its real sibling Fear Resistance (same shape) is fully known at `2/4/6/9`, not 8. Confidence scales with how many independent siblings agree (see the script's own docstring for the tiers); a gap bounded by two of the AA's own known costs can still get a lower-confidence interpolated guess, since the true value is provably between them either way.

Rewrites `costGuesses.js` from scratch every run, so a guess that's since been confirmed (or lost its supporting evidence) just stops appearing — nothing to clean up by hand. Run it after any `data.src.js` change that could move the picture.

For the handful of slots nothing else can reach, the script also has a small hand-maintained `MANUAL_GUESSES` dict — curator judgment calls, used only as a last resort and tagged with their own `"very-low"` tier so they never read as the same kind of evidence as the algorithmic ones. A real cross-AA match always wins over a manual entry automatically, the moment one exists.

### Estimating undocumented effect values

```
python wiki-sync/guess_effects.py
```

Same idea, applied to the numeric values inside AA effect descriptions instead of per-rank costs — the `?` in something like `"Increases your critical hit chance by 1/?/5/10%."`. Regenerates `src/effectGuesses.js`, keyed one level deeper than costs since a single description can hold more than one independent progression (Adamant Will's resist-charm and resist-mesmerization percentages are two separate ones in the same sentence).

The one real difference: sibling matching only compares AAs within an explicitly hand-declared group (`EFFECT_SIBLING_GROUPS` in the script) — a human confirming two AAs share the same formula, not a text-similarity guess. A cost curve recurring across AAs is a real pattern (the game reuses cost templates); an effect *magnitude* recurring is just coincidence. Interpolation and the manual fallback otherwise work the same as the cost version.

## Running locally

No build tools, no server — just open `index.html` in a browser.

## Development

The app logic is authored as real ES modules under `src/` (`aaIds.js`, `costGuesses.js`, `effectGuesses.js`, `keys.js`, `changelogData.js`, `state.js`, `logic.js`, `builds.js`, `dom.js`, `render.js`, `exportImport.js`, `events.js`, `main.js`). Native ES modules don't work over `file://` in Chrome, and this app is deliberately built to run by just double-clicking `index.html` with no local server — so `build_minify.py` assembles the `src/` modules back into a single classic script and minifies it, which is what `index.html` actually loads.

`build_minify.py` also checks a data-integrity invariant before building (see the comment on `check_prereq_disambiguation_invariant`) and fails the build with an explanation if it's violated, rather than shipping AA data that would resolve a prerequisite unpredictably. If a build fails on this, the error message says what to fix.

### Saved builds are keyed by AA name, not array position

At runtime, `state.ranks` and `purchaseOrder` address AAs by index into `AA_DATA` — simple, and every render/logic function already works that way. But that index is *not* what gets persisted to localStorage, exported text, or share links: `src/keys.js` derives a stable key from each AA's name instead, so a save survives `data.src.js` being reordered or regenerated by a wiki scrape. Without this, reordering an AA would silently shift every index-based save onto the wrong ability.

`keys.js` also carries a frozen snapshot of `AA_DATA`'s ordering as of 2026-07-09 (`LEGACY_AA_ORDER`), used only to migrate saves made before this existed. Never update it — it's a historical record of what old saves meant, not current data.

### Named builds don't replace the always-autosaving current build

`state.js`'s `STORAGE_KEY` is whatever build you're currently looking at — autosaved on every change, loaded unconditionally on boot. `src/builds.js` adds named snapshots on top as a separate concern: saving copies the current state into its own key, loading overwrites the current state with a saved copy. Which slot a loaded/saved build is "active" is tracked only for UI display, and cleared on Reset/Import/a share link so a later save can't mistake unrelated content for an update to a slot it no longer matches.

### Owned progress lives outside any single build

`state.owned` (the Progression tab's "actually trained in-game" watermark) persists to its own `localStorage` key (`OWNED_STORAGE_KEY`), not inside the build payload or a Builds slot. It's loaded once at boot and never touched when switching Builds, loading a share link, or importing text — that's what lets it survive flipping between saved plans without re-syncing by hand. A build/share code can opt into *carrying* owned data too (the Export modal's checkbox), but importing one asks first, since overwriting someone's real progress from a pasted link is the one case here that isn't easily undone.

### A cost or effect estimate can never outrank a real one

`src/costGuesses.js` is only ever consulted through `keys.js`'s `costGuessFor`, and only when the real `costs[rankIdx]` is exactly `"?"` — `logic.js`'s `costNum()`/`spentPoints()` never look at it, so an estimate can't affect real point totals. The moment a real number replaces `"?"` in `data.src.js`, that slot's guess (if one still exists) is simply never read again.

`src/effectGuesses.js` has the same guarantee: `render.js`'s `highlightRankValue` only substitutes a guess where the description text is literally `"?"` — search, export text, and everywhere else a description is read still see the real, unmodified string.

To make a change:

1. Edit files under `src/` (app logic), `data.src.js` (AA data), or `styles.css`.
2. Run `python build_minify.py`. This regenerates `app.src.js` (assembled, readable — generated, don't edit directly), `app.js`/`data.js` (minified, what ships), and re-stamps `index.html` with a cache-busting version hash.
3. Open `index.html` to test.

## Testing

`tests/` has data-independent Python unit tests for `wiki-sync/guess_costs.py`'s and `wiki-sync/guess_effects.py`'s core logic, plus 14 Playwright browser tests that drive the actual app — cost/effect estimates, class-based rank caps, hiding AAs, Progression's drag/auto-scroll/reorder, and the Other Classes tab, among others. See `tests/README.md` for the full list, prerequisites, and how to run them. None are wired into CI — run the relevant ones by hand after touching whatever they cover.

## Deployment

Hosted on GitHub Pages, served from `main` on every push.
