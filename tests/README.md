# Tests

Two kinds, both plain Python scripts (no pytest) — run each file directly and
check its exit code; every one prints `ALL PASS` on success and asserts
loudly on failure.

## Running everything at once

```
python tests/run_all.py
```

Discovers every `test_*.py` in this directory, starts its own local server
for the duration (killed again when the run ends, whether or not everything
passed), and runs each test as its own subprocess with a timeout so one
stalled test can't hang the whole run. Prints a pass/fail line per test plus
a summary, and exits non-zero if anything failed or timed out. Not wired
into CI (see below) - this is the manual-run convenience, nothing more.

## Data-independent unit tests

`test_guess_costs_interpolation.py` and `test_guess_effects.py` exercise
`wiki-sync/guess_costs.py`'s and `wiki-sync/guess_effects.py`'s core logic
directly, against synthetic reference pools rather than the live dataset. No
server, no browser — just:

```
python tests/test_guess_costs_interpolation.py
python tests/test_guess_effects.py
python tests/test_assign_aa_ids.py
```

This is deliberately *not* pinned to any AA's current confidence tier: the
whole point of the guessing feature is that a guess resolves away the moment
the wiki confirms the real value, so a test asserting "AA X is currently
medium-confidence" would break the instant the feature does its job. They
test the algorithms' rules instead (unanimous vs. majority voting,
bounded-vs-trailing interpolation, the manual-guess fallback and its
zero-known edge case, and — for effects specifically — multi-progression
extraction and that sibling-matching only works within an explicitly
declared group, never a coincidental text match) with hand-built inputs that
stay true regardless of what `data.src.js` says on any given day.

`test_assign_aa_ids.py` tests `wiki-sync/assign_aa_ids.py`'s rename-detection
logic (`compute_vanished`) the same way — synthetic id tables, not a wait for
an actual pending wiki rename to exercise it against.

## Browser (Playwright) tests

