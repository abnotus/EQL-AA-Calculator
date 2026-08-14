// Entry point: wires everything together and boots the app on DOMContentLoaded.

import {
  state, loadLocal, applyLoaded, saveLocal, loadAndApplyOwned, loadAndApplyHidden,
  DISCLAIMER_DISMISSED_KEY, cleanupStaleStorageKeys, migrateLegacyOwnedProfile, LEGACY_OWNED_PROFILE_ID
} from "./state.js";
import { cacheDom, el } from "./dom.js";
import { populateStaticControls, renderAll, showToast } from "./render.js";
import { findInvalidatedPicks, reconcilePurchaseOrderCounts } from "./logic.js";
import { wireEvents } from "./events.js";
import { applySharedBuildFromUrl } from "./exportImport.js";
import { migrateStaleBuildSlots, cleanupOrphanedOwnedProfiles } from "./builds.js";

async function init() {
  cacheDom();
  populateStaticControls();
  // Must run before loadAndApplyOwned below, which reads from whichever
  // profile the current session ends up pointing at - if that's the
  // shared legacy one, its content needs to already be copied over.
  migrateLegacyOwnedProfile();
  // Must run before anything could call activeBuildMatchesCurrent() and
  // compare a saved slot against today's payload - see migrateStaleBuildSlots.
  migrateStaleBuildSlots();
  const rawLocal = loadLocal();
  const localResult = applyLoaded(rawLocal);
  // ownedProfileId isn't part of applyLoaded's own contract (same as owned
  // itself - see state.js) since import/share-link payloads never carry
  // it and shouldn't disturb whatever's already tracking; boot is the one
  // caller that always wants to adopt the saved session's own value,
  // falling back to the shared legacy profile for a pre-migration save.
  state.ownedProfileId = (rawLocal && typeof rawLocal.ownedProfileId === "string" && rawLocal.ownedProfileId) || LEGACY_OWNED_PROFILE_ID;
  // Owned loads from that profile now, independent of whichever build ends
  // up active below (see state.js). Folded into localResult.droppedRanks
  // so the notice below and applySharedBuildFromUrl's extraRisk gate both
  // account for it already.
  const ownedResult = loadAndApplyOwned(rawLocal);
  localResult.droppedRanks += ownedResult.droppedOwned;
  // Hidden, like owned, loads independently of whichever build ends up
  // active - no dropped-count to fold in, since a since-removed AA's
  // hidden entry is just silently skipped, not worth a load-time notice.
  loadAndApplyHidden();
  // If a share link applies, it replaces whatever localStorage just loaded.
  // Neither path toasts directly - this function assembles and shows one
  // combined load-time notice instead of several overwriting each other.
  const shared = await applySharedBuildFromUrl(localResult);
  wireEvents();
  cleanupStaleStorageKeys();
  // Must run after applySharedBuildFromUrl above, which can itself mint a
  // fresh owned profile (an incoming share link carrying owned data) that
  // needs to already count as "referenced" before anything unreferenced
  // gets swept.
  cleanupOrphanedOwnedProfiles();
  try {
    if (!localStorage.getItem(DISCLAIMER_DISMISSED_KEY)) el.disclaimerBanner.classList.remove("hidden");
  } catch (e) {
    el.disclaimerBanner.classList.remove("hidden");
  }

  const notices = [];
  if (shared.notice) notices.push(shared.notice);
  if (!shared.applied && localResult.droppedRanks) {
    const n = localResult.droppedRanks;
    notices.push(`${n} saved pick${n === 1 ? "" : "s"} no longer exist${n === 1 ? "s" : ""} in the current data and ${n === 1 ? "was" : "were"} skipped`);
  }
  // purchaseOrder can end up with a different entry count than the rank
  // actually held for an AA (see reconcilePurchaseOrderCounts) - repair it
  // before the first render, since computeProgressionSteps would otherwise
  // display a rank number that disagrees with the tree/side panel.
  const repaired = reconcilePurchaseOrderCounts();
  if (repaired) {
    notices.push(`${repaired} pick${repaired === 1 ? "'s" : "s'"} purchase history was out of sync and ${repaired === 1 ? "was" : "were"} repaired`);
  }
  // Persisting a repair is safe - it's a lossless normalization of state
  // already in memory. Persisting a drop is not: localStorage is this
  // path's only copy of the build, so writing back with a dropped AA
  // missing risks turning a recoverable loss into a permanent one. Only
  // persist when something was actually repaired, and never on the same
  // load a drop happened - the drop notice recurs every visit until the
  // data is fixed, which is the point.
  //
  // This only protects against the load itself overwriting the save - any
  // normal interaction afterward (changeRank, an import, accepting a share
  // link) still calls saveLocal() and persists whatever's in memory,
  // dropped picks included. It buys a chance to notice and back up before
  // that happens, not a guarantee.
  if (!shared.applied && repaired > 0 && !localResult.droppedRanks) saveLocal();
  // Data can drift out from under a saved build (a resync renaming/reshaping a
  // prereq target, or reselecting classes away from a class-rank-cap AA's
  // qualifying class, say) — catch it once on load rather than leaving the
  // user to discover a quietly-broken pick on their own.
  const invalidated = findInvalidatedPicks();
  if (invalidated.length) {
    const n = invalidated.length;
    notices.push(`${n} pick${n === 1 ? "" : "s"} no longer meet${n === 1 ? "s" : ""} its requirements — check the highlighted AAs`);
  }
  if (notices.length) {
    showToast(notices.join("; "));
  }
  renderAll();
}

document.addEventListener("DOMContentLoaded", init);
