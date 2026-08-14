// Build export/import: the text format, the share-code encoding, share links, and modal wiring.

import { state, AA_CATEGORY_KEYS, applyLoaded, saveLocal, SAVE_FORMAT_VERSION, serializeRanks, serializePurchaseOrder, payloadOwnedHasContent, adoptImportedOwnedAsNewProfile } from "./state.js";
import { el } from "./dom.js";
import { getList, effectiveRank, labelFor, spentPoints, computeProgressionSteps, computeProgressionTimeline, clearLastMutation, reconcilePurchaseOrderCounts, loadIssuesSuffix } from "./logic.js";
import { clearActiveBuild, saveImportedBuild, confirmReplaceCurrentBuild, isActiveBuildTheImportedSlot } from "./builds.js";
import { renderAll, showToast, costDisplay } from "./render.js";
import { idForKey, entryForId } from "./keys.js";

// Wire-format version for BUILD_CODE specifically (share links, export
// text) — independent of state.js's SAVE_FORMAT_VERSION, which governs
// localStorage only and stays name-keyed (readable, no size pressure
// there). BUILD_CODE trades that readability for size: numeric AA ids
// instead of name keys, a positional array instead of a keyed object (v3+)
// - [v, c, l, r, p, o, w] - and (v4+) r/o stored columnar - [[ids...],
// [ranks...]] instead of [[id,rank],[id,rank],...]. Same information
// either way; separating same-typed values into their own runs just gives
// the compressor longer, more repetitive stretches to work with than an
// interleaved id/rank/id/rank/... sequence does - measured ~10-15%
// smaller on a realistic build, even after compression already ate most
// of the naive JSON-shrink number. A future field is still safe to add
// additively at the end (position 7, 8, ...) the same way o/w were once
// added to v2 without a version bump - an older, shorter array just
// destructures the new position as undefined, same as a missing object
// key always has. v2 (keyed object) and v3 (positional, pair-shaped r/o)
// both still decode - see expandCompactPayload/expandCompactRanks.
const BUILD_CODE_VERSION = 4;

// An AA missing from aaIds.js shouldn't happen for anything currently
// pickable (build_minify.py's invariant check + assign_aa_ids.py being run
// together keep them in sync) - degrades to "dropped" rather than guessed
// at, same as everywhere else this app handles an unresolved key.
function pushCompactRank(ids, ranks, scope, className, key, rank) {
  const id = idForKey(scope, className, key);
  if (id != null) { ids.push(id); ranks.push(rank); }
}

function compactRanksFor(ranksLike) {
  const serialized = serializeRanks(ranksLike);
  const ids = [];
  const ranks = [];
  ["general", "archetype", "special"].forEach((scope) => {
    const store = serialized[scope] || {};
    Object.keys(store).forEach((key) => pushCompactRank(ids, ranks, scope, null, key, store[key]));
  });
  Object.keys(serialized.classes || {}).forEach((className) => {
    const store = serialized.classes[className] || {};
    Object.keys(store).forEach((key) => pushCompactRank(ids, ranks, "class", className, key, store[key]));
  });
  return [ids, ranks];
}

// owned is per-build/per-profile (state.js's ownedProfileId), so it's
// unconditional here just like ranks/purchaseOrder/waypoints - it's this
// build's own data, not a separate account-wide pool an export would be
// reaching outside the plan to include. On the import side, an incoming
// `o` field always lands in its own fresh profile rather than touching
// the receiver's existing one - see maybeImportOwned below.
function buildCodeArray() {
  const compactPurchaseOrder = serializePurchaseOrder(state.purchaseOrder)
    .map((e) => idForKey(e.scope, e.className, e.key))
    .filter((id) => id != null);

  const compactOwned = compactRanksFor(state.owned);
  // Same unconditional treatment as owned above - plan structure ("get
  // these by 75 pts" is a statement about this ordering), same as ranks/
  // purchaseOrder. No AA identity involved (just a point total + label +
  // color), so no id lookup needed the way compactRanksFor needs for
  // ranks/owned - a bare [pts, label, color] triple per waypoint.
  const waypoints = state.waypoints.map((w) => [w.pts, w.label, w.color]);

  return [
    BUILD_CODE_VERSION,
    state.selectedClasses.map((name) => CLASS_LIST.indexOf(name)),
    state.charLevel,
    compactRanksFor(state.ranks),
    compactPurchaseOrder,
    // compactRanksFor always returns the 2-element [ids, ranks] pair -
    // check the ids array itself for actual entries, not the wrapper.
    compactOwned[0].length ? compactOwned : null,
    waypoints.length ? waypoints : null
  ];
}