`test_cost_guess.py`, `test_manual_guess.py`, `test_guess_all_tabs.py`,
`test_disclaimer_banner.py`, `test_estimated_total.py`, `test_effect_guess.py`,
`test_build_slot_migration.py`, `test_active_build_match.py`,
`test_class_rank_cap.py`, `test_progression_autoscroll.py`,
`test_hidden_aas.py`, `test_other_classes.py`,
`test_owned_inactive_classes.py`, `test_owned_legacy_migration.py`,
`test_owned_profiles.py`, `test_owned_profile_cleanup.py`,
`test_share_code_compression.py`, `test_share_code_binary.py`,
`test_purchase_order_cap.py`, `test_per_rank_description.py`,
`test_progression_move_to.py`, `test_cross_class_prereq_dependency.py`,
`test_real_world_build.py`, `test_archetype_class_eligibility.py`,
`test_builds_index_cache.py`, `test_tree_click_delegation.py`,
`test_progression_drag_warn_cache.py`, `test_save_build_partial_failure.py`,
`test_builds_cross_tab_sync.py`, `test_decompression_bomb.py`,
`test_auto_grant_class_eligibility.py`
drive the actual app in a real Chrome instance via
[Playwright](https://playwright.dev/python/).

**Prerequisites:**
- `pip install playwright`
- A Chrome/Chromium install on PATH (these launch with `channel="chrome"` —
  the system browser, not a Playwright-managed one, so no `playwright
  install` download step is needed if Chrome is already present)
- The app served locally, default port 8743:
  ```
  python -m http.server 8743
  ```
  (run from the repo root, in a separate terminal, before the tests). To use
  a different port (e.g. it's already taken), serve on that port instead and
  set `AACALC_TEST_PORT` to match before running the tests:
  ```
  python -m http.server 8080
  AACALC_TEST_PORT=8080 python tests/test_cost_guess.py
  ```

Then, from the repo root:

```
python tests/test_cost_guess.py
python tests/test_manual_guess.py
python tests/test_guess_all_tabs.py
python tests/test_disclaimer_banner.py
python tests/test_estimated_total.py
python tests/test_effect_guess.py
python tests/test_build_slot_migration.py
python tests/test_active_build_match.py
python tests/test_class_rank_cap.py
python tests/test_progression_autoscroll.py
python tests/test_hidden_aas.py
python tests/test_other_classes.py
python tests/test_owned_inactive_classes.py
python tests/test_owned_legacy_migration.py
python tests/test_owned_profiles.py
python tests/test_owned_profile_cleanup.py
python tests/test_share_code_compression.py
python tests/test_share_code_binary.py
python tests/test_purchase_order_cap.py
python tests/test_per_rank_description.py
python tests/test_progression_move_to.py
python tests/test_cross_class_prereq_dependency.py
python tests/test_real_world_build.py
python tests/test_archetype_class_eligibility.py
python tests/test_builds_index_cache.py
python tests/test_tree_click_delegation.py
python tests/test_progression_drag_warn_cache.py
python tests/test_save_build_partial_failure.py
python tests/test_builds_cross_tab_sync.py
python tests/test_decompression_bomb.py
```

A few of these load a hand-crafted or hand-decoded `?build=` share code to
reach a specific scenario (an already-purchased guessed rank, a build with
several unconfirmed-cost ranks already spent, an inactive-class step) rather
than clicking through the UI to build it up live — faster, and pins the
exact scenario being tested instead of leaving it implicit in a sequence of
clicks.

## Tests pinned to live data

Several tests use specific live AAs as their guessed-value examples:
`test_effect_guess.py`'s Quick Evacuation, `test_cost_guess.py`'s Combat Fury
and Turn Summoned, `test_guess_all_tabs.py`'s Cannibalization and Turn
Summoned, and `test_estimated_total.py`'s Combat Agility and Turn Summoned.
A wiki scrape that confirms one of those specific ranks breaks that test.
When that happens, regenerate `costGuesses.js`/`effectGuesses.js`, pick a
fresh example from whichever guess table still has one, and swap it in; the
affected test's own comments describe how the last swap went. Turn Summoned
is currently the only AA left in the dataset with a real cost still
unconfirmed, so a couple of these tests lean on it alone.

`test_manual_guess.py` is the exception: there is currently no live AA with a
manual (curator-judgment, very-low confidence) *cost* guess, and the one AA
still carrying an unguessed cost (Turn Summoned) already has its own real,
high-confidence algorithmic guess. Rather than invent a `MANUAL_GUESSES`
entry with no real justification, that test intercepts the `app.js` request
and serves `app.src.js` (unminified, so `COST_GUESS_TABLE`'s name survives;
real `app.js` has it mangled by esbuild) with Turn Summoned's real table
entry replaced outright by a synthetic one. A plain string-prepend isn't
enough, since Turn Summoned's own entry declared later in the same object
literal would win over a prepended duplicate key. If a real manual cost guess
ever reappears, prefer swapping back to it over keeping the synthetic one.

`test_effect_guess.py`'s Quick Evacuation is Druid's copy: real confirmed
costs but an unconfirmed effect percentage, which resolves to a
medium-confidence guess sibling-matched against Wizard's own (confirmed)
Quick Evacuation. Should every effect guess ever drop back to manual-only,
this test would go back to pinning rendering rather than a particular tier;
the sibling-matching and interpolation rules themselves are covered
data-independently by `test_guess_effects.py`. When picking its next
example, prefer an AA a player actually spends points on. Banestrike is the
only other AA with a guessed effect value, but it is free and unlocked by
Slayer achievements, so a test driving it with `#incBtn` would be buying a
rank that cannot be bought in game.

The cost-guess table has run out of medium-confidence entries; what is left
is either high-confidence or manual very-low, so `test_guess_all_tabs.py`
pins those two tiers only.

`test_real_world_build.py` is pinned to a whole real share link (a live
user's actual Paladin/Enchanter/Druid build) rather than one AA. A wiki
change affecting any of its 180 picks would shift its exact row and
point-total assertions and need a fresh share link swapped in; the file's own
header comment says when a refresh is worth the rework versus leaving it be.
The same build also shows up as a lighter-weight fixture in
`test_guess_all_tabs.py` (one inactive-class row) and
`test_progression_autoscroll.py` (reused purely for its row count).

## CI

None of these are wired into CI yet, deliberately, not by oversight:
`run_all.py` above needs to actually be the established way this project runs
its tests first, and Chrome (not Playwright's own bundled browser) needs
installing in whatever runs it, since every browser test launches with
`channel="chrome"` on purpose. Revisit once the runner is established and the
manual discipline it's meant to replace starts costing more than automating
it would. A lighter first step, if that day comes, would be CI over just the
3 data-independent tests plus `build_minify.py`'s own prereq/id invariant
checks, none of which need a browser at all, before taking on the full
Playwright suite.

## When to run which

Run these by hand after a change that touches the areas below, before
rebuilding and committing.

- **Guessing features.** `wiki-sync/guess_costs.py` or
  `wiki-sync/guess_effects.py`, their consumers in `src/keys.js`,
  `src/logic.js`, and `src/render.js`, the disclaimer banner, the topbar, or
  Progression's blended running total and the plain-text export mirroring it.
  Run the `test_*guess*.py` files, `test_disclaimer_banner.py`, and
  `test_estimated_total.py`.
- **Class rank caps.** `classRankCapFor`, `structuralLockReason`,
  `heldRankInvalidReason`, `effectiveDisplayRank`, or
  `computeProgressionSteps`'s `classCapWarn`.
  `test_class_rank_cap.py`.
- **Archetype class eligibility.** `isClassEligible`, its branches in
  `structuralLockReason` (`kind: "classEligibility"`),
  `heldRankInvalidReason`, and `computeProgressionSteps`'s
  `classEligibilityWarn`, the tree's `.locked-classlock` and
  `.costtag.classlock-tag`, or Browse's `.eligible-info` line in
  `renderBrowse`. `test_archetype_class_eligibility.py`. `data.src.js`'s
  `eligibleClasses` field is a hand-compiled, not-yet-in-game-confirmed
  dataset, so a mismatch there is a data fix, not a logic bug.
- **Auto-granted AAs with eligibleClasses.** `effectiveRankScoped`'s
  `aa.auto` branch, and the ineligible-but-auto rendering in `renderTree`
  (`autoIneligible`, the `.locked-classlock`/`.costtag.classlock-tag`
  fallback in place of the `AUTO` tag) and `renderSidePanel`.
  `test_auto_grant_class_eligibility.py`.
- **Progression drag-to-reorder auto-scroll.** `updateAutoScroll`,
  `autoScrollStep`, `stopAutoScroll`, or any drop handler wired in
  `renderProgression`/`wireProgressionDropZone`.
  `test_progression_autoscroll.py`.
- **Hiding AAs.** `isHidden`/`isHiddenScoped`, `setHidden`/`setHiddenScoped`,
  `hasAnyHidden`, the filtering in `renderTree`/`renderBrowse`, or
  `HIDDEN_STORAGE_KEY`/`loadAndApplyHidden`/`saveHidden`.
  `test_hidden_aas.py`.
- **A class swap's persistent data.** `spentPoints`/`estimatedExtraPoints`/
  `ownedPoints`'s lifetime scope, `spentForClass`/`spentOnInactiveClasses`,
  `effectiveRankScoped`, `otherClassesWithPicks`/`countOtherClassesPicked`,
  the `.inactive` muted/read-only row treatment `renderProgression` gives a
  swapped-out class's picks, or `renderOtherClasses`/`renderSummary`'s shared
  `otherClassesSectionsHtml` helper. `test_other_classes.py` and
  `test_owned_inactive_classes.py`, plus `test_real_world_build.py` for a
  large-scale real-build sanity check on the same behavior.
- **Per-build owned-tracking profiles.** `ownedStorageKeyFor`,
  `state.ownedProfileId`, `linkOwnedProfile`/`splitOwnedProfile`/
  `mergeOwnedProfileInto`/`adoptImportedOwnedAsNewProfile`,
  `listOwnedProfileIds`/`removeOwnedProfile` (all in `state.js`),
  `saveBuildAs`/`loadBuild`'s profile handling,
  `migrateLegacyOwnedProfile`/`migrateStaleBuildSlots`'s backfill,
  `linkOwnedToBuild`/`mergeOwnedFromBuild`/`splitOwnedFromCurrent`,
  `cleanupOrphanedOwnedProfiles` (in `builds.js`), or the Manage Owned
  Tracking modal in `render.js`. Split three ways:
  `test_owned_legacy_migration.py` for backward compatibility and migration,
  `test_owned_profiles.py` for new-build independence, Link/Merge/Split, and
  silent profile creation on import, and `test_owned_profile_cleanup.py` for
  the orphaned-profile sweep.
- **Share-code encoding.** `packV5`/`expandBinaryPayload`'s bit layout, the
  `bitWriter`/`bitReader` pair, `crc16`, `indexWidth`,
  `encodeBuildCode`/`decodeBuildCode`'s format-sniffing chain,
  `compress`/`decompress`, or `compactRanksFor`/`expandCompactRanks`, all in
  `exportImport.js`. `test_share_code_binary.py` covers the current v5
  binary format and `test_share_code_compression.py` covers every historical
  one still decoding. The v5 file's property test (randomized builds through
  the real export/import path) is the load-bearing one: a wrong bit width or
  a missed read shifts every field after it and can still yield values that
  are individually in-range, which the CRC cannot catch because the encoder
  checksums its own wrong output. Three narrower cases sit alongside it:
  - a rank of 26 (Hunter's Attack Power, reachable only through an imported
    payload) pins `V5_BITS.rank` at 5, since the property test's own builds
    never exceed 10;
  - a flipped byte in a trailing waypoint label pins the CRC itself, being
    the one corruption that lands after every bit read completes and so
    slips past `bitReader`'s bounds check;
  - the id bitmap's low boundary: an empty build and one holding only id 0
    (Adamant Will) both store `hi = 0` and are told apart only by the bitmap
    being written as `hi + 1` bits unconditionally.
- **Purchase-order ceiling.** `MAX_PURCHASE_ORDER`/`deserializePurchaseOrder`
  in `state.js`. `test_purchase_order_cap.py`.
- **Per-rank descriptions.** `splitPerRankLines`/`markProgressions` and
  `highlightRankValue`'s branch between them in `logic.js`, or the
  `.rank-line`/`.is-current-rank` rules in `styles.src.css`.
  `test_per_rank_description.py`. An AA whose ranks each do something
  different is written as consecutive "Rank N: " clauses in `data.src.js` and
  rendered one line per rank, since a slash progression would line its slots
  up against the wrong ranks.
- **AA id rename detection.** `compute_vanished` in
  `wiki-sync/assign_aa_ids.py`. `test_assign_aa_ids.py`.
- **Move To popover.** `absoluteIndexForVisiblePosition`,
  `moveToVisiblePosition`, `waypointSections`'s fit-aware section-boundary
  math, `moveMenuHtml`, or `s.visiblePos`'s role in
  `computeProgressionSteps`/step-num display (now just `s.index + 1` for
  every row, active class or not, since nothing gets filtered out of
  Progression anymore). `test_progression_move_to.py`.
- **Prerequisite and dependency resolution.** `resolvePrereqTarget`/
  `resolvePrereqTargetScoped`, `isDependedOn`, `tryResolvePrereq`.
  `test_cross_class_prereq_dependency.py`.
- **Saved-builds index cache.** `cachedIndex`/`loadIndex`/`saveIndex` in
  `builds.js`. `test_builds_index_cache.py`. `saveIndex` is the only write
  path, and every caller besides `deleteBuild` mutates `loadIndex()`'s
  returned array in place before calling it, which already updates the cache
  by reference. Only `deleteBuild`'s freshly-`.filter()`'d array depends on
  `saveIndex` reassigning `cachedIndex`, so that's the one path worth
  testing.
- **Tree node selection delegation.** `el.treeWrap`'s click/keydown
  listeners in `events.js`, which resolve a clicked node's category from
  `state.activeTab` rather than a per-node listener.
  `test_tree_click_delegation.py`. A wrong category would still pass on the
  General tab, since General is also `state.activeTab` there, so this
  specifically checks a non-default tab.
- **Progression's drag-hover warning cache.** `dragWarnCacheToIndex`/
  `dragWouldIntroduceWarn` in `render.js`, reset at every `dragstart` since a
  new drag can revisit the same insertion point with a different answer.
  `test_progression_drag_warn_cache.py`.
- **`saveBuildAs` and `deleteBuild` failure reporting.**
  `saveOwnedProfileTo`/`saveIndex` return whether their own write landed
  rather than swallowing a failure. A brand-new slot's seeded owned-profile
  write or the index write failing after the slot write already succeeded
  must still report the whole save as failed, not a false success. A failed
  delete must not remove the slot's own data when the index write that was
  supposed to drop the reference didn't land, since that leaves a dangling
  reference instead of a safely retryable no-op.
  `test_save_build_partial_failure.py`.
- **Cross-tab index invalidation.** The `"storage"` listener in `events.js`
  that calls `dropCachedIndex`. `cachedIndex` otherwise only tracks this
  tab's own writes, so a save from another tab could get silently clobbered
  by a save made afterward in this one. `test_builds_cross_tab_sync.py`.
- **Size limits on a share/import code.** `MAX_ENCODED_CODE_LENGTH`/
  `MAX_DECOMPRESSED_BYTES` in `exportImport.js`. An otherwise-valid build
  padded past either cap must still be rejected, proving the limit is what's
  catching it rather than some unrelated parse failure.
  `test_decompression_bomb.py`.
