# Tests

Two kinds, both plain Python scripts (no pytest) — run each file directly and
check its exit code; every one prints `ALL PASS` on success and asserts
loudly on failure.

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
`test_progression_drag_warn_cache.py`
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
```

A few of these load a hand-crafted or hand-decoded `?build=` share code to
reach a specific scenario (an already-purchased guessed rank, a build with
several unconfirmed-cost ranks already spent, an inactive-class step) rather
than clicking through the UI to build it up live — faster, and pins the
exact scenario being tested instead of leaving it implicit in a sequence of
clicks.

Several of these tests are pinned to specific live AAs as their guessed-value
examples (`test_effect_guess.py`'s Quick Evacuation,
`test_cost_guess.py`'s Combat Fury and Turn Summoned,
`test_guess_all_tabs.py`'s Cannibalization and Turn Summoned,
`test_estimated_total.py`'s Combat Agility and Turn Summoned) —
a future wiki scrape confirming one of those specific ranks will break that
test, same as it's already happened repeatedly (Adamant Will, Combat
Stability, Combat Fury's effect value, Packrat's entire cost/effect
progression, Alchemy Mastery, Baking Mastery, Conjurer's Efficiency, First
Aid, Unbound Boon, and most recently Thief's Intuition and Wizard's Quick
Evacuation - Reaching Notes among them turned out to alternate real/free
ranks on confirmation, the same formula Symphonic Aura uses, not truly
unknown - all resolved to real data and had to be swapped out for a
still-live example over the course of this project). Turn Summoned is
currently the only AA left anywhere in the dataset with a real cost still
unconfirmed, so a couple of these tests lost their second, differently-
scoped example when Quick Evacuation resolved and now lean on Turn Summoned
alone. Regenerate `costGuesses.js`/`effectGuesses.js` first, then pick a
fresh example from whichever guess table still has one - see the affected
test's own comments for how the swap played out last time.

`test_manual_guess.py` is the one exception: as of this writing there is no
live AA with a manual (curator-judgment, very-low confidence) *cost* guess
at all - every `MANUAL_GUESSES` entry that used to apply has since been
confirmed by the wiki, and the one AA still carrying an unguessed cost
(Turn Summoned) already has its own real, high-confidence algorithmic guess.
Rather than invent a `MANUAL_GUESSES` entry with no real justification just
to have a live example, that test intercepts the `app.js` request and serves
`app.src.js` (unminified, so `COST_GUESS_TABLE`'s name survives - real
`app.js` has it mangled by esbuild) with Turn Summoned's real table entry
replaced outright by a synthetic one - a plain string-prepend isn't enough
here (unlike when this test used Thief's Intuition, which had no real entry
to collide with), since Turn Summoned's own real entry declared later in the
same object literal would just win over a prepended duplicate key. If a real
manual cost guess ever reappears, prefer swapping back to it over keeping
the synthetic one.

`test_effect_guess.py`'s Quick Evacuation is Druid's copy - real confirmed
costs but an unconfirmed effect percentage - which now resolves to a
medium-confidence guess sibling-matched against Wizard's own (confirmed)
Quick Evacuation, rather than the manual very-low guess it carried before
Wizard's numbers were confirmed. Should every effect guess ever drop back to
manual-only, this test would go back to pinning rendering rather than a
particular tier; the sibling-matching and interpolation rules themselves are
covered data-independently by `test_guess_effects.py`. When picking its next
example, prefer an AA a player actually spends points on - Banestrike is the
only other AA with a guessed effect value, but it is free and unlocked by
Slayer achievements, so a test driving it with `#incBtn` would be buying a
rank that cannot be bought in game.

The cost-guess table has likewise run out of medium-confidence entries;
what is left is either high-confidence or manual very-low, so
`test_guess_all_tabs.py` pins those two tiers only.

