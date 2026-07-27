// Named build slots: save/load/rename/delete snapshots of the current build
// in localStorage, independent of state.js's always-autosaving STORAGE_KEY
// (which keeps holding whatever you're currently editing). Loading a slot
// just overwrites the current working state, which then autosaves as normal.

import { state, saveLocal, serializeRanks, serializePurchaseOrder, applyLoaded, SAVE_FORMAT_VERSION } from "./state.js";
import { spentPoints, clearLastMutation, reconcilePurchaseOrderCounts } from "./logic.js";

const BUILDS_INDEX_KEY = "eql_aa_builds_index_v1";
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

function loadIndex() {
  try {
    const raw = localStorage.getItem(BUILDS_INDEX_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    return [];
  }
}

function saveIndex(index) {
  try {
    localStorage.setItem(BUILDS_INDEX_KEY, JSON.stringify(index));
  } catch (e) { /* storage unavailable/full - the slot data write already failed first if so */ }
}

function genId() {
  return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
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

// One-time migration: strips the dead `totalPoints` field (gone once the
// point cap was removed) from every saved slot's stored JSON. Purely
// cosmetic now that activeBuildMatchesCurrent ignores extra keys anyway -
// kept so old slots don't carry stale data forever. Runs once at boot; a
// no-op after the first pass per slot.
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
    if (!parsed || typeof parsed !== "object" || !("totalPoints" in parsed)) return;
    delete parsed.totalPoints;
    try {
      localStorage.setItem(key, JSON.stringify(parsed));
    } catch (e) {
      // storage unavailable/full - leave the stale field in place, same
      // "nothing changed" outcome as any other failed write here
    }
  });
}

function buildPayload() {
  return {
    v: SAVE_FORMAT_VERSION,
    selectedClasses: state.selectedClasses,
    charLevel: state.charLevel,
    ranks: serializeRanks(state.ranks),
    purchaseOrder: serializePurchaseOrder(state.purchaseOrder),
    // Unlike owned (deliberately NOT part of a slot's snapshot - see
    // OWNED_STORAGE_KEY), waypoints describe the plan itself, so a saved
    // slot captures them same as ranks/purchaseOrder.
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
// slot's id, or null if localStorage rejected the write (full/unavailable),
// in which case nothing was changed.
function saveBuildAs(name, id = null) {
  const targetId = id || genId();
  try {
    localStorage.setItem(BUILD_KEY_PREFIX + targetId, JSON.stringify(buildPayload()));
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
  saveIndex(index);
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
export function saveImportedBuild() {
  const existing = findImportedSlot();
  return saveBuildAs(IMPORTED_BUILD_NAME, existing ? existing.id : null);
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
  setActiveBuildId(id);
  saveLocal();
  return { droppedRanks: result.droppedRanks, repaired };
}

// False on a name collision with a *different* slot, not just "not found" -
// renameBuild doesn't merge/overwrite the other entry, so the caller needs
// to tell the two apart and report a clash rather than treating it as
// nothing happened.
export function renameBuild(id, name) {
  const index = loadIndex();
  const entry = index.find((b) => b.id === id);
  if (!entry) return "missing";
  if (index.some((b) => b.id !== id && b.name === name)) return "collision";
  entry.name = name;
  saveIndex(index);
  return "ok";
}

export function deleteBuild(id) {
  saveIndex(loadIndex().filter((b) => b.id !== id));
  try {
    localStorage.removeItem(BUILD_KEY_PREFIX + id);
  } catch (e) { /* ignore */ }
  if (getActiveBuildId() === id) setActiveBuildId(null);
}