// An id that no longer resolves (entryForId returns null - the AA was
// removed since this link's ranks were assigned their ids) is dropped, same
// degrade-gracefully philosophy as an unresolved name key elsewhere.
// Accepts either the current columnar shape (BUILD_CODE_VERSION 4+,
// [[ids...],[ranks...]]) or the older array-of-pairs shape (v2/v3,
// [[id,rank],[id,rank],...]) - columnar says which to expect, decided by
// expandCompactPayload from the code's own version number.
function expandCompactRanks(list, columnar) {
  const ranks = { general: {}, archetype: {}, special: {}, classes: {} };
  if (!list) return ranks;
  const pairs = columnar ? list[0].map((id, i) => [id, list[1][i]]) : list;
  pairs.forEach(([id, rank]) => {
    const entry = entryForId(id);
    if (!entry) return;
    if (entry.scope === "class") {
      ranks.classes[entry.className] = ranks.classes[entry.className] || {};
      ranks.classes[entry.className][entry.key] = rank;
    } else {
      ranks[entry.scope][entry.key] = rank;
    }
  });
  return ranks;
}

// Reconstructs the verbose, name-keyed shape applyLoaded already understands
// (the same shape a SAVE_FORMAT_VERSION 4 localStorage/legacy payload is in
// - an unrelated version number, see state.js) from a decoded compact
// BUILD_CODE payload, so applyLoaded itself never needs to know the compact
// format exists — only this file and keys.js do. Accepts the current
// positional-array shape (BUILD_CODE_VERSION 3+, [v,c,l,r,p,o,w]) or the
// older keyed-object shape (v2, {v,c,l,r,p,o?,w?}) - same fields either
// way, just normalized to plain variables up front so the rest of this
// function doesn't care which container they arrived in. r/o's own inner
// shape (columnar vs pair-array) is decided separately, by version.
function expandCompactPayload(compact) {
  const isArray = Array.isArray(compact);
  const v = isArray ? compact[0] : compact.v;
  const [c, l, r, p, o, w] = isArray
    ? compact.slice(1)
    : [compact.c, compact.l, compact.r, compact.p, compact.o, compact.w];
  const columnar = v >= 4;
  const purchaseOrder = (p || []).map((id) => {
    const entry = entryForId(id);
    return entry ? { scope: entry.scope, className: entry.className, key: entry.key } : null;
  }).filter(Boolean);
  return {
    v: SAVE_FORMAT_VERSION,
    selectedClasses: (c || []).map((i) => CLASS_LIST[i]).filter(Boolean),
    charLevel: l,
    // An older share code/link may still carry a `t` (totalPoints) field,
    // from before the point cap was removed - simply never read into
    // anything here, same graceful-ignore as any unrecognized field.
    ranks: expandCompactRanks(r, columnar),
    purchaseOrder,
    // Raw [pts, label] pairs, or absent/null on an older link/build
    // predating this field - either way applyLoaded's sanitizeWaypoints
    // call handles validating/clamping/defaulting, same as it does for a
    // verbose payload.
    waypoints: w || [],
    // null/absent only if the sender genuinely had nothing owned yet -
    // expandCompactRanks(null/undefined) degrades to the empty shape
    // either way. applyLoaded itself still never reads this (owned isn't
    // part of "the build" it applies); the import layer inspects it
    // separately via payloadOwnedHasContent before deciding whether to
    // create a fresh profile for it (see maybeImportOwned).
    owned: expandCompactRanks(o, columnar)
  };
}

// purchaseOrder is highly repetitive (one entry per rank bought, not per AA —
// a maxed 6-rank AA repeats the same scope/className/key six times), so
// compression beats every hand-rolled format short of assigning every AA a
// stable numeric id, which is a bigger change than this one. CompressionStream
// is the standard streams-based API for this; no library needed. Needs
// Firefox 113+ / Safari 16.4+ (mid-2023) - no feature-detection fallback,
// since that's an old floor for this app's audience; an unsupported browser
// fails on both encode and decode (share links / export text), not just one.
//
// Raw DEFLATE ("deflate-raw"), not gzip - same underlying compression, but
// without gzip's 10-byte header + 8-byte trailer (magic bytes, mtime, a
// CRC32, ...) that a code embedded in a URL/text blob has no use for.
// Same browser floor either way - every engine's initial CompressionStream
// shipped all three formats together, deflate-raw included. Saves a fixed
// ~24 base64 characters per code regardless of build size, which is most
// noticeable proportionally on an already-short link for a small build.
//
// Piped through a Blob's stream rather than manually writing to a
// writer - decodeBuildCode below tries more than one format in sequence
// on the same rejected input, and a manual writer.write()'s own promise
// goes unawaited/unhandled the moment the stream rejects, independently
// of the awaited read side a try/catch actually guards. Piping avoids
// that split entirely: every failure surfaces as the one promise this
// function already returns.
async function compress(bytes, format) {
  const stream = new Blob([bytes]).stream().pipeThrough(new CompressionStream(format));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

async function decompress(bytes, format) {
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream(format));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

function bytesToBase64(bytes) {
  let binary = "";
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary);
}