`test_real_world_build.py` is pinned the same way, but to a whole real
share link (a live user's actual Paladin/Enchanter/Druid build) rather than
one AA - a wiki change affecting any of its 183 picks would shift its exact
row/point-total assertions and need a fresh share link swapped in (already
happened once - see the file's own header comment for when a refresh is
actually worth the rework, vs. just leaving it be). The same build also
shows up as a lighter-weight fixture in `test_guess_all_tabs.py` (one
inactive-class row) and `test_progression_autoscroll.py` (reused purely
for its row count).

None of these are wired into CI; run them by hand after a change that
touches either guessing feature (`wiki-sync/guess_costs.py` or
`wiki-sync/guess_effects.py`, their consumers in `src/keys.js`/
`src/logic.js`/`src/render.js`, the disclaimer banner, the topbar, or
Progression's own blended running total / the plain-text export mirroring
it), class-rank-cap logic (`classRankCapFor`, `structuralLockReason`,
`heldRankInvalidReason`, `effectiveDisplayRank`, `computeProgressionSteps`'s
`classCapWarn` - `test_class_rank_cap.py`), Archetype class-eligibility
gating (`isClassEligible`, its own branches in `structuralLockReason`
(`kind: "classEligibility"`)/`heldRankInvalidReason`/
`computeProgressionSteps`'s `classEligibilityWarn`, the tree's
`.locked-classlock`/`.costtag.classlock-tag`, or Browse's `.eligible-info`
line in `renderBrowse` - `test_archetype_class_eligibility.py`;
`data.src.js`'s `eligibleClasses` field itself is a hand-compiled,
not-yet-in-game-confirmed dataset, so a mismatch there is a data fix, not
a logic bug), Progression's drag-to-reorder
auto-scroll (`updateAutoScroll`, `autoScrollStep`, `stopAutoScroll`, or any
of the drop handlers wired in `renderProgression`/`wireProgressionDropZone` -
`test_progression_autoscroll.py`), hiding AAs (`isHidden`/`isHiddenScoped`,
`setHidden`/`setHiddenScoped`, `hasAnyHidden`, the filtering in
`renderTree`/`renderBrowse`, or `HIDDEN_STORAGE_KEY`/`loadAndApplyHidden`/
`saveHidden` - `test_hidden_aas.py`), or a class swap's now-persistent data
(`spentPoints`/`estimatedExtraPoints`/`ownedPoints`'s lifetime scope,
`spentForClass`/`spentOnInactiveClasses`, `effectiveRankScoped`,
`otherClassesWithPicks`/`countOtherClassesPicked`, the `.inactive`
muted/read-only row treatment `renderProgression` now gives a swapped-out
class's picks instead of hiding them, or `renderOtherClasses`/
`renderSummary`'s shared `otherClassesSectionsHtml` helper -
`test_other_classes.py`, `test_owned_inactive_classes.py`, and
`test_real_world_build.py` for a large-scale real-build sanity check on the
same behavior), per-build owned-tracking profiles
(`ownedStorageKeyFor`, `state.ownedProfileId`, `linkOwnedProfile`/
`splitOwnedProfile`/`mergeOwnedProfileInto`/`adoptImportedOwnedAsNewProfile`
in `state.js`; `saveBuildAs`/`loadBuild`'s profile handling,
`migrateLegacyOwnedProfile`/`migrateStaleBuildSlots`'s backfill,
`linkOwnedToBuild`/`mergeOwnedFromBuild`/`splitOwnedFromCurrent`, or
`cleanupOrphanedOwnedProfiles` in `builds.js`; `listOwnedProfileIds`/
`removeOwnedProfile` in `state.js`; the Manage Owned Tracking modal in
`render.js` - split across `test_owned_legacy_migration.py` for the
backward-compatibility/migration side, `test_owned_profiles.py` for
new-build independence, Link/Merge/Split, and silent-import-profile-
creation, and `test_owned_profile_cleanup.py` for the orphaned-profile
sweep specifically), share-code encoding
(`packV5`/`expandBinaryPayload`'s bit layout, the `bitWriter`/`bitReader`
pair, `crc16`, `indexWidth`, `encodeBuildCode`/`decodeBuildCode`'s
format-sniffing chain, `compress`/`decompress`, or
`compactRanksFor`/`expandCompactRanks`, in `exportImport.js` - split
across `test_share_code_binary.py` for the current v5 binary format and
`test_share_code_compression.py` for every historical one still decoding.
The v5 file's property test - randomized builds through the real
export/import path - is the load-bearing one: a wrong bit width or a
missed read shifts every field after it and can still yield values that
are individually in-range, which the CRC cannot catch because the encoder
checksums its own wrong output. Two narrower cases sit either side of it:
a rank of 26 (Hunter's Attack Power, reachable only through an imported
payload) pins `V5_BITS.rank` at 5, since the property test's own builds
never exceed 10; and a flipped byte in a trailing waypoint label pins the
CRC itself, being the one corruption that lands after every bit read
completes and so slips past `bitReader`'s bounds check. A third pins the
id bitmap's low boundary, where an empty build and one holding only id 0
(Adamant Will) both store `hi = 0` and are told apart only by the bitmap
being written as `hi + 1` bits unconditionally),
`MAX_PURCHASE_ORDER`/
`deserializePurchaseOrder` in `state.js` (`test_purchase_order_cap.py`),
per-rank descriptions (`splitPerRankLines`/`markProgressions` and
`highlightRankValue`'s branch between them in `logic.js`, or the
`.rank-line`/`.is-current-rank` rules in `styles.src.css` -
`test_per_rank_description.py`; an AA whose ranks each do something
different is written as consecutive "Rank N: " clauses in `data.src.js`
and rendered one line per rank, since a slash progression would line its
slots up against the wrong ranks), rename-detection in
`wiki-sync/assign_aa_ids.py` (`compute_vanished` -
`test_assign_aa_ids.py`), or the Move To popover
(`absoluteIndexForVisiblePosition`, `moveToVisiblePosition`,
`waypointSections`'s fit-aware section-boundary math, `moveMenuHtml`, or
`s.visiblePos`'s role in `computeProgressionSteps`/step-num display - now
just `s.index + 1` for every row, active class or not, since nothing gets
filtered out of Progression anymore - `test_progression_move_to.py`), or
prereq/dependency resolution
(`resolvePrereqTarget`/`resolvePrereqTargetScoped`, `isDependedOn`,
`tryResolvePrereq` - `test_cross_class_prereq_dependency.py`), the saved-
builds index cache (`cachedIndex`/`loadIndex`/`saveIndex` in `builds.js` -
`test_builds_index_cache.py`; `saveIndex` is the only write path, and every
caller besides `deleteBuild` mutates `loadIndex()`'s returned array in
place before calling it, which already updates the cache by reference
regardless of whether `saveIndex` itself reassigns `cachedIndex` - only
`deleteBuild`'s freshly-`.filter()`'d array actually depends on that
reassignment, so it's the one path worth testing), tree node selection
delegation (`el.treeWrap`'s click/keydown listeners in `events.js`, which
resolve a clicked node's category from `state.activeTab` rather than a
per-node listener - `test_tree_click_delegation.py`; a wrong category would
still pass on the General tab, since General is also `state.activeTab`
there, so this specifically checks a non-default tab), or Progression's
drag-hover warning cache (`dragWarnCacheToIndex`/`dragWouldIntroduceWarn` in
`render.js`, reset at every `dragstart` since a new drag can revisit the
same insertion point with a different answer - `test_progression_drag_warn_cache.py`)
before rebuilding and committing.
