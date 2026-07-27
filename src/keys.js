// Stable per-AA keys, derived from name (not array position), used at the
// state-persistence boundary: localStorage, exported build text, and share
// links. Runtime code elsewhere still addresses AAs by index into AA_DATA;
// only saving/loading goes through here, since AA_DATA gets regenerated
// from eqlwiki periodically and reordering would silently repoint an
// index-based save at the wrong AA. Name keys survive reordering and
// degrade gracefully (an unknown key is dropped) instead of resolving wrong.
//
// aaIds.js is a separate, smaller append-only numeric id table used only
// for the compact share/export format, where URL length matters;
// localStorage keeps using name keys directly.
//
// LEGACY_AA_ORDER is a frozen snapshot of AA_DATA's ordering as of
// 2026-07-09, the last point before AA data was index-addressed. It exists
// only to translate old index-based saves into name keys on load, must
// never be regenerated, and must never be deleted even once it feels
// obsolete — a legacy save that migrates cleanly isn't rewritten to v4
// form until the user's next actual mutation, so an untouched old save can
// sit in localStorage indefinitely without this table's help.

import { AA_ID_TABLE } from "./aaIds.js";
import { COST_GUESS_TABLE } from "./costGuesses.js";
import { EFFECT_GUESS_TABLE } from "./effectGuesses.js";

const LEGACY_AA_ORDER = {
  "general": [
    "Adamant Will", "Alchemy Mastery", "Baking Mastery", "Blacksmithing Mastery",
    "Brewing Mastery", "Circular Breathing", "Combat Agility", "Combat Fury",
    "Combat Stability", "Crafting Mastery", "Fear Resistance", "First Aid",
    "Fletching Mastery", "Foraging", "Gather Party", "Innate Eminence",
    "Innate Lung Capacity", "Innate Metabolism", "Innate Regeneration",
    "Innate Spell Resistance", "Jewel Craft Mastery", "Natural Durability",
    "Origin", "Packrat", "Permanent Illusion", "Pottery Mastery", "Quick Buff",
    "Steadfast Will", "Stoicism", "Tailoring Mastery"
  ],
  "archetype": [
    "Acrobatics", "Ambidexterity", "Burst of Power", "Companion's Discipline",
    "Critical Affliction", "Destructive Cascade", "Destructive Fury",
    "Double Riposte", "Exodus", "Finishing Blow", "Fury of Magic",
    "Healing Adept", "Healing Boon", "Healing Gift", "Improved Bash",
    "Innate Camouflage", "Innate Invis to Undead", "Intimidation",
    "Mass Group Buff", "Master of All", "Mastery of the Past", "Mend Companion",
    "Mental Clarity", "Mnemonic Retention", "Persistent Casting", "Pet Affinity",
    "Physical Enhancement", "Quick Damage", "Rampage", "Spell Casting Deftness",
    "Spell Casting Mastery", "Spell Casting Reinforcement",
    "Spell Casting Subtlety", "Thief's Intuition"
  ],
  "special": ["Banestrike"],
  "classes": {
    "Bard": ["Instrument Mastery", "Jam Fest", "Reaching Notes", "Scribble Notes", "Singing Mastery", "Symphonic Aura"],
    "Beastlord": ["Frenzy of Spirit", "Hobble of Spirits", "Paragon of Spirit", "Playing Possum"],
    "Berserker": ["Blood Rune", "Innate Power Strike", "Tireless Spirit", "Unbound Fury"],
    // The only duplicate name in the whole snapshot — recorded with explicit
    // auto flags (instead of plain strings) so the ordinal below can be
    // derived from *that*, not from which one happened to be listed first.
    "Cleric": [{ name: "Divine Aura", auto: true }, { name: "Divine Aura", auto: false }, "Bestow Divine Aura", "Purify Soul", "Turn Undead", "Unbound Boon"],
    "Druid": ["Enhanced Root", "Quick Evacuation", "Unbound Nature"],
    "Enchanter": ["Unbound Clarity"],
    "Magician": ["Companion's Fury", "Conjurer's Efficiency", "Elemental Form", "Turn Summoned", "Unbound Companion"],
    "Monk": ["Dragon Force", "Improved Mend", "Purify Body", "Rapid Feign"],
    "Necromancer": ["Dead Mesmerization", "Fear Storm", "Flesh to Bone", "Life Burn", "Unbound Affliction"],
    "Paladin": ["Act of Valor", "Divine Stun", "Holy Steed", "Lay on Hands", "Slay Undead", "Valiant Steed"],
    "Ranger": ["Hunter's Attack Power", "Innate Called Shot", "Unbounded Strikethrough", "Weapon Mastery of the Scout"],
    "Rogue": ["Chaotic Stab", "Escape", "Innate Sneakiness", "Purge Poison", "Shroud of Stealth"],
    "Shadow Knight": ["Unholy Steed", "Abyssal Steed", "Harm Touch", "Leech Touch", "Soul Abrasion"],
    "Shaman": ["Cannibalization", "Unbound Cascade"],
    "Warrior": ["Area Taunt", "Heroic Leap", "Innate Fighters Tenacity", "Unbound Wrath", "War Cry", "Warrior's Endurance"],
    "Wizard": ["Improved Familiar", "Mana Burn", "Quick Evacuation", "Strong Root", "Unbound Destruction"]
  }
};

