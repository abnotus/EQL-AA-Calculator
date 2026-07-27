// Business logic: everything that reads or derives from `state` and AA_DATA,
// plus the mutation functions for spending/refunding points. No HTML/DOM here.
// Depends on state.js and (for costGuess/effectGuess) keys.js — never on
// render.js — so the dependency graph stays one-directional (render depends
// on logic, not the other way around).

import { state, CLASS_SLOT_KEYS, AA_CATEGORY_KEYS, saveLocal, saveOwned, saveHidden, sanitizeWaypoints } from "./state.js";
import { costGuessFor, effectGuessFor } from "./keys.js";

export function costNum(c) {
  const n = parseInt(c, 10);
  return isNaN(n) ? 0 : n;
}

export function escapeHtml(str) {
  // '&apos;' not '&#39;' — highlightRankValue re-parses this output for
  // slash-separated progressions, and '&#39;' embeds a digit pair ("39")
  // that could be misread as a phantom rank slot next to an apostrophe.
  return String(str == null ? "" : str)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}

export function iconLetter(name) {
  return (name || "?").trim().charAt(0).toUpperCase();
}

// Builds the tooltip text for a guess object ({value, confidence, basedOn,
// interpolated, manual}). Shared by formatGuessDisplay (render.js, costs)
// and highlightRankValue (below, effect values) so both read the same.
export function guessTitle(guess) {
  if (guess.manual) return `Estimated (very low confidence) — hand-picked pending wiki confirmation, not derived from other AAs. Not confirmed on the wiki.`;
  if (guess.interpolated) return `Estimated (${guess.confidence} confidence) — no comparable AA found, interpolated between this AA's own known ranks. Not confirmed on the wiki.`;
  return `Estimated (${guess.confidence} confidence) from ${guess.basedOn.join(", ")} — not confirmed on the wiki.`;
}

// Highlights the value matching the current rank inside slash-separated
// progressions, e.g. "20/40/60%" at rank 2 -> "20/<mark>40</mark>/60%".
// If guessLookup is given, also substitutes a pattern-inferred estimate
// for any "?" slot — independent of rank, so it still runs when rank is
// falsy/0 (Browse's rank-agnostic view). guessLookup(progIdx, rankIdx) ->
// guess or null; progIdx counts progressions in order of appearance (a
// description can hold more than one — see effectGuesses.js).
export function highlightRankValue(text, rank, guessLookup) {
  const escaped = escapeHtml(text);
  if (!guessLookup && (!rank || rank < 1)) return escaped;
  let progIdx = -1;
  return escaped.replace(/\d+(?:\.\d+)?%?(?:\/(?:\d+(?:\.\d+)?%?|\?)){1,}/g, (match) => {
    progIdx++;
    const parts = match.split("/");
    const highlightIdx = rank && rank >= 1 ? rank - 1 : -1;
    return parts.map((part, i) => {
      if (part === "?") {
        const guess = guessLookup ? guessLookup(progIdx, i) : null;
        if (!guess) return part;
        const cls = `is-estimate tier-${guess.confidence}${i === highlightIdx ? " rank-highlight" : ""}`;
        return `<span class="${cls}" title="${escapeHtml(guessTitle(guess))}">~${guess.value}</span>`;
      }
      return i === highlightIdx ? `<span class="rank-highlight">${part}</span>` : part;
    }).join("/");
  });
}

// For descriptions phrased as a flat "N per rank" (e.g. "4 points per rank"),
// shows the total at the current rank with the per-rank amount noted alongside,
// e.g. "24 points (4 per rank)" at rank 6. Left untouched at rank <= 1, where
// total and per-rank are the same number.
export function applyPerRankTotal(text, rank) {
  if (!rank || rank < 2) return text;
  return text.replace(/(\d+(?:\.\d+)?)(%)?\s*(points?|seconds?)?\s*(chance)?\s*\(?per rank\)?/gi,
    (match, numStr, pct, unit, chanceWord) => {
      const num = parseFloat(numStr);
      const total = num * rank;
      const fmt = (n) => (Number.isInteger(n) ? String(n) : n.toFixed(2).replace(/0+$/, "").replace(/\.$/, ""));
      let unitLabel = "";
      if (pct) unitLabel = "%";
      else if (unit) {
        const singular = unit.replace(/s$/i, "");
        unitLabel = " " + (total === 1 ? singular : singular + "s");
      }
      const chancePart = chanceWord ? " chance" : "";
      return `${fmt(total)}${unitLabel}${chancePart} (${fmt(num)}${pct ? "%" : ""} per rank)`;
    });
}

// Shared by the tree view, tab match badges, and Browse All — one search box,
// same matching rule everywhere it's used.
export function aaMatchesQuery(aa, query) {
  if (!query) return false;
  const q = query.trim().toLowerCase();
  if (!q) return false;
  return aa.name.toLowerCase().includes(q) || aa.description.toLowerCase().includes(q);
}

// Count of AAs in a category matching the current search, for tab badges.
// Must exclude hidden AAs the same way renderTree/renderBrowse do, or a
// hidden match would inflate a badge while the tab itself shows nothing
// for it.
export function countMatches(catKey, query) {
  if (!query || !query.trim()) return 0;
  return getList(catKey).filter((aa, idx) => {
    if (!aaMatchesQuery(aa, query)) return false;
    if (isHidden(catKey, idx) && !state.showHidden && effectiveRank(catKey, idx) === 0) return false;
    return true;
  }).length;
}

function classSlotIndex(catKey) {
  const i = CLASS_SLOT_KEYS.indexOf(catKey);
  return i;
}

export function labelFor(catKey) {
  if (catKey === "general") return "General AA";
  if (catKey === "archetype") return "Archetype AA";
  if (catKey === "special") return "Special AA";
  const slot = classSlotIndex(catKey);
  if (slot >= 0) return state.selectedClasses[slot] + " AA";
  return catKey;
}

// Short form used for tab labels and Summary section headers (no " AA" suffix).
export function shortCategoryLabel(catKey) {
  if (catKey === "general") return "General";
  if (catKey === "archetype") return "Archetype";
  if (catKey === "special") return "Special";
  const slot = classSlotIndex(catKey);
  if (slot >= 0) return state.selectedClasses[slot];
  return catKey;
}

export function getList(catKey) {
  const slot = classSlotIndex(catKey);
  if (slot >= 0) return AA_DATA.classes[state.selectedClasses[slot]] || [];
  return AA_DATA[catKey] || [];
}

// Auto-granted AAs (0-cost on the wiki) are trained automatically as the
// character levels — the wiki documents one unlock level, not per-rank
// breakpoints, so these sit at max rank once unlocked rather than
// trickling in.
//
// `autoRanks: N` is rarer: only the first N ranks are free (e.g. Symphonic
// Aura's rank 1 is free, rank 2+ cost points). effectiveRank returns the
// greater of the free baseline and whatever's been purchased, so the free
// ranks never need their own purchaseOrder entry.
export function effectiveRank(catKey, idx) {
  const { scope, className } = categoryToScopeClassName(catKey);
  return effectiveRankScoped(scope, className, idx);
}

