// Build export/import: the text format, the share-code encoding, share links, and modal wiring.

import { state, AA_CATEGORY_KEYS, applyLoaded, saveLocal, SAVE_FORMAT_VERSION, serializeRanks, serializePurchaseOrder, payloadOwnedHasContent, adoptImportedOwnedAsNewProfile, WAYPOINT_COLORS } from "./state.js";
import { el } from "./dom.js";
import { getList, effectiveRank, labelFor, spentPoints, ownedPoints, computeProgressionSteps, computeProgressionTimeline, clearLastMutation, reconcilePurchaseOrderCounts, loadIssuesSuffix } from "./logic.js";
import { clearActiveBuild, saveImportedBuild, confirmReplaceCurrentBuild, isActiveBuildTheImportedSlot } from "./builds.js";
import { renderAll, showToast, costDisplayScoped } from "./render.js";
import { idForKey, entryForId } from "./keys.js";

// Wire-format version for BUILD_CODE specifically (share links, export
// text) — independent of state.js's SAVE_FORMAT_VERSION, which governs
// localStorage only and stays name-keyed (readable, no size pressure
// there).
//
// v5 (current, written by packV5) drops JSON entirely for packed bits,
// sized per field from each value's real enforced ceiling. JSON spends
// most of its bytes on structure - commas, brackets, and decimal digits
// for values that need 4-9 bits - and DEFLATE can only partly recover
// that. Measured 41-67% smaller than v4 across build sizes, ~43% on a
// realistic one, with no field dropped or approximated.
//
// v2-v4 are JSON and still decode, so every link ever issued keeps
// working: v2 is a keyed object, v3 a positional array [v,c,l,r,p,o,w],
// v4 the same array with r/o columnar ([[ids...],[ranks...]] rather than
// [[id,rank],...]). See expandCompactPayload/expandCompactRanks; the
// container around them (gzip, deflate-raw, or plain) is sniffed
// separately in decodeBuildCode.
const BUILD_CODE_VERSION = 5;

// A real build's own code is tiny - the largest known real-world build
// (183 picks) is a few hundred characters even uncompressed as v4 JSON.
// These are generous by 100x+ over any legitimate build, not a tight
// bound - they exist purely to reject an obviously-hostile input (a share
// link or pasted/imported text carrying a huge blob, or a small
// compressed payload crafted to decompress into an enormous one - a
// "decompression bomb") before spending memory/time on it, not to
// constrain what a real character's build can hold.
const MAX_ENCODED_CODE_LENGTH = 262144; // chars, base64/base64url text - checked before any decoding
const MAX_DECOMPRESSED_BYTES = 4 * 1024 * 1024; // bytes - checked while streaming out of DecompressionStream, never materialized past this

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

// Reads the decompressed stream chunk-by-chunk rather than materializing
// it in one shot (new Response(stream).arrayBuffer(), the previous
// approach) specifically so a decompression bomb - a small, legitimately-
// encoded compressed input engineered to expand far past
// MAX_DECOMPRESSED_BYTES - gets its stream cancelled the moment the running
// total crosses that cap, instead of first fully inflating into memory and
// only then being rejected.
async function decompress(bytes, format) {
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream(format));
  const reader = stream.getReader();
  const chunks = [];
  let total = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > MAX_DECOMPRESSED_BYTES) {
      await reader.cancel();
      throw new Error("decompressed payload exceeds the size limit");
    }
    chunks.push(value);
  }
  const out = new Uint8Array(total);
  let offset = 0;
  chunks.forEach((c) => { out.set(c, offset); offset += c.byteLength; });
  return out;
}

// ---- v5 binary wire format -------------------------------------------------
//
// A v5 code is packed bits, uncompressed. Everything before it was JSON run
// through DEFLATE; packed bits are already near-maximum entropy, so
// compressing them measurably costs bytes rather than saving them. That
// also gives up the integrity check DEFLATE was providing incidentally (a
// truncated stream fails to inflate), which is why V5 carries its own CRC.
//
// Byte 0 is a magic number no earlier format can start with: every one of
// them decodes to text beginning "[" (0x5B) or "{" (0x7B). decodeBuildCode
// checks it before attempting any decompression, so a v5 payload can never
// be mistaken for deflate-raw input that happens to inflate into garbage.
const V5_MAGIC = 0xe5;

