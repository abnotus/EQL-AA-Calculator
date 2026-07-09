// Stable per-AA keys, derived from name (not array position), used at the
// state-persistence boundary: localStorage, exported build text, and share
// links. Runtime code everywhere else still addresses AAs by their index into
// AA_DATA — only saving/loading goes through here.
//
// Why this exists: state.ranks and purchaseOrder used to store raw array
// indexes directly. That's fine in memory, but AA_DATA gets regenerated from
// eqlwiki periodically (see wiki-sync/), and a fresh scrape can reorder or
// insert entries. An index saved against yesterday's ordering silently means
// a different ability today — not an error, a wrong-but-plausible build. Name
// keys survive reordering/insertion, and degrade gracefully (an unknown key
// is just dropped) instead of resolving to the wrong AA.
//
// No internal deps: reads the global AA_DATA (from data.js, loaded before
// this runs) plus the frozen LEGACY_AA_ORDER snapshot below, which captures
// AA_DATA's exact ordering (and, where needed to disambiguate a duplicate
// name, its `auto` flag) as of 2026-07-09 — the last point before any AA
// data was index-addressed. It exists only to translate old index-based
// saves (from before this file existed) into name keys on load, and must
// never be regenerated/updated after the fact, or it stops describing what
// those old saves actually meant.
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
// doesn't repeat just gets its slug. A name that repeats is disambiguated by
// auto-ness, not position: build_minify.py's invariant check guarantees
// exactly one non-auto occurrence per repeated name within a category, so
// that one gets the bare slug (nothing else can mean it), and any auto
// occurrence(s) get -auto / -auto-2 / ... among themselves. This is the same
// discriminator resolvePrereqTarget's duplicate-name tie-break uses (see
// logic.js) — deriving from *content*, not array position, means reordering
// the source data can't silently repoint an old save at the wrong AA.
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
