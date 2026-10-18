// Cached DOM element references, populated once on init.

export const el = {};

export function cacheDom() {
  el.classSelects = [
    document.getElementById("classSelect0"),
    document.getElementById("classSelect1"),
    document.getElementById("classSelect2")
  ];
  el.levelInput = document.getElementById("levelInput");
  el.spentValue = document.getElementById("spentValue");
  el.browseToggle = document.getElementById("browseToggle");
  el.exportBtn = document.getElementById("exportBtn");
  el.importBtn = document.getElementById("importBtn");
  el.importFile = document.getElementById("importFile");
  el.importModal = document.getElementById("importModal");
  el.importText = document.getElementById("importText");
  el.loadImportFileBtn = document.getElementById("loadImportFileBtn");
  el.doImportBtn = document.getElementById("doImportBtn");
  el.closeImportBtn = document.getElementById("closeImportBtn");
  el.resetBtn = document.getElementById("resetBtn");
  el.exportModal = document.getElementById("exportModal");
  el.exportText = document.getElementById("exportText");
  el.shareLinkInput = document.getElementById("shareLinkInput");
  el.copyShareLinkBtn = document.getElementById("copyShareLinkBtn");
  el.copyExportBtn = document.getElementById("copyExportBtn");
  el.saveExportBtn = document.getElementById("saveExportBtn");
  el.closeExportBtn = document.getElementById("closeExportBtn");
  el.tabs = document.getElementById("tabs");
  el.calculatorView = document.getElementById("calculatorView");
  el.browseView = document.getElementById("browseView");
  el.summaryView = document.getElementById("summaryView");
  el.summaryHeader = document.getElementById("summaryHeader");
  el.summaryContent = document.getElementById("summaryContent");
  el.otherClassesView = document.getElementById("otherClassesView");
  el.otherClassesContent = document.getElementById("otherClassesContent");
  el.progressionView = document.getElementById("progressionView");
  el.progressionWrap = document.getElementById("progressionWrap");
  el.progressionContent = document.getElementById("progressionContent");
  el.undoLastBtn = document.getElementById("undoLastBtn");
  el.ownedSummary = document.getElementById("ownedSummary");
  el.clearOwnedBtn = document.getElementById("clearOwnedBtn");
  el.manageOwnedTrackingBtn = document.getElementById("manageOwnedTrackingBtn");
  el.ownedTrackingModal = document.getElementById("ownedTrackingModal");
  el.ownedTrackingStatus = document.getElementById("ownedTrackingStatus");
  el.ownedTrackingBuildSelect = document.getElementById("ownedTrackingBuildSelect");
  el.ownedTrackingLinkBtn = document.getElementById("ownedTrackingLinkBtn");
  el.ownedTrackingMergeBtn = document.getElementById("ownedTrackingMergeBtn");
  el.ownedTrackingSplitBtn = document.getElementById("ownedTrackingSplitBtn");
  el.closeOwnedTrackingBtn = document.getElementById("closeOwnedTrackingBtn");
  el.addWaypointBtn = document.getElementById("addWaypointBtn");
  el.waypointChips = document.getElementById("waypointChips");
  el.waypointModal = document.getElementById("waypointModal");
  el.waypointModalTitle = document.getElementById("waypointModalTitle");
  el.waypointPtsInput = document.getElementById("waypointPtsInput");
  el.waypointLabelInput = document.getElementById("waypointLabelInput");
  el.waypointColorSwatches = document.getElementById("waypointColorSwatches");
  el.deleteWaypointBtn = document.getElementById("deleteWaypointBtn");
  el.cancelWaypointBtn = document.getElementById("cancelWaypointBtn");
  el.saveWaypointBtn = document.getElementById("saveWaypointBtn");
  el.treeWrap = document.getElementById("treeWrap");
  el.sidePanel = document.getElementById("sidePanel");
  el.globalSearch = document.getElementById("globalSearch");
  el.clearSearchBtn = document.getElementById("clearSearchBtn");
  el.showHiddenToggle = document.getElementById("showHiddenToggle");
  el.browseFilter = document.getElementById("browseFilter");
  el.browseUnownedToggle = document.getElementById("browseUnownedToggle");
  el.browseGrid = document.getElementById("browseGrid");
  el.toast = document.getElementById("toast");
  el.disclaimerBanner = document.getElementById("disclaimerBanner");
  el.dismissBannerBtn = document.getElementById("dismissBannerBtn");
  el.versionTag = document.getElementById("versionTag");
  el.changelogModal = document.getElementById("changelogModal");
  el.changelogContent = document.getElementById("changelogContent");
  el.changelogFade = document.getElementById("changelogFade");
  el.closeChangelogBtn = document.getElementById("closeChangelogBtn");
  el.buildsBtn = document.getElementById("buildsBtn");
  el.buildsModal = document.getElementById("buildsModal");
  el.buildSaveName = document.getElementById("buildSaveName");
  el.buildSaveBtn = document.getElementById("buildSaveBtn");
  el.buildsList = document.getElementById("buildsList");
  el.closeBuildsBtn = document.getElementById("closeBuildsBtn");
  el.resetModal = document.getElementById("resetModal");
  el.resetClearOwnedCheckbox = document.getElementById("resetClearOwnedCheckbox");
  el.confirmResetBtn = document.getElementById("confirmResetBtn");
  el.cancelResetBtn = document.getElementById("cancelResetBtn");
}

const FOCUSABLE = 'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])';
const modalReturnFocus = new Map();

// Shows a modal overlay and moves focus into it (to `target`, or its first
// control), remembering what had focus so closeModal can put it back.
export function openModal(overlay, target) {
  if (overlay.classList.contains("hidden")) modalReturnFocus.set(overlay, document.activeElement);
  overlay.classList.remove("hidden");
  const first = target || overlay.querySelector(FOCUSABLE);
  if (first) first.focus();
}

export function closeModal(overlay) {
  if (overlay.classList.contains("hidden")) return;
  overlay.classList.add("hidden");
  const back = modalReturnFocus.get(overlay);
  modalReturnFocus.delete(overlay);
  if (back && back.isConnected && typeof back.focus === "function") back.focus();
}

// Keeps Tab and Shift+Tab inside the open modal, wrapping at either end.
export function trapModalFocus(e) {
  if (e.key !== "Tab") return;
  const overlay = Array.from(document.querySelectorAll(".modal-overlay:not(.hidden)")).pop();
  if (!overlay) return;
  const items = Array.from(overlay.querySelectorAll(FOCUSABLE)).filter((n) => n.getClientRects().length > 0);
  if (!items.length) return;
  const first = items[0];
  const last = items[items.length - 1];
  const active = document.activeElement;
  if (!overlay.contains(active)) {
    e.preventDefault();
    first.focus();
  } else if (e.shiftKey && active === first) {
    e.preventDefault();
    last.focus();
  } else if (!e.shiftKey && active === last) {
    e.preventDefault();
    first.focus();
  }
}