// Field widths. Each is sized from the real enforced ceiling, not from
// what today's data happens to contain:
//   rank      - data.src.js's largest `ranks` is 26 (Ranger's Hunter's
//               Attack Power), and setOwnedRank (logic.js) doesn't clamp
//               on write, so 5 bits rather than the 4 a max of 10 implies.
//   id        - aaIds.js is append-only and never reuses an id, so the
//               ceiling grows with every wiki scrape; 9 bits leaves room.
//   pts       - MAX_WAYPOINT_PTS is 100000.
//   labelLen  - sanitizeWaypoints caps labels at 60 UTF-16 units, which is
//               up to 240 UTF-8 bytes.
const V5_BITS = {
  version: 4, idMode: 1, classSlot: 5, level: 6, id: 9, count: 9,
  rank: 5, poCount: 11, deltaCount: 8, wpCount: 8, pts: 17, color: 3, labelLen: 8
};
const V5_CLASS_NONE = 31; // CLASS_LIST.indexOf miss; applyLoaded rejects the set anyway

function bitWriter() {
  const bits = [];
  return {
    put(value, width) { bits.push((value >>> 0).toString(2).padStart(width, "0").slice(-width)); },
    putBits(str) { bits.push(str); },
    bytes() {
      let s = bits.join("");
      s += "0".repeat((8 - (s.length % 8)) % 8);
      const out = new Uint8Array(s.length / 8);
      for (let i = 0; i < out.length; i++) out[i] = parseInt(s.slice(i * 8, i * 8 + 8), 2);
      return out;
    }
  };
}

// Throws on running past the end rather than returning zeros - a truncated
// code must fail loudly, not decode into a plausible-looking short build.
function bitReader(bytes, startByte) {
  let pos = startByte * 8;
  const total = bytes.length * 8;
  function bit(i) { return (bytes[i >>> 3] >>> (7 - (i & 7))) & 1; }
  return {
    take(width) {
      if (pos + width > total) throw new Error("build code truncated");
      let v = 0;
      for (let i = 0; i < width; i++) v = (v << 1) | bit(pos + i);
      pos += width;
      return v >>> 0;
    },
    alignedByteOffset() { return (pos + 7) >>> 3; }
  };
}