// Same lookup as effectiveRank, by (scope, className) directly rather than
// a slot-relative catKey - for the Other Classes tab, where an inactive
// class has no catKey at all (classSlotIndex returns -1 for it). Same
// split as costGuess/costGuessScoped.
export function effectiveRankScoped(scope, className, idx) {
  const list = scope === "class" ? (AA_DATA.classes[className] || []) : (AA_DATA[scope] || []);
  const aa = list[idx];
  // An auto-granted AA's free portion only applies while its class is
  // active — it's a level-gated freebie, not a standing investment like a
  // manually-trained rank (which persists while inactive; see Other
  // Classes). Without this gate, a scoped call for an inactive class would
  // report the AA as "picked" despite never being granted.
  const classActive = scope !== "class" || state.selectedClasses.includes(className);
  if (aa && aa.auto) {
    const levelReq = parseInt(aa.levelReq, 10) || 1;
    return classActive && state.charLevel >= levelReq ? aa.ranks : 0;
  }
  const store = scope === "class" ? (state.ranks.classes[className] || {}) : (state.ranks[scope] || {});
  const purchased = store[idx] || 0;
  if (aa && aa.autoRanks) {
    const levelReq = parseInt(aa.levelReq, 10) || 1;
    const freeRanks = classActive && state.charLevel >= levelReq ? Math.min(aa.autoRanks, aa.ranks) : 0;
    return Math.max(freeRanks, purchased);
  }
  return purchased;
}

// The static, level-independent count of an autoRanks AA's free ranks -
// unlike autoFloor below, this ignores state.charLevel. Used to reconcile
// purchaseOrder counts against a held rank (how many ranks never went
// through purchaseOrder), which can diverge from "what's currently
// buyable" if charLevel changes after the free ranks were granted.
function autoRanksOffset(aa) {
  return aa && aa.autoRanks ? Math.min(aa.autoRanks, aa.ranks) : 0;
}

function getRanksStore(catKey) {
  const slot = classSlotIndex(catKey);
  if (slot >= 0) {
    const className = state.selectedClasses[slot];
    if (!state.ranks.classes[className]) state.ranks.classes[className] = {};
    return state.ranks.classes[className];
  }
  return state.ranks[catKey];
}

// Unlike getRanksStore, keyed by scope/className directly rather than a
// slot-relative catKey — owned status is about the AA's real identity, not
// which slot a class currently occupies (same reasoning purchaseOrder
// entries use; a slot key stops meaning the same class once slots are
// rearranged).
function getOwnedStore(scope, className) {
  if (scope === "class") {
    if (!state.owned.classes[className]) state.owned.classes[className] = {};
    return state.owned.classes[className];
  }
  return state.owned[scope];
}

function ownedRank(scope, className, idx) {
  return getOwnedStore(scope, className)[idx] || 0;
}

// Pure state mutation, same spirit as changeRank/moveEntry: sets the owned
// watermark for one AA and records enough to undo it. Unlike changeRank,
// doesn't clamp against the AA's rank count — the caller (Progression's
// toggle) is responsible for passing a sane value.
export function setOwnedRank(scope, className, idx, rank) {
  const store = getOwnedStore(scope, className);
  const from = store[idx] || 0;
  if (rank <= 0) delete store[idx]; else store[idx] = rank;
  lastMutation = { type: "own", scope, className, idx, from, to: rank };
  // Owned persists to its own storage key (state.js), not the build
  // payload saveLocal writes — nothing here touches ranks/purchaseOrder.
  saveOwned();
}

// Same scope/className identity-keying as getOwnedStore, for the same
// reason - hiding is about the AA's real identity, not which of the 3 slots
// a class currently occupies.
function getHiddenStore(scope, className) {
  if (scope === "class") {
    if (!state.hiddenAAs.classes[className]) state.hiddenAAs.classes[className] = {};
    return state.hiddenAAs.classes[className];
  }
  return state.hiddenAAs[scope];
}

// Scope/className form, for callers (Browse) that need to check an AA
// outside the 3 active class slots, where categoryToScopeClassName would
// return null - same split as costGuess/costGuessScoped.
export function isHiddenScoped(scope, className, idx) {
  return !!getHiddenStore(scope, className)[idx];
}

export function isHidden(catKey, idx) {
  const { scope, className } = categoryToScopeClassName(catKey);
  return isHiddenScoped(scope, className, idx);
}

export function setHiddenScoped(scope, className, idx, hidden) {
  const store = getHiddenStore(scope, className);
  if (hidden) store[idx] = true; else delete store[idx];
  // Display preference, not build state - its own storage key (state.js),
  // never lastMutation/saveLocal, so hiding something is never part of
  // Undo Last and never marks the build itself as changed.
  saveHidden();
}

export function setHidden(catKey, idx, hidden) {
  const { scope, className } = categoryToScopeClassName(catKey);
  setHiddenScoped(scope, className, idx, hidden);
}

// Whether state.hiddenAAs holds anything at all, across every scope/class —
// hides the "Show Hidden" toggle entirely when there's nothing to reveal.
export function hasAnyHidden() {
  const h = state.hiddenAAs;
  if (Object.keys(h.general).length || Object.keys(h.archetype).length || Object.keys(h.special).length) return true;
  return Object.keys(h.classes).some((className) => Object.keys(h.classes[className]).length > 0);
}

// Whether state.owned holds anything at all, across every scope/class —
// owned is global, not scoped to the current 3 slots. Disables the
// standalone "Clear Owned" control when there's nothing to do.
export function hasAnyOwned() {
  const o = state.owned;
  if (Object.keys(o.general).length || Object.keys(o.archetype).length || Object.keys(o.special).length) return true;
  return Object.keys(o.classes).some((className) => Object.keys(o.classes[className]).length > 0);
}

// Wipes owned entirely — the standalone counterpart to performReset's
// clearOwnedToo option, for clearing real-world progress without touching
// the plan. Not undoable (the single-level undo only records one AA's
// watermark at a time); the confirm before calling this is the safety net.
export function clearAllOwned() {
  state.owned = { general: {}, archetype: {}, special: {}, classes: {} };
  lastMutation = null;
  saveOwned();
}

// Sets (or replaces, if one exists at this exact total) a named point-total
// marker. Plan annotation, not a plan mutation — deliberately doesn't touch
// lastMutation, so it never clobbers (or is clobbered by) a pending Undo
// Last. Returns false without changing anything if pts isn't a valid
// non-negative number.
export function addOrUpdateWaypoint(pts, label, color) {
  const n = parseInt(pts, 10);
  if (!Number.isFinite(n) || n < 0) return false;
  // sanitizeWaypoints does the actual clamping/label-cleaning/color-
  // validating/sorting/dedup (last entry for a given pts wins), so re-run
  // the merged array through it rather than duplicating that logic here.
  const merged = state.waypoints.filter((w) => w.pts !== n);
  merged.push({ pts: n, label, color });
  state.waypoints = sanitizeWaypoints(merged);
  saveLocal();
  return true;
}