function base64ToBytes(b64) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

async function encodeBuildCode() {
  const bytes = new TextEncoder().encode(JSON.stringify(buildCodeArray()));
  return bytesToBase64(await compress(bytes, "deflate-raw"));
}

// gzip's fixed 2-byte magic number - the one format this app has ever
// compressed with that's actually self-identifying. deflate-raw (this
// app's current format) has no header at all by design, and neither does
// plain pre-compression JSON, so between those two there's nothing
// reliable to sniff - see decodeBuildCode's own fallback for how that
// gets resolved without it.
const GZIP_MAGIC_0 = 0x1f;
const GZIP_MAGIC_1 = 0x8b;

// Decodes every format this app has ever encoded with, so a link/export
// made before this exact format was current keeps working forever -
// format-sniffed on the bytes themselves rather than gated on
// BUILD_CODE_VERSION, which governs the JSON shape inside, not the bytes
// wrapping it. Checks gzip's magic bytes directly instead of just
// attempting every format in sequence and catching failures - a real,
// growing cost otherwise, since every format this app has ever moved away
// from adds one more guaranteed-failing attempt to the common case.
async function decodeBuildCode(code) {
  const bytes = base64ToBytes(code);
  let jsonBytes;
  if (bytes.length >= 2 && bytes[0] === GZIP_MAGIC_0 && bytes[1] === GZIP_MAGIC_1) {
    // An older share code/export, from when this app compressed with gzip
    // instead of raw deflate.
    jsonBytes = await decompress(bytes, "gzip");
  } else {
    try {
      jsonBytes = await decompress(bytes, "deflate-raw");
    } catch (e) {
      // Not gzip (checked above) and not valid deflate-raw either - a code
      // from before compression existed, plain UTF-8 JSON straight from
      // base64. Fall back to reading it that way so links/exports from
      // every era keep working.
      jsonBytes = bytes;
    }
  }
  const parsed = JSON.parse(new TextDecoder().decode(jsonBytes));
  // A compact payload (v2 keyed-object, v3+ positional-array - see
  // expandCompactPayload) needs expanding back to the name-keyed shape
  // applyLoaded understands; anything else (a verbose SAVE_FORMAT_VERSION
  // payload, or an old legacy shape) is already in that shape and passes
  // through as-is - applyLoaded's own v check handles that case from here.
  // Range check rather than an explicit per-version list - every compact
  // version so far (2, 3, 4, ...) has stayed compact-shaped, so there's
  // been no reason yet to expect that to stop.
  const v = Array.isArray(parsed) ? parsed[0] : parsed && parsed.v;
  return v >= 2 ? expandCompactPayload(parsed) : parsed;
}

