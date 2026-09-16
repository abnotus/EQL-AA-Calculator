// All addEventListener wiring, run once from main.js after cacheDom().

import { state, CLASS_SLOT_KEYS, DISCLAIMER_DISMISSED_KEY, saveLocal } from "./state.js";
import { el } from "./dom.js";
import { clearAllOwned } from "./logic.js";
import {
  renderAll, showToast, renderBrowse, undoLast,
  openChangelogModal, closeChangelogModal, wireProgressionDropZone,
  openBuildsModal, closeBuildsModal, handleBuildSave,
  openResetModal, closeResetModal, handleConfirmReset,
  openWaypointModal, closeWaypointModal, handleSaveWaypoint, handleDeleteWaypoint,
  closeMoveMenu,
  openOwnedTrackingModal, closeOwnedTrackingModal, handleOwnedTrackingLink,
  handleOwnedTrackingMerge, handleOwnedTrackingSplit
} from "./render.js";
import {
  openExportModal, copyExportText, copyShareLink, saveExportAsTxt, closeExportModal,
  openImportModal, closeImportModal, doImport
} from "./exportImport.js";
import { BUILDS_INDEX_KEY, dropCachedIndex } from "./builds.js";

export function wireEvents() {
  // Another tab's own save/rename/delete writes BUILDS_INDEX_KEY directly;
  // this only fires here (never in the tab that made the write), so it's
  // exactly the signal this tab's own cachedIndex needs to know it's stale.
  // Fixes the case where that other write happened arbitrarily long ago -
  // without this, this tab's cache would never learn about it no matter
  // how much later its own next save lands. Doesn't provide true mutual
  // exclusion: two tabs saving within the same short window, before either
  // one's event has been delivered, can still race and clobber each
  // other - this only closes the "permanently stale, event never checked"
  // gap, not every concurrent-write ordering.
  window.addEventListener("storage", (e) => {
    if (e.key === BUILDS_INDEX_KEY) dropCachedIndex();
  });

  el.classSelects.forEach((sel, i) => {
    sel.addEventListener("change", () => {
      const newValue = sel.value;
      const oldValue = state.selectedClasses[i];
      if (newValue === oldValue) return;
      const dupSlot = state.selectedClasses.findIndex((c, j) => j !== i && c === newValue);

      // A genuine replacement (oldValue leaving the 3-class combo) no
      // longer wipes its picks - they just stop being "active"
      // (resolveEntryCategory), staying visible in the Other Classes tab
      // and counted in spentPoints() until swapped back in.

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

  el.browseToggle.addEventListener("click", () => {
    state.activeView = state.activeView === "browse" ? "calculator" : "browse";
    renderAll();
  });

  el.exportBtn.addEventListener("click", openExportModal);
  el.copyExportBtn.addEventListener("click", copyExportText);
  el.copyShareLinkBtn.addEventListener("click", copyShareLink);
  el.saveExportBtn.addEventListener("click", saveExportAsTxt);
  el.closeExportBtn.addEventListener("click", closeExportModal);
  el.exportModal.addEventListener("click", (e) => { if (e.target === el.exportModal) closeExportModal(); });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (!el.exportModal.classList.contains("hidden")) closeExportModal();
    if (!el.importModal.classList.contains("hidden")) closeImportModal();
    if (!el.changelogModal.classList.contains("hidden")) closeChangelogModal();
    if (!el.buildsModal.classList.contains("hidden")) closeBuildsModal();
    if (!el.ownedTrackingModal.classList.contains("hidden")) closeOwnedTrackingModal();
    if (!el.resetModal.classList.contains("hidden")) closeResetModal();
    if (!el.waypointModal.classList.contains("hidden")) closeWaypointModal();
    closeMoveMenu();
  });

  el.versionTag.addEventListener("click", openChangelogModal);
  el.closeChangelogBtn.addEventListener("click", closeChangelogModal);
  el.changelogModal.addEventListener("click", (e) => { if (e.target === el.changelogModal) closeChangelogModal(); });

  el.buildsBtn.addEventListener("click", openBuildsModal);
  el.closeBuildsBtn.addEventListener("click", closeBuildsModal);
  el.buildsModal.addEventListener("click", (e) => { if (e.target === el.buildsModal) closeBuildsModal(); });
  el.buildSaveBtn.addEventListener("click", handleBuildSave);
  el.buildSaveName.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleBuildSave();
  });

  el.importBtn.addEventListener("click", openImportModal);
  el.loadImportFileBtn.addEventListener("click", () => el.importFile.click());
  el.importFile.addEventListener("change", () => {
    const file = el.importFile.files[0];
    if (!file) return;
    // Even the most verbose legitimate export (every AA in every class,
    // fully written out) is on the order of tens of KB - this is checked
    // before ever reading the file into memory as a string, well ahead of
    // decodeBuildCode's own MAX_ENCODED_CODE_LENGTH check on just the code
    // substring within it.
    if (file.size > 2 * 1024 * 1024) {
      showToast("That file is too large to be a build export.");
      el.importFile.value = "";
      return;
    }
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

  el.resetBtn.addEventListener("click", openResetModal);
  el.cancelResetBtn.addEventListener("click", closeResetModal);
  el.confirmResetBtn.addEventListener("click", handleConfirmReset);
  el.resetModal.addEventListener("click", (e) => { if (e.target === el.resetModal) closeResetModal(); });

  // Standalone counterpart to Reset Build's checkbox: clears owned progress
  // without touching the plan. No modal needed - just a yes/no on a
  // destructive action, so a plain confirm() is enough.
  el.clearOwnedBtn.addEventListener("click", () => {
    if (el.clearOwnedBtn.disabled) return;
    const ok = confirm("Clear owned progress for this build's tracking? This can't be undone, and won't affect your planned picks. If this build shares tracking with another (see Manage tracking…), that one is cleared too.");
    if (!ok) return;
    clearAllOwned();
    renderAll();
    showToast("Owned progress cleared");
  });

  el.manageOwnedTrackingBtn.addEventListener("click", openOwnedTrackingModal);
  el.closeOwnedTrackingBtn.addEventListener("click", closeOwnedTrackingModal);
  el.ownedTrackingModal.addEventListener("click", (e) => { if (e.target === el.ownedTrackingModal) closeOwnedTrackingModal(); });
  el.ownedTrackingLinkBtn.addEventListener("click", handleOwnedTrackingLink);
  el.ownedTrackingMergeBtn.addEventListener("click", handleOwnedTrackingMerge);
  el.ownedTrackingSplitBtn.addEventListener("click", handleOwnedTrackingSplit);

  el.addWaypointBtn.addEventListener("click", () => openWaypointModal());
  el.cancelWaypointBtn.addEventListener("click", closeWaypointModal);
  el.saveWaypointBtn.addEventListener("click", handleSaveWaypoint);
  el.deleteWaypointBtn.addEventListener("click", handleDeleteWaypoint);
  el.waypointModal.addEventListener("click", (e) => { if (e.target === el.waypointModal) closeWaypointModal(); });
  el.waypointLabelInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleSaveWaypoint();
  });
  el.waypointPtsInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleSaveWaypoint();
  });

  el.dismissBannerBtn.addEventListener("click", () => {
    el.disclaimerBanner.classList.add("hidden");
    try { localStorage.setItem(DISCLAIMER_DISMISSED_KEY, "1"); } catch (e) { /* storage unavailable, ignore */ }
  });

  el.undoLastBtn.addEventListener("click", undoLast);

  // Delegated on the never-recreated wrapper rather than per-node - renderTree
  // tears down and rebuilds every AA node on every render, so binding here
  // once avoids attaching (and discarding) a fresh listener per node per
  // render. The tree only ever shows state.activeTab's list, so that's the
  // node's category at click time.
  el.treeWrap.addEventListener("click", (e) => {
    const node = e.target.closest(".node");
    if (!node) return;
    state.selectedNode = { category: state.activeTab, idx: parseInt(node.dataset.idx, 10) };
    renderAll();
  });
  el.treeWrap.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " " && e.key !== "Spacebar") return;
    const node = e.target.closest(".node");
    if (!node) return;
    e.preventDefault();
    state.selectedNode = { category: state.activeTab, idx: parseInt(node.dataset.idx, 10) };
    renderAll();
  });

  wireProgressionDropZone();

  // Debounced rather than firing a full renderAll (rebuilds the tree/badges/
  // Browse from scratch) on every keystroke - short enough that typing still
  // feels immediate, long enough to collapse a fast typist's keystrokes into
  // one render instead of one per character.
  let searchDebounceTimer = null;
  el.globalSearch.addEventListener("input", () => {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
      state.browseSearch = el.globalSearch.value;
      renderAll();
    }, 120);
  });

  el.clearSearchBtn.addEventListener("click", () => {
    clearTimeout(searchDebounceTimer);
    state.browseSearch = "";
    el.globalSearch.value = "";
    el.globalSearch.focus();
    renderAll();
  });

  el.browseFilter.addEventListener("change", () => {
    state.browseFilter = el.browseFilter.value;
    renderBrowse();
  });

  el.showHiddenToggle.addEventListener("click", () => {
    state.showHidden = !state.showHidden;
    renderAll();
  });
}