export function removeWaypoint(pts) {
  state.waypoints = state.waypoints.filter((w) => w.pts !== pts);
  saveLocal();
}

// Purchase-order entries key AA picks by class NAME (not slot position), since class
// names are already unique and stable — swapping which slot a class occupies shouldn't
// orphan its place in the progression list.
function scopeForCategory(category) {
  const slot = classSlotIndex(category);
  return slot >= 0 ? "class" : category;
}

function classNameForCategory(category) {
  const slot = classSlotIndex(category);
  return slot >= 0 ? state.selectedClasses[slot] : null;
}

function categoryToScopeClassName(category) {
  const slot = classSlotIndex(category);
  return slot >= 0 ? { scope: "class", className: state.selectedClasses[slot] } : { scope: category, className: null };
}

// A pattern-inferred cost estimate for rank rankIdx of the AA at
// (catKey, idx), or null. Only meaningful when the AA's real
// costs[rankIdx] is "?" — callers check that themselves. Purely a display
// hint: nothing here or upstream ever substitutes a guess into
// costNum()/spentPoints().
export function costGuess(catKey, idx, rankIdx) {
  const { scope, className } = categoryToScopeClassName(catKey);
  return costGuessFor(scope, className, idx, rankIdx);
}

// Same lookup as costGuess, but by (scope, className) directly rather than
// one of the 3 active class slots — for callers like Browse that show every
// class regardless of whether it's currently selected, where categoryToScopeClassName
// would return null for a class sitting outside the active 3.
export function costGuessScoped(scope, className, idx, rankIdx) {
  return costGuessFor(scope, className, idx, rankIdx);
}

// Same shape as costGuess/costGuessScoped, one axis deeper for progIdx (a
// description can hold more than one independent progression - see
// effectGuesses.js's own header). Only ever meaningful to call when the
// real slot at that position is "?", same contract as costGuess.
export function effectGuess(catKey, idx, progIdx, rankIdx) {
  const { scope, className } = categoryToScopeClassName(catKey);
  return effectGuessFor(scope, className, idx, progIdx, rankIdx);
}

export function effectGuessScoped(scope, className, idx, progIdx, rankIdx) {
  return effectGuessFor(scope, className, idx, progIdx, rankIdx);
}

function entryKey(scope, className, idx) {
  return `${scope}|${className || ""}|${idx}`;
}

// Which category key currently displays this entry's class, or null if that class
// isn't in any of the 3 active slots right now.
function resolveEntryCategory(entry) {
  if (entry.scope !== "class") return entry.scope;
  const slot = state.selectedClasses.indexOf(entry.className);
  return slot >= 0 ? CLASS_SLOT_KEYS[slot] : null;
}

// Whether a purchaseOrder entry belongs to one of the 3 currently active
// classes (general/archetype/special always are) - exported for
// render.js's up/down arrow reordering, which needs to skip over an
// inactive entry sitting between two visible rows rather than swap with it
// and produce no visible change at all.
export function isEntryActive(entry) {
  return resolveEntryCategory(entry) !== null;
}

function pushPurchase(category, idx) {
  state.purchaseOrder.push({ scope: scopeForCategory(category), className: classNameForCategory(category), idx });
}

// Returns the removed entry and the array position it was removed from (needed to
// restore it to the same spot later), or null if no matching entry was found.
function popLastPurchase(category, idx) {
  const scope = scopeForCategory(category);
  const className = classNameForCategory(category);
  for (let i = state.purchaseOrder.length - 1; i >= 0; i--) {
    const e = state.purchaseOrder[i];
    if (e.scope === scope && e.idx === idx && (e.className || null) === (className || null)) {
      const [entry] = state.purchaseOrder.splice(i, 1);
      return { entry, position: i };
    }
  }
  return null;
}

// Reset Build, but selective: wipes every planned pick down to its owned
// watermark instead of to zero, unless clearOwnedToo also wipes owned.
// Auto-granted AAs need no handling here — they never get a
// ranks/purchaseOrder entry in the first place.
export function performReset(clearOwnedToo) {
  // Trims each planned rank down to min(owned, planned), never up. Owned
  // can legitimately exceed the plan (e.g. refund below an already-trained
  // rank), so capping against owned rather than the AA's max rank stops
  // Reset from re-inflating a plan the user deliberately lowered. An AA
  // with no ranks entry (owned but not planned) is never visited, so
  // Reset never adds a pick that wasn't already part of the plan.
  //
  // A kept rank at or below the AA's free autoRanks floor is dropped
  // entirely rather than stored at that value, matching changeRank's own
  // convention that a ranks-store entry only exists for ranks purchased
  // beyond the free floor — reconcilePurchaseOrderCounts assumes the same.
  function trimmedRanks(ranksStore, ownedStore, list) {
    const kept = {};
    Object.keys(ranksStore).forEach((idxStr) => {
      const idx = parseInt(idxStr, 10);
      const aa = list[idx];
      if (!aa) return;
      const planned = ranksStore[idx] || 0;
      const owned = clearOwnedToo ? 0 : Math.min(ownedStore[idx] || 0, planned);
      if (owned > autoRanksOffset(aa)) kept[idx] = owned;
    });
    return kept;
  }

  const newRanks = { general: {}, archetype: {}, special: {}, classes: {} };
  ["general", "archetype", "special"].forEach((scope) => {
    newRanks[scope] = trimmedRanks(state.ranks[scope] || {}, state.owned[scope] || {}, AA_DATA[scope] || []);
  });
  Object.keys(state.ranks.classes || {}).forEach((className) => {
    const kept = trimmedRanks(
      state.ranks.classes[className] || {},
      (state.owned.classes || {})[className] || {},
      AA_DATA.classes[className] || []
    );
    if (Object.keys(kept).length) newRanks.classes[className] = kept;
  });

  // Rebuild purchaseOrder to match: keep only the first N entries per AA
  // (N = the kept rank minus its free autoRanks floor, same accounting
  // reconcilePurchaseOrderCounts uses), in original relative order — so the
  // owned portion's purchase history survives intact instead of being
  // wiped and re-synthesized in arbitrary order.
  const remaining = {};
  ["general", "archetype", "special"].forEach((scope) => {
    const list = AA_DATA[scope] || [];
    Object.keys(newRanks[scope]).forEach((idxStr) => {
      const idx = parseInt(idxStr, 10);
      remaining[entryKey(scope, null, idxStr)] = newRanks[scope][idxStr] - autoRanksOffset(list[idx]);
    });
  });
  Object.keys(newRanks.classes).forEach((className) => {
    const list = AA_DATA.classes[className] || [];
    Object.keys(newRanks.classes[className]).forEach((idxStr) => {
      const idx = parseInt(idxStr, 10);
      remaining[entryKey("class", className, idxStr)] = newRanks.classes[className][idxStr] - autoRanksOffset(list[idx]);
    });
  });
  const newPurchaseOrder = [];
  state.purchaseOrder.forEach((e) => {
    const k = entryKey(e.scope, e.className, e.idx);
    if (remaining[k] > 0) {
      newPurchaseOrder.push(e);
      remaining[k]--;
    }
  });

  state.ranks = newRanks;
  state.purchaseOrder = newPurchaseOrder;
  if (clearOwnedToo) state.owned = { general: {}, archetype: {}, special: {}, classes: {} };
  state.selectedNode = null;
  lastMutation = null;
  // Belt-and-suspenders: the trimming above should already leave
  // ranks/purchaseOrder in sync, but this is cheap enough to just always run.
  reconcilePurchaseOrderCounts();
  saveLocal();
  // Only clearOwnedToo actually mutates state.owned - saveOwned runs
  // unconditionally anyway, rather than adding a branch that could drift.
  saveOwned();
}

