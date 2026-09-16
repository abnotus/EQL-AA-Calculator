// App-wide constants, the mutable state object, and localStorage persistence.
// Nothing here touches the DOM — that's render.js / dom.js.

import { keyForIdx, idxForKey, currentIdxForLegacyIdx, aaAt } from "./keys.js";

// A waypoint's point total is read from untrusted sources too (a pasted
// share link isn't something we generated), so it still gets an upper
// bound — generous enough that no real build ever approaches it, tight
// enough that a bogus value doesn't produce nonsense in the UI.
export const MAX_WAYPOINT_PTS = 100000;

// Bumped whenever the persisted shape changes. v4 introduced name-based keys
// for ranks/purchaseOrder (see keys.js) — anything below that is index-based
// against the frozen LEGACY_AA_ORDER snapshot and gets migrated on load.
export const SAVE_FORMAT_VERSION = 4;

export const STORAGE_KEY = "eql_aa_builder_v1";
// Owned status lives in its own key, deliberately separate from the build
// payload above - it's character-global real-world truth, not part of any
// one plan, so it must survive switching between builds/slots/share links
// untouched by any of that (see loadAndApplyOwned/saveOwned below).
export const OWNED_STORAGE_KEY = "eql_aa_owned_v1";
// Well-known profile id every pre-existing build/session is backfilled to
// (see migrateLegacyOwnedProfile/loadBuild in builds.js) - not a generated
// id, just a fixed name for "whatever OWNED_STORAGE_KEY already held".
// Lets every existing user's builds keep sharing owned progress exactly
// like before per-build tracking existed, with no migration bookkeeping
// beyond this one constant.
export const LEGACY_OWNED_PROFILE_ID = "legacy";

// Per-build "owned profile" storage - state.ownedProfileId says which one
// the current session is showing; each saved Build slot has its own
// ownedProfileId field pointing at one too (builds.js). Two builds
// pointing at the same profile id read/write the same key here, which is
// what "linked" owned tracking (see linkOwnedProfile) means concretely.
export function ownedStorageKeyFor(profileId) {
  return `eql_aa_owned_${profileId}`;
}

// Short, sufficiently-unique id for a new owned profile or build slot -
// timestamp plus a random suffix, not cryptographic, just collision-averse
// enough for this app's scale. Shared by builds.js for its own slot ids.
export function genId() {
  return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
}

// Bumped whenever the banner's content changes enough to be worth
// re-showing to someone who already dismissed the old wording - a flat
// "dismissed" flag has no notion of *which* text was dismissed, so a new
// key is the only way to force a re-acknowledgment.
export const DISCLAIMER_DISMISSED_KEY = "eql_aa_disclaimer_dismissed_v5";
// Which AAs are hidden from the tree/Browse decluttering views - a personal
// display preference, not build data, so it lives in its own key rather
// than the build payload or an exported/shared field: opening someone
// else's share link (or your own build on another browser) shows every AA,
// same reasoning OWNED_STORAGE_KEY already established for a different kind
// of "outside the plan" data. See isHidden/setHidden (logic.js).
export const HIDDEN_STORAGE_KEY = "eql_aa_hidden_v1";
// Every prior wording's dismiss flag, orphaned in storage forever the
// moment a rewording bumps DISCLAIMER_DISMISSED_KEY. Removed once on boot
// (see cleanupStaleStorageKeys). A flat list rather than derived from the
// version number - if a bump forgets to add an entry here, the cost is a
// few stray bytes, not a functional bug.
const STALE_DISCLAIMER_KEYS = [
  "eql_aa_disclaimer_dismissed",
  "eql_aa_disclaimer_dismissed_v2",
  "eql_aa_disclaimer_dismissed_v3",
  "eql_aa_disclaimer_dismissed_v4",
];

