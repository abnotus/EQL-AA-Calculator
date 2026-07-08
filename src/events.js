// All addEventListener wiring, run once from main.js after cacheDom().

import { state, CLASS_SLOT_KEYS, DISCLAIMER_DISMISSED_KEY, saveLocal } from "./state.js";
import { el } from "./dom.js";
import { costNum, clearClassData } from "./logic.js";
import { renderAll, showToast, populateClassSelects, renderTree, renderBrowse } from "./render.js";
import {
  openExportModal, copyExportText, saveExportAsTxt, closeExportModal,
  openImportModal, closeImportModal, doImport
} from "./exportImport.js";

export function wireEvents() {
  el.classSelects.forEach((sel, i) => {
    sel.addEventListener("change", () => {
      const newValue = sel.value;
      const oldValue = state.selectedClasses[i];
      if (newValue === oldValue) return;
      const dupSlot = state.selectedClasses.findIndex((c, j) => j !== i && c === newValue);

      if (dupSlot < 0) {
        // Genuine replacement (not a swap) — oldValue is leaving the 3-class combo, so its
        // picks become invisible. Warn if it actually has anything spent, then wipe it clean
        // rather than leaving orphaned data sitting around indefinitely.
        const oldStore = state.ranks.classes[oldValue];
        const oldList = AA_DATA.classes[oldValue] || [];
        let oldSpent = 0;
        if (oldStore) {
          Object.keys(oldStore).forEach((key) => {
            const aa = oldList[key];
            if (!aa) return;
            const r = oldStore[key] || 0;
            for (let k = 0; k < r; k++) oldSpent += costNum(aa.costs[k]);
          });
        }
        if (oldSpent > 0) {
          const ok = confirm(`Switching Class ${i + 1} from ${oldValue} to ${newValue} will remove ${oldValue}'s AA picks (${oldSpent} point${oldSpent === 1 ? "" : "s"} spent) from this build. Continue?`);
          if (!ok) { populateClassSelects(); return; }
        }
        clearClassData(oldValue);
      }

      state.selectedClasses[i] = newValue;
      if (dupSlot >= 0) {
        state.selectedClasses[dupSlot] = oldValue;
        if (state.activeTab === CLASS_SLOT_KEYS[dupSlot]) state.selectedNode = null;
      }
      if (state.activeTab === CLASS_SLOT_KEYS[i]) state.selectedNode = null;
      saveLocal();
      renderAll();
    });
  });

  el.levelInput.addEventListener("change", () => {
    const v = parseInt(el.levelInput.value, 10);
    state.charLevel = isNaN(v) ? state.charLevel : Math.max(1, Math.min(50, v));
    saveLocal();
    renderAll();
  });

  el.totalPointsInput.addEventListener("change", () => {
    const v = parseInt(el.totalPointsInput.value, 10);
    state.totalPoints = isNaN(v) ? state.totalPoints : Math.max(0, v);
    saveLocal();
    renderAll();
  });

  el.browseToggle.addEventListener("click", () => {
    state.activeView = state.activeView === "browse" ? "calculator" : "browse";
    renderAll();
  });

  el.exportBtn.addEventListener("click", openExportModal);
  el.copyExportBtn.addEventListener("click", copyExportText);
  el.saveExportBtn.addEventListener("click", saveExportAsTxt);
  el.closeExportBtn.addEventListener("click", closeExportModal);
  el.exportModal.addEventListener("click", (e) => { if (e.target === el.exportModal) closeExportModal(); });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (!el.exportModal.classList.contains("hidden")) closeExportModal();
    if (!el.importModal.classList.contains("hidden")) closeImportModal();
  });

  el.importBtn.addEventListener("click", openImportModal);
  el.loadImportFileBtn.addEventListener("click", () => el.importFile.click());
  el.importFile.addEventListener("change", () => {
    const file = el.importFile.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      el.importText.value = String(reader.result);
      doImport();
    };
    reader.readAsText(file);
    el.importFile.value = "";
  });
  el.doImportBtn.addEventListener("click", doImport);
  el.closeImportBtn.addEventListener("click", closeImportModal);
  el.importModal.addEventListener("click", (e) => { if (e.target === el.importModal) closeImportModal(); });

  el.resetBtn.addEventListener("click", () => {
    if (!confirm("Reset all spent AA points across every category and class? This cannot be undone.")) return;
    state.ranks = { general: {}, archetype: {}, special: {}, classes: {} };
    state.purchaseOrder = [];
    state.selectedNode = null;
    saveLocal();
    renderAll();
    showToast("Build reset");
  });

  el.dismissBannerBtn.addEventListener("click", () => {
    el.disclaimerBanner.classList.add("hidden");
    try { localStorage.setItem(DISCLAIMER_DISMISSED_KEY, "1"); } catch (e) { /* storage unavailable, ignore */ }
  });

  el.browseSearch.addEventListener("input", () => {
    state.browseSearch = el.browseSearch.value;
    renderBrowse();
  });

  el.browseFilter.addEventListener("change", () => {
    state.browseFilter = el.browseFilter.value;
    renderBrowse();
  });

  window.addEventListener("resize", () => {
    if (state.activeView === "calculator") renderTree(state.activeTab);
  });
}