// Shared by spentPoints/spentForClass: walks one (list, store) pair -
// general/archetype/special, or one class's ranks, active or not - summing
// every non-auto AA's real cost up to its held rank.
function sumRealCost(list, store) {
  let total = 0;
  list.forEach((aa, idx) => {
    if (aa.auto) return; // automatically granted, doesn't draw from the point pool
    const r = store[idx] || 0;
    for (let i = 0; i < r; i++) total += costNum(aa.costs[i]);
  });
  return total;
}

// A genuine lifetime total: every point ever spent, across every class
// you've ever picked, not just the 3 active slots. Walks
// Object.keys(state.ranks.classes) directly rather than AA_CATEGORY_KEYS/
// getList, since a class swap no longer wipes an inactive class's ranks.
// Progression's own running total deliberately stays active-only (see
// computeProgressionSteps' stepCost) — the two numbers are allowed to
// diverge; renderTopbar's tooltip surfaces the split.
export function spentPoints() {
  let total = sumRealCost(AA_DATA.general, state.ranks.general)
    + sumRealCost(AA_DATA.archetype, state.ranks.archetype)
    + sumRealCost(AA_DATA.special, state.ranks.special);
  Object.keys(state.ranks.classes).forEach((className) => {
    total += sumRealCost(AA_DATA.classes[className] || [], state.ranks.classes[className]);
  });
  return total;
}

// Real points spent on one specific class alone, active or not — the
// Other Classes tab's per-class subtotal. Sums the one class directly
// with sumRealCost rather than deriving it from spentPoints().
export function spentForClass(className) {
  return sumRealCost(AA_DATA.classes[className] || [], state.ranks.classes[className] || {});
}

// Sum of spentForClass across every class NOT currently active — the
// slice of spentPoints()'s lifetime total that lives "elsewhere" right
// now. Surfaced in the topbar tooltip and Progression's toolbar note so
// the gap vs. Progression's active-only total is legible, not silent.
export function spentOnInactiveClasses() {
  return Object.keys(state.ranks.classes)
    .filter((className) => !state.selectedClasses.includes(className))
    .reduce((sum, className) => sum + spentForClass(className), 0);
}

// Lifetime total of points marked owned, across every class ever picked —
// mirrors spentPoints()'s own lifetime scope. Progression's "owned / to
// go" split is spentPoints() minus this; both sides need the same scope
// or an AA owned on a swapped-away class would inflate "still to go"
// despite already being trained.
export function ownedPoints() {
  let total = sumRealCost(AA_DATA.general, state.owned.general)
    + sumRealCost(AA_DATA.archetype, state.owned.archetype)
    + sumRealCost(AA_DATA.special, state.owned.special);
  Object.keys(state.owned.classes).forEach((className) => {
    total += sumRealCost(AA_DATA.classes[className] || [], state.owned.classes[className]);
  });
  return total;
}

// Shared by estimatedExtraPoints, same reasoning as sumRealCost above:
// scope/className identify the AA (needed for costGuessScoped's lookup),
// list/store are what's actually being walked.
function sumEstimatedExtra(scope, className, list, store) {
  let extra = 0;
  list.forEach((aa, idx) => {
    if (aa.auto) return;
    const r = store[idx] || 0;
    for (let i = 0; i < r; i++) {
      if (aa.costs[i] !== "?") continue;
      const guess = costGuessScoped(scope, className, idx, i);
      if (guess) extra += guess.value;
    }
  });
  return extra;
}

// How much higher spentPoints() would probably be if every purchased rank
// with an unconfirmed cost ("?") cost what its pattern-inferred guess
// says, instead of the 0 costNum() gives it. Purely informational — never
// added into spentPoints(), never used for an afford check, never
// persisted; the topbar shows it as a separate "~N incl. estimates" note.
// Same lifetime-total scope as spentPoints() (every class ever picked).
export function estimatedExtraPoints() {
  let extra = sumEstimatedExtra("general", null, AA_DATA.general, state.ranks.general)
    + sumEstimatedExtra("archetype", null, AA_DATA.archetype, state.ranks.archetype)
    + sumEstimatedExtra("special", null, AA_DATA.special, state.ranks.special);
  Object.keys(state.ranks.classes).forEach((className) => {
    extra += sumEstimatedExtra("class", className, AA_DATA.classes[className] || [], state.ranks.classes[className]);
  });
  return extra;
}

// Plain "Requires X rank N" gates the whole ability behind a fixed target rank.
// "Requires X rank 1/2/3" (matching the wiki's own phrasing for rank-synced
// prereqs, e.g. Destructive Cascade needing the matching Critical Affliction
// rank) instead requires source rank K to be gated on target rank K.
function parsePrereqText(text) {
  if (!text) return null;
  const m = text.match(/^Requires\s+(.+?)\s+(?:rank|(?:at\s+)?level)\s+(\d+(?:\/\d+)*)\s*$/i);
  if (!m) return null;
  const ranks = m[2].split("/").map((n) => parseInt(n, 10));
  return ranks.length > 1
    ? { name: m[1].trim(), synced: true, ranks }
    : { name: m[1].trim(), synced: false, rank: ranks[0] };
}