// Disclaimer-specific today (STALE_DISCLAIMER_KEYS is the only list swept
// here) - OWNED_STORAGE_KEY/HIDDEN_STORAGE_KEY are both still on their
// original _v1 suffix, nothing to clean up for them yet. If either ever
// bumps to _v2 for a format change, extend this the same way: a flat
// stale-keys list for that key, swept here alongside the disclaimer one.
export function cleanupStaleStorageKeys() {
  try {
    STALE_DISCLAIMER_KEYS.forEach((k) => localStorage.removeItem(k));
  } catch (e) {
    // storage unavailable - nothing to clean up, nothing to fail on
  }
}

export const LAST_SEEN_VERSION_KEY = "eql_aa_last_seen_version";
export const CLASS_SLOT_KEYS = ["classSlot0", "classSlot1", "classSlot2"];
// Canonical display/iteration order for the 6 real AA categories (excludes the
// Summary/Progression meta-views, which aren't AA categories).
export const AA_CATEGORY_KEYS = ["general", "archetype", ...CLASS_SLOT_KEYS, "special"];

export let state = {
  selectedClasses: [CLASS_LIST[0], CLASS_LIST[1], CLASS_LIST[2]],
  charLevel: 50,
  ranks: { general: {}, archetype: {}, special: {}, classes: {} },
  purchaseOrder: [], // [{ scope: 'general'|'archetype'|'special'|'class', className?: string, idx: number }, ...] in click order
  // Real-world "I've actually trained this" watermark, same shape as ranks
  // (idx -> highest owned rank), identity-keyed by scope/className rather
  // than anything slot-relative, same reasoning as purchaseOrder. Independent
  // of ranks/purchaseOrder (the plan): owned tracks what's actually true
  // in-game, so Reset Build keeps it by default and it's persisted under
  // a profile-specific key (see ownedProfileId below) instead of any
  // build's payload - see loadAndApplyOwned/saveOwned.
  owned: { general: {}, archetype: {}, special: {}, classes: {} },
  // Which owned profile `owned` above is currently loaded from/saved to -
  // see ownedStorageKeyFor. Defaults to the shared legacy profile so a
  // fresh session behaves exactly like the old single-global-owned system
  // until something (a new saved build, an import carrying owned data, or
  // the Link/Merge/Split controls) diverges it. Part of the same payload
  // saveLocal() persists, so it survives reloads like selectedClasses does;
  // each saved Build slot carries its own copy of this field too (builds.js).
  ownedProfileId: LEGACY_OWNED_PROFILE_ID,
  // Same shape/identity-keying as owned, but a display preference rather
  // than real-world truth: which AAs to leave out of the tree/Browse grids.
  // Persisted under its own key (HIDDEN_STORAGE_KEY), never part of the
  // build payload/exports/share links - see loadAndApplyHidden/saveHidden.
  // Never suppresses an AA with rank > 0, no matter what this holds.
  hiddenAAs: { general: {}, archetype: {}, special: {}, classes: {} },
  // Whether hidden AAs are shown anyway right now - a session-only view
  // toggle (not persisted, same as browseSearch/browseFilter), not part of
  // hiddenAAs itself.
  showHidden: false,
  // Named point-total markers ({ pts, label, color }), sorted ascending and
  // deduped by pts. Unlike owned, these describe the PLAN itself, so they
  // live inside the build payload/slots/share codes, not a separate key.
  // Anchored to a point total rather than a list position or step reference
  // - a position would break under reorder/undo/reset; a point total just
  // gets re-derived against whatever the current order happens to be.
  waypoints: [],
  activeView: "calculator", // 'calculator' | 'browse' | 'summary' | 'progression'
  activeTab: "general", // 'general' | 'archetype' | 'classSlot0' | 'classSlot1' | 'classSlot2' | 'special'
  selectedNode: null, // { category, idx }
  browseSearch: "",
  browseFilter: "all"
};

