// Business logic: everything that reads or derives from `state` and AA_DATA,
// plus the mutation functions for spending/refunding points. No HTML/DOM here.

import { state, CLASS_SLOT_KEYS, AA_CATEGORY_KEYS, saveLocal } from "./state.js";
import { renderAll, showToast } from "./render.js";

export function costNum(c) {
  const n = parseInt(c, 10);
  return isNaN(n) ? 0 : n;
}

export function escapeHtml(str) {
  return String(str == null ? "" : str)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

export function iconLetter(name) {
  return (name || "?").trim().charAt(0).toUpperCase();
}

// Highlights the value matching the current rank inside slash-separated progressions
// in a description, e.g. "20/40/60%" at rank 2 -> "20/<mark>40</mark>/60%".
export function highlightRankValue(text, rank) {
  const escaped = escapeHtml(text);
  if (!rank || rank < 1) return escaped;
  return escaped.replace(/\d+(?:\.\d+)?%?(?:\/(?:\d+(?:\.\d+)?%?|\?)){1,}/g, (match) => {
    const parts = match.split("/");
    const idx = rank - 1;
    if (idx < 0 || idx >= parts.length) return match;
    parts[idx] = `<span class="rank-highlight">${parts[idx]}</span>`;
    return parts.join("/");
  });
}

export function classSlotIndex(catKey) {
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

// Auto-granted AAs (0-cost on the wiki) are trained automatically as the character levels, no points spent.
// The wiki documents a single unlock level per ability, not per-rank breakpoints, so once unlocked these
// sit at max rank rather than trickling in one rank at a time.
export function effectiveRank(catKey, idx) {
  const aa = getList(catKey)[idx];
  if (aa && aa.auto) {
    const levelReq = parseInt(aa.levelReq, 10) || 1;
    return state.charLevel >= levelReq ? aa.ranks : 0;
  }
  const store = getRanksStore(catKey);
  return store[idx] || 0;
}

export function getRanksStore(catKey) {
  const slot = classSlotIndex(catKey);
  if (slot >= 0) {
    const className = state.selectedClasses[slot];
    if (!state.ranks.classes[className]) state.ranks.classes[className] = {};
    return state.ranks.classes[className];
  }
  return state.ranks[catKey];
}

// Purchase-order entries key AA picks by class NAME (not slot position), since class
// names are already unique and stable — swapping which slot a class occupies shouldn't
// orphan its place in the progression list.
export function scopeForCategory(category) {
  const slot = classSlotIndex(category);
  return slot >= 0 ? "class" : category;
}

export function classNameForCategory(category) {
  const slot = classSlotIndex(category);
  return slot >= 0 ? state.selectedClasses[slot] : null;
}

export function categoryToScopeClassName(category) {
  const slot = classSlotIndex(category);
  return slot >= 0 ? { scope: "class", className: state.selectedClasses[slot] } : { scope: category, className: null };
}

export function entryKey(scope, className, idx) {
  return `${scope}|${className || ""}|${idx}`;
}

// Which category key currently displays this entry's class, or null if that class
// isn't in any of the 3 active slots right now.
export function resolveEntryCategory(entry) {
  if (entry.scope !== "class") return entry.scope;
  const slot = state.selectedClasses.indexOf(entry.className);
  return slot >= 0 ? CLASS_SLOT_KEYS[slot] : null;
}

export function pushPurchase(category, idx) {
  state.purchaseOrder.push({ scope: scopeForCategory(category), className: classNameForCategory(category), idx });
}

export function popLastPurchase(category, idx) {
  const scope = scopeForCategory(category);
  const className = classNameForCategory(category);
  for (let i = state.purchaseOrder.length - 1; i >= 0; i--) {
    const e = state.purchaseOrder[i];
    if (e.scope === scope && e.idx === idx && (e.className || null) === (className || null)) {
      state.purchaseOrder.splice(i, 1);
      return;
    }
  }
}

export function clearClassData(className) {
  delete state.ranks.classes[className];
  state.purchaseOrder = state.purchaseOrder.filter((e) => !(e.scope === "class" && e.className === className));
}

export function spentPoints() {
  let total = 0;
  AA_CATEGORY_KEYS.forEach((catKey) => {
    const list = getList(catKey);
    const store = getRanksStore(catKey);
    list.forEach((aa, idx) => {
      if (aa.auto) return; // automatically granted, doesn't draw from the point pool
      const r = store[idx] || 0;
      for (let i = 0; i < r; i++) total += costNum(aa.costs[i]);
    });
  });
  return total;
}

export function parsePrereqText(text) {
  if (!text) return null;
  const m = text.match(/^Requires\s+(.+?)\s+(?:rank|(?:at\s+)?level)\s+(\d+)\s*$/i);
  if (!m) return null;
  return { name: m[1].trim(), rank: parseInt(m[2], 10) };
}

export function resolvePrereqTarget(text, sourceCategory) {
  const parsed = parsePrereqText(text);
  if (!parsed) return null;
  const order = [];
  const seen = new Set();
  [sourceCategory, "general", "archetype", "special", ...CLASS_SLOT_KEYS].forEach((k) => {
    if (!seen.has(k)) { seen.add(k); order.push(k); }
  });
  for (const key of order) {
    const list = getList(key);
    let foundIdx = -1;
    list.forEach((aa, i) => { if (aa.name.toLowerCase() === parsed.name.toLowerCase()) foundIdx = i; });
    if (foundIdx >= 0) return { category: key, idx: foundIdx, requiredRank: parsed.rank };
  }
  return null;
}

// Structural reasons (level / prerequisite) that permanently block a rank regardless of points.
export function structuralLockReason(catKey, idx) {
  const aa = getList(catKey)[idx];
  const levelReq = parseInt(aa.levelReq, 10) || 1;
  if (state.charLevel < levelReq) return `Requires character level ${levelReq}.`;
  if (aa.prereq) {
    const resolved = resolvePrereqTarget(aa.prereq, catKey);
    if (resolved) {
      const targetRank = effectiveRank(resolved.category, resolved.idx);
      if (targetRank < resolved.requiredRank) {
        const targetAA = getList(resolved.category)[resolved.idx];
        return `Requires ${targetAA ? targetAA.name : "prerequisite"} rank ${resolved.requiredRank}.`;
      }
    }
  }
  return null;
}

// Full reason a rank can't be purchased right now, including affordability.
export function getBlockReason(catKey, idx) {
  const structural = structuralLockReason(catKey, idx);
  if (structural) return structural;
  const aa = getList(catKey)[idx];
  const rank = effectiveRank(catKey, idx);
  const nextCost = costNum(aa.costs[rank]);
  const remaining = state.totalPoints - spentPoints();
  if (remaining < nextCost) return `Not enough AA points remaining (need ${nextCost}).`;
  return null;
}

export function isDependedOn(category, idx, currentRank) {
  const newRank = currentRank - 1;
  for (const catKey of AA_CATEGORY_KEYS) {
    const list = getList(catKey);
    for (let i = 0; i < list.length; i++) {
      const aa = list[i];
      if (!aa.prereq) continue;
      if (effectiveRank(catKey, i) <= 0) continue;
      const r = resolvePrereqTarget(aa.prereq, catKey);
      if (r && r.category === category && r.idx === idx && newRank < r.requiredRank) return true;
    }
  }
  return false;
}

export function changeRank(category, idx, delta) {
  const store = getRanksStore(category);
  const aa = getList(category)[idx];
  const cur = store[idx] || 0;
  const next = cur + delta;
  if (next < 0 || next > aa.ranks) return;
  if (next === 0) delete store[idx]; else store[idx] = next;
  if (delta > 0) pushPurchase(category, idx);
  else popLastPurchase(category, idx);
  saveLocal();
  renderAll();
}

export function attemptIncrement(category, idx) {
  const aa = getList(category)[idx];
  if (aa.auto) { showToast(`${aa.name} is automatically granted — no points needed.`); return; }
  const rank = effectiveRank(category, idx);
  if (rank >= aa.ranks) return;
  const reason = getBlockReason(category, idx);
  if (reason) { showToast(reason); return; }
  changeRank(category, idx, 1);
}

export function attemptDecrement(category, idx) {
  const aa = getList(category)[idx];
  if (aa.auto) { showToast(`${aa.name} is automatically granted and can't be removed.`); return; }
  const rank = effectiveRank(category, idx);
  if (rank <= 0) return;
  if (isDependedOn(category, idx, rank)) {
    showToast("Can't lower this — another AA depends on the current rank.");
    return;
  }
  changeRank(category, idx, -1);
}

export function countPicked() {
  let n = 0;
  AA_CATEGORY_KEYS.forEach((catKey) => {
    getList(catKey).forEach((aa, idx) => { if (effectiveRank(catKey, idx) > 0) n++; });
  });
  return n;
}

// Shared by the Progression tab and the export text, so both always agree on
// step ranks, per-step cost, and the running cumulative total.
export function computeProgressionSteps() {
  const counts = {};
  let cumulative = 0;
  return state.purchaseOrder.map((entry, i) => {
    const key = entryKey(entry.scope, entry.className, entry.idx);
    const category = resolveEntryCategory(entry);
    const active = category !== null;
    const aa = entry.scope === "class" ? (AA_DATA.classes[entry.className] || [])[entry.idx] : (AA_DATA[entry.scope] || [])[entry.idx];
    const stepRank = (counts[key] || 0) + 1;

    let prereqWarn = false;
    if (active && aa && aa.prereq) {
      const resolved = resolvePrereqTarget(aa.prereq, category);
      if (resolved) {
        const t = categoryToScopeClassName(resolved.category);
        const targetKey = entryKey(t.scope, t.className, resolved.idx);
        if ((counts[targetKey] || 0) < resolved.requiredRank) prereqWarn = true;
      }
    }

    counts[key] = stepRank;

    const stepCost = active && aa ? costNum(aa.costs[stepRank - 1]) : 0;
    cumulative += stepCost;

    const label = entry.scope === "class" ? `${entry.className} AA` : labelFor(entry.scope);
    const name = aa ? aa.name : "(unknown AA)";

    return { index: i, aa, active, stepRank, stepCost, cumulative, prereqWarn, label, name };
  });
}
