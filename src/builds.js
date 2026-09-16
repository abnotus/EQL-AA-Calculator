// Named build slots: save/load/rename/delete snapshots of the current build
// in localStorage, independent of state.js's always-autosaving STORAGE_KEY
// (which keeps holding whatever you're currently editing). Loading a slot
// just overwrites the current working state, which then autosaves as normal.

import {
  state, saveLocal, serializeRanks, serializePurchaseOrder, applyLoaded, SAVE_FORMAT_VERSION,
  genId, LEGACY_OWNED_PROFILE_ID, loadAndApplyOwned, saveOwnedProfileTo,
  linkOwnedProfile, splitOwnedProfile, mergeOwnedProfileInto,
  listOwnedProfileIds, removeOwnedProfile
} from "./state.js";
import { spentPoints, clearLastMutation, reconcilePurchaseOrderCounts } from "./logic.js";

export const BUILDS_INDEX_KEY = "eql_aa_builds_index_v1";
const BUILD_KEY_PREFIX = "eql_aa_build_";
// The reuse key for an auto-imported share link is this name, not a fixed id
// - see findImportedSlot for why an id can't serve that role once renames
// enter the picture.
const IMPORTED_BUILD_NAME = "Imported Build";
// Which saved slot (if any) the current working state was last loaded from or
// saved as — purely for UI orientation (highlighting it in the list, showing
// its name near the Builds button). Not part of any build's own payload, and
// never trusted for anything beyond display: loading/saving always resolves
// by id against the index, not the other way around.
const ACTIVE_BUILD_KEY = "eql_aa_active_build_id";

// In-memory cache of the parsed index, avoiding a localStorage.getItem +
// JSON.parse on every read (listBuilds() alone runs on every renderTopbar,
// i.e. every renderAll). null means "not loaded yet"; every mutation goes
// through saveIndex, which keeps this in lockstep with what's persisted -
// but only for writes made from THIS tab. Another tab saving/renaming/
// deleting a build writes BUILDS_INDEX_KEY directly, which this cache has
// no way to see on its own - events.js listens for the "storage" event
// (which only ever fires in OTHER tabs, never the one that made the write)
// and calls dropCachedIndex so the next loadIndex() here re-reads from
// localStorage instead of writing back a now-stale copy that would clobber
// whatever the other tab just added.
let cachedIndex = null;

export function dropCachedIndex() {
  cachedIndex = null;
}