// --- ranks/purchaseOrder <-> persisted-shape conversion -------------------
// Runtime state always addresses AAs by index into AA_DATA (simple, and every
// other module already works that way). Only these functions know that saved
// data instead uses name keys (v4+) or, for anything saved before keys.js
// existed, indexes against the frozen LEGACY_AA_ORDER snapshot.

export function serializeRanks(ranks) {
  const out = { general: {}, archetype: {}, special: {}, classes: {} };
  ["general", "archetype", "special"].forEach((scope) => {
    const store = ranks[scope] || {};
    Object.keys(store).forEach((idxStr) => {
      const key = keyForIdx(scope, null, parseInt(idxStr, 10));
      if (key) out[scope][key] = store[idxStr];
    });
  });
  const classes = ranks.classes || {};
  Object.keys(classes).forEach((className) => {
    const store = classes[className] || {};
    const outStore = {};
    Object.keys(store).forEach((idxStr) => {
      const key = keyForIdx("class", className, parseInt(idxStr, 10));
      if (key) outStore[key] = store[idxStr];
    });
    if (Object.keys(outStore).length) out.classes[className] = outStore;
  });
  return out;
}

// Saved rank values come from localStorage, pasted text, or a URL — none of
// which are guaranteed to have gone through this app. Coerce to an integer
// and clamp to the AA's real rank range so a bogus value (huge, negative,
// non-numeric) can't produce a broken-looking build or a costly loop
// somewhere downstream that assumes ranks are always small and sane.
function clampRankValue(scope, className, idx, rawValue) {
  const aa = aaAt(scope, className, idx);
  if (!aa) return 0;
  const n = parseInt(rawValue, 10);
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.min(aa.ranks, n));
}

// Returns { ranks, dropped } — `dropped` is how many saved rank entries had a
// key that no longer resolves to any current AA (renamed/removed since the
// save was made). Every key here represents at least one spent point
// (changeRank deletes a store entry the moment it hits 0), so a drop always
// means real invested points just vanished from the build — worth telling
// the user about instead of leaving them to notice a lower total on their own.
function deserializeRanks(saved, resolveIdx) {
  const out = { general: {}, archetype: {}, special: {}, classes: {} };
  let dropped = 0;
  if (!saved || typeof saved !== "object") return { ranks: out, dropped };
  ["general", "archetype", "special"].forEach((scope) => {
    const store = saved[scope] || {};
    Object.keys(store).forEach((k) => {
      const idx = resolveIdx(scope, null, k);
      if (idx >= 0) out[scope][idx] = clampRankValue(scope, null, idx, store[k]);
      else dropped++;
    });
  });
  const classes = saved.classes || {};
  Object.keys(classes).forEach((className) => {
    const store = classes[className] || {};
    const outStore = {};
    Object.keys(store).forEach((k) => {
      const idx = resolveIdx("class", className, k);
      if (idx >= 0) outStore[idx] = clampRankValue("class", className, idx, store[k]);
      else dropped++;
    });
    if (Object.keys(outStore).length) out.classes[className] = outStore;
  });
  return { ranks: out, dropped };
}

// Same idx<->name-key indirection as serializeRanks/deserializeRanks, but
// flags rather than magnitudes - a hidden AA either has an entry or it
// doesn't, so there's no clampRankValue-style range to validate against.
function serializeHidden(hidden) {
  const out = { general: {}, archetype: {}, special: {}, classes: {} };
  ["general", "archetype", "special"].forEach((scope) => {
    const store = hidden[scope] || {};
    Object.keys(store).forEach((idxStr) => {
      const key = keyForIdx(scope, null, parseInt(idxStr, 10));
      if (key) out[scope][key] = true;
    });
  });
  const classes = hidden.classes || {};
  Object.keys(classes).forEach((className) => {
    const store = classes[className] || {};
    const outStore = {};
    Object.keys(store).forEach((idxStr) => {
      const key = keyForIdx("class", className, parseInt(idxStr, 10));
      if (key) outStore[key] = true;
    });
    if (Object.keys(outStore).length) out.classes[className] = outStore;
  });
  return out;
}