// CRC-16/CCITT-FALSE. Small, no table, and enough to catch the truncation
// and single-character mangling that a copy-pasted link actually suffers.
function crc16(bytes, end) {
  let crc = 0xffff;
  for (let i = 0; i < end; i++) {
    crc ^= bytes[i] << 8;
    for (let b = 0; b < 8; b++) crc = crc & 0x8000 ? ((crc << 1) ^ 0x1021) & 0xffff : (crc << 1) & 0xffff;
  }
  return crc & 0xffff;
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

// How many bits an index into a list of `n` needs. A 1-entry list still
// needs 1 bit rather than 0, so the reader and writer agree on a width.
function indexWidth(n) {
  return Math.max(1, 32 - Math.clz32(Math.max(1, n - 1)));
}

// Packs one build. idMode 0 stores the AA ids as a bitmap over 0..highest,
// 1 stores them as an explicit list; which one wins depends entirely on the
// build (a handful of high-id class AAs is far cheaper explicitly than as a
// 130-bit mostly-empty bitmap), so packV5 gets called both ways and the
// smaller result is what ships. See encodeBuildCode.
function packV5(idMode) {
  const [plannedIds, plannedRanks] = compactRanksFor(state.ranks);
  const [ownedIds, ownedRanks] = compactRanksFor(state.owned);
  const planned = new Map();
  plannedIds.forEach((id, i) => planned.set(id, plannedRanks[i]));
  const owned = new Map();
  ownedIds.forEach((id, i) => owned.set(id, ownedRanks[i]));

  // Sorted so the bitmap form and the purchaseOrder indices share one
  // canonical ordering. The order itself carries no information - ranks
  // travel alongside their id either way.
  const ids = Array.from(planned.keys()).sort((a, b) => a - b);
  const slot = new Map();
  ids.forEach((id, i) => slot.set(id, i));

  const w = bitWriter();
  w.put(BUILD_CODE_VERSION, V5_BITS.version);
  w.put(idMode, V5_BITS.idMode);
  state.selectedClasses.forEach((name) => {
    const i = CLASS_LIST.indexOf(name);
    w.put(i < 0 ? V5_CLASS_NONE : i, V5_BITS.classSlot);
  });
  w.put(state.charLevel, V5_BITS.level);

  if (idMode === 0) {
    const hi = ids.length ? ids[ids.length - 1] : 0;
    w.put(hi, V5_BITS.id);
    // Always hi + 1 bits, so a zero-AA build writes a single "0" rather than
    // nothing. Both it and a build holding only id 0 store hi = 0, so an
    // empty bitmap would be indistinguishable from a set one bit wide.
    const present = new Array(hi + 1).fill("0");
    ids.forEach((id) => { present[id] = "1"; });
    w.putBits(present.join(""));
  } else {
    w.put(ids.length, V5_BITS.count);
    ids.forEach((id) => w.put(id, V5_BITS.id));
  }
  ids.forEach((id) => w.put(planned.get(id), V5_BITS.rank));

  // purchaseOrder entries index into this build's own id list, not the
  // global id space - 6 bits instead of 9 on a typical build, and it's the
  // single largest field.
  const po = serializePurchaseOrder(state.purchaseOrder)
    .map((e) => idForKey(e.scope, e.className, e.key))
    .filter((id) => id != null && slot.has(id));
  w.put(po.length, V5_BITS.poCount);
  const poWidth = indexWidth(ids.length);
  po.forEach((id) => w.put(slot.get(id), poWidth));

  // owned is near-perfectly redundant with planned in practice (an owned
  // rank almost always equals its planned rank - 42 of 43 on a real build),
  // so it rides as one bit per planned AA meaning "owned at the planned
  // rank", plus explicit (which, by how much) pairs only where the two
  // disagree. The pair carries its own index because the flags alone can't
  // say which owned entries differ.
  const ownedList = ids.filter((id) => owned.has(id));
  w.putBits(ids.map((id) => (owned.has(id) ? "1" : "0")).join(""));
  const diffs = [];
  ownedList.forEach((id, i) => {
    if (owned.get(id) !== planned.get(id)) diffs.push([i, planned.get(id) - owned.get(id)]);
  });
  const diffWidth = indexWidth(ownedList.length);
  w.put(diffs.length, V5_BITS.deltaCount);
  diffs.forEach(([i, d]) => { w.put(i, diffWidth); w.put(d, V5_BITS.rank); });

  const labels = [];
  w.put(state.waypoints.length, V5_BITS.wpCount);
  state.waypoints.forEach((wp) => {
    w.put(wp.pts, V5_BITS.pts);
    const ci = WAYPOINT_COLORS.findIndex((c) => c.key === wp.color);
    w.put(ci < 0 ? 0 : ci + 1, V5_BITS.color); // 0 = no color
    const bytes = new TextEncoder().encode(wp.label || "");
    w.put(bytes.length, V5_BITS.labelLen);
    labels.push(bytes);
  });

  // Labels sit after the bit region rather than inside it - they're
  // variable-length UTF-8, and byte-aligning them keeps the reader simple.
  const head = w.bytes();
  const labelLen = labels.reduce((n, b) => n + b.length, 0);
  const out = new Uint8Array(1 + head.length + labelLen + 2);
  out[0] = V5_MAGIC;
  out.set(head, 1);
  let at = 1 + head.length;
  labels.forEach((b) => { out.set(b, at); at += b.length; });
  const crc = crc16(out, at);
  out[at] = crc >>> 8;
  out[at + 1] = crc & 0xff;
  return out;
}

function expandBinaryPayload(bytes) {
  if (bytes.length < 4) throw new Error("build code truncated");
  const end = bytes.length - 2;
  const want = (bytes[end] << 8) | bytes[end + 1];
  if (crc16(bytes, end) !== want) throw new Error("build code failed its checksum");

  const r = bitReader(bytes, 1);
  const v = r.take(V5_BITS.version);
  if (v !== 5) throw new Error(`unsupported binary build code version ${v}`);
  const idMode = r.take(V5_BITS.idMode);
  const selectedClasses = [];
  for (let i = 0; i < 3; i++) {
    const ci = r.take(V5_BITS.classSlot);
    if (ci !== V5_CLASS_NONE && CLASS_LIST[ci]) selectedClasses.push(CLASS_LIST[ci]);
  }
  const charLevel = r.take(V5_BITS.level);

  let ids = [];
  if (idMode === 0) {
    const hi = r.take(V5_BITS.id);
    const width = hi + 1;
    const bits = [];
    for (let i = 0; i < width; i++) bits.push(r.take(1));
    bits.forEach((b, i) => { if (b) ids.push(i); });
  } else {
    const n = r.take(V5_BITS.count);
    for (let i = 0; i < n; i++) ids.push(r.take(V5_BITS.id));
  }
  const plannedRanks = ids.map(() => r.take(V5_BITS.rank));

  const poCount = r.take(V5_BITS.poCount);
  const poWidth = indexWidth(ids.length);
  const poIdx = [];
  for (let i = 0; i < poCount; i++) poIdx.push(r.take(poWidth));

  const ownedFlags = ids.map(() => r.take(1));
  const ownedIds = [];
  const ownedRanks = [];
  ids.forEach((id, i) => {
    if (!ownedFlags[i]) return;
    ownedIds.push(id);
    ownedRanks.push(plannedRanks[i]); // same-as-planned unless a delta says otherwise
  });
  const deltaCount = r.take(V5_BITS.deltaCount);
  const diffWidth = indexWidth(ownedIds.length);
  for (let k = 0; k < deltaCount; k++) {
    const i = r.take(diffWidth);
    const d = r.take(V5_BITS.rank);
    if (i < ownedRanks.length) ownedRanks[i] -= d;
  }

  const wpCount = r.take(V5_BITS.wpCount);
  const wpMeta = [];
  for (let i = 0; i < wpCount; i++) {
    wpMeta.push({
      pts: r.take(V5_BITS.pts),
      color: r.take(V5_BITS.color),
      len: r.take(V5_BITS.labelLen)
    });
  }
  let at = r.alignedByteOffset();
  const waypoints = wpMeta.map((m) => {
    const slice = bytes.subarray(at, at + m.len);
    if (at + m.len > end) throw new Error("build code truncated");
    at += m.len;
    return [m.pts, m.len ? new TextDecoder().decode(slice) : null,
      m.color === 0 ? null : (WAYPOINT_COLORS[m.color - 1] || {}).key || null];
  });

  // Reuses expandCompactRanks' id->AA resolution rather than duplicating it,
  // by handing it the same columnar shape v4 already produces.
  const purchaseOrder = poIdx.map((i) => {
    const entry = entryForId(ids[i]);
    return entry ? { scope: entry.scope, className: entry.className, key: entry.key } : null;
  }).filter(Boolean);

  return {
    v: SAVE_FORMAT_VERSION,
    selectedClasses,
    charLevel,
    ranks: expandCompactRanks([ids, plannedRanks], true),
    purchaseOrder,
    waypoints,
    owned: expandCompactRanks([ownedIds, ownedRanks], true)
  };
}

async function encodeBuildCode() {
  const bitmap = packV5(0);
  const explicit = packV5(1);
  return bytesToBase64(bitmap.length <= explicit.length ? bitmap : explicit);
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
  // Checked before base64ToBytes (which calls atob, itself an unbounded
  // allocation) rather than after - see MAX_ENCODED_CODE_LENGTH's own
  // comment for why this exists at all.
  if (code.length > MAX_ENCODED_CODE_LENGTH) throw new Error("build code exceeds the size limit");
  const bytes = base64ToBytes(code);
  // v5 is packed bits, not JSON, and isn't compressed - so it has to be
  // recognized here, ahead of both the decompression attempts and the
  // unconditional JSON.parse below. Checking the magic byte rather than
  // trying-and-failing also rules out raw binary that happens to be valid
  // deflate-raw input and would otherwise inflate into garbage.
  if (bytes.length && bytes[0] === V5_MAGIC) return expandBinaryPayload(bytes);
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
  const owned = ownedPoints();
  const lines = [];
  lines.push("EverQuest Legends - AA Build");
  lines.push(`Classes: ${state.selectedClasses.join(" / ")}`);
  lines.push(`Points Owned: ${owned}`);
  lines.push(`Points Planned: ${spent}`);
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
    lines.push("== Progression (pick order) ==");
    // Reuses computeProgressionTimeline (logic.js) rather than re-deriving
    // where a waypoint's boundary falls - the readable listing should show
    // the same divider placement the Progression tab itself does, not a
    // second, independently-computed opinion of it. Waypoints ride the
    // BUILD_CODE either way (unconditionally - see packV5), but
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
      const suffix = s.active ? "" : " (not one of your current 3 classes)";
      const ownedSuffix = s.owned ? " [OWNED]" : "";
      // Mirrors the Progression tab's own row exactly: a guessed step (real
      // cost still "?") shows its "~N" estimate instead of a flat 0, and the
      // running total blends the same way s.blendedCumulative does there
      // (see computeProgressionSteps) instead of freezing through every
      // guessed step. Scoped by (scope, className) rather than category so
      // this resolves the same way for a step whose class isn't active.
      const stepDisp = s.aa ? costDisplayScoped(s.scope, s.className, s.idx, s.stepRank - 1, s.aa.costs[s.stepRank - 1]) : { isGuess: false };
      const costText = stepDisp.isGuess ? stepDisp.text : s.stepCost;
      // Same conditional pluralization as the row's own cost-this pill in
      // render.js - a guessed cost keeps the literal "pt(s)" (matching that
      // pill), a real one properly pluralizes.
      const costUnit = stepDisp.isGuess ? "pt(s)" : `pt${s.stepCost === 1 ? "" : "s"}`;
      const totalText = s.blendedCumulative !== s.cumulative ? `~${s.blendedCumulative}` : s.cumulative;
      lines.push(`  ${s.index + 1}. ${s.name} rank ${s.stepRank}${maxRank} — ${costText} ${costUnit}, ${totalText} total${suffix}${ownedSuffix}`);
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
  // The length floor only exists to stop a short scrap of prose being taken for a code;
  // it has to stay under the smallest real one, and v5 packs a minimal build into
  // roughly 16 characters (a v4 code for the same build was over 40).
  const compact = trimmed.replace(/\s+/g, "");
  if (compact.length > 10 && /^[A-Za-z0-9_+/-]+={0,2}$/.test(compact)) return compact;
  return null;
}

// Owned rides every export unconditionally (packV5), but importing
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