export function resolvePrereqTarget(text, sourceCategory) {
  const parsed = parsePrereqText(text);
  if (!parsed) return null;
  // Only the source's own category plus the shared trees — a class AA's
  // prereq should never resolve against whichever *other* class happens
  // to occupy another slot right now. Widening this would make resolution
  // depend on which classes are currently selected, not just the AA.
  const order = [];
  const seen = new Set();
  [sourceCategory, "general", "archetype", "special"].forEach((k) => {
    if (!seen.has(k)) { seen.add(k); order.push(k); }
  });
  for (const key of order) {
    const list = getList(key);
    let foundIdx = -1;
    list.forEach((aa, i) => {
      if (aa.name.toLowerCase() !== parsed.name.toLowerCase()) return;
      if (foundIdx < 0) { foundIdx = i; return; }
      // Duplicate name in this category (e.g. Cleric's two "Divine Aura"
      // rows) — prefer whichever costs points over an auto-granted one,
      // since gating behind a free ability isn't a meaningful prereq.
      // Otherwise keep the first match, so resolution doesn't flip if the
      // data gets reordered by a resync.
      if (list[foundIdx].auto && !aa.auto) foundIdx = i;
    });
    if (foundIdx >= 0) {
      return {
        category: key,
        idx: foundIdx,
        // Required target rank for the source AA to hold `sourceRank`. Fixed
        // prereqs ignore sourceRank; synced ones look up the matching entry
        // (clamped to the list, so a too-high/low sourceRank still resolves).
        forRank(sourceRank) {
          if (!parsed.synced) return parsed.rank;
          const i = Math.min(Math.max(sourceRank, 1), parsed.ranks.length) - 1;
          return parsed.ranks[i];
        }
      };
    }
  }
  return null;
}

// Resolves a prereq, distinguishing *why* it failed: malformed text (a bug
// in our own data.src.js, since we write every prereq string ourselves)
// vs. text that parses fine but names a target that no longer exists
// (renamed/removed by a resync). Both must block, but callers want
// different wording — one says "fix the data", the other "the data changed."
function tryResolvePrereq(text, sourceCategory) {
  const parsed = parsePrereqText(text);
  if (!parsed) return { ok: false, malformed: true };
  const resolved = resolvePrereqTarget(text, sourceCategory);
  if (!resolved) return { ok: false, malformed: false, name: parsed.name };
  return { ok: true, resolved };
}

function unresolvedPrereqMessage(text, attempt) {
  return attempt.malformed
    ? `Prerequisite text "${text}" isn't in a recognized format — this needs fixing in the data, not the wiki.`
    : `Requires "${attempt.name}", which no longer resolves to an existing ability.`;
}

// Some AAs (Steadfast Will is the one live example) cap their max reachable
// rank based on which of the 3 selected classes you have, rather than a
// flat per-AA maximum — data.src.js's classRankCap: { default, byClass:
// { Name: cap, ... } }. Tri-class COMBINES rather than switches, so ANY of
// the 3 selected classes granting a higher cap applies. Absent
// classRankCap, an AA's only cap is its own aa.ranks, as always.
//
// Evaluates against state.selectedClasses — correct for Steadfast Will (a
// general AA, always in-context) but not meaningful for a hypothetical
// class-specific classRankCap AA shown in the Other Classes tab, which
// would evaluate against the wrong classes. Not a live bug today; flagged
// for whoever adds the first one.
export function classRankCapFor(aa) {
  if (!aa.classRankCap) return aa.ranks;
  const { default: def, byClass } = aa.classRankCap;
  let cap = def;
  state.selectedClasses.forEach((c) => {
    if (byClass[c] !== undefined && byClass[c] > cap) cap = byClass[c];
  });
  return cap;
}

// The rank whose description slot should read as "your current effect" —
// usually the held rank, but a class-capped AA held beyond today's cap
// (Steadfast Will at rank 8 with no qualifying class) only actually grants
// the capped rank's effect in-game. The held rank itself stays untouched
// (still shown as "8/8"); only which slot gets highlighted changes.
export function effectiveDisplayRank(aa, rank) {
  return aa.classRankCap ? Math.min(rank, classRankCapFor(aa)) : rank;
}

// Returns { kind: "level" | "classCap" | "prereq", text } rather than a bare string so callers
// that render (not just report) a lock reason can tell a level-gate apart from a class-cap gate
// apart from a prerequisite-gate - each needs different treatment in the tree, since "level too
// low" is self-evidently solved by playing, "capped for your classes" needs a specific class
// swap, and "needs another AA" requires the user to notice and go buy something specific
// elsewhere.
export function structuralLockReason(catKey, idx) {
  const aa = getList(catKey)[idx];
  const levelReq = parseInt(aa.levelReq, 10) || 1;
  if (state.charLevel < levelReq) return { kind: "level", text: `Requires character level ${levelReq}.` };
  if (aa.classRankCap) {
    const cap = classRankCapFor(aa);
    const nextRank = effectiveRank(catKey, idx) + 1;
    if (nextRank > cap) return { kind: "classCap", text: `Capped at rank ${cap} for your currently selected classes.` };
  }
  if (aa.prereq) {
    const attempt = tryResolvePrereq(aa.prereq, catKey);
    if (!attempt.ok) return { kind: "prereq", text: unresolvedPrereqMessage(aa.prereq, attempt) };
    const resolved = attempt.resolved;
    const sourceRank = effectiveRank(catKey, idx) + 1; // the rank about to be purchased
    const requiredRank = resolved.forRank(sourceRank);
    const targetRank = effectiveRank(resolved.category, resolved.idx);
    if (targetRank < requiredRank) {
      const targetAA = getList(resolved.category)[resolved.idx];
      return { kind: "prereq", text: `Requires ${targetAA ? targetAA.name : "prerequisite"} rank ${requiredRank}.` };
    }
  }
  return null;
}

// Whether a rank the user already holds still satisfies its prerequisite
// or class-rank-cap under today's AA_DATA + current class selection.
// Unlike structuralLockReason (checks whether the NEXT rank is
// purchasable), this checks every rank already held, catching drift from a
// changed prereq target or class selection. Purely a function of current
// state + data, so it clears itself once the gap closes — never strips
// the held rank itself.
export function heldRankInvalidReason(catKey, idx) {
  const aa = getList(catKey)[idx];
  if (!aa || aa.auto) return null;
  const purchased = getRanksStore(catKey)[idx] || 0;
  if (purchased <= 0) return null;
  if (aa.classRankCap) {
    // Assumes classRankCap never coexists with autoRanks — true of every
    // AA today. `purchased` excludes an autoRanks AA's free floor, so this
    // would undercount if that combination ever showed up; flagged for
    // whoever adds the first one.
    const cap = classRankCapFor(aa);
    if (purchased > cap) return `exceeds the rank ${cap} cap for your currently selected classes.`;
  }
  if (!aa.prereq) return null;
  const attempt = tryResolvePrereq(aa.prereq, catKey);
  if (!attempt.ok) return unresolvedPrereqMessage(aa.prereq, attempt);
  const resolved = attempt.resolved;
  const targetRank = effectiveRank(resolved.category, resolved.idx);
  for (let r = 1; r <= purchased; r++) {
    const required = resolved.forRank(r);
    if (targetRank < required) {
      const targetAA = getList(resolved.category)[resolved.idx];
      return `Rank ${r} requires ${targetAA ? targetAA.name : "a prerequisite"} rank ${required}, which you no longer have.`;
    }
  }
  return null;
}