function deserializeHidden(saved) {
  const out = { general: {}, archetype: {}, special: {}, classes: {} };
  if (!saved || typeof saved !== "object") return out;
  ["general", "archetype", "special"].forEach((scope) => {
    const store = saved[scope] || {};
    Object.keys(store).forEach((k) => {
      const idx = idxForKey(scope, null, k);
      if (idx >= 0) out[scope][idx] = true;
    });
  });
  const classes = saved.classes || {};
  Object.keys(classes).forEach((className) => {
    const store = classes[className] || {};
    const outStore = {};
    Object.keys(store).forEach((k) => {
      const idx = idxForKey("class", className, k);
      if (idx >= 0) outStore[idx] = true;
    });
    if (Object.keys(outStore).length) out.classes[className] = outStore;
  });
  return out;
}

// Mirrors saveOwned/loadAndApplyOwned - called by setHidden (logic.js)
// whenever state.hiddenAAs changes, and once at boot from main.js. No
// migration-from-main-payload path to worry about (unlike owned's history):
// this feature never stored hidden anywhere else.
export function saveHidden() {
  try {
    localStorage.setItem(HIDDEN_STORAGE_KEY, JSON.stringify({ v: SAVE_FORMAT_VERSION, hidden: serializeHidden(state.hiddenAAs) }));
  } catch (e) { /* storage unavailable, ignore */ }
}

export function loadAndApplyHidden() {
  try {
    const raw = localStorage.getItem(HIDDEN_STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && parsed.hidden && typeof parsed.hidden === "object") {
        state.hiddenAAs = deserializeHidden(parsed.hidden);
        return;
      }
    }
  } catch (e) { /* storage unavailable or corrupt, ignore */ }
  state.hiddenAAs = { general: {}, archetype: {}, special: {}, classes: {} };
}

export function serializePurchaseOrder(purchaseOrder) {
  return (purchaseOrder || []).map((e) => {
    const key = keyForIdx(e.scope, e.className || null, e.idx);
    return key ? { scope: e.scope, className: e.className || null, key } : null;
  }).filter(Boolean);
}

// The entire AA roster - every class, general/archetype/special, everything
// maxed - is a few hundred entries at most (well under 500 as of this
// writing). Generous headroom above that, but a hard ceiling: without one,
// a crafted purchaseOrder array costs reconcilePurchaseOrderCounts (logic.js)
// far worse than linear time to reconcile against the real, small rank
// counts in `r` - a multi-second tab freeze from a share link short enough
// to paste in chat, not a large download. Applied to the raw untrusted
// input before any per-entry work, so a malicious array can't cost more
// than this many entries' worth of processing no matter how large it claims
// to be.
const MAX_PURCHASE_ORDER = 2000;

// Unlike deserializeRanks, a dropped purchaseOrder entry isn't its own
// user-facing signal — reconcilePurchaseOrderCounts (logic.js) checks
// purchaseOrder's entry count against each AA's actual held rank directly
// after load and repairs any mismatch, which catches this and every other
// way the two could end up disagreeing, not just this one cause (including
// the truncation below, on the rare/hostile input that needs it).
function deserializePurchaseOrder(saved, entryIdOf, resolveIdx) {
  const list = Array.isArray(saved) ? saved.slice(0, MAX_PURCHASE_ORDER) : [];
  return list.map((e) => {
    if (!e || typeof e !== "object" || typeof e.scope !== "string") return null;
    const id = entryIdOf(e);
    if (id == null) return null;
    const idx = resolveIdx(e.scope, e.className || null, id);
    return idx >= 0 ? { scope: e.scope, className: e.className || null, idx } : null;
  }).filter(Boolean);
}

// Generous enough that no real user approaches it, tight enough that a
// hostile pasted code/link can't inject an unbounded array (same spirit as
// MAX_WAYPOINT_PTS above).
const MAX_WAYPOINTS = 200;

