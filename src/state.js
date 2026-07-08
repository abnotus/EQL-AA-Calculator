// App-wide constants, the mutable state object, and localStorage persistence.
// Nothing here touches the DOM — that's render.js / dom.js.

export const STORAGE_KEY = "eql_aa_builder_v1";
export const DISCLAIMER_DISMISSED_KEY = "eql_aa_disclaimer_dismissed";
export const CLASS_SLOT_KEYS = ["classSlot0", "classSlot1", "classSlot2"];
// Canonical display/iteration order for the 6 real AA categories (excludes the
// Summary/Progression meta-views, which aren't AA categories).
export const AA_CATEGORY_KEYS = ["general", "archetype", ...CLASS_SLOT_KEYS, "special"];

export let state = {
  selectedClasses: [CLASS_LIST[0], CLASS_LIST[1], CLASS_LIST[2]],
  charLevel: 50,
  totalPoints: 1000,
  ranks: { general: {}, archetype: {}, special: {}, classes: {} },
  purchaseOrder: [], // [{ scope: 'general'|'archetype'|'special'|'class', className?: string, idx: number }, ...] in click order
  activeView: "calculator", // 'calculator' | 'browse' | 'summary' | 'progression'
  activeTab: "general", // 'general' | 'archetype' | 'classSlot0' | 'classSlot1' | 'classSlot2' | 'special'
  selectedNode: null, // { category, idx }
  browseSearch: "",
  browseFilter: "all"
};

export function saveLocal() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
  catch (e) { /* storage unavailable, ignore */ }
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

export function applyLoaded(loaded) {
  if (!loaded) return;
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
  if (typeof loaded.totalPoints === "number" && !isNaN(loaded.totalPoints)) {
    state.totalPoints = Math.max(0, loaded.totalPoints);
  }
  if (loaded.ranks && typeof loaded.ranks === "object") {
    state.ranks = {
      general: loaded.ranks.general || {},
      archetype: loaded.ranks.archetype || {},
      special: loaded.ranks.special || {},
      classes: loaded.ranks.classes || {}
    };
  }
  if (Array.isArray(loaded.purchaseOrder)) {
    state.purchaseOrder = loaded.purchaseOrder.filter((e) => e && typeof e === "object" && typeof e.scope === "string" && typeof e.idx === "number");
  }
}