// Every currently-held pick that fails heldRankInvalidReason, across all
// categories — for a one-time notice on load.
export function findInvalidatedPicks() {
  const results = [];
  AA_CATEGORY_KEYS.forEach((catKey) => {
    getList(catKey).forEach((aa, idx) => {
      const reason = heldRankInvalidReason(catKey, idx);
      if (reason) results.push({ category: catKey, idx, name: aa.name, reason });
    });
  });
  return results;
}

// For every AA the user holds a rank in, purchaseOrder should contain
// exactly (held rank - any free autoRanks floor) entries for it, and none
// for an AA that isn't held at all. computeProgressionSteps walks
// purchaseOrder directly without consulting effectiveRank, so a mismatch
// renders wrong either way: too few/many entries show the wrong rank
// number, and an orphan entry renders as a fabricated step with its cost
// added to the running total. Reachable from a crafted ?build= link, same
// threat model clampRankValue exists for.
//
// Repairs by adding/removing entries until each count matches (at the
// end, so earlier purchases keep their order) and dropping orphans.
// state.ranks itself is never touched — only a step's displayed rank and
// position can change.
export function reconcilePurchaseOrderCounts() {
  function countFor(scope, className, idx) {
    let n = 0;
    for (const e of state.purchaseOrder) {
      if (e.scope === scope && (e.className || null) === (className || null) && e.idx === idx) n++;
    }
    return n;
  }
  function expectedFor(aa, held) {
    return Math.max(0, held - autoRanksOffset(aa));
  }
  function key(scope, className, idx) {
    return `${scope}|${className || ""}|${idx}`;
  }

  // aa.auto entries are excluded from targets: nothing ever legitimately
  // writes a purchaseOrder entry for one, so they fall into the "not
  // held" case below rather than getting a count to satisfy.
  const targets = [];
  const targetKeys = new Set();
  ["general", "archetype", "special"].forEach((scope) => {
    const list = AA_DATA[scope] || [];
    Object.keys(state.ranks[scope] || {}).forEach((idxStr) => {
      const idx = parseInt(idxStr, 10);
      const aa = list[idx];
      if (aa && !aa.auto) {
        targets.push({ scope, className: null, idx, aa, held: state.ranks[scope][idxStr] });
        targetKeys.add(key(scope, null, idx));
      }
    });
  });
  Object.keys(state.ranks.classes || {}).forEach((className) => {
    const list = AA_DATA.classes[className] || [];
    Object.keys(state.ranks.classes[className] || {}).forEach((idxStr) => {
      const idx = parseInt(idxStr, 10);
      const aa = list[idx];
      if (aa && !aa.auto) {
        targets.push({ scope: "class", className, idx, aa, held: state.ranks.classes[className][idxStr] });
        targetKeys.add(key("class", className, idx));
      }
    });
  });

  let repaired = 0;

  const orphanKeys = new Set();
  state.purchaseOrder.forEach((e) => {
    const k = key(e.scope, e.className || null, e.idx);
    if (!targetKeys.has(k)) orphanKeys.add(k);
  });
  if (orphanKeys.size) {
    state.purchaseOrder = state.purchaseOrder.filter((e) => targetKeys.has(key(e.scope, e.className || null, e.idx)));
    repaired += orphanKeys.size;
  }

  targets.forEach(({ scope, className, idx, aa, held }) => {
    const expected = expectedFor(aa, held);
    const actual = countFor(scope, className, idx);
    if (expected === actual) return;
    repaired++;
    if (actual > expected) {
      let toRemove = actual - expected;
      for (let i = state.purchaseOrder.length - 1; i >= 0 && toRemove > 0; i--) {
        const e = state.purchaseOrder[i];
        if (e.scope === scope && (e.className || null) === (className || null) && e.idx === idx) {
          state.purchaseOrder.splice(i, 1);
          toRemove--;
        }
      }
    } else {
      for (let i = 0; i < expected - actual; i++) {
        state.purchaseOrder.push({ scope, className, idx });
      }
    }
  });
  return repaired;
}

// Builds a " (...)" suffix summarizing anything applyLoaded dropped and/or
// reconcilePurchaseOrderCounts repaired — "" if neither applies. Shared
// wording for the single-action load paths (share link, text import,
// loading a build slot); main.js's startup path assembles its own
// multi-item notice instead. Lives here (not exportImport.js) so builds.js
// can use it too without the two importing each other.
export function loadIssuesSuffix(result, repaired) {
  const parts = [];
  if (result.droppedRanks) {
    const n = result.droppedRanks;
    parts.push(`${n} pick${n === 1 ? "" : "s"} no longer exist${n === 1 ? "s" : ""} in the current data and ${n === 1 ? "was" : "were"} skipped`);
  }
  if (repaired) {
    parts.push(`${repaired} pick${repaired === 1 ? "'s" : "s'"} purchase history was out of sync and ${repaired === 1 ? "was" : "were"} repaired`);
  }
  return parts.length ? ` (${parts.join("; ")})` : "";
}

// Full reason a rank can't be purchased right now (prereqs, level gates,
// structural locks). No points-remaining check here - there's no total
// point pool to run out of; the app tracks and displays spent points only.
export function getBlockReason(catKey, idx) {
  const structural = structuralLockReason(catKey, idx);
  return structural ? structural.text : null;
}

export function isDependedOn(category, idx, currentRank) {
  const newRank = currentRank - 1;
  for (const catKey of AA_CATEGORY_KEYS) {
    const list = getList(catKey);
    for (let i = 0; i < list.length; i++) {
      const aa = list[i];
      if (!aa.prereq) continue;
      const aaRank = effectiveRank(catKey, i);
      if (aaRank <= 0) continue;
      const r = resolvePrereqTarget(aa.prereq, catKey);
      if (r && r.category === category && r.idx === idx && newRank < r.forRank(aaRank)) return true;
    }
  }
  return false;
}

// Single-level undo: remembers only the most recent changeRank, moveEntry,
// or setOwnedRank call, in enough detail to reverse it exactly. Overwritten
// by every subsequent call, including the reversal itself, so undoing
// twice toggles between the two most recent states rather than walking
// back further. Explicitly cleared by anything that mutates
// ranks/purchaseOrder/owned without going through one of the three.
let lastMutation = null;

export function clearLastMutation() {
  lastMutation = null;
}

export function canUndo() {
  return !!lastMutation;
}

// Pure state mutation, same spirit as changeRank: moves the entry at
// fromIdx to array position toIdx (both real positions, already resolved —
// render.js's callers translate drag/arrow intent into these first).
// Reversing it is just calling it again with the positions swapped, which
// is how undoLastMutation's "reorder" case restores the original order.
export function moveEntry(fromIdx, toIdx) {
  const [entry] = state.purchaseOrder.splice(fromIdx, 1);
  state.purchaseOrder.splice(toIdx, 0, entry);
  lastMutation = { type: "reorder", from: fromIdx, to: toIdx };
  saveLocal();
}