// Curated palette rather than a free color picker - a handful of
// distinguishable, pre-tuned-for-the-dark-theme options is enough to color
// code a build's steps, and keeps every colored segment/swatch/divider
// dot readable without needing per-color contrast checking against
// arbitrary user-chosen hex values. key is what's actually stored on a
// waypoint and round-tripped through save/export; hex is only for the
// swatch-picker UI (render.js) - the segment/divider tints themselves are
// plain CSS classes keyed off it (styles.src.css).
export const WAYPOINT_COLORS = [
  { key: "red", hex: "#d94c4c" },
  { key: "orange", hex: "#d98a3d" },
  { key: "yellow", hex: "#d9c23d" },
  { key: "green", hex: "#4c8c52" },
  { key: "teal", hex: "#3da6a0" },
  { key: "blue", hex: "#4c7fd9" },
  { key: "purple", hex: "#9c4cd9" }
];
const WAYPOINT_COLOR_KEYS = new Set(WAYPOINT_COLORS.map((c) => c.key));

// Waypoints don't reference any AA identity, so there's no name-key
// resolution here - just validating/clamping untrusted input (localStorage,
// a pasted build code, or a share link) into the { pts, label, color }
// shape state.waypoints uses. Accepts either that shape or the compact
// [pts, label, color] triple exportImport.js's `w` field uses. Duplicate
// pts values collapse to the last one seen; an unrecognized color (stale,
// or a palette entry an older client doesn't know) degrades to no color.
export function sanitizeWaypoints(list) {
  if (!Array.isArray(list)) return [];
  const byPts = new Map();
  list.forEach((entry) => {
    let rawPts, rawLabel, rawColor;
    if (Array.isArray(entry)) [rawPts, rawLabel, rawColor] = entry;
    else if (entry && typeof entry === "object") { rawPts = entry.pts; rawLabel = entry.label; rawColor = entry.color; }
    else return;
    const pts = parseInt(rawPts, 10);
    if (!Number.isFinite(pts) || pts < 0) return;
    const clamped = Math.min(pts, MAX_WAYPOINT_PTS);
    const label = typeof rawLabel === "string" && rawLabel.trim() ? rawLabel.trim().slice(0, 60) : null;
    const color = typeof rawColor === "string" && WAYPOINT_COLOR_KEYS.has(rawColor) ? rawColor : null;
    byPts.set(clamped, { label, color });
  });
  return Array.from(byPts.entries())
    .map(([pts, { label, color }]) => ({ pts, label, color }))
    .sort((a, b) => a.pts - b.pts)
    .slice(0, MAX_WAYPOINTS);
}

