// Build export/import: the text format, the share-code encoding, and the modal wiring.

import { state, AA_CATEGORY_KEYS, applyLoaded, saveLocal } from "./state.js";
import { el } from "./dom.js";
import { getList, effectiveRank, labelFor, spentPoints, computeProgressionSteps } from "./logic.js";
import { renderAll, showToast } from "./render.js";

export function buildExportText() {
  const spent = spentPoints();
  const lines = [];
  lines.push("EverQuest Legends - AA Build");
  lines.push(`Classes: ${state.selectedClasses.join(" / ")}`);
  lines.push(`Points Spent: ${spent} / ${state.totalPoints}`);
  lines.push(`Exported: ${new Date().toLocaleString()}`);
  lines.push("");

  AA_CATEGORY_KEYS.forEach((catKey) => {
    const list = getList(catKey);
    const spentAAs = list.map((aa, idx) => ({ aa, rank: effectiveRank(catKey, idx) })).filter((x) => x.rank > 0);
    if (!spentAAs.length) return;
    lines.push(`== ${labelFor(catKey)} ==`);
    spentAAs.forEach(({ aa, rank }) => lines.push(`  ${aa.name}: rank ${rank}/${aa.ranks}${aa.auto ? " (auto-granted)" : ""}`));
    lines.push("");
  });

  if (state.purchaseOrder.length) {
    lines.push("== Progression (click order) ==");
    computeProgressionSteps().forEach((s) => {
      const maxRank = s.aa ? `/${s.aa.ranks}` : "";
      const suffix = s.active ? "" : " (class not currently selected)";
      lines.push(`  ${s.index + 1}. ${s.name} rank ${s.stepRank}${maxRank} — ${s.stepCost} pt(s), ${s.cumulative} total${suffix}`);
    });
    lines.push("");
  }

  const codeObj = {
    v: 3,
    selectedClasses: state.selectedClasses,
    totalPoints: state.totalPoints,
    ranks: state.ranks,
    purchaseOrder: state.purchaseOrder
  };
  const code = btoa(unescape(encodeURIComponent(JSON.stringify(codeObj))));
  lines.push(`BUILD_CODE:${code}`);
  return lines.join("\n");
}

export function openExportModal() {
  el.exportText.value = buildExportText();
  el.exportModal.classList.remove("hidden");
  el.exportText.focus();
  el.exportText.select();
}

export function closeExportModal() {
  el.exportModal.classList.add("hidden");
}

export function copyExportText() {
  const text = el.exportText.value;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(
      () => showToast("Copied to clipboard"),
      () => fallbackCopy(text)
    );
  } else {
    fallbackCopy(text);
  }
}

export function fallbackCopy(text) {
  el.exportText.value = text;
  el.exportText.select();
  try {
    document.execCommand("copy");
    showToast("Copied to clipboard");
  } catch (e) {
    showToast("Couldn't copy automatically — select and copy manually.");
  }
}

export function saveExportAsTxt() {
  const blob = new Blob([el.exportText.value], { type: "text/plain" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `eql-aa-build-${state.selectedClasses.join("_").replace(/\s+/g, "_")}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(a.href);
  showToast("Saved as .txt");
}

// Accepts either the full exported text (with a "BUILD_CODE:" line buried in it)
// or just the bare base64 code on its own, so pasting either works.
export function extractBuildCode(text) {
  const trimmed = text.trim();
  const m = trimmed.match(/BUILD_CODE:(\S+)/);
  if (m) return m[1];
  // Maybe they pasted just the bare code, possibly line-wrapped by whatever they copied
  // it from — strip all embedded whitespace before checking if it looks like base64.
  const compact = trimmed.replace(/\s+/g, "");
  if (compact.length > 20 && /^[A-Za-z0-9+/]+={0,2}$/.test(compact)) return compact;
  return null;
}

export function importBuildFromText(text) {
  const code = extractBuildCode(text);
  if (!code) { showToast("No build code found in that text"); return false; }
  try {
    const json = JSON.parse(decodeURIComponent(escape(atob(code))));
    applyLoaded(json);
    state.selectedNode = null;
    saveLocal();
    renderAll();
    showToast("Build imported");
    return true;
  } catch (e) {
    showToast("Failed to read build text");
    return false;
  }
}

export function openImportModal() {
  el.importText.value = "";
  el.importModal.classList.remove("hidden");
  el.importText.focus();
}

export function closeImportModal() {
  el.importModal.classList.add("hidden");
}

export function doImport() {
  const text = el.importText.value.trim();
  if (!text) { showToast("Paste build text first"); return; }
  if (importBuildFromText(text)) closeImportModal();
}