// The level-gated floor for an autoRanks AA: the free ranks once the
// character reaches the level that grants them, 0 below that. Shared by
// changeRank (what a refund can't go below) and attemptDecrement (the
// UI-facing gate in front of it), so the two can't drift apart.
function autoFloor(aa) {
  if (!aa.autoRanks) return 0;
  const levelReq = parseInt(aa.levelReq, 10) || 1;
  return state.charLevel >= levelReq ? Math.min(aa.autoRanks, aa.ranks) : 0;
}

// Pure state mutation — no rendering, no user feedback. Returns whether a change
// actually happened, so callers (the UI layer) decide what to do about it.
export function changeRank(category, idx, delta) {
  const store = getRanksStore(category);
  const aa = getList(category)[idx];
  // For an autoRanks AA, the free ranks are a floor you can never buy below (they're
  // not "purchased" at all) — step from the current effective rank, not the raw stored
  // one. See autoFloor for why the floor itself is level-gated.
  const floor = autoFloor(aa);
  const cur = aa.autoRanks ? effectiveRank(category, idx) : (store[idx] || 0);
  const next = cur + delta;
  if (next < floor || next > aa.ranks) return false;
  // At or below the floor, nothing counts as an actual purchase (floor===0
  // already worked this way at next===0). Without this, refunding an
  // autoRanks AA back to its floor left a phantom store entry forever.
  if (next <= floor) delete store[idx]; else store[idx] = next;
  if (delta > 0) {
    pushPurchase(category, idx);
    // Stored as {scope, className, idx}, not the raw category (slot key) -
    // a slot key means "whatever class occupies this slot now", which
    // stops meaning the class that was here at purchase time once slots
    // get swapped. resolveEntryCategory re-resolves via className instead.
    const { scope, className } = categoryToScopeClassName(category);
    lastMutation = { type: "add", entry: { scope, className, idx } };
  } else {
    const popped = popLastPurchase(category, idx);
    lastMutation = popped ? { type: "remove", entry: popped.entry, position: popped.position } : null;
  }
  saveLocal();
  return true;
}

// Reverses whatever changeRank, moveEntry, or setOwnedRank last did. Consumes
// the record either way, so pressing this twice in a row toggles between the
// last two states rather than walking back further - see the lastMutation
// comment.
export function undoLastMutation() {
  const m = lastMutation;
  if (!m) return { changed: false, message: "Nothing to undo." };
  lastMutation = null;

  if (m.type === "add") {
    const category = resolveEntryCategory(m.entry);
    if (!category) return { changed: false, message: "Can't undo — that class isn't currently selected." };
    const rank = effectiveRank(category, m.entry.idx);
    if (rank <= 0) return { changed: false, message: "Nothing to undo." };
    if (isDependedOn(category, m.entry.idx, rank)) {
      return { changed: false, message: "Can't undo — another AA now depends on this rank." };
    }
    return { changed: changeRank(category, m.entry.idx, -1), message: null };
  }

  if (m.type === "reorder") {
    // The array may have changed shape since (an add/remove would have overwritten
    // this record via changeRank, but check anyway rather than trust it blindly).
    if (m.from < 0 || m.from >= state.purchaseOrder.length || m.to < 0 || m.to >= state.purchaseOrder.length) {
      return { changed: false, message: "Can't undo — the list has changed too much." };
    }
    moveEntry(m.to, m.from);
    return { changed: true, message: null };
  }

  if (m.type === "own") {
    // Unlike ranks, owned isn't slot-relative (see getOwnedStore) - no class-
    // selection check needed, this always resolves regardless of what's
    // currently in the 3 slots.
    setOwnedRank(m.scope, m.className, m.idx, m.from);
    return { changed: true, message: null };
  }

  // m.type === "remove": restore the entry to its original array position and
  // bump that AA's rank back up by one.
  const category = resolveEntryCategory(m.entry);
  if (!category) return { changed: false, message: "Can't undo — that class isn't currently selected." };
  const aa = getList(category)[m.entry.idx];
  if (!aa) return { changed: false, message: "Can't undo — that AA is no longer available." };
  const store = getRanksStore(category);
  const cur = store[m.entry.idx] || 0;
  if (cur >= aa.ranks) return { changed: false, message: "Can't undo — already at max rank." };
  store[m.entry.idx] = cur + 1;
  const pos = Math.min(m.position, state.purchaseOrder.length);
  state.purchaseOrder.splice(pos, 0, m.entry);
  saveLocal();
  return { changed: true, message: null };
}

// attemptIncrement/attemptDecrement report the outcome instead of triggering a
// render or toast themselves, so this module has no dependency on the render layer —
// dependencies only flow one way: render.js depends on logic.js, never the reverse.
export function attemptIncrement(category, idx) {
  const aa = getList(category)[idx];
  if (aa.auto) return { changed: false, message: `${aa.name} is automatically granted — no points needed.` };
  const rank = effectiveRank(category, idx);
  if (rank >= aa.ranks) return { changed: false, message: null };
  const reason = getBlockReason(category, idx);
  if (reason) return { changed: false, message: reason };
  return { changed: changeRank(category, idx, 1), message: null };
}

export function attemptDecrement(category, idx) {
  const aa = getList(category)[idx];
  if (aa.auto) return { changed: false, message: `${aa.name} is automatically granted and can't be removed.` };
  const rank = effectiveRank(category, idx);
  if (rank <= 0) return { changed: false, message: null };
  if (aa.autoRanks && rank <= autoFloor(aa)) {
    const plural = aa.autoRanks === 1 ? "rank is" : "ranks are";
    return { changed: false, message: `${aa.name}'s first ${aa.autoRanks} ${plural} automatically granted and can't be removed.` };
  }
  if (isDependedOn(category, idx, rank)) {
    return { changed: false, message: "Can't lower this — another AA depends on the current rank." };
  }
  return { changed: changeRank(category, idx, -1), message: null };
}

export function countPicked() {
  let n = 0;
  AA_CATEGORY_KEYS.forEach((catKey) => {
    getList(catKey).forEach((aa, idx) => { if (effectiveRank(catKey, idx) > 0) n++; });
  });
  return n;
}

// Same shape as countPicked, for the Other Classes tab's own badge - only
// classes NOT one of the 3 active slots, since countPicked/Summary already
// cover those.
export function countOtherClassesPicked() {
  let n = 0;
  Object.keys(state.ranks.classes).forEach((className) => {
    if (state.selectedClasses.includes(className)) return;
    const list = AA_DATA.classes[className] || [];
    list.forEach((aa, idx) => { if (effectiveRankScoped("class", className, idx) > 0) n++; });
  });
  return n;
}