// Still swallows its own write failure silently, unlike saveBuildAs's
// named-save path (builds.js) - deliberately out of scope there, not an
// oversight: this is the always-on autosave, called from nearly every
// state-changing action in the app, with no discrete "did this specific
// action succeed" moment a toast could attach to the way Save As has one.
// Surfacing every failed autosave would mean a toast on almost every
// click while storage is full/unavailable. Broader persistence-failure
// visibility (this, saveOwned below, and the owned-tracking Link/Merge/
// Split primitives further down) remains an open, separate piece of work.
export function saveLocal() {
  try {
    const payload = {
      v: SAVE_FORMAT_VERSION,
      selectedClasses: state.selectedClasses,
      charLevel: state.charLevel,
      ranks: serializeRanks(state.ranks),
      purchaseOrder: serializePurchaseOrder(state.purchaseOrder),
      waypoints: state.waypoints,
      ownedProfileId: state.ownedProfileId
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  } catch (e) { /* storage unavailable, ignore */ }
}

// Writes arbitrary owned-shaped data under a specific profile id, without
// touching state.ownedProfileId itself - the primitive a brand-new saved
// build's seeded copy (builds.js) needs, distinct from saveOwned's "persist
// whatever the current session is showing" job below. Returns whether the
// write actually landed - builds.js's saveBuildAs checks this for a
// brand-new slot's seeded profile, since silently swallowing the failure
// there would leave the new slot pointing at a profile with no data behind
// it while still reporting a successful save.
export function saveOwnedProfileTo(profileId, ownedLike) {
  try {
    localStorage.setItem(ownedStorageKeyFor(profileId), JSON.stringify({ v: SAVE_FORMAT_VERSION, owned: serializeRanks(ownedLike) }));
    return true;
  } catch (e) {
    return false;
  }
}

// Persists the current session's owned data to whichever profile
// state.ownedProfileId currently points at - called by
// setOwnedRank/performReset in logic.js whenever owned itself changes,
// and by the Link/Merge/Split primitives below after they change what's
// showing.
export function saveOwned() {
  saveOwnedProfileTo(state.ownedProfileId, state.owned);
}

function loadOwnedProfileRaw(profileId) {
  try {
    const raw = localStorage.getItem(ownedStorageKeyFor(profileId));
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : null;
  } catch (e) { return null; }
}

// Ensures the legacy global owned key's content is reachable under the
// well-known "legacy" profile id every pre-existing build/session
// implicitly used before per-build tracking existed. Copies once, on
// first encounter, and never overwrites an existing copy again - a
// profile that's since diverged via real Link/Merge/Split use must not be
// reset back to the original snapshot on a later boot. Safe to call every
// boot; a no-op once the copy exists. Called from main.js's init(),
// before loadAndApplyOwned runs.
export function migrateLegacyOwnedProfile() {
  try {
    const legacyRaw = localStorage.getItem(OWNED_STORAGE_KEY);
    if (!legacyRaw) return;
    const profileKey = ownedStorageKeyFor(LEGACY_OWNED_PROFILE_ID);
    if (localStorage.getItem(profileKey) != null) return;
    localStorage.setItem(profileKey, legacyRaw);
  } catch (e) { /* storage unavailable, ignore */ }
}

// Every eql_aa_owned_<profileId> key currently in storage, except the
// permanent legacy profile - callers (builds.js's orphan sweep) use this
// to compute which profiles exist before checking which are still
// referenced. Excludes OWNED_STORAGE_KEY itself too, in case its own
// "_v1" suffix were ever mistaken for a profile id under the same prefix.
export function listOwnedProfileIds() {
  const prefix = "eql_aa_owned_";
  const ids = [];
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key || !key.startsWith(prefix) || key === OWNED_STORAGE_KEY) continue;
      const id = key.slice(prefix.length);
      if (id !== LEGACY_OWNED_PROFILE_ID) ids.push(id);
    }
  } catch (e) { /* storage unavailable, ignore */ }
  return ids;
}

// Removes a single owned profile's storage - refuses to touch the
// permanent legacy profile no matter what a caller passes, since
// preserving it is the one invariant this exists to never violate.
export function removeOwnedProfile(profileId) {
  if (profileId === LEGACY_OWNED_PROFILE_ID) return;
  try {
    localStorage.removeItem(ownedStorageKeyFor(profileId));
  } catch (e) { /* storage unavailable, ignore */ }
}

export function loadLocal() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return null;
    return parsed;
  } catch (e) { return null; }
}

