// Cached DOM element references, populated once on init.

export const el = {};

export function cacheDom() {
  el.classSelects = [
    document.getElementById("classSelect0"),
    document.getElementById("classSelect1"),
    document.getElementById("classSelect2")
  ];
  el.levelInput = document.getElementById("levelInput");
  el.totalPointsInput = document.getElementById("totalPointsInput");
  el.spentValue = document.getElementById("spentValue");
  el.remainingValue = document.getElementById("remainingValue");
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
  el.copyExportBtn = document.getElementById("copyExportBtn");
  el.saveExportBtn = document.getElementById("saveExportBtn");
  el.closeExportBtn = document.getElementById("closeExportBtn");
  el.tabs = document.getElementById("tabs");
  el.calculatorView = document.getElementById("calculatorView");
  el.browseView = document.getElementById("browseView");
  el.summaryView = document.getElementById("summaryView");
  el.summaryHeader = document.getElementById("summaryHeader");
  el.summaryContent = document.getElementById("summaryContent");
  el.progressionView = document.getElementById("progressionView");
  el.progressionContent = document.getElementById("progressionContent");
  el.treeWrap = document.getElementById("treeWrap");
  el.sidePanel = document.getElementById("sidePanel");
  el.browseSearch = document.getElementById("browseSearch");
  el.browseFilter = document.getElementById("browseFilter");
  el.browseGrid = document.getElementById("browseGrid");
  el.toast = document.getElementById("toast");
  el.disclaimerBanner = document.getElementById("disclaimerBanner");
  el.dismissBannerBtn = document.getElementById("dismissBannerBtn");
}