// Every className outside the 3 active slots that currently has at least
// one picked (rank > 0) AA - the Other Classes tab's own section list,
// sorted for a stable render order (Object.keys' own order otherwise just
// reflects insertion history, which is meaningless here).
export function otherClassesWithPicks() {
  return Object.keys(state.ranks.classes)
    .filter((className) => !state.selectedClasses.includes(className))
    .filter((className) => {
      const list = AA_DATA.classes[className] || [];
      return list.some((aa, idx) => effectiveRankScoped("class", className, idx) > 0);
    })
    .sort();
}

// Shared by the Progression tab and the export text, so both always agree on
// step ranks, per-step cost, and the running cumulative total. Takes an
// explicit order (defaulting to the real state.purchaseOrder) so a caller can
// also ask "what would this look like" for a hypothetical arrangement -
// e.g. the drag-and-drop prereq indicator - without touching real state.
export function computeProgressionSteps(order = state.purchaseOrder) {
  // Total occurrences of each AA, so a step can tell whether it's the topmost
  // (and therefore the only one that can be removed without leaving a rank gap).
  const totalCounts = {};
  order.forEach((entry) => {
    const key = entryKey(entry.scope, entry.className, entry.idx);
    totalCounts[key] = (totalCounts[key] || 0) + 1;
  });

  const counts = {};
  let cumulative = 0;
  let blendedCumulative = 0;
  return order.map((entry, i) => {
    const key = entryKey(entry.scope, entry.className, entry.idx);
    const category = resolveEntryCategory(entry);
    const active = category !== null;
    const aa = entry.scope === "class" ? (AA_DATA.classes[entry.className] || [])[entry.idx] : (AA_DATA[entry.scope] || [])[entry.idx];
    // purchaseCount tracks how many times THIS purchase has been made (for isLast/
    // reordering bookkeeping); stepRank is the true effective rank it represents,
    // offset by any free autoRanks that never went through purchaseOrder at all.
    const purchaseCount = (counts[key] || 0) + 1;
    const autoOffset = autoRanksOffset(aa);
    const stepRank = purchaseCount + autoOffset;

    let prereqWarn = false;
    if (active && aa && aa.prereq) {
      const attempt = tryResolvePrereq(aa.prereq, category);
      if (!attempt.ok) {
        prereqWarn = true; // malformed or unresolvable - same "unmet" signal as elsewhere
      } else {
        const targetAA = getList(attempt.resolved.category)[attempt.resolved.idx];
        // A fully-auto target never goes through purchaseOrder, and an
        // autoRanks target's free floor doesn't either — counts[targetKey]
        // alone would under-count it, unlike effectiveRank elsewhere
        // (which folds the free floor in). Mirrors the source step's own
        // autoOffset rather than reusing effectiveRank directly, since
        // effectiveRank reports the CURRENT total rank, not how much had
        // been trained at this point in the sequence.
        const targetAutoFloor = targetAA && targetAA.auto ? targetAA.ranks
          : targetAA && targetAA.autoRanks ? Math.min(targetAA.autoRanks, targetAA.ranks)
          : 0;
        const t = categoryToScopeClassName(attempt.resolved.category);
        const targetKey = entryKey(t.scope, t.className, attempt.resolved.idx);
        const targetHeld = (counts[targetKey] || 0) + targetAutoFloor;
        if (targetHeld < attempt.resolved.forRank(stepRank)) prereqWarn = true;
      }
    }

    // Unlike prereqWarn, this never depends on click order — a step's own
    // stepRank against today's cap is all that matters, so reordering can
    // never introduce or clear it. Deliberately separate from prereqWarn:
    // the two conditions are unrelated (a step can be class-capped without
    // a prereq at all).
    const classCapWarn = active && aa && aa.classRankCap && stepRank > classRankCapFor(aa);

    counts[key] = purchaseCount;
    const isLast = purchaseCount === totalCounts[key];

    const stepCost = active && aa ? costNum(aa.costs[stepRank - 1]) : 0;
    cumulative += stepCost;

    // Running blend of the same kind estimatedExtraPoints() computes as
    // one final topbar figure, computed incrementally here so a per-row
    // running total doesn't stay frozen through a step whose own pill
    // shows a nonzero estimate. Same guarantee as every guess: never read
    // by spentPoints()/getBlockReason/any affordability check — purely
    // what .cost-total displays. Forced to 0 for an inactive step, same as
    // stepCost above.
    let blendedStepCost = stepCost;
    if (active && aa && aa.costs[stepRank - 1] === "?") {
      const guess = costGuess(category, entry.idx, stepRank - 1);
      if (guess) blendedStepCost = guess.value;
    }
    blendedCumulative += blendedStepCost;

    const label = entry.scope === "class" ? `${entry.className} AA` : labelFor(entry.scope);
    const name = aa ? aa.name : "(unknown AA)";
    // Real-world progress, independent of active/prereqWarn - you can own a
    // rank for a class that isn't in one of the 3 slots right now, same as
    // the rank itself can be held that way.
    const owned = stepRank <= ownedRank(entry.scope, entry.className, entry.idx);

    return {
      index: i, aa, idx: entry.idx, scope: entry.scope, className: entry.className,
      category, active, stepRank, stepCost, cumulative, blendedCumulative, prereqWarn, classCapWarn, label, name, isLast, owned
    };
  });
}

// Interleaves computeProgressionSteps' output with divider markers for
// each waypoint, in cumulative order: { type: "step", ...s, segmentColor }
// or { type: "divider", pts, label, color, unreached }. A divider for
// waypoint W goes right after the last step whose cumulative is <= W.pts
// (inclusive boundary). state.waypoints is already sorted ascending, so
// this is a single merge pass.
//
// segmentColor is the color of the smallest not-yet-flushed waypoint that
// still contains the step — null past every threshold or if that waypoint
// has no color. Lets every colored segment show at once, not just one
// selected zone.
//
// A waypoint whose pts is never reached gets flushed after the last step
// with unreached:true. That same tail flush also catches a waypoint whose
// pts exactly equals the final step's cumulative (nothing after it to
// trigger the in-loop flush) — compared against lastCumulative so an exact
// hit still reads as reached, not unreached.
//
// Cumulative treats an undocumented "?" cost as 0, so a boundary can land
// slightly off when unknowns are involved — same disclosure as everywhere
// else costs are shown.
export function computeProgressionTimeline(steps) {
  const wps = state.waypoints;
  const timeline = [];
  let wi = 0;
  let lastCumulative = 0;
  steps.forEach((s) => {
    while (wi < wps.length && wps[wi].pts < s.cumulative) {
      timeline.push({ type: "divider", pts: wps[wi].pts, label: wps[wi].label, color: wps[wi].color, unreached: false });
      wi++;
    }
    const owner = wi < wps.length ? wps[wi] : null;
    timeline.push({ type: "step", ...s, segmentColor: owner ? owner.color : null });
    lastCumulative = s.cumulative;
  });
  while (wi < wps.length) {
    timeline.push({ type: "divider", pts: wps[wi].pts, label: wps[wi].label, color: wps[wi].color, unreached: wps[wi].pts > lastCumulative });
    wi++;
  }
  return timeline;
}