// Returns { droppedRanks } — how many saved rank entries had a key that no
// longer resolves to a current AA. Callers use this to tell the user
// something vanished, instead of a build that's just quietly smaller than
// they left it.
export function applyLoaded(loaded) {
  if (!loaded) return { droppedRanks: 0 };
  if (
    Array.isArray(loaded.selectedClasses) &&
    loaded.selectedClasses.length === 3 &&
    loaded.selectedClasses.every((c) => CLASS_LIST.includes(c)) &&
    new Set(loaded.selectedClasses).size === 3
  ) {
    state.selectedClasses = loaded.selectedClasses.slice();
  }
  if (typeof loaded.charLevel === "number" && !isNaN(loaded.charLevel)) {
    state.charLevel = Math.max(1, Math.min(50, loaded.charLevel));
  }
  // v4+ saves store name keys, resolved straight against today's AA_DATA.
  // Anything older stored raw indexes against the ordering AA_DATA happened
  // to have at save time — resolved instead through the frozen snapshot, so
  // reordering/regenerating the wiki data doesn't quietly reattach old points
  // to the wrong ability. Either way, an AA that no longer resolves is
  // dropped rather than guessed at.
  const isLegacy = !(typeof loaded.v === "number" && loaded.v >= 4);
  let droppedRanks = 0;
  if (loaded.ranks && typeof loaded.ranks === "object") {
    const result = isLegacy
      ? deserializeRanks(loaded.ranks, (scope, cls, idxStr) => currentIdxForLegacyIdx(scope, cls, parseInt(idxStr, 10)))
      : deserializeRanks(loaded.ranks, (scope, cls, key) => idxForKey(scope, cls, key));
    state.ranks = result.ranks;
    droppedRanks = result.dropped;
  }
  if (Array.isArray(loaded.purchaseOrder)) {
    state.purchaseOrder = isLegacy
      ? deserializePurchaseOrder(loaded.purchaseOrder, (e) => (typeof e.idx === "number" ? e.idx : null), (scope, cls, legacyIdx) => currentIdxForLegacyIdx(scope, cls, legacyIdx))
      : deserializePurchaseOrder(loaded.purchaseOrder, (e) => (typeof e.key === "string" ? e.key : null), (scope, cls, key) => idxForKey(scope, cls, key));
  }
  // owned is deliberately NOT handled here - it lives outside the build
  // payload entirely (see OWNED_STORAGE_KEY/loadAndApplyOwned) and must
  // survive loading any build/slot/share link untouched. If `loaded` has
  // an owned field anyway (an old payload, or a share code that once
  // carried it), it's just ignored here as an unrecognized extra field.
  //
  // Unlike ranks/purchaseOrder (left as-is if the field is simply missing),
  // waypoints always get reset here, present or not - they ARE part of
  // "the build" being loaded. A build saved before this feature has no
  // waypoints field at all, and loading it must actually clear whatever
  // waypoints the previous build in memory had, not silently carry them over.
  state.waypoints = sanitizeWaypoints(loaded.waypoints);
  return { droppedRanks };
}

// Loads state.owned from whichever profile state.ownedProfileId currently
// points at - the caller (main.js at boot, builds.js's loadBuild) is
// responsible for setting that first, since which profile applies depends
// on context (the current session's own saved value, or the build slot
// being loaded). rawMainPayload is the raw object loadLocal() returned,
// needed for exactly one purpose: a one-time migration for saves made
// while this feature briefly stored owned inside the main build payload
// instead of its own key, well before per-build profiles existed. Pass
// null when there's no such payload to fall back to (every caller besides
// boot). Returns { droppedOwned } in the same spirit as applyLoaded's
// droppedRanks, so callers can fold it into their own load-time notice.
export function loadAndApplyOwned(rawMainPayload) {
  const stored = loadOwnedProfileRaw(state.ownedProfileId);
  if (stored && stored.owned && typeof stored.owned === "object") {
    const result = deserializeRanks(stored.owned, (scope, cls, key) => idxForKey(scope, cls, key));
    state.owned = result.ranks;
    return { droppedOwned: result.dropped };
  }
  if (rawMainPayload && rawMainPayload.owned && typeof rawMainPayload.owned === "object") {
    // owned only ever existed in the main payload under SAVE_FORMAT_VERSION
    // 4 (it shipped well after v4 became name-keyed) - no legacy index-based
    // form to handle here, unlike ranks/purchaseOrder above.
    const result = deserializeRanks(rawMainPayload.owned, (scope, cls, key) => idxForKey(scope, cls, key));
    state.owned = result.ranks;
    saveOwned();
    return { droppedOwned: result.dropped };
  }
  state.owned = { general: {}, archetype: {}, special: {}, classes: {} };
  return { droppedOwned: 0 };
}