function loadIndex() {
  if (cachedIndex !== null) return cachedIndex;
  try {
    const raw = localStorage.getItem(BUILDS_INDEX_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    cachedIndex = Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    cachedIndex = [];
  }
  return cachedIndex;
}

// Returns whether the write actually landed. cachedIndex is updated either
// way (see the comment below) so the UI stays in sync with what this
// session sees, but a caller reporting overall success to the user must
// still check this - localStorage.setItem here is its own independent
// write, not guaranteed to succeed just because an earlier write (e.g. the
// slot data itself, in saveBuildAs) did. Two writes of a few KB each can
// straddle a quota boundary either way; there's no ordering that makes one
// of them a reliable proxy for the other.
function saveIndex(index) {
  // Load-bearing, not defensive: saveBuildAs/renameBuild both mutate the
  // array loadIndex() just returned (the cached one, by reference) before
  // calling this, so for them the cache already reflects the change with or
  // without this line. deleteBuild is the one caller that builds a genuinely
  // NEW array (loadIndex().filter(...)), so this is the only thing that
  // repoints the cache for that path - drop it and a deleted build keeps
  // showing in the Builds modal until the next full page load, even though
  // localStorage is already correct (test_builds_index_cache.py pins this).
  cachedIndex = index;
  try {
    localStorage.setItem(BUILDS_INDEX_KEY, JSON.stringify(index));
    return true;
  } catch (e) {
    return false;
  }
}

// Most-recently-updated first — the one you're most likely to want is at the top.
export function listBuilds() {
  return loadIndex().slice().sort((a, b) => b.updatedAt - a.updatedAt);
}

export function getActiveBuildId() {
  try {
    return localStorage.getItem(ACTIVE_BUILD_KEY) || null;
  } catch (e) {
    return null;
  }
}

function setActiveBuildId(id) {
  try {
    if (id) localStorage.setItem(ACTIVE_BUILD_KEY, id);
    else localStorage.removeItem(ACTIVE_BUILD_KEY);
  } catch (e) { /* ignore */ }
}

// Called whenever the current working state gets replaced by something other
// than loadBuild — an import, a share link, Reset Build — so a subsequent
// save can't mistake unrelated content for an update to whatever slot used
// to be active.
export function clearActiveBuild() {
  setActiveBuildId(null);
}

// Sweeps every saved slot's stored JSON for two independent, self-healing
// fixups: strips the dead `totalPoints` field (gone once the point cap was
// removed), and backfills a missing `ownedProfileId` to the shared legacy
// profile (see LEGACY_OWNED_PROFILE_ID) - a slot saved before per-build
// owned tracking existed always meant "the one global pool", so this keeps
// it behaving exactly that way until something (Save As, or the Link/
// Merge/Split controls) deliberately diverges it. Deliberately re-checked
// on every boot rather than gated behind a "have we migrated" flag, so a
// slot that only reaches this browser later (restored from a backup,
// synced from another device) still gets caught.
export function migrateStaleBuildSlots() {
  loadIndex().forEach(({ id }) => {
    const key = BUILD_KEY_PREFIX + id;
    let raw;
    try {
      raw = localStorage.getItem(key);
    } catch (e) {
      return;
    }
    if (!raw) return;
    let parsed;
    try {
      parsed = JSON.parse(raw);
    } catch (e) {
      return;
    }
    if (!parsed || typeof parsed !== "object") return;
    let changed = false;
    if ("totalPoints" in parsed) { delete parsed.totalPoints; changed = true; }
    if (typeof parsed.ownedProfileId !== "string" || !parsed.ownedProfileId) {
      parsed.ownedProfileId = LEGACY_OWNED_PROFILE_ID;
      changed = true;
    }
    if (!changed) return;
    try {
      localStorage.setItem(key, JSON.stringify(parsed));
    } catch (e) {
      // storage unavailable/full - leave the stale data in place, same
      // "nothing changed" outcome as any other failed write here
    }
  });
}

function readBuildRaw(id) {
  try {
    const raw = localStorage.getItem(BUILD_KEY_PREFIX + id);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

// A saved slot's own owned-tracking pointer, defaulting to the shared
// legacy profile for a slot that somehow still lacks the field (shouldn't
// happen once migrateStaleBuildSlots has run, but cheap to be defensive).
function ownedProfileIdOfBuild(id) {
  const raw = readBuildRaw(id);
  return (raw && typeof raw.ownedProfileId === "string" && raw.ownedProfileId) || LEGACY_OWNED_PROFILE_ID;
}

// Owned profiles are minted freely - every brand-new Save As, every Split,
// every owned-carrying import mints its own (state.js) - but nothing ever
// un-mints one when the build(s) pointing at it are deleted or re-linked
// elsewhere. Sweeps any profile with no build slot's own ownedProfileId
// pointing at it AND that isn't the live session's own state.ownedProfileId
// either - a build still pointing at it, even one that isn't currently
// loaded, means it's still reachable and must be left alone.
// removeOwnedProfile (state.js) refuses to touch the legacy profile on its
// own, so there's no need to special-case it here too. Called from
// main.js alongside migrateStaleBuildSlots/cleanupStaleStorageKeys, once
// per boot - cheap at the scale of profiles one browser actually
// accumulates.
export function cleanupOrphanedOwnedProfiles() {
  const referenced = new Set([state.ownedProfileId]);
  loadIndex().forEach(({ id }) => referenced.add(ownedProfileIdOfBuild(id)));
  listOwnedProfileIds().forEach((profileId) => {
    if (!referenced.has(profileId)) removeOwnedProfile(profileId);
  });
}

// Deliberately just the plan - selectedClasses/charLevel/ranks/
// purchaseOrder/waypoints. A slot's owned-tracking pointer
// (ownedProfileId) is real data too, but it's assigned by saveBuildAs
// below with its own logic (fresh + seeded for a new slot, preserved
// as-is for an overwrite), not read off the current session the way
// everything here is - keeping it out of this function is also what lets
// deepEqualIgnoringExtraKeys below ignore it automatically when deciding
// whether a slot is already backed up.
function buildPayload() {
  return {
    v: SAVE_FORMAT_VERSION,
    selectedClasses: state.selectedClasses,
    charLevel: state.charLevel,
    ranks: serializeRanks(state.ranks),
    purchaseOrder: serializePurchaseOrder(state.purchaseOrder),
    waypoints: state.waypoints
  };
}

// Object-key order doesn't matter here; array order still does, since it's
// meaningful for purchaseOrder/waypoints/selectedClasses.
function deepEqual(a, b) {
  if (a === b) return true;
  if (typeof a !== "object" || typeof b !== "object" || a === null || b === null) return false;
  if (Array.isArray(a) || Array.isArray(b)) {
    if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) return false;
    return a.every((v, i) => deepEqual(v, b[i]));
  }
  return Object.keys(a).length === Object.keys(b).length
    && Object.keys(a).every((k) => Object.prototype.hasOwnProperty.call(b, k) && deepEqual(a[k], b[k]));
}

function isEmptyComposite(v) {
  if (Array.isArray(v)) return v.length === 0;
  return typeof v === "object" && v !== null && Object.keys(v).length === 0;
}

// Whether every field current buildPayload() defines matches a stored
// slot - checking only `current`'s own keys, tolerant of key-set
// mismatches in both directions: a key stored has but current doesn't is a
// retired field (e.g. totalPoints) and is simply ignored; a key current
// has but stored doesn't is one that didn't exist yet when the slot was
// saved (e.g. waypoints, added in 1.5.0) and only counts as a match if
// today's value for it is an empty array/object - anything else is a real
// difference. Either way, a key one side lacks entirely is an artifact of
// the payload's shape changing over time, not a real change to the plan.
function deepEqualIgnoringExtraKeys(stored, current) {
  if (typeof stored !== "object" || stored === null) return false;
  return Object.keys(current).every((k) => {
    if (stored[k] === undefined && isEmptyComposite(current[k])) return true;
    return deepEqual(stored[k], current[k]);
  });
}

// Whether the current working state matches what's stored under the active
// slot - not just "there is an active slot", since changes since the last
// save/load would leave the two diverged. Lets a caller about to replace
// the build (Load, a share link, a text import - every caller of
// confirmReplaceCurrentBuild) skip warning about losing something already
// backed up, without threading a "dirty" flag through every mutation path.
//
// Structural, not a string/JSON comparison - immune to buildPayload's
// shape changing over time (a field added or removed) or the stored JSON's
// keys simply serializing in a different order.
function activeBuildMatchesCurrent() {
  const id = getActiveBuildId();
  if (!id) return false;
  try {
    const raw = localStorage.getItem(BUILD_KEY_PREFIX + id);
    if (raw == null) return false;
    return deepEqualIgnoringExtraKeys(JSON.parse(raw), buildPayload());
  } catch (e) {
    return false;
  }
}

// Snapshots the current build into a named slot — a new one, or an existing
// one if id is given (the caller's "overwrite this slot" path). Returns the
// slot's id, or null if localStorage rejected any of this function's writes
// (full/unavailable) - the seeded owned-profile write for a brand-new slot,
// the slot data itself, or the index. A caller must not treat a non-null
// id as "fully saved" unless this function itself already confirmed every
// write it made along the way; reporting success on the strength of the
// slot write alone (the previous behavior) let a later write's own failure
// go unnoticed, leaving a slot that looks saved this session but is gone
// after reload.
//
// A brand-new slot gets its own fresh owned profile, seeded with a copy of
// whatever the current session is showing right now (not empty - you've
// likely already been tracking progress against this exact plan). The
// current session's own state.ownedProfileId is left untouched either way
// - saving a snapshot doesn't change what's live, only what the snapshot
// itself will show if loaded later. Overwriting an existing slot leaves
// its ownedProfileId exactly as it already was. mirrorProfileId is an
// override for saveImportedBuild below, where the slot needs to track
// exactly the same profile the live session is using, not an independent
// fork of it (see that function's own comment for why).
function saveBuildAs(name, id = null, mirrorProfileId = null) {
  const targetId = id || genId();
  const payload = buildPayload();
  if (mirrorProfileId) {
    payload.ownedProfileId = mirrorProfileId;
  } else if (id) {
    payload.ownedProfileId = ownedProfileIdOfBuild(id);
  } else {
    payload.ownedProfileId = genId();
    if (!saveOwnedProfileTo(payload.ownedProfileId, state.owned)) return null;
  }
  try {
    localStorage.setItem(BUILD_KEY_PREFIX + targetId, JSON.stringify(payload));
  } catch (e) {
    return null;
  }
  const index = loadIndex();
  const existing = index.find((b) => b.id === targetId);
  const updatedAt = Date.now();
  if (existing) {
    existing.name = name;
    existing.updatedAt = updatedAt;
  } else {
    index.push({ id: targetId, name, updatedAt });
  }
  if (!saveIndex(index)) return null;
  setActiveBuildId(targetId);
  return targetId;
}

// Saves under `name`, confirming first if it would silently duplicate an
// existing slot's name. Both interactive-save entry points (handleBuildSave
// in render.js, and confirmReplaceCurrentBuild's save-first offer below)
// go through here. Returns the slot's id, false if the user declined the
// overwrite, or null on a storage failure - a decline isn't an error worth
// a "couldn't save" toast, so callers need to tell the two apart.
export function saveWithNameCheck(name) {
  const existing = listBuilds().find((b) => b.name === name);
  if (existing && !confirm(`A build named "${name}" already exists. Overwrite it?`)) return false;
  return saveBuildAs(name, existing ? existing.id : null);
}

// Gate in front of anything about to fully replace the current working
// state (a share link, a text import, loading a different slot). Proceeds
// silently if there's nothing at risk or the build already matches a saved
// slot; otherwise offers to save it under a name first, falling back to a
// plain replace-confirmation if that's declined.
//
// extraRisk covers a risk source that doesn't fit "spentPoints() > 0"
// (applySharedBuildFromUrl's droppedRanks check). trustMatch lets a caller
// say the active-slot match itself isn't trustworthy - opening a share
// link while the active slot is the reused "Imported Build" one is about
// to overwrite that very slot, so its match shouldn't count as backed up.
export function confirmReplaceCurrentBuild(verb, target, { extraRisk = false, trustMatch = true } = {}) {
  const isBackedUp = trustMatch && activeBuildMatchesCurrent();
  if ((spentPoints() <= 0 && !extraRisk) || isBackedUp) return true;
  const wantsSave = confirm(`Your current build isn't saved. Save it as a named build before ${verb}ing ${target}?`);
  if (wantsSave) {
    const name = prompt("Name this build:", "");
    if (!name || !name.trim()) return false;
    const result = saveWithNameCheck(name.trim());
    // false (declined the overwrite) backs out the same as declining to
    // name it - nothing was saved, so proceeding would replace a build the
    // user never agreed to lose. null (storage full) must also not
    // proceed, even though the user did everything right.
    if (result === false) return false;
    if (result === null) {
      alert('Couldn\'t save — local storage may be full or unavailable. Nothing was changed.');
      return false;
    }
    return true;
  }
  return confirm(`${verb.charAt(0).toUpperCase()}${verb.slice(1)} ${target}? This will replace your current build and can't be undone.`);
}

// The slot saveImportedBuild would target next - whichever entry is
// currently named "Imported Build", regardless of id. Looked up by name,
// not id: a rename only changes an entry's name, so the id it already has
// stays attached to it - looking up by a fixed id would keep finding the
// old (now-renamed) entry and allocate a fresh slot on every future import
// instead of reusing the current one.
//
// isActiveBuildTheImportedSlot and saveImportedBuild share this lookup so
// they can't drift apart on what counts as "the" imported slot. Naming
// your own build "Imported Build" opts it into being the reuse target - a
// known tradeoff, not a bug.
function findImportedSlot() {
  return loadIndex().find((b) => b.name === IMPORTED_BUILD_NAME) || null;
}

// True only while the active slot is the one the next saveImportedBuild()
// call would overwrite. Once renamed away from the default name,
// findImportedSlot() no longer finds it, so there's nothing left to
// distrust in confirmReplaceCurrentBuild's trustMatch check.
export function isActiveBuildTheImportedSlot() {
  const slot = findImportedSlot();
  return !!slot && slot.id === getActiveBuildId();
}

// A share link is often opened passively (a link in chat) rather than a
// deliberate "load a build" action - easy to lose track of once it's not
// the active working state anymore. Auto-saves it under one reused slot
// (see findImportedSlot) so it stays one click away in the Builds list
// without piling up a fresh entry per link opened.
//
// Mirrors state.ownedProfileId exactly rather than forking an independent
// copy the way a deliberate Save As does - this slot IS the current
// session, not a separate named build alongside it, so it needs to keep
// showing whatever the session shows (including anything marked owned
// after this auto-save), not a snapshot frozen at import time.
export function saveImportedBuild() {
  const existing = findImportedSlot();
  return saveBuildAs(IMPORTED_BUILD_NAME, existing ? existing.id : null, state.ownedProfileId);
}

// Replaces the current working state with a saved slot's contents — same
// mechanism as loadLocal/applyLoaded on boot, or a text import. Returns
// { droppedRanks, repaired } (see loadIssuesSuffix in logic.js) so the UI can
// surface the same kind of notice an on-load drop already gets, or null if
// the slot doesn't exist / storage failed, in which case nothing changed.
export function loadBuild(id) {
  let parsed;
  try {
    const raw = localStorage.getItem(BUILD_KEY_PREFIX + id);
    if (!raw) return null;
    parsed = JSON.parse(raw);
  } catch (e) {
    return null;
  }
  const result = applyLoaded(parsed);
  state.selectedNode = null;
  clearLastMutation();
  const repaired = reconcilePurchaseOrderCounts();
  // Switches owned tracking to this slot's own profile - the one
  // genuinely visible behavior change for existing multi-build users:
  // two builds only show the same owned progress now if explicitly
  // linked (see linkOwnedToBuild below), not implicitly just by both
  // being builds.
  state.ownedProfileId = (typeof parsed.ownedProfileId === "string" && parsed.ownedProfileId) || LEGACY_OWNED_PROFILE_ID;
  loadAndApplyOwned(null);
  setActiveBuildId(id);
  saveLocal();
  return { droppedRanks: result.droppedRanks, repaired };
}

// "collision" on a name clash with a *different* slot, "missing" if the id
// doesn't resolve, "failed" if the rename itself didn't persist (storage
// full/unavailable - the in-memory list still shows the new name until
// reload, same lockstep-cache caveat as everywhere else here), "ok"
// otherwise. Callers need every one of these distinguished rather than
// collapsed into a boolean, since each means a different message to the user.
export function renameBuild(id, name) {
  const index = loadIndex();
  const entry = index.find((b) => b.id === id);
  if (!entry) return "missing";
  if (index.some((b) => b.id !== id && b.name === name)) return "collision";
  entry.name = name;
  return saveIndex(index) ? "ok" : "failed";
}

// Returns whether the index write persisted - the in-memory list (and thus
// the Builds modal) drops the entry either way, but a caller should still
// tell the user if that removal didn't survive a reload.
export function deleteBuild(id) {
  const persisted = saveIndex(loadIndex().filter((b) => b.id !== id));
  try {
    localStorage.removeItem(BUILD_KEY_PREFIX + id);
  } catch (e) { /* ignore */ }
  if (getActiveBuildId() === id) setActiveBuildId(null);
  return persisted;
}

// --- Owned-tracking management (Link / Merge / Split) ----------------------
// Build-aware wrappers around state.js's profile primitives: those only
// touch state.owned/state.ownedProfileId, so anything here that changes
// which profile is live also needs to keep the active saved slot (if the
// current session is one right now) in sync, or reloading that slot later
// would show something different from what's showing today.

function persistActiveBuildOwnedProfile() {
  const id = getActiveBuildId();
  if (!id) return;
  const parsed = readBuildRaw(id);
  if (!parsed) return;
  parsed.ownedProfileId = state.ownedProfileId;
  try {
    localStorage.setItem(BUILD_KEY_PREFIX + id, JSON.stringify(parsed));
  } catch (e) { /* storage unavailable, ignore */ }
}

// Other saved builds (never the one currently active/loaded) that
// currently share the live session's owned profile - drives the "Manage
// owned tracking…" status line in render.js.
export function buildsSharingCurrentOwnedProfile() {
  const activeId = getActiveBuildId();
  return listBuilds().filter((b) => b.id !== activeId && ownedProfileIdOfBuild(b.id) === state.ownedProfileId);
}

// "Just use one or the other" - repoints the live session (and its active
// saved slot, if any) at targetBuildId's own profile. From then on the two
// read/write the same data until Split pulls them apart again.
export function linkOwnedToBuild(targetBuildId) {
  linkOwnedProfile(ownedProfileIdOfBuild(targetBuildId));
  persistActiveBuildOwnedProfile();
  saveLocal();
}

// "Combine progress from save slots" - one-time, one-directional union
// into the live session's own profile. sourceBuildId's own data is never
// modified.
export function mergeOwnedFromBuild(sourceBuildId) {
  return mergeOwnedProfileInto(ownedProfileIdOfBuild(sourceBuildId));
}

// Inverse of Link - the live session (and its active saved slot, if any)
// gets its own fresh, independent profile, seeded with a copy of whatever
// it's showing right now. Whatever it used to share with is unaffected.
export function splitOwnedFromCurrent() {
  splitOwnedProfile();
  persistActiveBuildOwnedProfile();
  saveLocal();
}