function slugify(name) {
  return String(name || "")
    .toLowerCase()
    .replace(/'/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function normalizeEntry(e) {
  return typeof e === "string" ? { name: e, auto: false } : e;
}

// Stable key for position `idx` within `rawEntries` (name strings, or
// {name, auto} objects where auto-ness needs to be explicit). A name that
// doesn't repeat just gets its slug. A repeated name is disambiguated by
// auto-ness, not position: build_minify.py's invariant guarantees exactly
// one non-auto occurrence per repeated name, so that one gets the bare
// slug, and any auto occurrence(s) get -auto / -auto-2 / ... among
// themselves - the same discriminator resolvePrereqTarget's duplicate-name
// tie-break uses (logic.js).
function keyForEntryIdx(rawEntries, idx) {
  const entries = rawEntries.map(normalizeEntry);
  const entry = entries[idx];
  if (!entry) return null;
  const base = slugify(entry.name);
  const sameName = entries
    .map((e, i) => ({ auto: e.auto, i }))
    .filter((e) => slugify(entries[e.i].name) === base);
  if (sameName.length <= 1) return base;
  if (!entry.auto) return base;
  const autoSiblings = sameName.filter((e) => e.auto);
  const autoPos = autoSiblings.findIndex((e) => e.i === idx);
  return autoPos === 0 ? `${base}-auto` : `${base}-auto-${autoPos + 1}`;
}

function idxForEntryKey(rawEntries, key) {
  for (let i = 0; i < rawEntries.length; i++) {
    if (keyForEntryIdx(rawEntries, i) === key) return i;
  }
  return -1;
}

function currentList(scope, className) {
  return scope === "class" ? (AA_DATA.classes[className] || []) : (AA_DATA[scope] || []);
}

function currentEntries(scope, className) {
  return currentList(scope, className).map((aa) => ({ name: aa.name, auto: !!aa.auto }));
}

// The actual AA object at idx in today's AA_DATA, or null. Used to validate
// deserialized rank values against the AA's real max rank instead of trusting
// whatever number was in a save file.
export function aaAt(scope, className, idx) {
  return currentList(scope, className)[idx] || null;
}

function legacyEntries(scope, className) {
  return scope === "class" ? (LEGACY_AA_ORDER.classes[className] || []) : (LEGACY_AA_ORDER[scope] || []);
}

// idx into today's AA_DATA -> stable name key, for writing new saves.
export function keyForIdx(scope, className, idx) {
  return keyForEntryIdx(currentEntries(scope, className), idx);
}

// Stable name key -> idx into today's AA_DATA, for reading saves already in
// key form. -1 if that AA no longer exists under this scope/class.
export function idxForKey(scope, className, key) {
  return idxForEntryKey(currentEntries(scope, className), key);
}

// idx captured against the frozen pre-key ordering -> idx into today's
// AA_DATA, for migrating old index-based saves. -1 if that AA was renamed
// or removed since the snapshot was taken. Routed through the same
// auto-aware key both directions use (not a plain name lookup), so
// same-named rows (e.g. Cleric's two "Divine Aura" entries) map to their
// matching occurrence instead of both collapsing onto the first one.
export function currentIdxForLegacyIdx(scope, className, legacyIdx) {
  const entries = legacyEntries(scope, className);
  if (legacyIdx < 0 || legacyIdx >= entries.length) return -1;
  const key = keyForEntryIdx(entries, legacyIdx);
  if (!key) return -1;
  return idxForEntryKey(currentEntries(scope, className), key);
}

let idToEntryCache = null;
function idToEntry() {
  if (!idToEntryCache) {
    idToEntryCache = {};
    Object.keys(AA_ID_TABLE).forEach((idKey) => {
      const id = AA_ID_TABLE[idKey];
      const sep1 = idKey.indexOf(":");
      const sep2 = idKey.indexOf(":", sep1 + 1);
      const scope = idKey.slice(0, sep1);
      const className = idKey.slice(sep1 + 1, sep2) || null;
      const key = idKey.slice(sep2 + 1);
      idToEntryCache[id] = { scope, className, key };
    });
  }
  return idToEntryCache;
}

// (scope, className, name key) -> the stable small integer id for it, or
// null if this AA isn't in AA_ID_TABLE (shouldn't happen for anything
// currently in AA_DATA — see build_minify.py's check — but a defensively
// missing id degrades to null the same way an unresolved name key does).
export function idForKey(scope, className, key) {
  const idKey = `${scope}:${className || ""}:${key}`;
  return Object.prototype.hasOwnProperty.call(AA_ID_TABLE, idKey) ? AA_ID_TABLE[idKey] : null;
}

// Reverse of idForKey: a stable id -> { scope, className, key }, or null for
// an id the table doesn't recognize (an AA removed since that id was
// assigned — the id itself is never reused, so this is unambiguous).
export function entryForId(id) {
  return idToEntry()[id] || null;
}

// (scope, className, aaIdx, rankIdx) -> a pattern-inferred cost estimate
// for that one rank, or null. aaIdx picks the AA (via keyForIdx); rankIdx
// is the position within that AA's own costs array - a different axis, not
// identity. Callers are expected to only ask this when costs[rankIdx] is
// already "?" (see logic.js's costGuess); this function doesn't check that
// itself.
export function costGuessFor(scope, className, aaIdx, rankIdx) {
  const key = keyForIdx(scope, className, aaIdx);
  if (!key) return null;
  const idKey = `${scope}:${className || ""}:${key}`;
  const entry = COST_GUESS_TABLE[idKey];
  return entry ? (entry[rankIdx] || null) : null;
}

// Same shape as costGuessFor, one axis deeper: progIdx picks WHICH
// progression within the AA's description (order of appearance - a
// description can hold more than one, see effectGuesses.js's own header),
// rankIdx the slot position within THAT progression. Callers are expected
// to only ask this when the real slot text is already known to be "?"
// (see logic.js's effectGuess), same contract as costGuessFor.
export function effectGuessFor(scope, className, aaIdx, progIdx, rankIdx) {
  const key = keyForIdx(scope, className, aaIdx);
  if (!key) return null;
  const idKey = `${scope}:${className || ""}:${key}`;
  const entry = EFFECT_GUESS_TABLE[idKey];
  if (!entry) return null;
  const prog = entry[progIdx];
  return prog ? (prog[rankIdx] || null) : null;
}