// Whether a name-keyed owned payload (the shape loadLocal/decodeBuildCode
// hand around, before deserializeRanks turns it into idx-keyed state.owned)
// actually has anything in it - used by exportImport.js to decide whether an
// imported build is even carrying owned data worth creating a profile for,
// without needing to deserialize it first just to find out it's empty.
export function payloadOwnedHasContent(owned) {
  if (!owned || typeof owned !== "object") return false;
  if (Object.keys(owned.general || {}).length || Object.keys(owned.archetype || {}).length || Object.keys(owned.special || {}).length) return true;
  const classes = owned.classes || {};
  return Object.keys(classes).some((className) => Object.keys(classes[className] || {}).length > 0);
}

// An import (share link or pasted text) that carries its own owned data
// always gets a brand-new profile seeded from it, rather than touching
// whatever the current session was already tracking - silent, no
// confirmation, since nothing existing is ever at risk of being
// overwritten this way. exportImport.js's maybeImportOwned is the only
// caller.
export function adoptImportedOwnedAsNewProfile(ownedField) {
  const newId = genId();
  const result = deserializeRanks(ownedField, (scope, cls, key) => idxForKey(scope, cls, key));
  state.ownedProfileId = newId;
  state.owned = result.ranks;
  saveOwned();
  return { dropped: result.dropped };
}

// --- Ongoing owned-tracking controls: Link / Merge / Split -----------------
// The three primitives behind the Progression tab's "Manage owned
// tracking…" control (render.js). Each one only touches state.owned/
// state.ownedProfileId - keeping the active saved build slot's own stored
// ownedProfileId field in sync (if the current session is a saved slot
// right now) is builds.js's job, not this file's.

// Repoints the current session at an existing profile (someone else's
// build, or your own) - from then on the two read/write the same storage
// key, so marking something owned in either shows up in both immediately.
export function linkOwnedProfile(targetProfileId) {
  state.ownedProfileId = targetProfileId;
  loadAndApplyOwned(null);
}

// Inverse of Link: starts a fresh, independent profile seeded with a copy
// of whatever's currently showing. Whatever the session used to share
// with is completely unaffected - this only ever writes to the new key.
export function splitOwnedProfile() {
  state.ownedProfileId = genId();
  saveOwned();
}

// One-directional, non-destructive union: anything owned in sourceProfileId
// ends up owned in the current profile too, taking the higher rank on any
// entry both sides have (mirrors how "owned" itself means "owned up to
// rank N"). Nothing already marked owned can become unmarked, and
// sourceProfileId's own data is only ever read here, never modified.
export function mergeOwnedProfileInto(sourceProfileId) {
  const sourceRaw = loadOwnedProfileRaw(sourceProfileId);
  if (!sourceRaw || !sourceRaw.owned || typeof sourceRaw.owned !== "object") return { merged: 0 };
  const source = deserializeRanks(sourceRaw.owned, (scope, cls, key) => idxForKey(scope, cls, key)).ranks;
  let merged = 0;
  function mergeStore(target, src) {
    Object.keys(src).forEach((idxStr) => {
      const idx = parseInt(idxStr, 10);
      const current = target[idx] || 0;
      if (src[idx] > current) { target[idx] = src[idx]; merged++; }
    });
  }
  ["general", "archetype", "special"].forEach((scope) => mergeStore(state.owned[scope], source[scope]));
  Object.keys(source.classes).forEach((className) => {
    if (!state.owned.classes[className]) state.owned.classes[className] = {};
    mergeStore(state.owned.classes[className], source.classes[className]);
  });
  if (merged) saveOwned();
  return { merged };
}