// Standard base64 (as used in BUILD_CODE) uses +, /, and = padding, which are legal
// in a URL query value but get percent-encoded and look ugly, and occasionally get
// mangled by chat apps that "helpfully" reformat long links. Base64url (RFC 4648 §5)
// swaps those for -, _ and drops padding, so the shared link stays plain alphanumeric.
function toBase64Url(b64) {
  return b64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromBase64Url(b64url) {
  let b64 = b64url.replace(/-/g, "+").replace(/_/g, "/");
  while (b64.length % 4) b64 += "=";
  return b64;
}

export async function buildShareUrl() {
  const url = new URL(window.location.href);
  url.search = "";
  url.hash = "";
  url.searchParams.set("build", toBase64Url(await encodeBuildCode()));
  return url.toString();
}

// Called once on startup. If the URL has a ?build= param, offers to load it — with
// a confirmation if it would clobber an existing non-empty build — then strips the
// param from the address bar either way so a refresh doesn't re-prompt. Returns
// { applied, notice } rather than toasting directly — main.js combines this
// outcome with other load-time notices into one toast.
//
// localLoadResult is applyLoaded(loadLocal())'s result, from immediately
// before this runs — needed because a build that lost every point to a bad
// resync would otherwise read as empty, skip the confirm, and get silently
// overwritten here on the exact load where preserving the original save
// mattered most.
export async function applySharedBuildFromUrl(localLoadResult) {
  const params = new URLSearchParams(window.location.search);
  const raw = params.get("build");
  if (!raw) return { applied: false, notice: null };

  let json = null;
  try {
    json = await decodeBuildCode(fromBase64Url(raw));
  } catch (e) {
    json = null;
  }

  let applied = false;
  let notice = null;
  if (json) {
    const extraRisk = !!(localLoadResult && localLoadResult.droppedRanks > 0);
    // trustMatch: false when the active slot is the reused "imported" one -
    // proceeding is about to overwrite that exact slot via saveImportedBuild
    // below, so treating a match against it as "safely backed up" would
    // trust the very copy this operation is about to destroy. Open link A
    // with no edits, then link B: without this, the gate sees A "matching"
    // the imported slot, skips the prompt, and saveImportedBuild silently
    // overwrites A with B.
    const proceed = confirmReplaceCurrentBuild("load", "the shared build from this link", {
      extraRisk,
      trustMatch: !isActiveBuildTheImportedSlot()
    });
    if (proceed) {
      const result = applyLoaded(json);
      state.selectedNode = null;
      clearLastMutation();
      clearActiveBuild();
      const repaired = reconcilePurchaseOrderCounts();
      const ownedOutcome = maybeImportOwned(json);
      result.droppedRanks += ownedOutcome.dropped;
      saveLocal();
      saveImportedBuild();
      notice = `Loaded shared build from link — saved as "Imported Build" in Builds${loadIssuesSuffix(result, repaired)}${ownedNoticeSuffix(ownedOutcome)}`;
      applied = true;
    }
  } else {
    notice = "That share link's build data looks invalid";
  }

  const cleanUrl = new URL(window.location.href);
  cleanUrl.searchParams.delete("build");
  window.history.replaceState({}, "", cleanUrl.toString());
  return { applied, notice };
}

export async function buildExportText() {
  const spent = spentPoints();
  const lines = [];
  lines.push("EverQuest Legends - AA Build");
  lines.push(`Classes: ${state.selectedClasses.join(" / ")}`);
  lines.push(`Points Spent: ${spent}`);
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
    // Reuses computeProgressionTimeline (logic.js) rather than re-deriving
    // where a waypoint's boundary falls - the readable listing should show
    // the same divider placement the Progression tab itself does, not a
    // second, independently-computed opinion of it. Waypoints ride the
    // BUILD_CODE either way (unconditionally - see buildCodeArray), but
    // without this a human just reading the text has no way to see them at
    // all, unlike owned's [OWNED] marker a few lines below.
    computeProgressionTimeline(computeProgressionSteps()).forEach((entry) => {
      if (entry.type === "divider") {
        const labelPart = entry.label ? ` · ${entry.label}` : "";
        const reachedNote = entry.unreached ? " (not reached yet)" : "";
        lines.push(`  --- ${entry.pts} pts${labelPart} ---${reachedNote}`);
        return;
      }
      const s = entry;
      const maxRank = s.aa ? `/${s.aa.ranks}` : "";
      const suffix = s.active ? "" : " (class not currently selected)";
      const ownedSuffix = s.owned ? " [OWNED]" : "";
      // Mirrors the Progression tab's own row exactly, both pieces: a
      // guessed step (real cost still "?", stepCost forced to 0) shows its
      // "~N" estimate instead of a flat 0, and the running total blends the
      // same way s.blendedCumulative does there (see computeProgressionSteps)
      // instead of freezing through every guessed step. Only for an active
      // step - an inactive one's pill stays plain in the UI too (see
      // render.js), so costDisplay is skipped here the same way.
      const stepDisp = s.active && s.aa ? costDisplay(s.category, s.idx, s.stepRank - 1, s.aa.costs[s.stepRank - 1]) : { isGuess: false };
      const costText = stepDisp.isGuess ? stepDisp.text : s.stepCost;
      const totalText = s.blendedCumulative !== s.cumulative ? `~${s.blendedCumulative}` : s.cumulative;
      lines.push(`  ${s.index + 1}. ${s.name} rank ${s.stepRank}${maxRank} — ${costText} pt(s), ${totalText} total${suffix}${ownedSuffix}`);
    });
    lines.push("");
  }

  lines.push(`BUILD_CODE:${await encodeBuildCode()}`);
  return lines.join("\n");
}

export async function openExportModal() {
  el.exportText.value = "Generating…";
  el.shareLinkInput.value = "";
  el.exportModal.classList.remove("hidden");
  await regenerateExportContent();
}

// Re-populates both the export text and share link. A second call (an
// impatient re-click of the Export button while the first is still
// compressing) could resolve out of order - bail if a newer call has
// already started, so the fields never end up showing a stale result.
let exportGeneration = 0;
async function regenerateExportContent() {
  const generation = ++exportGeneration;
  const [text, url] = await Promise.all([buildExportText(), buildShareUrl()]);
  if (generation !== exportGeneration) return;
  el.exportText.value = text;
  el.shareLinkInput.value = url;
  el.exportText.focus();
  el.exportText.select();
}

export function closeExportModal() {
  el.exportModal.classList.add("hidden");
}

function copyFrom(inputEl, text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(
      () => showToast("Copied to clipboard"),
      () => fallbackCopyFrom(inputEl, text)
    );
  } else {
    fallbackCopyFrom(inputEl, text);
  }
}

function fallbackCopyFrom(inputEl, text) {
  inputEl.value = text;
  inputEl.select();
  try {
    document.execCommand("copy");
    showToast("Copied to clipboard");
  } catch (e) {
    showToast("Couldn't copy automatically — select and copy manually.");
  }
}

export function copyExportText() {
  copyFrom(el.exportText, el.exportText.value);
}

export function copyShareLink() {
  copyFrom(el.shareLinkInput, el.shareLinkInput.value);
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

// Accepts the full exported text (with a "BUILD_CODE:" line buried in it), a
// whole pasted share link (?build=... pulled out of it), or just the bare
// code on its own — standard base64 (export text) or base64url (share
// links), so pasting any of the things this app itself produces works.
function extractBuildCode(text) {
  const trimmed = text.trim();
  const m = trimmed.match(/BUILD_CODE:(\S+)/);
  if (m) return m[1];
  const urlMatch = trimmed.match(/[?&]build=([^&\s]+)/);
  if (urlMatch) return urlMatch[1];
  // Maybe they pasted just the bare code, possibly line-wrapped by whatever they copied
  // it from — strip all embedded whitespace before checking if it looks like base64/base64url.
  const compact = trimmed.replace(/\s+/g, "");
  if (compact.length > 20 && /^[A-Za-z0-9_+/-]+={0,2}$/.test(compact)) return compact;
  return null;
}

// Owned rides every export unconditionally (buildCodeArray), but importing
// one never touches the receiver's own owned tracking directly - an
// incoming `o` field always lands in its own brand-new profile
// (adoptImportedOwnedAsNewProfile) instead, silent and unconfirmed, since
// nothing existing is ever at risk of being overwritten. A no-op if the
// sender genuinely had nothing owned yet (no `o` field to begin with).
function maybeImportOwned(json) {
  if (!payloadOwnedHasContent(json.owned)) return { imported: false, dropped: 0, hadOwned: false };
  const result = adoptImportedOwnedAsNewProfile(json.owned);
  return { imported: true, dropped: result.dropped, hadOwned: true };
}

function ownedNoticeSuffix(ownedOutcome) {
  if (!ownedOutcome.hadOwned) return "";
  return " — owned progress included (tracked separately from your existing progress)";
}

export async function importBuildFromText(text) {
  const code = extractBuildCode(text);
  if (!code) { showToast("No build code found in that text"); return false; }
  // Decode before gating: the replace-confirmation chain (possibly several
  // dialogs deep) is pointless work - and a strange thing to interrogate the
  // user with - if what they pasted turns out to be unreadable garbage.
  let json;
  try {
    // fromBase64Url is a no-op on plain base64 (only touches -/_ chars and
    // pads to length%4, which export-text codes already satisfy), so it's
    // safe to always apply regardless of which format `code` came from.
    json = await decodeBuildCode(fromBase64Url(code));
  } catch (e) {
    showToast("Failed to read build text");
    return false;
  }
  if (!confirmReplaceCurrentBuild("import", "this build")) return false;
  try {
    const result = applyLoaded(json);
    state.selectedNode = null;
    clearLastMutation();
    clearActiveBuild();
    const repaired = reconcilePurchaseOrderCounts();
    const ownedOutcome = maybeImportOwned(json);
    result.droppedRanks += ownedOutcome.dropped;
    saveLocal();
    renderAll();
    showToast(`Build imported${loadIssuesSuffix(result, repaired)}${ownedNoticeSuffix(ownedOutcome)}`);
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

export async function doImport() {
  const text = el.importText.value.trim();
  if (!text) { showToast("Paste build text first"); return; }
  if (await importBuildFromText(text)) closeImportModal();
}
