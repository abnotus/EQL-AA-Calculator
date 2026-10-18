// GENERATED FILE - do not edit directly. Source lives in src/*.js; run
// build_minify.py, which bundles them into this file and minifies it into
// app.js (the file index.html actually loads).
"use strict";
(() => {
  // src/aaIds.js
  var AA_ID_TABLE = {
    "general::adamant-will": 0,
    "general::alchemy-mastery": 1,
    "general::baking-mastery": 2,
    "general::blacksmithing-mastery": 3,
    "general::brewing-mastery": 4,
    "general::circular-breathing": 5,
    "general::combat-agility": 6,
    "general::combat-fury": 7,
    "general::combat-stability": 8,
    "general::crafting-mastery": 9,
    "general::fear-resistance": 10,
    "general::first-aid": 11,
    "general::fletching-mastery": 12,
    "general::foraging": 13,
    "general::gather-party": 14,
    "general::innate-eminence": 15,
    "general::innate-lung-capacity": 16,
    "general::innate-metabolism": 17,
    "general::innate-regeneration": 18,
    "general::innate-spell-resistance": 19,
    "general::jewel-craft-mastery": 20,
    "general::natural-durability": 21,
    "general::origin": 22,
    "general::packrat": 23,
    "general::permanent-illusion": 24,
    "general::pottery-mastery": 25,
    "general::quick-buff": 26,
    "general::steadfast-will": 27,
    "general::stoicism": 28,
    "general::tailoring-mastery": 29,
    "archetype::acrobatics": 30,
    "archetype::ambidexterity": 31,
    "archetype::burst-of-power": 32,
    "archetype::companions-discipline": 33,
    "archetype::critical-affliction": 34,
    "archetype::destructive-cascade": 35,
    "archetype::destructive-fury": 36,
    "archetype::double-riposte": 37,
    "archetype::exodus": 38,
    "archetype::finishing-blow": 39,
    "archetype::fury-of-magic": 40,
    "archetype::healing-adept": 41,
    "archetype::healing-boon": 42,
    "archetype::healing-gift": 43,
    "archetype::improved-bash": 44,
    "archetype::innate-camouflage": 45,
    "archetype::innate-invis-to-undead": 46,
    "archetype::intimidation": 47,
    "archetype::mass-group-buff": 48,
    "archetype::master-of-all": 49,
    "archetype::mastery-of-the-past": 50,
    "archetype::mend-companion": 51,
    "archetype::mental-clarity": 52,
    "archetype::mnemonic-retention": 53,
    "archetype::persistent-casting": 54,
    "archetype::pet-affinity": 55,
    "archetype::physical-enhancement": 56,
    "archetype::quick-damage": 57,
    "archetype::rampage": 58,
    "archetype::spell-casting-deftness": 59,
    "archetype::spell-casting-mastery": 60,
    "archetype::spell-casting-reinforcement": 61,
    "archetype::spell-casting-subtlety": 62,
    "archetype::thiefs-intuition": 63,
    "special::banestrike": 64,
    "class:Bard:instrument-mastery": 65,
    "class:Bard:jam-fest": 66,
    "class:Bard:reaching-notes": 67,
    "class:Bard:scribble-notes": 68,
    "class:Bard:singing-mastery": 69,
    "class:Bard:symphonic-aura": 70,
    "class:Beastlord:frenzy-of-spirit": 71,
    "class:Beastlord:hobble-of-spirits": 72,
    "class:Beastlord:paragon-of-spirit": 73,
    "class:Beastlord:playing-possum": 74,
    "class:Berserker:blood-rune": 75,
    "class:Berserker:innate-power-strike": 76,
    "class:Berserker:tireless-sprint": 77,
    "class:Berserker:unbound-fury": 78,
    "class:Cleric:innate-divine-healing": 79,
    "class:Cleric:divine-aura": 80,
    "class:Cleric:bestow-divine-aura": 81,
    "class:Cleric:purify-soul": 82,
    "class:Cleric:turn-undead": 83,
    "class:Cleric:unbound-boon": 84,
    "class:Druid:enhanced-root": 85,
    "class:Druid:quick-evacuation": 86,
    "class:Druid:unbound-nature": 87,
    "class:Enchanter:unbound-clarity": 88,
    "class:Magician:companions-fury": 89,
    "class:Magician:conjurers-efficiency": 90,
    "class:Magician:elemental-form": 91,
    "class:Magician:turn-summoned": 92,
    "class:Magician:unbound-companion": 93,
    "class:Monk:dragon-force": 94,
    "class:Monk:improved-mend": 95,
    "class:Monk:purify-body": 96,
    "class:Monk:rapid-feign": 97,
    "class:Necromancer:dead-mesmerization": 98,
    "class:Necromancer:fear-storm": 99,
    "class:Necromancer:flesh-to-bone": 100,
    "class:Necromancer:life-burn": 101,
    "class:Necromancer:unbound-affliction": 102,
    "class:Paladin:act-of-valor": 103,
    "class:Paladin:divine-stun": 104,
    "class:Paladin:holy-steed": 105,
    "class:Paladin:lay-on-hands": 106,
    "class:Paladin:slay-undead": 107,
    "class:Paladin:valiant-steed": 108,
    "class:Ranger:hunters-attack-power": 109,
    "class:Ranger:innate-called-shot": 110,
    "class:Ranger:unbounded-strikethrough": 111,
    "class:Ranger:weapon-mastery-of-the-scout": 112,
    "class:Rogue:chaotic-stab": 113,
    "class:Rogue:escape": 114,
    "class:Rogue:innate-sneakiness": 115,
    "class:Rogue:purge-poison": 116,
    "class:Rogue:shroud-of-stealth": 117,
    "class:Shadow Knight:unholy-steed": 118,
    "class:Shadow Knight:abyssal-steed": 119,
    "class:Shadow Knight:harm-touch": 120,
    "class:Shadow Knight:leech-touch": 121,
    "class:Shadow Knight:soul-abrasion": 122,
    "class:Shaman:cannibalization": 123,
    "class:Shaman:unbound-cascade": 124,
    "class:Warrior:area-taunt": 125,
    "class:Warrior:heroic-leap": 126,
    "class:Warrior:innate-fighters-tenacity": 127,
    "class:Warrior:unbound-wrath": 128,
    "class:Warrior:war-cry": 129,
    "class:Warrior:warriors-endurance": 130,
    "class:Wizard:improved-familiar": 131,
    "class:Wizard:mana-burn": 132,
    "class:Wizard:quick-evacuation": 133,
    "class:Wizard:strong-root": 134,
    "class:Wizard:unbound-destruction": 135,
    "class:Bard:unbound-versatility": 136,
    "class:Beastlord:unbound-ferocity": 137,
    "class:Enchanter:tricksters-misdirection": 138,
    "class:Monk:unbound-alacrity": 139,
    "class:Paladin:unbound-life": 140,
    "class:Rogue:unbound-lethality": 141,
    "class:Shadow Knight:unbound-drain": 142,
    "general::full-potential": 143,
    "archetype::point-blank-fire": 144,
    "general::widened-perception": 145
  };

  // src/costGuesses.js
  var COST_GUESS_TABLE = {
    "class:Magician:turn-summoned": { "2": { value: 9, confidence: "high", basedOn: ["Acrobatics", "Alchemy Mastery", "Burst of Power", "Critical Affliction", "Double Riposte", "Healing Boon", "Improved Mend", "Instrument Mastery", "Jam Fest", "Quick Damage", "Quick Evacuation", "Rapid Feign", "Singing Mastery", "Slay Undead", "Soul Abrasion", "Weapon Mastery of the Scout"] } }
  };

  // src/effectGuesses.js
  var EFFECT_GUESS_TABLE = {
    "special::banestrike": { "0": { "2": { value: 6, confidence: "very-low", basedOn: [], manual: true }, "3": { value: 8, confidence: "very-low", basedOn: [], manual: true } } }
  };

  // src/keys.js
  var RENAMED_KEYS = {
    "class:Berserker:tireless-spirit": "tireless-sprint"
  };
  var LEGACY_AA_ORDER = {
    "general": [
      "Adamant Will",
      "Alchemy Mastery",
      "Baking Mastery",
      "Blacksmithing Mastery",
      "Brewing Mastery",
      "Circular Breathing",
      "Combat Agility",
      "Combat Fury",
      "Combat Stability",
      "Crafting Mastery",
      "Fear Resistance",
      "First Aid",
      "Fletching Mastery",
      "Foraging",
      "Gather Party",
      "Innate Eminence",
      "Innate Lung Capacity",
      "Innate Metabolism",
      "Innate Regeneration",
      "Innate Spell Resistance",
      "Jewel Craft Mastery",
      "Natural Durability",
      "Origin",
      "Packrat",
      "Permanent Illusion",
      "Pottery Mastery",
      "Quick Buff",
      "Steadfast Will",
      "Stoicism",
      "Tailoring Mastery"
    ],
    "archetype": [
      "Acrobatics",
      "Ambidexterity",
      "Burst of Power",
      "Companion's Discipline",
      "Critical Affliction",
      "Destructive Cascade",
      "Destructive Fury",
      "Double Riposte",
      "Exodus",
      "Finishing Blow",
      "Fury of Magic",
      "Healing Adept",
      "Healing Boon",
      "Healing Gift",
      "Improved Bash",
      "Innate Camouflage",
      "Innate Invis to Undead",
      "Intimidation",
      "Mass Group Buff",
      "Master of All",
      "Mastery of the Past",
      "Mend Companion",
      "Mental Clarity",
      "Mnemonic Retention",
      "Persistent Casting",
      "Pet Affinity",
      "Physical Enhancement",
      "Quick Damage",
      "Rampage",
      "Spell Casting Deftness",
      "Spell Casting Mastery",
      "Spell Casting Reinforcement",
      "Spell Casting Subtlety",
      "Thief's Intuition"
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
    return String(name || "").toLowerCase().replace(/['‘’]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  }
  function normalizeEntry(e) {
    return typeof e === "string" ? { name: e, auto: false } : e;
  }
  function keyForEntryIdx(rawEntries, idx) {
    const entries = rawEntries.map(normalizeEntry);
    const entry = entries[idx];
    if (!entry) return null;
    const base = slugify(entry.name);
    const sameName = entries.map((e, i) => ({ auto: e.auto, i })).filter((e) => slugify(entries[e.i].name) === base);
    if (sameName.length <= 1) return base;
    if (!entry.auto) return base;
    const autoSiblings = sameName.filter((e) => e.auto);
    const autoPos = autoSiblings.findIndex((e) => e.i === idx);
    return autoPos === 0 ? `${base}-auto` : `${base}-auto-${autoPos + 1}`;
  }
  var SHARED_SCOPES = ["general", "archetype", "special"];
  var hasOwn = (obj, key) => !!obj && Object.prototype.hasOwnProperty.call(obj, key);
  function listIn(table, scope, className) {
    let list;
    if (scope === "class") list = hasOwn(table.classes, className) ? table.classes[className] : null;
    else if (SHARED_SCOPES.includes(scope)) list = table[scope];
    return Array.isArray(list) ? list : [];
  }
  function currentList(scope, className) {
    return listIn(AA_DATA, scope, className);
  }
  function currentEntries(scope, className) {
    return currentList(scope, className).map((aa) => ({ name: aa.name, auto: !!aa.auto }));
  }
  function aaAt(scope, className, idx) {
    return currentList(scope, className)[idx] || null;
  }
  function legacyEntries(scope, className) {
    return listIn(LEGACY_AA_ORDER, scope, className);
  }
  var entryKeyMapCache = /* @__PURE__ */ new Map();
  function entryKeyMaps(scope, className) {
    const cacheKey = `${scope}:${className || ""}`;
    let maps = entryKeyMapCache.get(cacheKey);
    if (!maps) {
      const entries = currentEntries(scope, className);
      const idxToKey = entries.map((_, idx) => keyForEntryIdx(entries, idx));
      const keyToIdx = /* @__PURE__ */ new Map();
      idxToKey.forEach((key, idx) => {
        if (key != null && !keyToIdx.has(key)) keyToIdx.set(key, idx);
      });
      maps = { idxToKey, keyToIdx };
      entryKeyMapCache.set(cacheKey, maps);
    }
    return maps;
  }
  function keyForIdx(scope, className, idx) {
    return entryKeyMaps(scope, className).idxToKey[idx] || null;
  }
  function idxForKey(scope, className, key) {
    const idx = entryKeyMaps(scope, className).keyToIdx.get(key);
    if (idx !== void 0) return idx;
    const renamedFrom = `${scope}:${className || ""}:${key}`;
    if (!hasOwn(RENAMED_KEYS, renamedFrom)) return -1;
    const renamed = RENAMED_KEYS[renamedFrom];
    const renamedIdx = entryKeyMaps(scope, className).keyToIdx.get(renamed);
    return renamedIdx === void 0 ? -1 : renamedIdx;
  }
  var legacyKeyCache = /* @__PURE__ */ new Map();
  function legacyKeys(scope, className) {
    const cacheKey = `${scope}:${className || ""}`;
    let keys = legacyKeyCache.get(cacheKey);
    if (!keys) {
      const entries = legacyEntries(scope, className);
      keys = entries.map((_, i) => keyForEntryIdx(entries, i));
      legacyKeyCache.set(cacheKey, keys);
    }
    return keys;
  }
  function currentIdxForLegacyIdx(scope, className, legacyIdx) {
    const keys = legacyKeys(scope, className);
    if (!Number.isInteger(legacyIdx) || legacyIdx < 0 || legacyIdx >= keys.length) return -1;
    return keys[legacyIdx] ? idxForKey(scope, className, keys[legacyIdx]) : -1;
  }
  var idToEntryCache = null;
  function idToEntry() {
    if (!idToEntryCache) {
      idToEntryCache = /* @__PURE__ */ new Map();
      Object.keys(AA_ID_TABLE).forEach((idKey) => {
        const id = AA_ID_TABLE[idKey];
        const sep1 = idKey.indexOf(":");
        const sep2 = idKey.indexOf(":", sep1 + 1);
        const scope = idKey.slice(0, sep1);
        const className = idKey.slice(sep1 + 1, sep2) || null;
        const key = idKey.slice(sep2 + 1);
        idToEntryCache.set(id, { scope, className, key });
      });
    }
    return idToEntryCache;
  }
  function idForKey(scope, className, key) {
    const idKey = `${scope}:${className || ""}:${key}`;
    return hasOwn(AA_ID_TABLE, idKey) ? AA_ID_TABLE[idKey] : null;
  }
  function entryForId(id) {
    return idToEntry().get(id) || null;
  }
  function costGuessFor(scope, className, aaIdx, rankIdx) {
    const key = keyForIdx(scope, className, aaIdx);
    if (!key) return null;
    const idKey = `${scope}:${className || ""}:${key}`;
    const entry = COST_GUESS_TABLE[idKey];
    return entry ? entry[rankIdx] || null : null;
  }
  function effectGuessFor(scope, className, aaIdx, progIdx, rankIdx) {
    const key = keyForIdx(scope, className, aaIdx);
    if (!key) return null;
    const idKey = `${scope}:${className || ""}:${key}`;
    const entry = EFFECT_GUESS_TABLE[idKey];
    if (!entry) return null;
    const prog = entry[progIdx];
    return prog ? prog[rankIdx] || null : null;
  }

  // src/state.js
  var MAX_WAYPOINT_PTS = 1e5;
  var MAX_CHAR_LEVEL = 50;
  var SAVE_FORMAT_VERSION = 4;
  var STORAGE_KEY = "eql_aa_builder_v1";
  var OWNED_STORAGE_KEY = "eql_aa_owned_v1";
  var LEGACY_OWNED_PROFILE_ID = "legacy";
  function ownedProfileIdOr(rawValue) {
    return typeof rawValue === "string" && rawValue || LEGACY_OWNED_PROFILE_ID;
  }
  function ownedStorageKeyFor(profileId) {
    return `eql_aa_owned_${profileId}`;
  }
  function genId() {
    return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
  }
  var DISCLAIMER_DISMISSED_KEY = "eql_aa_disclaimer_dismissed_v5";
  var HIDDEN_STORAGE_KEY = "eql_aa_hidden_v1";
  var STALE_DISCLAIMER_KEYS = [
    "eql_aa_disclaimer_dismissed",
    "eql_aa_disclaimer_dismissed_v2",
    "eql_aa_disclaimer_dismissed_v3",
    "eql_aa_disclaimer_dismissed_v4"
  ];
  function cleanupStaleStorageKeys() {
    try {
      STALE_DISCLAIMER_KEYS.forEach((k) => localStorage.removeItem(k));
    } catch (e) {
    }
  }
  var LAST_SEEN_VERSION_KEY = "eql_aa_last_seen_version";
  var CLASS_SLOT_KEYS = ["classSlot0", "classSlot1", "classSlot2"];
  var AA_CATEGORY_KEYS = ["general", "archetype", ...CLASS_SLOT_KEYS, "special"];
  var state = {
    selectedClasses: [CLASS_LIST[0], CLASS_LIST[1], CLASS_LIST[2]],
    charLevel: MAX_CHAR_LEVEL,
    ranks: { general: {}, archetype: {}, special: {}, classes: {} },
    purchaseOrder: [],
    // [{ scope: 'general'|'archetype'|'special'|'class', className?: string, idx: number }, ...] in click order
    // Real-world "I've actually trained this" watermark, same shape as ranks
    // (idx -> highest owned rank), identity-keyed by scope/className rather
    // than anything slot-relative, same reasoning as purchaseOrder. Independent
    // of ranks/purchaseOrder (the plan): owned tracks what's actually true
    // in-game, so Reset Build keeps it by default and it's persisted under
    // a profile-specific key (see ownedProfileId below) instead of any
    // build's payload - see loadAndApplyOwned/saveOwned.
    owned: { general: {}, archetype: {}, special: {}, classes: {} },
    // Which owned profile `owned` above is currently loaded from/saved to -
    // see ownedStorageKeyFor. Defaults to the shared legacy profile so a
    // fresh session behaves exactly like the old single-global-owned system
    // until something (a new saved build, an import carrying owned data, or
    // the Link/Merge/Split controls) diverges it. Part of the same payload
    // saveLocal() persists, so it survives reloads like selectedClasses does;
    // each saved Build slot carries its own copy of this field too (builds.js).
    ownedProfileId: LEGACY_OWNED_PROFILE_ID,
    // Same shape/identity-keying as owned, but a display preference rather
    // than real-world truth: which AAs to leave out of the tree/Browse grids.
    // Persisted under its own key (HIDDEN_STORAGE_KEY), never part of the
    // build payload/exports/share links - see loadAndApplyHidden/saveHidden.
    // Never suppresses an AA with rank > 0, no matter what this holds.
    hiddenAAs: { general: {}, archetype: {}, special: {}, classes: {} },
    // Whether hidden AAs are shown anyway right now - a session-only view
    // toggle (not persisted, same as browseSearch/browseFilter), not part of
    // hiddenAAs itself.
    showHidden: false,
    // Named point-total markers ({ pts, label, color }), sorted ascending and
    // deduped by pts. Unlike owned, these describe the PLAN itself, so they
    // live inside the build payload/slots/share codes, not a separate key.
    // Anchored to a point total rather than a list position or step reference
    // - a position would break under reorder/undo/reset; a point total just
    // gets re-derived against whatever the current order happens to be.
    waypoints: [],
    activeView: "calculator",
    // 'calculator' | 'browse' | 'summary' | 'progression'
    activeTab: "general",
    // 'general' | 'archetype' | 'classSlot0' | 'classSlot1' | 'classSlot2' | 'special'
    selectedNode: null,
    // { category, idx }
    browseSearch: "",
    browseFilter: "all",
    browseUnownedOnly: false
  };
  function mapIdxStoreToKeyed(source, toValue) {
    const out = { general: {}, archetype: {}, special: {}, classes: {} };
    ["general", "archetype", "special"].forEach((scope) => {
      const store = source[scope] || {};
      Object.keys(store).forEach((idxStr) => {
        const key = keyForIdx(scope, null, parseInt(idxStr, 10));
        if (key) out[scope][key] = toValue(store[idxStr]);
      });
    });
    const classes = source.classes || {};
    Object.keys(classes).forEach((className) => {
      const store = classes[className] || {};
      const outStore = {};
      Object.keys(store).forEach((idxStr) => {
        const key = keyForIdx("class", className, parseInt(idxStr, 10));
        if (key) outStore[key] = toValue(store[idxStr]);
      });
      if (Object.keys(outStore).length) out.classes[className] = outStore;
    });
    return out;
  }
  function serializeRanks(ranks) {
    return mapIdxStoreToKeyed(ranks, (v) => v);
  }
  function safeParseInt(value) {
    return typeof value === "number" || typeof value === "string" ? parseInt(value, 10) : NaN;
  }
  function clampRankValue(scope, className, idx, rawValue) {
    const aa = aaAt(scope, className, idx);
    if (!aa) return 0;
    const n = safeParseInt(rawValue);
    if (!Number.isFinite(n)) return 0;
    return Math.max(0, Math.min(aa.ranks, n));
  }
  function mapKeyedStoreToIdx(saved, resolveIdx, toValue, onDrop) {
    const out = { general: {}, archetype: {}, special: {}, classes: {} };
    if (!saved || typeof saved !== "object") return out;
    ["general", "archetype", "special"].forEach((scope) => {
      const store = saved[scope] || {};
      Object.keys(store).forEach((k) => {
        const idx = resolveIdx(scope, null, k);
        if (idx >= 0) out[scope][idx] = toValue(scope, null, idx, store[k]);
        else onDrop();
      });
    });
    const classes = saved.classes || {};
    Object.keys(classes).forEach((className) => {
      const store = classes[className] || {};
      const outStore = {};
      Object.keys(store).forEach((k) => {
        const idx = resolveIdx("class", className, k);
        if (idx >= 0) outStore[idx] = toValue("class", className, idx, store[k]);
        else onDrop();
      });
      if (Object.keys(outStore).length) out.classes[className] = outStore;
    });
    return out;
  }
  function safeSharedRankValue(value) {
    const n = safeParseInt(value);
    return Number.isFinite(n) ? n : 0;
  }
  function migrateSharedQuickEvacuation(ranksLike) {
    if (!ranksLike || typeof ranksLike !== "object") return;
    const classes = ranksLike.classes;
    if (!isObject(classes) || !isObject(classes.Wizard) || !("quick-evacuation" in classes.Wizard)) return;
    const fromWizard = safeSharedRankValue(classes.Wizard["quick-evacuation"]);
    delete classes.Wizard["quick-evacuation"];
    if (!isObject(classes.Druid)) classes.Druid = {};
    const fromDruid = safeSharedRankValue(classes.Druid["quick-evacuation"]);
    classes.Druid["quick-evacuation"] = Math.max(fromDruid, fromWizard);
  }
  function migrateSharedQuickEvacuationPurchaseOrder(purchaseOrder) {
    if (!Array.isArray(purchaseOrder)) return;
    purchaseOrder.forEach((e) => {
      if (e && e.key === "quick-evacuation" && e.scope === "class" && e.className === "Wizard") {
        e.className = "Druid";
      }
    });
  }
  function migrateSharedQuickEvacuationHidden(hiddenLike) {
    if (!hiddenLike || typeof hiddenLike !== "object") return;
    const classes = hiddenLike.classes;
    if (!isObject(classes) || !isObject(classes.Wizard)) return;
    const fromWizard = classes.Wizard["quick-evacuation"];
    if (fromWizard === void 0) return;
    delete classes.Wizard["quick-evacuation"];
    if (fromWizard) {
      if (!isObject(classes.Druid)) classes.Druid = {};
      classes.Druid["quick-evacuation"] = true;
    }
  }
  function deserializeRanks(saved, resolveIdx) {
    let dropped = 0;
    const ranks = mapKeyedStoreToIdx(saved, resolveIdx, clampRankValue, () => {
      dropped++;
    });
    return { ranks, dropped };
  }
  function serializeHidden(hidden) {
    return mapIdxStoreToKeyed(hidden, () => true);
  }
  function deserializeHidden(saved) {
    return mapKeyedStoreToIdx(saved, (scope, className, k) => idxForKey(scope, className, k), () => true, () => {
    });
  }
  function saveHidden() {
    try {
      localStorage.setItem(HIDDEN_STORAGE_KEY, JSON.stringify({ v: SAVE_FORMAT_VERSION, hidden: serializeHidden(state.hiddenAAs) }));
    } catch (e) {
    }
  }
  function loadAndApplyHidden() {
    try {
      const raw = localStorage.getItem(HIDDEN_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && parsed.hidden && typeof parsed.hidden === "object") {
          migrateSharedQuickEvacuationHidden(parsed.hidden);
          state.hiddenAAs = deserializeHidden(parsed.hidden);
          return;
        }
      }
    } catch (e) {
    }
    state.hiddenAAs = { general: {}, archetype: {}, special: {}, classes: {} };
  }
  function serializePurchaseOrder(purchaseOrder) {
    return (purchaseOrder || []).map((e) => {
      const key = keyForIdx(e.scope, e.className || null, e.idx);
      return key ? { scope: e.scope, className: e.className || null, key } : null;
    }).filter(Boolean);
  }
  var MAX_PURCHASE_ORDER = 2e3;
  function deserializePurchaseOrder(saved, entryIdOf, resolveIdx) {
    const list = Array.isArray(saved) ? saved.slice(0, MAX_PURCHASE_ORDER) : [];
    return list.map((e) => {
      if (!e || typeof e !== "object" || typeof e.scope !== "string") return null;
      const id = entryIdOf(e);
      if (id == null) return null;
      const idx = resolveIdx(e.scope, e.className || null, id);
      return idx >= 0 ? { scope: e.scope, className: e.className || null, idx } : null;
    }).filter(Boolean);
  }
  var MAX_WAYPOINTS = 200;
  var WAYPOINT_COLORS = [
    { key: "red", hex: "#d94c4c" },
    { key: "orange", hex: "#d98a3d" },
    { key: "yellow", hex: "#d9c23d" },
    { key: "green", hex: "#4c8c52" },
    { key: "teal", hex: "#3da6a0" },
    { key: "blue", hex: "#4c7fd9" },
    { key: "purple", hex: "#9c4cd9" }
  ];
  var WAYPOINT_COLOR_KEYS = new Set(WAYPOINT_COLORS.map((c) => c.key));
  function sanitizeWaypoints(list) {
    if (!Array.isArray(list)) return [];
    const byPts = /* @__PURE__ */ new Map();
    list.forEach((entry) => {
      let rawPts, rawLabel, rawColor;
      if (Array.isArray(entry)) [rawPts, rawLabel, rawColor] = entry;
      else if (entry && typeof entry === "object") {
        rawPts = entry.pts;
        rawLabel = entry.label;
        rawColor = entry.color;
      } else return;
      const pts = safeParseInt(rawPts);
      if (!Number.isFinite(pts) || pts < 0) return;
      const clamped = Math.min(pts, MAX_WAYPOINT_PTS);
      const label = typeof rawLabel === "string" && rawLabel.trim() ? rawLabel.trim().slice(0, 60) : null;
      const color = typeof rawColor === "string" && WAYPOINT_COLOR_KEYS.has(rawColor) ? rawColor : null;
      byPts.set(clamped, { label, color });
    });
    return Array.from(byPts.entries()).map(([pts, { label, color }]) => ({ pts, label, color })).sort((a, b) => a.pts - b.pts).slice(-MAX_WAYPOINTS);
  }
  function saveLocal() {
    try {
      const payload = {
        v: SAVE_FORMAT_VERSION,
        selectedClasses: state.selectedClasses,
        charLevel: state.charLevel,
        ranks: serializeRanks(state.ranks),
        purchaseOrder: serializePurchaseOrder(state.purchaseOrder),
        waypoints: state.waypoints,
        ownedProfileId: state.ownedProfileId
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    } catch (e) {
    }
  }
  function saveOwnedProfileTo(profileId, ownedLike) {
    try {
      localStorage.setItem(ownedStorageKeyFor(profileId), JSON.stringify({ v: SAVE_FORMAT_VERSION, savedAt: Date.now(), owned: serializeRanks(ownedLike) }));
      return true;
    } catch (e) {
      return false;
    }
  }
  function saveOwned() {
    saveOwnedProfileTo(state.ownedProfileId, state.owned);
  }
  function loadOwnedProfileRaw(profileId) {
    return readJsonFromStorage(ownedStorageKeyFor(profileId), isObject);
  }
  function refreshOwnedFromStorage() {
    const stored = loadOwnedProfileRaw(state.ownedProfileId);
    if (!stored || !isObject(stored.owned)) return;
    migrateSharedQuickEvacuation(stored.owned);
    state.owned = deserializeRanks(stored.owned, (scope, cls, key) => idxForKey(scope, cls, key)).ranks;
  }
  function migrateLegacyOwnedProfile() {
    try {
      const legacyRaw = localStorage.getItem(OWNED_STORAGE_KEY);
      if (!legacyRaw) return;
      const profileKey = ownedStorageKeyFor(LEGACY_OWNED_PROFILE_ID);
      if (localStorage.getItem(profileKey) != null) return;
      localStorage.setItem(profileKey, legacyRaw);
    } catch (e) {
    }
  }
  function listOwnedProfileIds() {
    const prefix = "eql_aa_owned_";
    const ids = [];
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (!key || !key.startsWith(prefix) || key === OWNED_STORAGE_KEY) continue;
        const id = key.slice(prefix.length);
        if (id !== LEGACY_OWNED_PROFILE_ID) ids.push(id);
      }
    } catch (e) {
    }
    return ids;
  }
  function removeOwnedProfile(profileId) {
    if (profileId === LEGACY_OWNED_PROFILE_ID) return;
    try {
      localStorage.removeItem(ownedStorageKeyFor(profileId));
    } catch (e) {
    }
  }
  function readJsonFromStorage(key, validate) {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (validate && !validate(parsed)) return null;
      return parsed;
    } catch (e) {
      return null;
    }
  }
  var isObject = (v) => !!v && typeof v === "object";
  function loadLocal() {
    return readJsonFromStorage(STORAGE_KEY, isObject);
  }
  function applyLoaded(loaded) {
    if (!loaded) return { droppedRanks: 0 };
    if (Array.isArray(loaded.selectedClasses) && loaded.selectedClasses.length === 3 && loaded.selectedClasses.every((c) => CLASS_LIST.includes(c)) && new Set(loaded.selectedClasses).size === 3) {
      state.selectedClasses = loaded.selectedClasses.slice();
    }
    const parsedLevel = safeParseInt(loaded.charLevel);
    if (Number.isFinite(parsedLevel)) {
      state.charLevel = Math.max(1, Math.min(MAX_CHAR_LEVEL, parsedLevel));
    }
    const isLegacy = !(typeof loaded.v === "number" && loaded.v >= 4);
    if (!isLegacy) {
      migrateSharedQuickEvacuation(loaded.ranks);
      migrateSharedQuickEvacuationPurchaseOrder(loaded.purchaseOrder);
    }
    let droppedRanks = 0;
    if (loaded.ranks && typeof loaded.ranks === "object") {
      const result = isLegacy ? deserializeRanks(loaded.ranks, (scope, cls, idxStr) => currentIdxForLegacyIdx(scope, cls, parseInt(idxStr, 10))) : deserializeRanks(loaded.ranks, (scope, cls, key) => idxForKey(scope, cls, key));
      state.ranks = result.ranks;
      droppedRanks = result.dropped;
    }
    if (Array.isArray(loaded.purchaseOrder)) {
      state.purchaseOrder = isLegacy ? deserializePurchaseOrder(loaded.purchaseOrder, (e) => typeof e.idx === "number" ? e.idx : null, (scope, cls, legacyIdx) => currentIdxForLegacyIdx(scope, cls, legacyIdx)) : deserializePurchaseOrder(loaded.purchaseOrder, (e) => typeof e.key === "string" ? e.key : null, (scope, cls, key) => idxForKey(scope, cls, key));
    }
    state.waypoints = sanitizeWaypoints(loaded.waypoints);
    return { droppedRanks };
  }
  function loadAndApplyOwned(rawMainPayload) {
    const stored = loadOwnedProfileRaw(state.ownedProfileId);
    if (stored && stored.owned && typeof stored.owned === "object") {
      migrateSharedQuickEvacuation(stored.owned);
      const result = deserializeRanks(stored.owned, (scope, cls, key) => idxForKey(scope, cls, key));
      state.owned = result.ranks;
      return { droppedOwned: result.dropped };
    }
    if (rawMainPayload && rawMainPayload.owned && typeof rawMainPayload.owned === "object") {
      migrateSharedQuickEvacuation(rawMainPayload.owned);
      const result = deserializeRanks(rawMainPayload.owned, (scope, cls, key) => idxForKey(scope, cls, key));
      state.owned = result.ranks;
      saveOwned();
      return { droppedOwned: result.dropped };
    }
    state.owned = { general: {}, archetype: {}, special: {}, classes: {} };
    return { droppedOwned: 0 };
  }
  function payloadOwnedHasContent(owned) {
    if (!owned || typeof owned !== "object") return false;
    if (Object.keys(owned.general || {}).length || Object.keys(owned.archetype || {}).length || Object.keys(owned.special || {}).length) return true;
    const classes = owned.classes || {};
    return Object.keys(classes).some((className) => Object.keys(classes[className] || {}).length > 0);
  }
  function adoptImportedOwnedAsNewProfile(ownedField) {
    const newId = genId();
    migrateSharedQuickEvacuation(ownedField);
    const result = deserializeRanks(ownedField, (scope, cls, key) => idxForKey(scope, cls, key));
    if (!saveOwnedProfileTo(newId, result.ranks)) return { dropped: result.dropped, saved: false };
    state.ownedProfileId = newId;
    state.owned = result.ranks;
    return { dropped: result.dropped, saved: true };
  }
  function linkOwnedProfile(targetProfileId) {
    state.ownedProfileId = targetProfileId;
    loadAndApplyOwned(null);
  }
  function splitOwnedProfile() {
    const newId = genId();
    if (!saveOwnedProfileTo(newId, state.owned)) return false;
    state.ownedProfileId = newId;
    return true;
  }
  function mergeOwnedProfileInto(sourceProfileId) {
    const sourceRaw = loadOwnedProfileRaw(sourceProfileId);
    if (!sourceRaw || !sourceRaw.owned || typeof sourceRaw.owned !== "object") return { merged: 0 };
    migrateSharedQuickEvacuation(sourceRaw.owned);
    const source = deserializeRanks(sourceRaw.owned, (scope, cls, key) => idxForKey(scope, cls, key)).ranks;
    refreshOwnedFromStorage();
    let merged = 0;
    function mergeStore(target, src) {
      Object.keys(src).forEach((idxStr) => {
        const idx = parseInt(idxStr, 10);
        const current = target[idx] || 0;
        if (src[idx] > current) {
          target[idx] = src[idx];
          merged++;
        }
      });
    }
    ["general", "archetype", "special"].forEach((scope) => mergeStore(state.owned[scope], source[scope]));
    Object.keys(source.classes).forEach((className) => {
      if (!state.owned.classes[className]) state.owned.classes[className] = {};
      mergeStore(state.owned.classes[className], source.classes[className]);
    });
    if (merged) saveOwned();
    return { merged };
  }

  // src/dom.js
  var el = {};
  function cacheDom() {
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
  var FOCUSABLE = 'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])';
  var modalReturnFocus = /* @__PURE__ */ new Map();
  function openModal(overlay, target) {
    if (overlay.classList.contains("hidden")) modalReturnFocus.set(overlay, document.activeElement);
    overlay.classList.remove("hidden");
    const first = target || overlay.querySelector(FOCUSABLE);
    if (first) first.focus();
  }
  function closeModal(overlay) {
    if (overlay.classList.contains("hidden")) return;
    overlay.classList.add("hidden");
    const back = modalReturnFocus.get(overlay);
    modalReturnFocus.delete(overlay);
    if (back && back.isConnected && typeof back.focus === "function") back.focus();
  }
  function trapModalFocus(e) {
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

  // src/changelogData.js
  var USER_CHANGELOG = [
    {
      version: "2.1.2",
      date: "2026-10-02",
      items: [
        "Quick Evacuation (Druid and Wizard) is now tracked as a single shared ability. Training it under either class adds to the same progress instead of two separate pools, matching how it actually works in game."
      ]
    },
    {
      version: "2.1.1",
      date: "2026-10-01",
      items: [
        "Share links and exports now keep your owned rank correctly when it's higher than your planned rank, or far from it. Links made before this update still open as before.",
        "Unmarking an AA that comes with free ranks no longer leaves it hidden from the Unowned Only filter.",
        "Move To now lands in the right spot when moving a step into a waypoint section.",
        "A pick on a class you've swapped away from now shows a notice if its prerequisite stops being met, and a share link with an AA the calculator doesn't recognize now tells you instead of dropping it silently."
      ]
    },
    {
      version: "2.1.0",
      date: "2026-09-28",
      items: [
        "Browse All AAs now has an Unowned Only filter, and every card shows your exact owned rank at a glance - handy once you've got a lot of AAs already trained. Auto-granted AAs are left out of the filter, since you never need to mark those owned.",
        "A share link or import with a corrupted value (like a garbled character level) is now rejected safely instead of freezing the calculator."
      ]
    },
    {
      version: "2.0.9",
      date: "2026-09-27",
      items: [
        "Undo now restores the right rank after you lower an AA that comes with free ranks.",
        "A damaged or incomplete share code now shows an error instead of loading as an empty build.",
        "If a shared link loads but can't be saved to Builds (for example when browser storage is full), you now get a warning instead of being told it was saved. Picking an import file that can't be read now shows a message too."
      ]
    },
    {
      version: "2.0.8",
      date: "2026-09-23",
      items: [
        "Three new AAs from the latest patch are now in the calculator: Full Potential (storage capacity), Point Blank Fire (a 0-point ranged combat AA for Berserker, Monk, Ranger, and Rogue), and Widened Perception (+1 loadout slot)."
      ]
    },
    {
      version: "2.0.7",
      date: "2026-09-16",
      items: [
        "Master of All is now a single rank costing 10 points, instead of four ranks at 5 points each. If you'd trained past rank 1 on an older build, it'll show the refund automatically.",
        "Data correction from a fresh wiki scrape: Turn Summoned's second rank is confirmed at 6 points (400/800 damage)."
      ]
    },
    {
      version: "2.0.6",
      date: "2026-09-13",
      items: [
        "Spell Casting Subtlety, Reaching Notes, and Symphonic Aura are now simple toggles in-game rather than needing a purchased rank to turn on and off. They show fewer total ranks to match - if you'd trained deep into one of these on an older build, it may display differently now, though the points you already spent still count the same.",
        "Data corrections from a fresh wiki scrape: Thief's Intuition's last two ranks are confirmed at 9 and 15 points (plus a final-rank passive trap-sensing bonus), and Wizard's Quick Evacuation is confirmed at 10/25/50%."
      ]
    },
    {
      version: "2.0.5",
      date: "2026-09-11",
      items: [
        "Fixed a rare bug where changing your character level or class selection could get silently discarded if something else on the page happened to redraw at that exact moment, leaving the old value showing instead of what you'd just entered.",
        "Data corrections from a fresh wiki scrape: First Aid's last two ranks are confirmed at 6 and 9 points, Reaching Notes now shows its real cost pattern (every other rank is free, the same formula Symphonic Aura uses), and Unbound Boon's rank 2 exceptional-heal chance is confirmed at 4%."
      ]
    },
    {
      version: "2.0.4",
      date: "2026-08-29",
      items: [
        "An AA whose ranks each do something different now shows one line per rank, with the rank you're on highlighted, instead of running them together in one paragraph. Conjurer's Efficiency is the first one written this way.",
        "Data corrections from a fresh wiki scrape: Conjurer's Efficiency's costs are all confirmed now at 3/5/6/6/6, replacing estimates, and Thief's Intuition's second rank is confirmed at 6 points for 3 seconds."
      ]
    },
    {
      version: "2.0.3",
      date: "2026-08-29",
      items: [
        "Valiant Steed and Abyssal Steed have been removed from the game, so they're gone from the tool too. If your plan included either one, its points are refunded and free to spend elsewhere.",
        "Data corrections from a fresh wiki scrape: the crafting Masteries (Alchemy, Baking, Blacksmithing, Brewing, Fletching, Pottery and Tailoring) now show their real 10/25/50% values instead of estimates, and so do Stoicism, Burst of Power's last rank, and Druid's Quick Evacuation costs."
      ]
    },
    {
      version: "2.0.2",
      date: "2026-08-29",
      items: [
        "Share links and exported build codes are much shorter again. A big build's link drops by about 40%, and a small one by more than half. Any link or export you already have keeps working."
      ]
    },
    {
      version: "2.0.1",
      date: "2026-08-28",
      items: [
        "Fixed: on an AA your class combo can't train but you'd already put points into, the CLASS badge and the warning sign drew on top of each other. They sit in separate corners now.",
        "Fixed: hiding an AA from Browse while a search was active left the tab counts showing their old numbers until something else refreshed the page."
      ]
    },
    {
      version: "2.0.0",
      date: "2026-08-21",
      items: [
        "Archetype AAs are now restricted to the classes that can actually train them in-game, instead of showing every one to every combo. A class combo that doesn't qualify shows a CLASS badge in the tree and a note in Browse; a rank you already trained before a class swap made it ineligible stays exactly as it was, just flagged, the same way an out-of-reach prerequisite already works. The eligible-class list is a first pass and may need the odd correction \u2014 let us know if something looks off."
      ]
    },
    {
      version: "1.9.4",
      date: "2026-08-20",
      items: [
        "Progression now shows every AA you've picked, not just the ones for your current 3 classes. A pick for a class you've swapped out stays right where it was, flagged with a small warning icon, instead of only living in the Other Classes tab. Progression's running total now always matches your Points Planned total at the top of the page."
      ]
    },
    {
      version: "1.9.3",
      date: "2026-08-17",
      items: [
        "The topbar's headline number now shows owned / spent instead of just spent, so you can see at a glance how much of your plan you've actually trained in-game against its total cost."
      ]
    },
    {
      version: "1.9.2",
      date: "2026-08-15",
      items: [
        "Share links and exported build codes are noticeably shorter now. Any link or export you already have keeps working exactly the same."
      ]
    },
    {
      version: "1.9.1",
      date: "2026-08-14",
      items: [
        "Build Summary now also shows picks for a class you've swapped away from, below a divider, so you don't have to switch to the Other Classes tab to see them."
      ]
    },
    {
      version: "1.9.0",
      date: "2026-08-14",
      items: [
        `New: owned progress is now tracked separately for each build by default, instead of one shared pool across everything. A "Manage tracking\u2026" link on the Progression tab lets you link two builds to share the same live progress, merge in progress from another build without touching it, or split one back off onto its own copy, whenever you want. Clear Owned now only clears the current build's own tracking, not every build's.`,
        "Importing a build that includes owned progress no longer asks to overwrite yours. It always keeps its own separate progress, with a quick toast to let you know.",
        "Your existing builds keep sharing progress exactly like they always did, until you choose to change that."
      ]
    },
    {
      version: "1.8.2",
      date: "2026-07-28",
      items: [
        `Fixed: the Progression tab's "owned / to go" split could quietly drop an owned rank's estimated cost, and in rare cases even show a negative number to go. Both figures now always add up to match the topbar's own total.`,
        `Data corrections from a fresh wiki scrape: several new AAs were added (including a handful of new "Unbound" abilities), Leech Touch's effect changed from an activated drain to a passive Harm Touch upgrade, and Steadfast Will's rank-7 tier now also covers Monk.`
      ]
    },
    {
      version: "1.8.1",
      date: "2026-07-28",
      items: [
        `New: a "Move To" button on each Progression row opens a quick-jump menu \u2014 top or bottom of the list, top or bottom of any waypoint, or a specific position \u2014 for reordering a long build without dragging it row by row. If a step's own cost would push it past the waypoint you're aiming for, it lands as close as it can instead of overshooting, and grays out if it truly can't fit.`
      ]
    },
    {
      version: "1.8.0",
      date: "2026-07-25",
      items: [
        "New: swapping a class no longer wipes its picks. They move to a new Other Classes tab instead of disappearing, grouped by class with their own subtotal, and still count toward your Points Spent total. Swap the class back in and everything's exactly as you left it. (Points Spent is now a lifetime total across every class you've used \u2014 Progression's own running total still only tracks your current 3, so don't be surprised if the two numbers don't match.)",
        "Reset Build and Clear Owned now cover every class you've used, not just your current 3 \u2014 matching how they already worked for your active classes.",
        "Progression rows now show a small colored badge for which of your 3 classes each one belongs to."
      ]
    },
    {
      version: "1.7.0",
      date: "2026-07-25",
      items: [
        `New: Hide an AA you don't care about \u2014 a Hide/Unhide toggle in the side panel and on each Browse card tucks it out of the tree, Browse All AAs, and search. A "Show Hidden" toggle brings hidden AAs back whenever you want. Hiding is purely a display preference: it never affects your build, an AA you've already spent points on always stays visible, and it's not saved to exports or share links.`
      ]
    },
    {
      version: "1.6.5",
      date: "2026-07-25",
      items: [
        "Progression tab: dragging a row near the top or bottom of the list now auto-scrolls it, speeding up the closer you get to the edge \u2014 no more pre-scrolling to where you want to drop before you can start."
      ]
    },
    {
      version: "1.6.4",
      date: "2026-07-22",
      items: [
        "New: class-based rank caps are now enforced. Steadfast Will is the current example \u2014 capped at rank 6 unless one of your 3 classes is Warrior, Paladin, Shadow Knight (rank 8), or Ranger (rank 7). Tri-class combines rather than switches, so any one of your 3 classes qualifying is enough.",
        "A rank that a later class swap puts out of reach is never stripped \u2014 it stays exactly as trained, flagged the same way a stale prerequisite is, on the tree, side panel, Summary, and Progression, with the out-of-reach portion of its progress bar dimmed. Swap back to a qualifying class and the warning clears automatically."
      ]
    },
    {
      version: "1.6.3",
      date: "2026-07-21",
      items: [
        'Fixed: a purchased rank with an estimated cost showed "0 pt(s)" in the plain-text export instead of its "~N" estimate, even though the tree, side panel, and Progression tab all showed the real guess.',
        "Fixed: Progression's own running point total used to freeze through any purchased rank with an estimated cost. It now blends estimates into the total the same way the topbar already does, and the plain-text export matches it exactly. Affordability still only ever counts confirmed costs."
      ]
    },
    {
      version: "1.6.2",
      date: "2026-07-19",
      items: [
        'Removed the "Total AA Points" field and the cap it enforced \u2014 the topbar now just shows points spent, with no ceiling to set or bump into. Waypoints already cover marking a point total worth planning around.',
        "When Points Spent includes estimates, the confirmed/estimated breakdown now lives in a tooltip on hover instead of a second number next to it."
      ]
    },
    {
      version: "1.6.1",
      date: "2026-07-19",
      items: [
        'New: pattern-inferred estimates now cover effect values too, not just costs \u2014 a "?" like the one in "Increases your critical hit chance by 1/?/5/10%" can now show a guess, wherever descriptions appear. Same confidence tiers and tooltips as cost estimates; still just a display hint.',
        "Data correction from a fresh wiki scrape: Packrat's ranks 2 and 3 weight-reduction values are now confirmed (10% and 15%).",
        `Hand-picked estimates now fill in the rest of the currently undocumented effect values \u2014 Adamant Will, the crafting Mastery AAs, the Innate line, Packrat's remaining ranks, and a few others \u2014 marked with their own "very low" confidence tier.`
      ]
    },
    {
      version: "1.6.0",
      date: "2026-07-18",
      items: [
        `New: undocumented per-rank costs (shown as "?" on the wiki) can now show a pattern-inferred estimate instead, wherever a cost appears \u2014 the tree, side panel, Browse All AAs, and Progression. Marked with a ~ and color-coded by confidence, with a tooltip explaining what it's based on. Always a cross-check against similar, fully-documented AAs, never a guess from one AA's numbers alone.`,
        "An estimate is shown for reference only and never affects point totals or affordability \u2014 the moment the wiki documents the real cost, that takes over automatically. If you've already purchased a rank like that, the topbar's Points Spent turns blue and blends the estimate in, with the breakdown in its tooltip.",
        "Data corrections from a fresh wiki scrape: Combat Fury and Combat Stability both had a previously-undocumented rank confirmed, and Packrat gained several confirmed ranks too.",
        'A handful of costs no comparable AA could cross-check now show a hand-picked estimate instead, marked with its own "very low" confidence tier.'
      ]
    },
    {
      version: "1.5.0",
      date: "2026-07-18",
      items: [
        'New: Waypoints on the Progression tab. Mark a point total worth returning to (with an optional name, like "Level 20" or "Turn-in gear") and it shows up as a labeled divider right where your training order crosses it. Give it a color to make that stretch of steps stand out \u2014 color-code your whole plan into stages at a glance. Click a chip or divider to edit it later.',
        "Waypoints are anchored to a point total rather than a position, so reordering, undo, and Reset Build never break them. They travel with the plan, in named Builds and share links alike."
      ]
    },
    {
      version: "1.4.1",
      date: "2026-07-18",
      items: [
        "Fixed: the version tag in the bottom-right corner could overlap the last card or row on the Summary and Progression tabs instead of having its own clear space."
      ]
    },
    {
      version: "1.4.0",
      date: "2026-07-18",
      items: [
        "New: mark AAs as owned on the Progression tab to track what you've actually trained in-game, separate from what you're just planning. Owned steps show a strikethrough, marking is undoable, and the toolbar shows a running total of points owned vs. still to go.",
        'Reset Build now keeps your owned AAs by default instead of wiping everything, with a checkbox to clear them too if you want a clean slate. A separate "Clear Owned" button clears owned progress on its own, without touching your plan.',
        "Owned progress is tracked per character, not per plan, so switching between Builds or opening a share link never touches it. It's left out of exported text and share links by default \u2014 a checkbox opts in, for moving it to another browser or sharing it. Importing a build with owned data asks first, since it would otherwise overwrite your own."
      ]
    },
    {
      version: "1.3.0",
      date: "2026-07-17",
      items: [
        "New: Builds \u2014 save named snapshots of your build and switch between them from the topbar. Handy for comparing class combos or planning alternate paths side by side.",
        `Opening a share link or importing text now offers to save your current build first, instead of just warning it'll be replaced. A share link's build is also auto-saved to a reusable "Imported Build" slot so it's easy to find again later.`,
        "Progression tab: Undo Last now covers reordering too, not just adding or removing a rank \u2014 drag or arrow-move a step by mistake and Undo Last puts it back."
      ]
    },
    {
      version: "1.2.1",
      date: "2026-07-16",
      items: [
        "Locked AAs in the tree now show whether they're blocked by a missing prerequisite (amber border + REQ badge) or just a level requirement, instead of looking identical either way.",
        "Browse view now flags a prerequisite you haven't met yet, matching the side panel.",
        "Progression tab: dragging a step shows an amber indicator if that drop would leave its own prerequisite unmet, and out-of-order steps are now dimmed for visibility, not just marked with \u26A0."
      ]
    },
    {
      version: "1.2.0",
      date: "2026-07-16",
      items: [
        "Progression tab: drag and drop a row to reorder it, in addition to the existing arrows.",
        "Data corrections from a fresh wiki scrape and in-game confirmation: Fury of Magic, Symphonic Aura (including its unusual per-rank cost/enable pattern), Rapid Feign, Fear Resistance, Holy Steed, and Soul Abrasion."
      ]
    },
    {
      version: "1.1.0",
      date: "2026-07-10",
      items: [
        "Much shorter share links and export codes \u2014 a heavily-built character's link is now roughly a tenth of its old length. Links and codes you already have saved or shared still work.",
        "If a data update ever removes or reshapes an AA you'd picked, you'll now see a notice on load explaining what changed, instead of a build that's just quietly different than you left it.",
        "AAs whose prerequisite is no longer met (because of a data update) are now flagged directly in the tree and side panel, not just silently blocked."
      ]
    },
    {
      version: "1.0.0",
      date: "2026-07-09",
      items: [
        "Next-rank preview: see what the next rank upgrades to before you buy it, in the side panel and as an expandable row in the Progression tab.",
        "Global search: highlights matches in the tab you're on and shows match-count badges on other tabs that have matches too.",
        "Progression tab: reorderable purchase history with per-step and running-total cost, add/remove controls, and single-level undo.",
        "Shareable build links, plus text export/import (paste text, paste a share link, or load a saved .txt file).",
        "Fixed a prerequisite bug: some prereqs (like Destructive Cascade needing Critical Affliction) now unlock rank-by-rank instead of requiring the target's max rank just to buy rank 1.",
        "Data corrections from in-game confirmation and a fresh wiki scrape: Unbound Companion, Hunter's Attack Power, Fury of Magic, Soul Abrasion, and others."
      ]
    }
  ];

  // src/logic.js
  function costNum(c) {
    const n = parseInt(c, 10);
    return isNaN(n) ? 0 : n;
  }
  function escapeHtml(str) {
    return String(str == null ? "" : str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
  }
  function iconLetter(name) {
    return (name || "?").trim().charAt(0).toUpperCase();
  }
  function eraBadge(aa) {
    if (aa.era === "kunark") return { letter: "K", cssClass: "era-kunark", label: "Kunark" };
    if (aa.era === "velious") return { letter: "V", cssClass: "era-velious", label: "Velious" };
    return null;
  }
  function guessTitle(guess) {
    if (guess.manual) return `Estimated (very low confidence) \u2014 hand-picked pending wiki confirmation, not derived from other AAs. Not confirmed on the wiki.`;
    if (guess.interpolated) return `Estimated (${guess.confidence} confidence) \u2014 no comparable AA found, interpolated between this AA's own known ranks. Not confirmed on the wiki.`;
    return `Estimated (${guess.confidence} confidence) from ${guess.basedOn.join(", ")} \u2014 not confirmed on the wiki.`;
  }
  function highlightRankValue(text, rank, guessLookup) {
    const lines = splitPerRankLines(text);
    if (lines) {
      let progIdx = -1;
      return lines.map(({ rank: lineRank, text: lineText }) => {
        const out = markProgressions(escapeHtml(lineText), 0, guessLookup, progIdx);
        progIdx = out.progIdx;
        const current = rank && lineRank === rank ? " is-current-rank" : "";
        return `<span class="rank-line${current}">${out.html}</span>`;
      }).join("");
    }
    const escaped = escapeHtml(text);
    if (!guessLookup && (!rank || rank < 1)) return escaped;
    return markProgressions(escaped, rank, guessLookup, -1).html;
  }
  var PER_RANK_HEAD = /^Rank (\d+):\s/;
  var PER_RANK_SPLIT = /(?=Rank \d+:\s)/;
  function splitPerRankLines(text) {
    const str = String(text == null ? "" : text);
    if (!PER_RANK_HEAD.test(str)) return null;
    const parts = str.split(PER_RANK_SPLIT).filter((p) => p.trim());
    if (parts.length < 2) return null;
    return parts.map((p) => ({ rank: parseInt(p.match(PER_RANK_HEAD)[1], 10), text: p.trim() }));
  }
  function markProgressions(escaped, rank, guessLookup, startIdx) {
    let progIdx = startIdx;
    const html = escaped.replace(/(?:\d+(?:\.\d+)?%?|\?)(?:\/(?:\d+(?:\.\d+)?%?|\?)){1,}/g, (match) => {
      progIdx++;
      const parts = match.split("/");
      const highlightIdx = rank && rank >= 1 ? rank - 1 : -1;
      return parts.map((part, i) => {
        if (part === "?") {
          const guess = guessLookup ? guessLookup(progIdx, i) : null;
          if (!guess) return part;
          const cls = `is-estimate tier-${guess.confidence}${i === highlightIdx ? " rank-highlight" : ""}`;
          return `<span class="${cls}" title="${escapeHtml(guessTitle(guess))}">~${guess.value}</span>`;
        }
        return i === highlightIdx ? `<span class="rank-highlight">${part}</span>` : part;
      }).join("/");
    });
    return { html, progIdx };
  }
  function applyPerRankTotal(text, rank) {
    if (!rank || rank < 2) return text;
    return text.replace(
      /(?<![\d./])(\d+(?:\.\d+)?)(%)?\s*(points?|seconds?)?\s*(chance)?\s*\(?per rank\)?/gi,
      (match, numStr, pct, unit, chanceWord) => {
        const num = parseFloat(numStr);
        const total = num * rank;
        const fmt = (n) => Number.isInteger(n) ? String(n) : n.toFixed(2).replace(/0+$/, "").replace(/\.$/, "");
        let unitLabel = "";
        if (pct) unitLabel = "%";
        else if (unit) {
          const singular = unit.replace(/s$/i, "");
          unitLabel = " " + (total === 1 ? singular : singular + "s");
        }
        const chancePart = chanceWord ? " chance" : "";
        return `${fmt(total)}${unitLabel}${chancePart} (${fmt(num)}${pct ? "%" : ""} per rank)`;
      }
    );
  }
  function aaMatchesQuery(aa, query) {
    if (!query) return false;
    const q = query.trim().toLowerCase();
    if (!q) return false;
    return aa.name.toLowerCase().includes(q) || aa.description.toLowerCase().includes(q);
  }
  function countMatches(catKey, query) {
    if (!query || !query.trim()) return 0;
    return getList(catKey).filter((aa, idx) => {
      if (!aaMatchesQuery(aa, query)) return false;
      return !isSuppressed(catKey, idx);
    }).length;
  }
  function classSlotIndex(catKey) {
    const i = CLASS_SLOT_KEYS.indexOf(catKey);
    return i;
  }
  function labelFor(catKey) {
    if (catKey === "general") return "General AA";
    if (catKey === "archetype") return "Archetype AA";
    if (catKey === "special") return "Special AA";
    const slot = classSlotIndex(catKey);
    if (slot >= 0) return state.selectedClasses[slot] + " AA";
    return catKey;
  }
  function shortCategoryLabel(catKey) {
    if (catKey === "general") return "General";
    if (catKey === "archetype") return "Archetype";
    if (catKey === "special") return "Special";
    const slot = classSlotIndex(catKey);
    if (slot >= 0) return state.selectedClasses[slot];
    return catKey;
  }
  function getList(catKey) {
    const slot = classSlotIndex(catKey);
    if (slot >= 0) return AA_DATA.classes[state.selectedClasses[slot]] || [];
    return AA_DATA[catKey] || [];
  }
  var rankLevelCache = /* @__PURE__ */ new WeakMap();
  function rankLevelReqs(aa) {
    let levels = rankLevelCache.get(aa);
    if (!levels) {
      const stated = {};
      for (const m of String(aa.description || "").matchAll(/\brank (\d+) requires level (\d+)/gi)) {
        stated[parseInt(m[1], 10)] = parseInt(m[2], 10);
      }
      levels = [];
      for (let r = 1; r <= aa.ranks; r++) {
        const floor = r === 1 ? parseInt(aa.levelReq, 10) || 1 : levels[r - 2];
        levels.push(Math.max(floor, stated[r] || 0));
      }
      rankLevelCache.set(aa, levels);
    }
    return levels;
  }
  function hasPerRankLevels(aa) {
    const levels = rankLevelReqs(aa);
    return levels[levels.length - 1] !== levels[0];
  }
  function ranksAtLevel(aa) {
    return rankLevelReqs(aa).filter((level) => state.charLevel >= level).length;
  }
  function effectiveRank(catKey, idx) {
    const { scope, className } = categoryToScopeClassName(catKey);
    return effectiveRankScoped(scope, className, idx);
  }
  function effectiveRankScoped(scope, className, idx) {
    const aa = aaAt(scope, className, idx);
    const classActive = scope !== "class" || state.selectedClasses.includes(className);
    if (aa && aa.auto) {
      return classActive && isClassEligible(aa) ? ranksAtLevel(aa) : 0;
    }
    const canonical = sharedCanonical(scope, className, idx);
    const store = canonical.scope === "class" ? state.ranks.classes[canonical.className] || {} : state.ranks[canonical.scope] || {};
    const purchased = store[canonical.idx] || 0;
    if (aa && aa.autoRanks) {
      const freeRanks = classActive ? Math.min(aa.autoRanks, ranksAtLevel(aa)) : 0;
      return Math.max(freeRanks, purchased);
    }
    return purchased;
  }
  function autoRanksOffset(aa) {
    return aa && aa.autoRanks ? Math.min(aa.autoRanks, aa.ranks) : 0;
  }
  function autoRanksOffsetScoped(scope, className, idx) {
    return autoRanksOffset(aaAt(scope, className, idx));
  }
  function getRanksStoreScoped(scope, className) {
    if (scope === "class") {
      if (!state.ranks.classes[className]) state.ranks.classes[className] = {};
      return state.ranks.classes[className];
    }
    return state.ranks[scope];
  }
  function sharedCanonical(scope, className, idx) {
    const aa = aaAt(scope, className, idx);
    if (!aa || !aa.sharedWithClass) return { scope, className, idx };
    const canonicalIdx = idxForKey("class", aa.sharedWithClass, slugify(aa.name));
    return canonicalIdx >= 0 ? { scope: "class", className: aa.sharedWithClass, idx: canonicalIdx } : { scope, className, idx };
  }
  function getOwnedStore(scope, className) {
    if (scope === "class") {
      if (!state.owned.classes[className]) state.owned.classes[className] = {};
      return state.owned.classes[className];
    }
    return state.owned[scope];
  }
  function ownedRank(scope, className, idx) {
    const canonical = sharedCanonical(scope, className, idx);
    const store = canonical.scope === "class" ? state.owned.classes[canonical.className] : state.owned[canonical.scope];
    return store && store[canonical.idx] || 0;
  }
  function setOwnedRank(scope, className, idx, rank) {
    refreshOwnedFromStorage();
    const canonical = sharedCanonical(scope, className, idx);
    const store = getOwnedStore(canonical.scope, canonical.className);
    const from = store[canonical.idx] || 0;
    if (rank <= 0) delete store[canonical.idx];
    else store[canonical.idx] = rank;
    lastMutation = { type: "own", scope: canonical.scope, className: canonical.className, idx: canonical.idx, from, to: rank };
    saveOwned();
  }
  function getHiddenStore(scope, className) {
    if (scope === "class") {
      if (!state.hiddenAAs.classes[className]) state.hiddenAAs.classes[className] = {};
      return state.hiddenAAs.classes[className];
    }
    return state.hiddenAAs[scope];
  }
  function isHiddenScoped(scope, className, idx) {
    const canonical = sharedCanonical(scope, className, idx);
    const store = canonical.scope === "class" ? state.hiddenAAs.classes[canonical.className] : state.hiddenAAs[canonical.scope];
    return !!(store && store[canonical.idx]);
  }
  function isHidden(catKey, idx) {
    const { scope, className } = categoryToScopeClassName(catKey);
    return isHiddenScoped(scope, className, idx);
  }
  function setHiddenScoped(scope, className, idx, hidden) {
    const canonical = sharedCanonical(scope, className, idx);
    const store = getHiddenStore(canonical.scope, canonical.className);
    if (hidden) store[canonical.idx] = true;
    else delete store[canonical.idx];
    saveHidden();
  }
  function setHidden(catKey, idx, hidden) {
    const { scope, className } = categoryToScopeClassName(catKey);
    setHiddenScoped(scope, className, idx, hidden);
  }
  function isSuppressedScoped(scope, className, idx) {
    if (!isHiddenScoped(scope, className, idx)) return false;
    if (state.showHidden) return false;
    const canonical = sharedCanonical(scope, className, idx);
    const store = canonical.scope === "class" ? state.ranks.classes[canonical.className] : state.ranks[canonical.scope];
    return !(store && store[canonical.idx] > 0);
  }
  function isSuppressed(catKey, idx) {
    const { scope, className } = categoryToScopeClassName(catKey);
    return isSuppressedScoped(scope, className, idx);
  }
  function hasAnyHidden() {
    const h = state.hiddenAAs;
    if (Object.keys(h.general).length || Object.keys(h.archetype).length || Object.keys(h.special).length) return true;
    return Object.keys(h.classes).some((className) => Object.keys(h.classes[className]).length > 0);
  }
  function hasAnyOwned() {
    const o = state.owned;
    if (Object.keys(o.general).length || Object.keys(o.archetype).length || Object.keys(o.special).length) return true;
    return Object.keys(o.classes).some((className) => Object.keys(o.classes[className]).length > 0);
  }
  function clearAllOwned() {
    state.owned = { general: {}, archetype: {}, special: {}, classes: {} };
    lastMutation = null;
    saveOwned();
  }
  function addOrUpdateWaypoint(pts, label, color) {
    const n = parseInt(pts, 10);
    if (!Number.isFinite(n) || n < 0) return false;
    const merged = state.waypoints.filter((w) => w.pts !== n);
    merged.push({ pts: n, label, color });
    state.waypoints = sanitizeWaypoints(merged);
    saveLocal();
    return true;
  }
  function removeWaypoint(pts) {
    state.waypoints = state.waypoints.filter((w) => w.pts !== pts);
    saveLocal();
  }
  function categoryToScopeClassName(category) {
    const slot = classSlotIndex(category);
    return slot >= 0 ? { scope: "class", className: state.selectedClasses[slot] } : { scope: category, className: null };
  }
  function costGuess(catKey, idx, rankIdx) {
    const { scope, className } = categoryToScopeClassName(catKey);
    return costGuessFor(scope, className, idx, rankIdx);
  }
  function costGuessScoped(scope, className, idx, rankIdx) {
    return costGuessFor(scope, className, idx, rankIdx);
  }
  function effectGuess(catKey, idx, progIdx, rankIdx) {
    const { scope, className } = categoryToScopeClassName(catKey);
    return effectGuessFor(scope, className, idx, progIdx, rankIdx);
  }
  function effectGuessScoped(scope, className, idx, progIdx, rankIdx) {
    return effectGuessFor(scope, className, idx, progIdx, rankIdx);
  }
  function entryKey(scope, className, idx) {
    return `${scope}|${className || ""}|${idx}`;
  }
  function sharedGroupClasses(scope, className, idx) {
    if (scope !== "class") return [className];
    const aa = aaAt(scope, className, idx);
    if (!aa) return [className];
    if (aa.sharedWithClass) return [className, aa.sharedWithClass];
    const siblings = CLASS_LIST.filter((c) => {
      if (c === className) return false;
      const otherIdx = idxForKey("class", c, slugify(aa.name));
      const otherAA = otherIdx >= 0 ? aaAt("class", c, otherIdx) : null;
      return otherAA && otherAA.sharedWithClass === className;
    });
    return siblings.length ? [className, ...siblings] : [className];
  }
  function activeEntryTarget(entry) {
    if (entry.scope !== "class") return { category: entry.scope, idx: entry.idx, classes: null };
    const classes = sharedGroupClasses(entry.scope, entry.className, entry.idx);
    const aa = aaAt(entry.scope, entry.className, entry.idx);
    for (const c of classes) {
      const slot = state.selectedClasses.indexOf(c);
      if (slot < 0) continue;
      const idx = c === entry.className ? entry.idx : idxForKey("class", c, slugify(aa.name));
      if (idx >= 0) return { category: CLASS_SLOT_KEYS[slot], idx, classes };
    }
    return { category: null, idx: entry.idx, classes };
  }
  function pushPurchase(scope, className, idx) {
    state.purchaseOrder.push({ scope, className, idx });
  }
  function popLastPurchase(scope, className, idx) {
    for (let i = state.purchaseOrder.length - 1; i >= 0; i--) {
      const e = state.purchaseOrder[i];
      if (e.scope === scope && e.idx === idx && (e.className || null) === (className || null)) {
        const [entry] = state.purchaseOrder.splice(i, 1);
        return { entry, position: i };
      }
    }
    return null;
  }
  function performReset(clearOwnedToo) {
    refreshOwnedFromStorage();
    function trimmedRanks(ranksStore, ownedStore, list) {
      const kept = {};
      Object.keys(ranksStore).forEach((idxStr) => {
        const idx = parseInt(idxStr, 10);
        const aa = list[idx];
        if (!aa) return;
        const planned = ranksStore[idx] || 0;
        const owned = clearOwnedToo ? 0 : Math.min(ownedStore[idx] || 0, planned);
        if (owned > autoRanksOffset(aa)) kept[idx] = owned;
      });
      return kept;
    }
    const newRanks = { general: {}, archetype: {}, special: {}, classes: {} };
    ["general", "archetype", "special"].forEach((scope) => {
      newRanks[scope] = trimmedRanks(state.ranks[scope] || {}, state.owned[scope] || {}, AA_DATA[scope] || []);
    });
    Object.keys(state.ranks.classes || {}).forEach((className) => {
      const kept = trimmedRanks(
        state.ranks.classes[className] || {},
        (state.owned.classes || {})[className] || {},
        AA_DATA.classes[className] || []
      );
      if (Object.keys(kept).length) newRanks.classes[className] = kept;
    });
    const remaining = {};
    ["general", "archetype", "special"].forEach((scope) => {
      const list = AA_DATA[scope] || [];
      Object.keys(newRanks[scope]).forEach((idxStr) => {
        const idx = parseInt(idxStr, 10);
        remaining[entryKey(scope, null, idxStr)] = newRanks[scope][idxStr] - autoRanksOffset(list[idx]);
      });
    });
    Object.keys(newRanks.classes).forEach((className) => {
      const list = AA_DATA.classes[className] || [];
      Object.keys(newRanks.classes[className]).forEach((idxStr) => {
        const idx = parseInt(idxStr, 10);
        remaining[entryKey("class", className, idxStr)] = newRanks.classes[className][idxStr] - autoRanksOffset(list[idx]);
      });
    });
    const newPurchaseOrder = [];
    state.purchaseOrder.forEach((e) => {
      const k = entryKey(e.scope, e.className, e.idx);
      if (remaining[k] > 0) {
        newPurchaseOrder.push(e);
        remaining[k]--;
      }
    });
    state.ranks = newRanks;
    state.purchaseOrder = newPurchaseOrder;
    if (clearOwnedToo) state.owned = { general: {}, archetype: {}, special: {}, classes: {} };
    state.selectedNode = null;
    lastMutation = null;
    reconcilePurchaseOrderCounts();
    saveLocal();
    if (clearOwnedToo) saveOwned();
  }
  function sumRealCost(list, store) {
    let total = 0;
    list.forEach((aa, idx) => {
      if (aa.auto) return;
      const r = store[idx] || 0;
      for (let i = 0; i < r; i++) total += costNum(aa.costs[i]);
    });
    return total;
  }
  function sumAcrossAllClasses(root, summer) {
    let total = summer("general", null, AA_DATA.general, root.general) + summer("archetype", null, AA_DATA.archetype, root.archetype) + summer("special", null, AA_DATA.special, root.special);
    Object.keys(root.classes).forEach((className) => {
      total += summer("class", className, AA_DATA.classes[className] || [], root.classes[className]);
    });
    return total;
  }
  function spentPoints() {
    return sumAcrossAllClasses(state.ranks, (scope, className, list, store) => sumRealCost(list, store));
  }
  function classPicks() {
    const out = /* @__PURE__ */ new Map();
    Object.keys(state.ranks.classes).forEach((stored) => {
      const store = state.ranks.classes[stored];
      Object.keys(store).forEach((idxStr) => {
        const idx = parseInt(idxStr, 10);
        const aa = aaAt("class", stored, idx);
        if (!aa || aa.auto || !(store[idxStr] > 0)) return;
        const target = activeEntryTarget({ scope: "class", className: stored, idx });
        const className = target.category ? state.selectedClasses[CLASS_SLOT_KEYS.indexOf(target.category)] : stored;
        const ownIdx = target.category ? target.idx : idx;
        if (!out.has(className)) out.set(className, []);
        out.get(className).push({ idx: ownIdx, aa: aaAt("class", className, ownIdx), rank: store[idxStr] });
      });
    });
    return out;
  }
  function picksForClass(className) {
    return (classPicks().get(className) || []).slice().sort((a, b) => a.idx - b.idx);
  }
  function pickCost({ aa, rank }) {
    let total = 0;
    for (let i = 0; i < rank; i++) total += costNum(aa.costs[i]);
    return total;
  }
  function spentForClass(className) {
    return picksForClass(className).reduce((sum, pick) => sum + pickCost(pick), 0);
  }
  function spentOnInactiveClasses() {
    let total = 0;
    classPicks().forEach((picks, className) => {
      if (!state.selectedClasses.includes(className)) total += picks.reduce((sum, pick) => sum + pickCost(pick), 0);
    });
    return total;
  }
  function ownedPoints() {
    return sumAcrossAllClasses(state.owned, (scope, className, list, store) => sumRealCost(list, store));
  }
  function sumEstimatedExtra(scope, className, list, store) {
    let extra = 0;
    list.forEach((aa, idx) => {
      if (aa.auto) return;
      const r = store[idx] || 0;
      for (let i = 0; i < r; i++) {
        if (aa.costs[i] !== "?") continue;
        const guess = costGuessScoped(scope, className, idx, i);
        if (guess) extra += guess.value;
      }
    });
    return extra;
  }
  function estimatedExtraPoints() {
    return sumAcrossAllClasses(state.ranks, sumEstimatedExtra);
  }
  function estimatedExtraOwnedPoints() {
    return sumAcrossAllClasses(state.owned, sumEstimatedExtra);
  }
  function parsePrereqText(text) {
    if (!text) return null;
    const m = text.match(/^Requires\s+(.+?)\s+(?:rank|(?:at\s+)?level)\s+(\d+(?:\/\d+)*)\s*$/i);
    if (!m) return null;
    const ranks = m[2].split("/").map((n) => parseInt(n, 10));
    return ranks.length > 1 ? { name: m[1].trim(), synced: true, ranks } : { name: m[1].trim(), synced: false, rank: ranks[0] };
  }
  var prereqTargetCache = /* @__PURE__ */ new Map();
  function resolvePrereqTargetScoped(text, scope, className) {
    const cacheKey = `${scope}|${className || ""}|${text}`;
    if (prereqTargetCache.has(cacheKey)) return prereqTargetCache.get(cacheKey);
    const result = computeResolvePrereqTargetScoped(text, scope, className);
    prereqTargetCache.set(cacheKey, result);
    return result;
  }
  function computeResolvePrereqTargetScoped(text, scope, className) {
    const parsed = parsePrereqText(text);
    if (!parsed) return null;
    const candidates = [[scope, className], ["general", null], ["archetype", null], ["special", null]];
    const seen = /* @__PURE__ */ new Set();
    const order = candidates.filter(([s, c]) => {
      const k = `${s}|${c || ""}`;
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    });
    for (const [s, c] of order) {
      const list = s === "class" ? AA_DATA.classes[c] || [] : AA_DATA[s] || [];
      let foundIdx = -1;
      list.forEach((aa, i) => {
        if (aa.name.toLowerCase() !== parsed.name.toLowerCase()) return;
        if (foundIdx < 0) {
          foundIdx = i;
          return;
        }
        if (list[foundIdx].auto && !aa.auto) foundIdx = i;
      });
      if (foundIdx >= 0) {
        return {
          scope: s,
          className: c,
          idx: foundIdx,
          // Required target rank for the source AA to hold `sourceRank`. Fixed
          // prereqs ignore sourceRank; synced ones look up the matching entry
          // (clamped to the list, so a too-high/low sourceRank still resolves).
          forRank(sourceRank) {
            if (!parsed.synced) return parsed.rank;
            const i = Math.min(Math.max(sourceRank, 1), parsed.ranks.length) - 1;
            return parsed.ranks[i];
          }
        };
      }
    }
    return null;
  }
  function resolvePrereqTarget(text, sourceCategory) {
    const { scope, className } = categoryToScopeClassName(sourceCategory);
    const resolved = resolvePrereqTargetScoped(text, scope, className);
    if (!resolved) return null;
    const category = resolved.scope === "class" ? CLASS_SLOT_KEYS[state.selectedClasses.indexOf(resolved.className)] : resolved.scope;
    return { category, idx: resolved.idx, forRank: resolved.forRank };
  }
  function tryResolvePrereq(text, sourceCategory) {
    const parsed = parsePrereqText(text);
    if (!parsed) return { ok: false, malformed: true };
    const resolved = resolvePrereqTarget(text, sourceCategory);
    if (!resolved) return { ok: false, malformed: false, name: parsed.name };
    return { ok: true, resolved };
  }
  function unresolvedPrereqMessage(text, attempt) {
    return attempt.malformed ? `Prerequisite text "${text}" isn't in a recognized format \u2014 this needs fixing in the data, not the wiki.` : `Requires "${attempt.name}", which no longer resolves to an existing ability.`;
  }
  function classRankCapFor(aa) {
    if (!aa.classRankCap) return aa.ranks;
    const { default: def, byClass } = aa.classRankCap;
    let cap = def;
    state.selectedClasses.forEach((c) => {
      if (byClass[c] !== void 0 && byClass[c] > cap) cap = byClass[c];
    });
    return cap;
  }
  function isClassEligible(aa) {
    return !aa.eligibleClasses || state.selectedClasses.some((c) => aa.eligibleClasses.includes(c));
  }
  function effectiveDisplayRank(aa, rank) {
    return aa.classRankCap ? Math.min(rank, classRankCapFor(aa)) : rank;
  }
  function structuralLockReason(catKey, idx) {
    const aa = getList(catKey)[idx];
    if (!aa) return null;
    if (!isClassEligible(aa)) {
      return { kind: "classEligibility", text: `Requires one of: ${aa.eligibleClasses.join(", ")}.` };
    }
    const nextRank = Math.min(effectiveRank(catKey, idx) + 1, aa.ranks);
    const levelReq = rankLevelReqs(aa)[nextRank - 1];
    if (state.charLevel < levelReq) {
      const who = nextRank > 1 && hasPerRankLevels(aa) ? `Rank ${nextRank} requires` : "Requires";
      return { kind: "level", text: `${who} character level ${levelReq}.` };
    }
    if (aa.classRankCap) {
      const cap = classRankCapFor(aa);
      const nextRank2 = effectiveRank(catKey, idx) + 1;
      if (nextRank2 > cap) return { kind: "classCap", text: `Capped at rank ${cap} for your currently selected classes.` };
    }
    if (aa.prereq) {
      const attempt = tryResolvePrereq(aa.prereq, catKey);
      if (!attempt.ok) return { kind: "prereq", text: unresolvedPrereqMessage(aa.prereq, attempt) };
      const resolved = attempt.resolved;
      const sourceRank = effectiveRank(catKey, idx) + 1;
      const requiredRank = resolved.forRank(sourceRank);
      const targetRank = effectiveRank(resolved.category, resolved.idx);
      if (targetRank < requiredRank) {
        const targetAA = getList(resolved.category)[resolved.idx];
        return { kind: "prereq", text: `Requires ${targetAA ? targetAA.name : "prerequisite"} rank ${requiredRank}.` };
      }
    }
    return null;
  }
  function heldRankInvalidReason(catKey, idx) {
    const { scope, className } = categoryToScopeClassName(catKey);
    return heldRankInvalidReasonScoped(scope, className, idx);
  }
  function heldRankInvalidReasonScoped(scope, className, idx) {
    const aa = aaAt(scope, className, idx);
    if (!aa || aa.auto) return null;
    const store = scope === "class" ? state.ranks.classes[className] || {} : state.ranks[scope] || {};
    const purchased = store[idx] || 0;
    if (purchased <= 0) return null;
    if (!isClassEligible(aa)) {
      return `requires one of: ${aa.eligibleClasses.join(", ")}, none of which are currently selected.`;
    }
    if (aa.classRankCap) {
      const cap = classRankCapFor(aa);
      if (purchased > cap) return `exceeds the rank ${cap} cap for your currently selected classes.`;
    }
    if (!aa.prereq) return null;
    const parsed = parsePrereqText(aa.prereq);
    if (!parsed) return unresolvedPrereqMessage(aa.prereq, { malformed: true });
    const resolved = resolvePrereqTargetScoped(aa.prereq, scope, className);
    if (!resolved) return unresolvedPrereqMessage(aa.prereq, { malformed: false, name: parsed.name });
    const targetRank = effectiveRankScoped(resolved.scope, resolved.className, resolved.idx);
    for (let r = 1; r <= purchased; r++) {
      const required = resolved.forRank(r);
      if (targetRank < required) {
        const targetAA = aaAt(resolved.scope, resolved.className, resolved.idx);
        return `Rank ${r} requires ${targetAA ? targetAA.name : "a prerequisite"} rank ${required}, which you no longer have.`;
      }
    }
    return null;
  }
  function findInvalidatedPicks() {
    const results = [];
    ["general", "archetype", "special"].forEach((scope) => {
      (AA_DATA[scope] || []).forEach((aa, idx) => {
        const reason = heldRankInvalidReasonScoped(scope, null, idx);
        if (reason) results.push({ scope, className: null, idx, name: aa.name, reason });
      });
    });
    Object.keys(state.ranks.classes).forEach((className) => {
      (AA_DATA.classes[className] || []).forEach((aa, idx) => {
        const reason = heldRankInvalidReasonScoped("class", className, idx);
        if (reason) results.push({ scope: "class", className, idx, name: aa.name, reason });
      });
    });
    return results;
  }
  function reconcilePurchaseOrderCounts() {
    function key(scope, className, idx) {
      return `${scope}|${className || ""}|${idx}`;
    }
    const targets = /* @__PURE__ */ new Map();
    function addTargets(scope, className, list, store) {
      Object.keys(store || {}).forEach((idxStr) => {
        const idx = parseInt(idxStr, 10);
        const aa = list[idx];
        if (aa && !aa.auto) {
          targets.set(key(scope, className, idx), { scope, className, idx, expected: Math.max(0, store[idxStr] - autoRanksOffset(aa)), seen: 0 });
        }
      });
    }
    ["general", "archetype", "special"].forEach((scope) => addTargets(scope, null, AA_DATA[scope] || [], state.ranks[scope]));
    Object.keys(state.ranks.classes || {}).forEach((className) => {
      addTargets("class", className, AA_DATA.classes[className] || [], state.ranks.classes[className]);
    });
    const orphanKeys = /* @__PURE__ */ new Set();
    const kept = [];
    state.purchaseOrder.forEach((e) => {
      const k = key(e.scope, e.className || null, e.idx);
      const t = targets.get(k);
      if (!t) {
        orphanKeys.add(k);
        return;
      }
      t.seen++;
      if (t.seen <= t.expected) kept.push(e);
    });
    let repaired = orphanKeys.size;
    targets.forEach((t) => {
      if (t.seen === t.expected) return;
      repaired++;
      for (let i = t.seen; i < t.expected; i++) kept.push({ scope: t.scope, className: t.className, idx: t.idx });
    });
    if (repaired) state.purchaseOrder = kept;
    return repaired;
  }
  function loadIssuesSuffix(result, repaired) {
    const parts = [];
    if (result.droppedRanks) {
      const n = result.droppedRanks;
      parts.push(`${n} pick${n === 1 ? "" : "s"} no longer exist${n === 1 ? "s" : ""} in the current data and ${n === 1 ? "was" : "were"} skipped`);
    }
    if (repaired) {
      parts.push(`${repaired} pick${repaired === 1 ? "'s" : "s'"} purchase history was out of sync and ${repaired === 1 ? "was" : "were"} repaired`);
    }
    return parts.length ? ` (${parts.join("; ")})` : "";
  }
  function getBlockReason(catKey, idx) {
    const structural = structuralLockReason(catKey, idx);
    return structural ? structural.text : null;
  }
  function checkPrereqDependents(list, scope, className, targetScope, targetClassName, idx, newRank) {
    for (let i = 0; i < list.length; i++) {
      const aa = list[i];
      if (!aa.prereq) continue;
      const aaRank = effectiveRankScoped(scope, className, i);
      if (aaRank <= 0) continue;
      const r = resolvePrereqTargetScoped(aa.prereq, scope, className);
      if (r && r.scope === targetScope && r.className === targetClassName && r.idx === idx && newRank < r.forRank(aaRank)) return true;
    }
    return false;
  }
  function isDependedOn(category, idx, currentRank) {
    const newRank = currentRank - 1;
    const { scope: targetScope, className: targetClassName } = categoryToScopeClassName(category);
    for (const catKey of AA_CATEGORY_KEYS) {
      const { scope, className } = categoryToScopeClassName(catKey);
      if (checkPrereqDependents(getList(catKey), scope, className, targetScope, targetClassName, idx, newRank)) return true;
    }
    for (const className of Object.keys(state.ranks.classes)) {
      if (state.selectedClasses.includes(className)) continue;
      if (checkPrereqDependents(AA_DATA.classes[className] || [], "class", className, targetScope, targetClassName, idx, newRank)) return true;
    }
    return false;
  }
  var lastMutation = null;
  function clearLastMutation() {
    lastMutation = null;
  }
  function canUndo() {
    return !!lastMutation;
  }
  function moveEntry(fromIdx, toIdx) {
    const [entry] = state.purchaseOrder.splice(fromIdx, 1);
    state.purchaseOrder.splice(toIdx, 0, entry);
    lastMutation = { type: "reorder", from: fromIdx, to: toIdx };
    saveLocal();
  }
  function autoFloor(aa) {
    return aa.autoRanks ? Math.min(aa.autoRanks, ranksAtLevel(aa)) : 0;
  }
  function changeRank(category, idx, delta) {
    const { scope, className } = categoryToScopeClassName(category);
    const aa = getList(category)[idx];
    const canonical = sharedCanonical(scope, className, idx);
    const store = getRanksStoreScoped(canonical.scope, canonical.className);
    const floor = autoFloor(aa);
    const cur = aa.autoRanks ? effectiveRank(category, idx) : store[canonical.idx] || 0;
    const next = cur + delta;
    if (next < floor || next > aa.ranks) return false;
    if (next <= floor) delete store[canonical.idx];
    else store[canonical.idx] = next;
    if (delta > 0) {
      pushPurchase(canonical.scope, canonical.className, canonical.idx);
      lastMutation = { type: "add", entry: { scope: canonical.scope, className: canonical.className, idx: canonical.idx } };
    } else {
      const popped = popLastPurchase(canonical.scope, canonical.className, canonical.idx);
      lastMutation = popped ? { type: "remove", entry: popped.entry, position: popped.position } : null;
    }
    saveLocal();
    return true;
  }
  function undoLastMutation() {
    const m = lastMutation;
    if (!m) return { changed: false, message: "Nothing to undo." };
    lastMutation = null;
    if (m.type === "add") {
      const { category: category2, idx: idx2 } = activeEntryTarget(m.entry);
      if (!category2) return { changed: false, message: "Can't undo \u2014 that class isn't currently selected." };
      const rank = effectiveRank(category2, idx2);
      if (rank <= 0) return { changed: false, message: "Nothing to undo." };
      if (isDependedOn(category2, idx2, rank)) {
        return { changed: false, message: "Can't undo \u2014 another AA now depends on this rank." };
      }
      return { changed: changeRank(category2, idx2, -1), message: null };
    }
    if (m.type === "reorder") {
      if (m.from < 0 || m.from >= state.purchaseOrder.length || m.to < 0 || m.to >= state.purchaseOrder.length) {
        return { changed: false, message: "Can't undo \u2014 the list has changed too much." };
      }
      moveEntry(m.to, m.from);
      return { changed: true, message: null };
    }
    if (m.type === "own") {
      setOwnedRank(m.scope, m.className, m.idx, m.from);
      return { changed: true, message: null };
    }
    const { category, idx } = activeEntryTarget(m.entry);
    if (!category) return { changed: false, message: "Can't undo \u2014 that class isn't currently selected." };
    const aa = getList(category)[idx];
    if (!aa) return { changed: false, message: "Can't undo \u2014 that AA is no longer available." };
    const store = getRanksStoreScoped(m.entry.scope, m.entry.className);
    const cur = aa.autoRanks ? effectiveRank(category, idx) : store[m.entry.idx] || 0;
    if (cur >= aa.ranks) return { changed: false, message: "Can't undo \u2014 already at max rank." };
    store[m.entry.idx] = cur + 1;
    const pos = Math.min(m.position, state.purchaseOrder.length);
    state.purchaseOrder.splice(pos, 0, m.entry);
    saveLocal();
    return { changed: true, message: null };
  }
  function attemptIncrement(category, idx) {
    const aa = getList(category)[idx];
    if (aa.auto) return { changed: false, message: `${aa.name} is automatically granted \u2014 no points needed.` };
    const rank = effectiveRank(category, idx);
    if (rank >= aa.ranks) return { changed: false, message: null };
    const reason = getBlockReason(category, idx);
    if (reason) return { changed: false, message: reason };
    return { changed: changeRank(category, idx, 1), message: null };
  }
  function attemptDecrement(category, idx) {
    const aa = getList(category)[idx];
    if (aa.auto) return { changed: false, message: `${aa.name} is automatically granted and can't be removed.` };
    const rank = effectiveRank(category, idx);
    if (rank <= 0) return { changed: false, message: null };
    if (aa.autoRanks && rank <= autoFloor(aa)) {
      const plural = aa.autoRanks === 1 ? "rank is" : "ranks are";
      return { changed: false, message: `${aa.name}'s first ${aa.autoRanks} ${plural} automatically granted and can't be removed.` };
    }
    if (isDependedOn(category, idx, rank)) {
      return { changed: false, message: "Can't lower this \u2014 another AA depends on the current rank." };
    }
    return { changed: changeRank(category, idx, -1), message: null };
  }
  function countPicked() {
    let n = 0;
    AA_CATEGORY_KEYS.forEach((catKey) => {
      getList(catKey).forEach((aa, idx) => {
        if (effectiveRank(catKey, idx) > 0) n++;
      });
    });
    return n;
  }
  function countOtherClassesPicked() {
    return otherClassesWithPicks().reduce((n, className) => n + picksForClass(className).length, 0);
  }
  function otherClassesWithPicks() {
    return Array.from(classPicks().keys()).filter((className) => !state.selectedClasses.includes(className)).sort();
  }
  function computeProgressionSteps(order = state.purchaseOrder) {
    const totalCounts = {};
    order.forEach((entry) => {
      const key = entryKey(entry.scope, entry.className, entry.idx);
      totalCounts[key] = (totalCounts[key] || 0) + 1;
    });
    const counts = {};
    let cumulative = 0;
    let blendedCumulative = 0;
    return order.map((entry, i) => {
      const key = entryKey(entry.scope, entry.className, entry.idx);
      const { category, idx: categoryIdx, classes: groupClasses } = activeEntryTarget(entry);
      const active = category !== null;
      const aa = aaAt(entry.scope, entry.className, entry.idx);
      const purchaseCount = (counts[key] || 0) + 1;
      const autoOffset = autoRanksOffset(aa);
      const stepRank = purchaseCount + autoOffset;
      let prereqWarn = false;
      if (aa && aa.prereq) {
        const resolved = resolvePrereqTargetScoped(aa.prereq, entry.scope, entry.className);
        if (!resolved) {
          prereqWarn = true;
        } else {
          const targetAA = aaAt(resolved.scope, resolved.className, resolved.idx);
          const targetAutoFloor = targetAA && targetAA.auto ? targetAA.ranks : targetAA && targetAA.autoRanks ? Math.min(targetAA.autoRanks, targetAA.ranks) : 0;
          const targetKey = entryKey(resolved.scope, resolved.className, resolved.idx);
          const targetHeld = (counts[targetKey] || 0) + targetAutoFloor;
          if (targetHeld < resolved.forRank(stepRank)) prereqWarn = true;
        }
      }
      const classCapWarn = aa && aa.classRankCap && stepRank > classRankCapFor(aa);
      const classEligibilityWarn = !!(aa && aa.eligibleClasses && !isClassEligible(aa));
      counts[key] = purchaseCount;
      const isLast = purchaseCount === totalCounts[key];
      const stepCost = aa ? costNum(aa.costs[stepRank - 1]) : 0;
      cumulative += stepCost;
      let blendedStepCost = stepCost;
      if (aa && aa.costs[stepRank - 1] === "?") {
        const guess = costGuessScoped(entry.scope, entry.className, entry.idx, stepRank - 1);
        if (guess) blendedStepCost = guess.value;
      }
      blendedCumulative += blendedStepCost;
      const label = entry.scope === "class" ? `${groupClasses.join("/")} AA` : labelFor(entry.scope);
      const classesLabel = entry.scope === "class" ? groupClasses.join(" or ") : "";
      const name = aa ? aa.name : "(unknown AA)";
      const owned = stepRank <= ownedRank(entry.scope, entry.className, entry.idx);
      return {
        index: i,
        aa,
        idx: entry.idx,
        categoryIdx,
        scope: entry.scope,
        className: entry.className,
        category,
        active,
        stepRank,
        stepCost,
        cumulative,
        blendedCumulative,
        prereqWarn,
        classCapWarn,
        classEligibilityWarn,
        label,
        classesLabel,
        name,
        isLast,
        owned
      };
    });
  }
  function computeProgressionTimeline(steps) {
    const wps = state.waypoints;
    const timeline = [];
    let wi = 0;
    let lastCumulative = 0;
    steps.forEach((s) => {
      while (wi < wps.length && wps[wi].pts < s.cumulative) {
        timeline.push({ type: "divider", pts: wps[wi].pts, label: wps[wi].label, color: wps[wi].color, unreached: false });
        wi++;
      }
      const owner = wi < wps.length ? wps[wi] : null;
      timeline.push({ type: "step", ...s, segmentColor: owner ? owner.color : null });
      lastCumulative = s.cumulative;
    });
    while (wi < wps.length) {
      timeline.push({ type: "divider", pts: wps[wi].pts, label: wps[wi].label, color: wps[wi].color, unreached: wps[wi].pts > lastCumulative });
      wi++;
    }
    return timeline;
  }

  // src/builds.js
  var BUILDS_INDEX_KEY = "eql_aa_builds_index_v1";
  var BUILD_KEY_PREFIX = "eql_aa_build_";
  var IMPORTED_BUILD_NAME = "Imported Build";
  var ACTIVE_BUILD_KEY = "eql_aa_active_build_id";
  var ORPHAN_GRACE_MS = 7 * 24 * 60 * 60 * 1e3;
  var cachedIndex = null;
  function dropCachedIndex() {
    cachedIndex = null;
  }
  function loadIndex() {
    if (cachedIndex !== null) return cachedIndex;
    try {
      const raw = localStorage.getItem(BUILDS_INDEX_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      cachedIndex = Array.isArray(parsed) ? parsed.filter((b) => isObject(b) && typeof b.id === "string") : [];
    } catch (e) {
      cachedIndex = [];
    }
    return cachedIndex;
  }
  function saveIndex(index) {
    cachedIndex = index;
    try {
      localStorage.setItem(BUILDS_INDEX_KEY, JSON.stringify(index));
      return true;
    } catch (e) {
      return false;
    }
  }
  function listBuilds() {
    return loadIndex().slice().sort((a, b) => b.updatedAt - a.updatedAt);
  }
  function sharedActiveBuildId() {
    try {
      return localStorage.getItem(ACTIVE_BUILD_KEY) || null;
    } catch (e) {
      return null;
    }
  }
  function getActiveBuildId() {
    try {
      let id = sessionStorage.getItem(ACTIVE_BUILD_KEY);
      if (id === null) {
        id = sharedActiveBuildId() || "";
        sessionStorage.setItem(ACTIVE_BUILD_KEY, id);
      }
      return id || null;
    } catch (e) {
      return sharedActiveBuildId();
    }
  }
  function setActiveBuildId(id) {
    try {
      sessionStorage.setItem(ACTIVE_BUILD_KEY, id || "");
    } catch (e) {
    }
    try {
      if (id) localStorage.setItem(ACTIVE_BUILD_KEY, id);
      else localStorage.removeItem(ACTIVE_BUILD_KEY);
    } catch (e) {
    }
  }
  function clearActiveBuild() {
    setActiveBuildId(null);
  }
  function migrateStaleBuildSlots() {
    loadIndex().forEach(({ id }) => {
      const key = BUILD_KEY_PREFIX + id;
      const parsed = readJsonFromStorage(key, isObject);
      if (!parsed) return;
      let changed = false;
      if ("totalPoints" in parsed) {
        delete parsed.totalPoints;
        changed = true;
      }
      const validOwnedProfileId = ownedProfileIdOr(parsed.ownedProfileId);
      if (validOwnedProfileId !== parsed.ownedProfileId) {
        parsed.ownedProfileId = validOwnedProfileId;
        changed = true;
      }
      if (!changed) return;
      try {
        localStorage.setItem(key, JSON.stringify(parsed));
      } catch (e) {
      }
    });
  }
  function readBuildRaw(id) {
    return readJsonFromStorage(BUILD_KEY_PREFIX + id, isObject);
  }
  function ownedProfileIdOfBuild(id) {
    const raw = readBuildRaw(id);
    return ownedProfileIdOr(raw && raw.ownedProfileId);
  }
  function cleanupOrphanedOwnedProfiles() {
    const referenced = /* @__PURE__ */ new Set([state.ownedProfileId]);
    const autosave = loadLocal();
    if (autosave) referenced.add(ownedProfileIdOr(autosave.ownedProfileId));
    loadIndex().forEach(({ id }) => referenced.add(ownedProfileIdOfBuild(id)));
    listOwnedProfileIds().forEach((profileId) => {
      if (referenced.has(profileId)) return;
      const raw = readJsonFromStorage(ownedStorageKeyFor(profileId), isObject);
      if (raw && typeof raw.savedAt === "number" && Date.now() - raw.savedAt < ORPHAN_GRACE_MS) return;
      removeOwnedProfile(profileId);
    });
  }
  function buildPayload() {
    return {
      v: SAVE_FORMAT_VERSION,
      selectedClasses: state.selectedClasses,
      charLevel: state.charLevel,
      ranks: serializeRanks(state.ranks),
      purchaseOrder: serializePurchaseOrder(state.purchaseOrder),
      waypoints: state.waypoints
    };
  }
  function deepEqual(a, b) {
    if (a === b) return true;
    if (typeof a !== "object" || typeof b !== "object" || a === null || b === null) return false;
    if (Array.isArray(a) || Array.isArray(b)) {
      if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) return false;
      return a.every((v, i) => deepEqual(v, b[i]));
    }
    return Object.keys(a).length === Object.keys(b).length && Object.keys(a).every((k) => Object.prototype.hasOwnProperty.call(b, k) && deepEqual(a[k], b[k]));
  }
  function isEmptyComposite(v) {
    if (Array.isArray(v)) return v.length === 0;
    return typeof v === "object" && v !== null && Object.keys(v).length === 0;
  }
  function deepEqualIgnoringExtraKeys(stored, current) {
    if (typeof stored !== "object" || stored === null) return false;
    return Object.keys(current).every((k) => {
      if (k === "v") return true;
      if (stored[k] === void 0 && isEmptyComposite(current[k])) return true;
      return deepEqual(stored[k], current[k]);
    });
  }
  function activeBuildMatchesCurrent() {
    const id = getActiveBuildId();
    if (!id) return false;
    const stored = readBuildRaw(id);
    if (!stored) return false;
    return deepEqualIgnoringExtraKeys(stored, buildPayload());
  }
  function saveBuildAs(name, id = null, mirrorCurrentProfile = false) {
    const targetId = id || genId();
    const payload = buildPayload();
    const keepProfile = mirrorCurrentProfile || id && ownedProfileIdOfBuild(id) === state.ownedProfileId;
    if (keepProfile) {
      payload.ownedProfileId = state.ownedProfileId;
    } else {
      payload.ownedProfileId = genId();
      if (!saveOwnedProfileTo(payload.ownedProfileId, state.owned)) return null;
    }
    try {
      localStorage.setItem(BUILD_KEY_PREFIX + targetId, JSON.stringify(payload));
    } catch (e) {
      return null;
    }
    const index = loadIndex();
    const existing = index.find((b) => b.id === targetId);
    const updatedAt = Date.now();
    if (existing) {
      existing.name = name;
      existing.updatedAt = updatedAt;
    } else {
      index.push({ id: targetId, name, updatedAt });
    }
    if (!saveIndex(index)) return null;
    setActiveBuildId(targetId);
    if (state.ownedProfileId !== payload.ownedProfileId) {
      state.ownedProfileId = payload.ownedProfileId;
      saveLocal();
    }
    return targetId;
  }
  function saveWithNameCheck(name) {
    const existing = listBuilds().find((b) => b.name === name);
    if (existing && !confirm(`A build named "${name}" already exists. Overwrite it?`)) return false;
    return saveBuildAs(name, existing ? existing.id : null);
  }
  function confirmReplaceCurrentBuild(verb, target, { extraRisk = false, trustMatch = true } = {}) {
    const isBackedUp = trustMatch && activeBuildMatchesCurrent();
    const nothingAtRisk = spentPoints() <= 0 && !state.waypoints.length && !extraRisk;
    if (nothingAtRisk || isBackedUp) return true;
    const wantsSave = confirm(`Your current build isn't saved. Save it as a named build before ${verb}ing ${target}?`);
    if (wantsSave) {
      const name = prompt("Name this build:", "");
      if (!name || !name.trim()) return false;
      const result = saveWithNameCheck(name.trim());
      if (result === false) return false;
      if (result === null) {
        alert("Couldn't save \u2014 local storage may be full or unavailable. Nothing was changed.");
        return false;
      }
      return true;
    }
    return confirm(`${verb.charAt(0).toUpperCase()}${verb.slice(1)} ${target}? This will replace your current build and can't be undone.`);
  }
  function findImportedSlot() {
    return loadIndex().find((b) => b.name === IMPORTED_BUILD_NAME) || null;
  }
  function isActiveBuildTheImportedSlot() {
    const slot = findImportedSlot();
    return !!slot && slot.id === getActiveBuildId();
  }
  function saveImportedBuild() {
    const existing = findImportedSlot();
    return saveBuildAs(IMPORTED_BUILD_NAME, existing ? existing.id : null, true);
  }
  function loadBuild(id) {
    let parsed;
    try {
      const raw = localStorage.getItem(BUILD_KEY_PREFIX + id);
      if (!raw) return null;
      parsed = JSON.parse(raw);
    } catch (e) {
      return null;
    }
    const result = applyLoaded(parsed);
    state.selectedNode = null;
    clearLastMutation();
    const repaired = reconcilePurchaseOrderCounts();
    state.ownedProfileId = ownedProfileIdOr(parsed.ownedProfileId);
    loadAndApplyOwned(null);
    setActiveBuildId(id);
    saveLocal();
    return { droppedRanks: result.droppedRanks, repaired };
  }
  function renameBuild(id, name) {
    const index = loadIndex();
    const entry = index.find((b) => b.id === id);
    if (!entry) return "missing";
    if (index.some((b) => b.id !== id && b.name === name)) return "collision";
    entry.name = name;
    return saveIndex(index) ? "ok" : "failed";
  }
  function deleteBuild(id) {
    const persisted = saveIndex(loadIndex().filter((b) => b.id !== id));
    if (persisted) {
      try {
        localStorage.removeItem(BUILD_KEY_PREFIX + id);
      } catch (e) {
      }
      if (getActiveBuildId() === id) setActiveBuildId(null);
    }
    return persisted;
  }
  function persistActiveBuildOwnedProfile() {
    const id = getActiveBuildId();
    if (!id) return;
    const parsed = readBuildRaw(id);
    if (!parsed) return;
    parsed.ownedProfileId = state.ownedProfileId;
    try {
      localStorage.setItem(BUILD_KEY_PREFIX + id, JSON.stringify(parsed));
    } catch (e) {
    }
  }
  function buildsSharingCurrentOwnedProfile() {
    const activeId = getActiveBuildId();
    return listBuilds().filter((b) => b.id !== activeId && ownedProfileIdOfBuild(b.id) === state.ownedProfileId);
  }
  function linkOwnedToBuild(targetBuildId) {
    clearLastMutation();
    linkOwnedProfile(ownedProfileIdOfBuild(targetBuildId));
    persistActiveBuildOwnedProfile();
    saveLocal();
  }
  function mergeOwnedFromBuild(sourceBuildId) {
    clearLastMutation();
    return mergeOwnedProfileInto(ownedProfileIdOfBuild(sourceBuildId));
  }
  function splitOwnedFromCurrent() {
    clearLastMutation();
    if (!splitOwnedProfile()) return false;
    persistActiveBuildOwnedProfile();
    saveLocal();
    return true;
  }

  // src/render.js
  function computePointTotals() {
    return {
      spent: spentPoints(),
      spentExtra: estimatedExtraPoints(),
      ownedReal: ownedPoints(),
      ownedExtra: estimatedExtraOwnedPoints()
    };
  }
  function renderAll() {
    const totals = computePointTotals();
    renderTopbar(totals);
    renderTabs();
    updateShowHiddenToggle();
    el.calculatorView.classList.add("hidden");
    el.browseView.classList.add("hidden");
    el.summaryView.classList.add("hidden");
    el.progressionView.classList.add("hidden");
    el.otherClassesView.classList.add("hidden");
    if (state.activeView === "browse") {
      el.browseView.classList.remove("hidden");
      renderBrowse();
    } else if (state.activeView === "summary") {
      el.summaryView.classList.remove("hidden");
      renderSummary(totals);
    } else if (state.activeView === "progression") {
      el.progressionView.classList.remove("hidden");
      renderProgression(totals);
    } else if (state.activeView === "otherClasses") {
      el.otherClassesView.classList.remove("hidden");
      renderOtherClasses();
    } else {
      el.calculatorView.classList.remove("hidden");
      renderTree(state.activeTab);
      renderSidePanel();
    }
  }
  function updateShowHiddenToggle() {
    const any = hasAnyHidden();
    if (!any && state.showHidden) state.showHidden = false;
    el.showHiddenToggle.classList.toggle("hidden", !any);
    el.showHiddenToggle.classList.toggle("active", state.showHidden);
    el.showHiddenToggle.textContent = state.showHidden ? "Hide Hidden" : "Show Hidden";
  }
  function setValueUnlessFocused(input, value) {
    if (document.activeElement !== input) input.value = value;
  }
  function renderTopbar(totals) {
    populateClassSelects();
    setValueUnlessFocused(el.levelInput, state.charLevel);
    const { spent, spentExtra, ownedReal, ownedExtra } = totals || computePointTotals();
    function blendedSpan(real, extra) {
      return extra > 0 ? `<span class="is-estimate">~${real + extra}</span>` : `${real}`;
    }
    el.spentValue.innerHTML = `${blendedSpan(ownedReal, ownedExtra)} / ${blendedSpan(spent, spentExtra)}`;
    const inactive = spentOnInactiveClasses();
    const titleParts = [];
    if (ownedExtra > 0) titleParts.push(`Owned: ${ownedReal} confirmed + ${ownedExtra} estimated.`);
    if (spentExtra > 0) titleParts.push(`Planned: ${spent} confirmed + ${spentExtra} estimated.`);
    if (inactive > 0) titleParts.push(`${inactive} pt${inactive === 1 ? "" : "s"} from classes not currently selected (see the Other Classes tab).`);
    if (titleParts.length) el.spentValue.title = titleParts.join(" ");
    else el.spentValue.removeAttribute("title");
    el.browseToggle.classList.toggle("active", state.activeView === "browse");
    const activeId = getActiveBuildId();
    const activeBuild = activeId ? listBuilds().find((b) => b.id === activeId) : null;
    el.buildsBtn.textContent = activeBuild ? `Builds: ${activeBuild.name} \u25BE` : "Builds \u25BE";
  }
  function populateClassSelects() {
    const html = CLASS_LIST.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("");
    el.classSelects.forEach((sel, i) => {
      if (sel.innerHTML !== html) sel.innerHTML = html;
      setValueUnlessFocused(sel, state.selectedClasses[i]);
    });
  }
  var VIEW_TAB_KEYS = ["summary", "progression", "otherClasses"];
  function renderTabs() {
    const tabDefs = [
      ...AA_CATEGORY_KEYS.map((key) => ({ key, label: shortCategoryLabel(key) })),
      { key: "otherClasses", label: "Other Classes" },
      { key: "summary", label: "Summary" },
      { key: "progression", label: "Progression" }
    ];
    const query = state.browseSearch;
    el.tabs.innerHTML = tabDefs.map((t) => {
      const isView = VIEW_TAB_KEYS.includes(t.key);
      const count = t.key === "summary" ? countPicked() : t.key === "progression" ? state.purchaseOrder.length : t.key === "otherClasses" ? countOtherClassesPicked() : getList(t.key).length;
      const isActive = isView ? state.activeView === t.key : state.activeView === "calculator" && state.activeTab === t.key;
      const matchCount = isView ? 0 : countMatches(t.key, query);
      const badge = matchCount > 0 ? `<span class="search-badge" title="${matchCount} match${matchCount === 1 ? "" : "es"} for &quot;${escapeHtml(query.trim())}&quot;">${matchCount}</span>` : "";
      return `<button data-tab="${t.key}" class="${isActive ? "active" : ""}${isView ? " summary-tab" : ""}">${escapeHtml(t.label)}<span class="count">(${count})</span>${badge}</button>`;
    }).join("");
    Array.from(el.tabs.querySelectorAll("button")).forEach((btn) => {
      btn.addEventListener("click", () => {
        const key = btn.getAttribute("data-tab");
        if (VIEW_TAB_KEYS.includes(key)) {
          state.activeView = key;
        } else {
          state.activeView = "calculator";
          state.activeTab = key;
          state.selectedNode = null;
        }
        renderAll();
      });
    });
  }
  function formatGuessDisplay(rawCost, guess) {
    if (rawCost !== "?") return { text: escapeHtml(rawCost), isGuess: false };
    if (!guess) return { text: "?", isGuess: false };
    return { text: `~${guess.value}`, isGuess: true, confidence: guess.confidence, basedOn: guess.basedOn, interpolated: !!guess.interpolated, manual: !!guess.manual, title: guessTitle(guess) };
  }
  function costDisplay(catKey, idx, rankIdx, rawCost) {
    return formatGuessDisplay(rawCost, rawCost === "?" ? costGuess(catKey, idx, rankIdx) : null);
  }
  function costDisplayScoped(scope, className, idx, rankIdx, rawCost) {
    return formatGuessDisplay(rawCost, rawCost === "?" ? costGuessScoped(scope, className, idx, rankIdx) : null);
  }
  function effectLookup(catKey, idx) {
    return (progIdx, rankIdx) => effectGuess(catKey, idx, progIdx, rankIdx);
  }
  function effectLookupScoped(scope, className, idx) {
    return (progIdx, rankIdx) => effectGuessScoped(scope, className, idx, progIdx, rankIdx);
  }
  function nextRankBoxHtml(catKey, idx, aa, rank, extraClass = "") {
    const nextRank = rank + 1;
    const disp = costDisplay(catKey, idx, rank, aa.costs[rank]);
    const chip = disp.isGuess ? ` <span class="confidence-chip tier-${disp.confidence}" title="${escapeHtml(disp.title)}">${disp.confidence}</span>` : "";
    return `<div class="next-rank-box${extraClass}${disp.isGuess ? " is-estimate" : ""}">
        <div class="next-rank-title">Next Rank (${nextRank}/${aa.ranks}) &middot; costs <b class="${disp.isGuess ? "is-estimate" : ""}" title="${disp.isGuess ? escapeHtml(disp.title) : ""}">${disp.text}</b> pt(s)${chip}</div>
        <div class="desc">${highlightRankValue(applyPerRankTotal(aa.description, nextRank), nextRank, effectLookup(catKey, idx))}</div>
      </div>`;
  }
  function eraBadgeHtml(aa) {
    const badge = eraBadge(aa);
    if (!badge) return "";
    return `<span class="era-badge ${badge.cssClass}" title="${badge.label} content">${badge.letter}</span>`;
  }
  function renderTree(catKey) {
    const list = getList(catKey);
    if (!list.length) {
      el.treeWrap.innerHTML = '<div class="empty" style="margin-top:60px;">No AAs documented for this category yet.</div>';
      return;
    }
    const hadFocusInTree = el.treeWrap.contains(document.activeElement);
    const grid = document.createElement("div");
    grid.className = "tree-grid";
    const query = state.browseSearch;
    const searching = !!query.trim();
    list.forEach((aa, idx) => {
      const rank = effectiveRank(catKey, idx);
      const hidden = isHidden(catKey, idx);
      if (isSuppressed(catKey, idx)) return;
      const autoIneligible = aa.auto && !isClassEligible(aa);
      const autoBelowLevel = aa.auto && !autoIneligible && rank === 0;
      const autoPartial = aa.auto && !autoIneligible && rank > 0 && rank < aa.ranks;
      const lockReason = !aa.auto && rank < aa.ranks ? structuralLockReason(catKey, idx) : null;
      const locked = !!lockReason || autoBelowLevel || autoIneligible;
      const invalidReason = rank > 0 ? heldRankInvalidReason(catKey, idx) : null;
      const classCap = aa.classRankCap ? classRankCapFor(aa) : aa.ranks;
      const capExceeded = rank > classCap;
      const node = document.createElement("div");
      node.className = "node";
      node.tabIndex = 0;
      node.setAttribute("role", "button");
      node.setAttribute("aria-label", `${aa.name}, rank ${rank} of ${aa.ranks}`);
      node.dataset.idx = String(idx);
      if (aa.auto && !autoBelowLevel && !autoIneligible) node.classList.add("auto");
      else if (!aa.auto && rank >= aa.ranks) node.classList.add("maxed");
      if (locked) node.classList.add("locked");
      if (lockReason && lockReason.kind === "prereq") node.classList.add("locked-prereq");
      if (lockReason && lockReason.kind === "classEligibility" || autoIneligible) node.classList.add("locked-classlock");
      if (invalidReason) node.classList.add("invalidated");
      if (hidden) node.classList.add("hidden-aa");
      if (searching) node.classList.add(aaMatchesQuery(aa, query) ? "search-match" : "search-dim");
      if (invalidReason) node.title = invalidReason;
      else if (autoIneligible) node.title = `Requires one of: ${aa.eligibleClasses.join(", ")}.`;
      else if (autoBelowLevel) node.title = `Automatically granted at level ${aa.levelReq} \u2014 no points needed.`;
      else if (autoPartial) node.title = `Automatically granted \u2014 rank ${rank + 1} at level ${rankLevelReqs(aa)[rank]}.`;
      else if (lockReason) node.title = lockReason.text;
      else if (aa.auto) node.title = "Automatically granted \u2014 no AA points needed.";
      if (state.selectedNode && state.selectedNode.category === catKey && state.selectedNode.idx === idx) {
        node.classList.add("selected");
      }
      node.innerHTML = `
      <div class="icon">${escapeHtml(iconLetter(aa.name))}${eraBadgeHtml(aa)}</div>
      <div class="name">${escapeHtml(aa.name)}</div>
      <div class="rankbar"><div class="fill" style="width:${Math.min(rank, classCap) / aa.ranks * 100}%"></div>${capExceeded ? `<div class="fill-capped" style="width:${(rank - classCap) / aa.ranks * 100}%"></div>` : ""}</div>
      <div class="ranktext">${rank} / ${aa.ranks}</div>
    `;
      if (aa.auto && autoIneligible) {
        const tag = document.createElement("div");
        tag.className = "costtag classlock-tag";
        tag.textContent = "CLASS";
        node.appendChild(tag);
      } else if (aa.auto && !autoBelowLevel) {
        const tag = document.createElement("div");
        tag.className = "costtag auto-tag";
        tag.textContent = "AUTO";
        node.appendChild(tag);
      } else if (aa.auto && autoBelowLevel) {
        const tag = document.createElement("div");
        tag.className = "costtag";
        tag.textContent = `Lv.${aa.levelReq}`;
        node.appendChild(tag);
      } else if (rank < aa.ranks) {
        const tag = document.createElement("div");
        const disp = costDisplay(catKey, idx, rank, aa.costs[rank]);
        tag.className = disp.isGuess ? `costtag is-estimate tier-${disp.confidence}` : "costtag";
        tag.textContent = disp.text;
        if (disp.isGuess) tag.title = disp.title;
        node.appendChild(tag);
      }
      if (lockReason && lockReason.kind === "prereq") {
        const req = document.createElement("div");
        req.className = "costtag prereq-tag";
        req.textContent = "REQ";
        node.appendChild(req);
      }
      if (lockReason && lockReason.kind === "classEligibility") {
        const cls = document.createElement("div");
        cls.className = "costtag classlock-tag";
        cls.textContent = "CLASS";
        node.appendChild(cls);
      }
      if (invalidReason) {
        const warn = document.createElement("div");
        warn.className = "costtag invalid-tag";
        warn.textContent = "\u26A0";
        node.appendChild(warn);
      }
      if (hidden) {
        const tag = document.createElement("div");
        tag.className = "costtag hidden-tag";
        tag.textContent = "HIDDEN";
        tag.title = "Hidden - showing anyway because you've spent points on it, or Show Hidden is on.";
        node.appendChild(tag);
      }
      grid.appendChild(node);
    });
    el.treeWrap.innerHTML = "";
    el.treeWrap.appendChild(grid);
    if (hadFocusInTree && state.selectedNode && state.selectedNode.category === catKey) {
      const focusTarget = grid.querySelector(`[data-idx="${state.selectedNode.idx}"]`);
      if (focusTarget) focusTarget.focus();
    }
  }
  function renderSidePanel() {
    const sel = state.selectedNode;
    if (!sel) {
      el.sidePanel.innerHTML = '<div class="empty">Select an AA node to see its details and spend points.</div>';
      return;
    }
    const list = getList(sel.category);
    const aa = list[sel.idx];
    if (!aa) {
      state.selectedNode = null;
      el.sidePanel.innerHTML = '<div class="empty">Select an AA node to see its details.</div>';
      return;
    }
    const rank = effectiveRank(sel.category, sel.idx);
    const resolved = aa.prereq ? resolvePrereqTarget(aa.prereq, sel.category) : null;
    const atMax = rank >= aa.ranks;
    const blockReason = atMax ? null : getBlockReason(sel.category, sel.idx);
    const nextCost = rank < aa.ranks ? costNum(aa.costs[rank]) : null;
    const dependedOn = rank > 0 && isDependedOn(sel.category, sel.idx, rank);
    const invalidReason = rank > 0 ? heldRankInvalidReason(sel.category, sel.idx) : null;
    const hidden = isHidden(sel.category, sel.idx);
    let html = `<div class="sidepanel-header"><h2>${escapeHtml(aa.name)}</h2><button id="hideToggleBtn" class="hide-toggle-btn${hidden ? " active" : ""}" title="${hidden ? "Unhide this AA" : "Hide this AA from the tree and Browse"}">${hidden ? "Unhide" : "Hide"}</button></div>`;
    html += `<div class="meta">${escapeHtml(labelFor(sel.category))} &middot; Level ${escapeHtml(aa.levelReq)}+</div>`;
    html += `<div class="desc">${highlightRankValue(aa.description, effectiveDisplayRank(aa, rank), effectLookup(sel.category, sel.idx))}</div>`;
    if (invalidReason) {
      html += `<div class="req-line warn">&#9888; No longer valid: ${escapeHtml(invalidReason)}</div>`;
    }
    if (aa.prereq) {
      html += `<div class="req-line ${resolved ? "" : "warn"}"><b>Requires:</b> ${escapeHtml(aa.prereq)}</div>`;
    }
    html += `<div class="rank-controls">
    <button id="decBtn" ${rank <= 0 || aa.auto ? "disabled" : ""} class="${dependedOn ? "blocked" : ""}">&minus;</button>
    <span class="current">${rank} / ${aa.ranks}</span>
    <button id="incBtn" ${atMax || aa.auto ? "disabled" : ""} class="${blockReason ? "blocked" : ""}">+</button>
  </div>`;
    if (aa.auto) {
      const levels = rankLevelReqs(aa);
      if (!isClassEligible(aa)) {
        html += `<div class="req-line warn">Requires one of: ${escapeHtml(aa.eligibleClasses.join(", "))}.</div>`;
      } else if (rank === 0) {
        html += `<div class="req-line warn">Automatically granted at level ${levels[0]} &mdash; not yet active at level ${state.charLevel}.</div>`;
      } else if (rank < aa.ranks) {
        html += `<div class="req-line">Automatically granted &mdash; no AA points required. Rank ${rank + 1} comes at level ${levels[rank]}.</div>`;
      } else {
        html += `<div class="req-line">Automatically granted &mdash; no AA points required, always active once unlocked.</div>`;
      }
      if (aa.ranks > 1 && !hasPerRankLevels(aa) && rank > 0) {
        html += `<div class="req-line" style="color:#63636a;">The wiki doesn't document per-rank level breakpoints for this ability, so it's shown at max rank once level ${levels[0]}+ is reached.</div>`;
      }
    } else {
      if (blockReason) {
        html += `<div class="req-line warn">${escapeHtml(blockReason)}</div>`;
      }
      if (dependedOn) {
        html += `<div class="req-line warn">Another AA depends on this rank &mdash; lower it first.</div>`;
      }
      if (nextCost !== null) {
        html += nextRankBoxHtml(sel.category, sel.idx, aa, rank);
      }
      html += `<div class="rank-costs">` + aa.costs.map((c, i) => {
        const disp = costDisplay(sel.category, sel.idx, i, c);
        const cls = `pip${i < rank ? " spent" : ""}${disp.isGuess ? ` is-estimate tier-${disp.confidence}` : ""}`;
        const title = disp.isGuess ? ` title="${escapeHtml(disp.title)}"` : "";
        return `<span class="${cls}"${title}>R${i + 1}: ${disp.text}</span>`;
      }).join("") + `</div>`;
      if (aa.costs.some((c) => String(c).trim() === "?")) {
        const anyGuessed = aa.costs.some((c, i) => c === "?" && costGuess(sel.category, sel.idx, i));
        html += `<div class="req-line" style="margin-top:10px; color:#63636a;">Some per-rank costs are undocumented on the wiki source ("?") and are treated as 0 pts until known${anyGuessed ? " &mdash; ranks marked with a ~ show a pattern-inferred estimate instead, for reference only" : ""}.</div>`;
      }
    }
    el.sidePanel.innerHTML = html;
    const incBtn = document.getElementById("incBtn");
    const decBtn = document.getElementById("decBtn");
    const hideBtn = document.getElementById("hideToggleBtn");
    if (incBtn) incBtn.addEventListener("click", () => applyAttempt(attemptIncrement(sel.category, sel.idx)));
    if (decBtn) decBtn.addEventListener("click", () => applyAttempt(attemptDecrement(sel.category, sel.idx)));
    if (hideBtn) hideBtn.addEventListener("click", () => {
      setHidden(sel.category, sel.idx, !hidden);
      renderAll();
    });
  }
  function applyAttempt(result) {
    if (result.message) showToast(result.message);
    if (result.changed) renderAll();
  }
  function catKeyForBrowseLabel(catLabel) {
    if (catLabel === "General") return "general";
    if (catLabel === "Archetype") return "archetype";
    if (catLabel === "Special") return "special";
    const slot = state.selectedClasses.indexOf(catLabel);
    return slot >= 0 ? CLASS_SLOT_KEYS[slot] : null;
  }
  function scopeForBrowseLabel(catLabel) {
    if (catLabel === "General") return { scope: "general", className: null };
    if (catLabel === "Archetype") return { scope: "archetype", className: null };
    if (catLabel === "Special") return { scope: "special", className: null };
    return { scope: "class", className: catLabel };
  }
  function renderBrowse() {
    const q = state.browseSearch.trim().toLowerCase();
    const filter = state.browseFilter;
    const items = [];
    function pushList(catLabel, list) {
      const catKey = catKeyForBrowseLabel(catLabel);
      list.forEach((aa, idx) => items.push({ cat: catLabel, aa, catKey, idx }));
    }
    if (filter === "all" || filter === "general") pushList("General", AA_DATA.general);
    if (filter === "all" || filter === "archetype") pushList("Archetype", AA_DATA.archetype);
    if (filter === "all" || filter === "special") pushList("Special", AA_DATA.special);
    if (filter === "all") {
      CLASS_LIST.forEach((c) => pushList(c, AA_DATA.classes[c] || []));
    } else if (CLASS_LIST.includes(filter)) {
      pushList(filter, AA_DATA.classes[filter] || []);
    }
    const searched = q ? items.filter(({ aa }) => aaMatchesQuery(aa, q)) : items;
    const filtered = searched.map((item) => {
      const { scope, className } = scopeForBrowseLabel(item.cat);
      return { ...item, scope, className, owned: ownedRank(scope, className, item.idx) };
    }).filter(({ scope, className, idx, owned, aa }) => {
      if (isSuppressedScoped(scope, className, idx)) return false;
      if (state.browseUnownedOnly && (owned > autoRanksOffset(aa) || aa.auto)) return false;
      return true;
    });
    el.browseGrid.innerHTML = filtered.length ? filtered.map(({ cat, aa, catKey, idx, scope, className, owned }) => {
      const hidden = isHiddenScoped(scope, className, idx);
      const lockReason = catKey ? structuralLockReason(catKey, idx) : null;
      let prereqInfo = "";
      if (aa.prereq) {
        const warn = !!(lockReason && lockReason.kind === "prereq");
        prereqInfo = ` &middot; <span class="prereq-info${warn ? " warn" : ""}">Requires: ${escapeHtml(aa.prereq)}</span>`;
      }
      let eligibleInfo = "";
      if (aa.eligibleClasses) {
        const warn = !!(lockReason && lockReason.kind === "classEligibility");
        eligibleInfo = ` &middot; <span class="eligible-info${warn ? " warn" : ""}">Classes: ${aa.eligibleClasses.map(escapeHtml).join(", ")}</span>`;
      }
      const ownedInfo = owned > 0 ? ` &middot; <span class="owned-info">Owned: ${owned}/${aa.ranks}</span>` : "";
      const costList = aa.costs.map((c, i) => {
        const disp = costDisplayScoped(scope, className, idx, i, c);
        return disp.isGuess ? `<span class="is-estimate tier-${disp.confidence}" title="${escapeHtml(disp.title)}">${disp.text}</span>` : disp.text;
      }).join(" / ");
      return `
      <div class="browse-card${hidden ? " hidden-aa" : ""}${owned > 0 ? " owned" : ""}">
        <div class="top">
          <span class="name">${escapeHtml(aa.name)}${aa.auto ? ' <span class="auto-badge">(AUTO)</span>' : ""}${eraBadgeHtml(aa)}</span>
          <button class="hide-toggle-btn${hidden ? " active" : ""}" data-scope="${scope}" data-classname="${className || ""}" data-idx="${idx}" title="${hidden ? "Unhide this AA" : "Hide this AA from the tree and Browse"}">${hidden ? "Unhide" : "Hide"}</button>
          <span class="cat">${escapeHtml(cat)}</span>
        </div>
        <div class="desc">${highlightRankValue(aa.description, null, effectLookupScoped(scope, className, idx))}</div>
        <div class="info">Ranks: ${aa.ranks} &middot; Cost/rank: ${costList} &middot; Level ${escapeHtml(aa.levelReq)}+${prereqInfo}${eligibleInfo}${ownedInfo}</div>
      </div>`;
    }).join("") : '<div class="empty">No AAs match your search.</div>';
  }
  function wireBrowseClickDelegation() {
    el.browseGrid.addEventListener("click", (e) => {
      const btn = e.target.closest(".hide-toggle-btn");
      if (!btn) return;
      const scope = btn.getAttribute("data-scope");
      const className = btn.getAttribute("data-classname") || null;
      const idx = parseInt(btn.getAttribute("data-idx"), 10);
      setHiddenScoped(scope, className, idx, !isHiddenScoped(scope, className, idx));
      updateShowHiddenToggle();
      renderTabs();
      renderBrowse();
    });
  }
  function renderSummary(totals) {
    const { spent } = totals || computePointTotals();
    el.summaryHeader.innerHTML = `<div class="summary-meta">Classes: <b>${state.selectedClasses.map(escapeHtml).join(" / ")}</b> &middot; Character Level <b>${state.charLevel}</b> &middot; Points Planned: <b>${spent}</b></div>`;
    const sections = AA_CATEGORY_KEYS.map((key) => ({ key, label: shortCategoryLabel(key) }));
    let html = "";
    let anyPicked = false;
    sections.forEach(({ key, label }) => {
      const list = getList(key);
      const picked = list.map((aa, idx) => ({ aa, idx, rank: effectiveRank(key, idx) })).filter((x) => x.rank > 0);
      if (!picked.length) return;
      anyPicked = true;
      html += `<h3 class="summary-section-title">${escapeHtml(label)}</h3>`;
      html += `<div class="browse-grid">` + picked.map(({ aa, idx, rank }) => {
        const invalidReason = heldRankInvalidReason(key, idx);
        const displayRank = effectiveDisplayRank(aa, rank);
        return `
      <div class="browse-card">
        <div class="top"><span class="name">${escapeHtml(aa.name)}${aa.auto ? ' <span class="auto-badge">(AUTO)</span>' : ""}${eraBadgeHtml(aa)}</span><span class="cat">Rank ${rank}/${aa.ranks}</span></div>
        <div class="desc">${highlightRankValue(applyPerRankTotal(aa.description, displayRank), displayRank, effectLookup(key, idx))}</div>
        ${invalidReason ? `<div class="req-line warn">&#9888; No longer valid: ${escapeHtml(invalidReason)}</div>` : ""}
      </div>`;
      }).join("") + `</div>`;
    });
    const otherClassNames = otherClassesWithPicks();
    if (otherClassNames.length) {
      anyPicked = true;
      html += `<div class="summary-other-classes-divider">Also includes picks for classes you're not currently using (see the Other Classes tab too):</div>`;
      html += otherClassesSectionsHtml(otherClassNames);
    }
    el.summaryContent.innerHTML = anyPicked ? html : '<div class="empty">No AAs selected yet &mdash; spend some points in the calculator, then check back here.</div>';
  }
  function otherClassesSectionsHtml(classNames) {
    return classNames.map((className) => {
      const picked = picksForClass(className);
      const subtotal = spentForClass(className);
      const cards = picked.map(({ aa, idx, rank }) => {
        const displayRank = effectiveDisplayRank(aa, rank);
        return `
      <div class="browse-card">
        <div class="top"><span class="name">${escapeHtml(aa.name)}${aa.auto ? ' <span class="auto-badge">(AUTO)</span>' : ""}${eraBadgeHtml(aa)}</span><span class="cat">Rank ${rank}/${aa.ranks}</span></div>
        <div class="desc">${highlightRankValue(applyPerRankTotal(aa.description, displayRank), displayRank, effectLookupScoped("class", className, idx))}</div>
      </div>`;
      }).join("");
      return `
      <h3 class="summary-section-title">${escapeHtml(className)}</h3>
      <div class="other-classes-subtotal">Not one of your current 3 classes &mdash; ${subtotal} point${subtotal === 1 ? "" : "s"} spent here still count${subtotal === 1 ? "s" : ""} toward Points Planned above.</div>
      <div class="browse-grid">${cards}</div>`;
    }).join("");
  }
  function renderOtherClasses() {
    const classNames = otherClassesWithPicks();
    if (!classNames.length) {
      el.otherClassesContent.innerHTML = '<div class="empty">Nothing here yet &mdash; swap a class out after spending points on it, and its picks show up here instead of disappearing.</div>';
      return;
    }
    el.otherClassesContent.innerHTML = otherClassesSectionsHtml(classNames);
  }
  var expandedSteps = /* @__PURE__ */ new Set();
  function expandKey(s) {
    return `${s.scope}:${s.className || ""}:${s.idx}:${s.stepRank}`;
  }
  var openMoveMenuKey = null;
  var editingWaypointPts = null;
  var modalSelectedColor = null;
  var PROGRESSION_DRAG_TYPE = "application/x-aacalc-progression-step";
  var dragSrcIndex = null;
  function isOwnDrag(e) {
    return dragSrcIndex !== null && e.dataTransfer.types.includes(PROGRESSION_DRAG_TYPE);
  }
  var AUTOSCROLL_EDGE_PX = 70;
  var AUTOSCROLL_MAX_SPEED = 18;
  var autoScrollDir = 0;
  var autoScrollSpeed = 0;
  var autoScrollRAF = null;
  var dragBaselineWarnCount = 0;
  var dragWarnCacheToIndex = null;
  var dragWarnCacheResult = false;
  var markedDragRow = null;
  function markDragOver(rowEl, cls) {
    rowEl.classList.add(cls);
    markedDragRow = rowEl;
  }
  function clearDragOverMarks() {
    if (!markedDragRow) return;
    markedDragRow.classList.remove("drag-over-top", "drag-over-bottom", "drag-warn");
    markedDragRow = null;
  }
  function autoScrollStep() {
    if (autoScrollDir === 0) {
      autoScrollRAF = null;
      return;
    }
    const before = el.progressionWrap.scrollTop;
    el.progressionWrap.scrollTop = before + autoScrollDir * autoScrollSpeed;
    if (el.progressionWrap.scrollTop === before) {
      autoScrollRAF = null;
      return;
    }
    autoScrollRAF = requestAnimationFrame(autoScrollStep);
  }
  function updateAutoScroll(e) {
    const rect = el.progressionWrap.getBoundingClientRect();
    const distTop = e.clientY - rect.top;
    const distBottom = rect.bottom - e.clientY;
    let dir = 0;
    let speed = 0;
    if (distTop < AUTOSCROLL_EDGE_PX) {
      dir = -1;
      speed = AUTOSCROLL_MAX_SPEED * (1 - Math.max(distTop, 0) / AUTOSCROLL_EDGE_PX);
    } else if (distBottom < AUTOSCROLL_EDGE_PX) {
      dir = 1;
      speed = AUTOSCROLL_MAX_SPEED * (1 - Math.max(distBottom, 0) / AUTOSCROLL_EDGE_PX);
    }
    autoScrollDir = dir;
    autoScrollSpeed = speed;
    if (dir !== 0 && autoScrollRAF === null) autoScrollRAF = requestAnimationFrame(autoScrollStep);
  }
  function stopAutoScroll() {
    autoScrollDir = 0;
    autoScrollSpeed = 0;
    if (autoScrollRAF !== null) {
      cancelAnimationFrame(autoScrollRAF);
      autoScrollRAF = null;
    }
  }
  function findPrecedingRow(fromEl) {
    let sib = fromEl.previousElementSibling;
    while (sib && !sib.classList.contains("progression-row")) sib = sib.previousElementSibling;
    return sib;
  }
  function countPrereqWarns(steps) {
    return steps.reduce((n, s) => n + (s.prereqWarn ? 1 : 0), 0);
  }
  function dragWouldIntroduceWarn(toIndex) {
    if (dragSrcIndex === null) return false;
    let insertAt = toIndex > dragSrcIndex ? toIndex - 1 : toIndex;
    if (insertAt === dragSrcIndex) return false;
    if (dragWarnCacheToIndex === toIndex) return dragWarnCacheResult;
    const hypothetical = state.purchaseOrder.slice();
    const [entry] = hypothetical.splice(dragSrcIndex, 1);
    hypothetical.splice(insertAt, 0, entry);
    const hypoSteps = computeProgressionSteps(hypothetical);
    const result = hypoSteps[insertAt].prereqWarn || countPrereqWarns(hypoSteps) > dragBaselineWarnCount;
    dragWarnCacheToIndex = toIndex;
    dragWarnCacheResult = result;
    return result;
  }
  function renderWaypointChips() {
    if (!state.waypoints.length) {
      el.waypointChips.innerHTML = "";
      return;
    }
    el.waypointChips.innerHTML = state.waypoints.map((w) => {
      const dot = w.color ? `<span class="color-dot color-${w.color}"></span>` : "";
      const labelText = w.label ? `${w.pts} pts &middot; ${escapeHtml(w.label)}` : `${w.pts} pts`;
      return `<span class="waypoint-chip" data-pts="${w.pts}">
      <span class="chip-label" data-pts="${w.pts}">${dot}${labelText}</span>
      <button class="chip-remove" data-pts="${w.pts}" title="Remove this waypoint" aria-label="Remove waypoint">&times;</button>
    </span>`;
    }).join("");
    Array.from(el.waypointChips.querySelectorAll(".chip-label")).forEach((labelEl) => {
      labelEl.addEventListener("click", () => {
        openWaypointModal(parseInt(labelEl.getAttribute("data-pts"), 10));
      });
    });
    Array.from(el.waypointChips.querySelectorAll(".chip-remove")).forEach((btn) => {
      btn.addEventListener("click", () => {
        removeWaypoint(parseInt(btn.getAttribute("data-pts"), 10));
        renderProgression();
      });
    });
  }
  function renderColorSwatches() {
    const noneSwatch = `<button type="button" class="color-swatch none${modalSelectedColor === null ? " active" : ""}" data-color="" title="No color" aria-label="No color"></button>`;
    const colorSwatches = WAYPOINT_COLORS.map(
      (c) => `<button type="button" class="color-swatch color-${c.key}${modalSelectedColor === c.key ? " active" : ""}" data-color="${c.key}" title="${c.key}" aria-label="${c.key}"></button>`
    ).join("");
    el.waypointColorSwatches.innerHTML = noneSwatch + colorSwatches;
    Array.from(el.waypointColorSwatches.querySelectorAll(".color-swatch")).forEach((btn) => {
      btn.addEventListener("click", () => {
        modalSelectedColor = btn.getAttribute("data-color") || null;
        renderColorSwatches();
      });
    });
  }
  function openWaypointModal(existingPts = null) {
    const existing = existingPts !== null ? state.waypoints.find((w) => w.pts === existingPts) : null;
    editingWaypointPts = existingPts;
    modalSelectedColor = existing ? existing.color : null;
    el.waypointModalTitle.textContent = existing ? "Edit Waypoint" : "Add Waypoint";
    el.waypointPtsInput.value = String(existing ? existing.pts : spentPoints());
    el.waypointLabelInput.value = existing && existing.label ? existing.label : "";
    el.deleteWaypointBtn.classList.toggle("hidden", !existing);
    renderColorSwatches();
    openModal(el.waypointModal, el.waypointPtsInput);
    el.waypointPtsInput.select();
  }
  function closeWaypointModal() {
    closeModal(el.waypointModal);
  }
  function handleSaveWaypoint() {
    const rawPts = parseInt(el.waypointPtsInput.value.trim(), 10);
    if (!Number.isFinite(rawPts) || rawPts < 0) {
      showToast("Enter a point total of 0 or more.");
      return;
    }
    const pts = Math.min(rawPts, MAX_WAYPOINT_PTS);
    const colliding = state.waypoints.find((w) => w.pts === pts && w.pts !== editingWaypointPts);
    if (colliding) {
      const desc = colliding.label ? `"${colliding.label}"` : "the unnamed waypoint";
      if (!confirm(`${desc} is already set at ${pts} pts. Replace it?`)) return;
    }
    if (editingWaypointPts !== null && editingWaypointPts !== pts) {
      removeWaypoint(editingWaypointPts);
    }
    addOrUpdateWaypoint(pts, el.waypointLabelInput.value, modalSelectedColor);
    closeWaypointModal();
    renderProgression();
  }
  function handleDeleteWaypoint() {
    if (editingWaypointPts !== null) removeWaypoint(editingWaypointPts);
    closeWaypointModal();
    renderProgression();
  }
  function classBadgeClass(s) {
    if (s.scope !== "class") return "";
    if (!s.active) return " step-cat-inactive";
    return ` step-cat-slot${CLASS_SLOT_KEYS.indexOf(s.category)}`;
  }
  function waypointSections(timeline, totalVisible, movingStepCost, movingIndex) {
    const adjustedCumulative = (step) => step.index >= movingIndex ? step.cumulative - movingStepCost : step.cumulative;
    const sections = [];
    for (let i = 0; i < timeline.length; i++) {
      let slotToVisiblePos = function(slot) {
        if (slot < sectionSteps.length) return { pos: sectionSteps[slot].visiblePos, anchored: true };
        for (let j = i + 1 + sectionSteps.length; j < timeline.length; j++) {
          if (timeline[j].type === "step") return { pos: timeline[j].visiblePos, anchored: true };
        }
        return { pos: totalVisible + 1, anchored: false };
      };
      const entry = timeline[i];
      if (entry.type !== "divider") continue;
      const sectionSteps = [];
      for (let j = i + 1; j < timeline.length && timeline[j].type !== "divider"; j++) {
        sectionSteps.push(timeline[j]);
      }
      let baselineBeforeSection = 0;
      for (let j = i - 1; j >= 0; j--) {
        if (timeline[j].type === "step") {
          baselineBeforeSection = adjustedCumulative(timeline[j]);
          break;
        }
      }
      let highPts = Infinity;
      for (let j = i + 1; j < timeline.length; j++) {
        if (timeline[j].type === "divider") {
          highPts = timeline[j].pts;
          break;
        }
      }
      const slotBaselines = [baselineBeforeSection, ...sectionSteps.map((st) => adjustedCumulative(st))];
      const upperFits = slotBaselines.map((b) => b + movingStepCost <= highPts);
      let topSlot = slotBaselines.findIndex((b) => b + movingStepCost > entry.pts);
      if (topSlot < 0) topSlot = slotBaselines.length;
      const topFits = topSlot < slotBaselines.length && upperFits[topSlot];
      let bottomSlot = topSlot;
      for (let k = topSlot; k < upperFits.length; k++) {
        if (upperFits[k]) bottomSlot = k;
        else break;
      }
      const notFitTitle = topFits ? "" : "This step doesn't fit anywhere in this section's points range.";
      const top = topFits ? slotToVisiblePos(topSlot) : null;
      const bottom = topFits ? slotToVisiblePos(bottomSlot) : null;
      sections.push({
        label: entry.label || `${entry.pts} pts`,
        topFits,
        topVisiblePos: top ? top.pos : null,
        topAnchored: top ? top.anchored : false,
        bottomFits: topFits,
        bottomVisiblePos: bottom ? bottom.pos : null,
        bottomAnchored: bottom ? bottom.anchored : false,
        notFitTitle
      });
    }
    return sections;
  }
  function moveMenuHtml(s, timeline, totalVisible) {
    const sections = waypointSections(timeline, totalVisible, s.stepCost, s.index);
    const items = [
      { label: "Top of list", pos: 1, fits: true, anchored: false },
      { label: "Bottom of list", pos: totalVisible, fits: true, anchored: false }
    ];
    sections.forEach((sec) => {
      items.push({ label: `${sec.label} \u2014 top`, pos: sec.topVisiblePos, fits: sec.topFits, title: sec.notFitTitle, anchored: sec.topAnchored });
      items.push({ label: `${sec.label} \u2014 bottom`, pos: sec.bottomVisiblePos, fits: sec.bottomFits, title: sec.notFitTitle, anchored: sec.bottomAnchored });
    });
    const itemsHtml = items.map(
      (item) => `<button type="button" class="move-menu-item" data-from-index="${s.index}" data-target-pos="${item.fits ? item.pos : ""}" data-anchored="${item.anchored ? 1 : 0}" ${item.fits ? "" : "disabled"} title="${escapeHtml(item.title || "")}">${escapeHtml(item.label)}</button>`
    ).join("");
    return `<div class="move-menu" data-key="${expandKey(s)}">
      ${itemsHtml}
      <div class="move-menu-position-row">
        <label class="move-menu-position-label">Position
          <input type="number" class="move-menu-position-input" min="1" max="${totalVisible}" value="${s.visiblePos}" />
        </label>
        <button type="button" class="btn move-menu-go" data-from-index="${s.index}">Go</button>
      </div>
    </div>`;
  }
  function renderProgression(totals) {
    el.undoLastBtn.disabled = !canUndo();
    el.clearOwnedBtn.disabled = !hasAnyOwned();
    const { ownedReal, ownedExtra } = totals || computePointTotals();
    const steps = computeProgressionSteps();
    let togoReal = 0;
    let togoExtra = 0;
    steps.forEach((s, i) => {
      if (s.owned) return;
      const prev = i > 0 ? steps[i - 1] : { cumulative: 0, blendedCumulative: 0 };
      togoReal += s.stepCost;
      togoExtra += s.blendedCumulative - prev.blendedCumulative - (s.cumulative - prev.cumulative);
    });
    function blendedFigure(real, extra) {
      return extra > 0 ? `<span class="is-estimate" title="${real} confirmed + ${extra} estimated.">~${real + extra}</span>` : `${real}`;
    }
    el.ownedSummary.innerHTML = `${blendedFigure(ownedReal, ownedExtra)} pt${ownedReal + ownedExtra === 1 ? "" : "s"} owned, ${blendedFigure(togoReal, togoExtra)} to go`;
    renderWaypointChips();
    if (!state.purchaseOrder.length) {
      el.progressionContent.innerHTML = '<div class="empty">No AAs picked yet &mdash; your training order will appear here as you spend points, and you can reorder it afterward to plan ahead.</div>';
      return;
    }
    steps.forEach((s, i) => {
      s.visiblePos = i + 1;
    });
    const timeline = computeProgressionTimeline(steps);
    const htmlParts = timeline.map((entry) => {
      if (entry.type === "divider") {
        const dot = entry.color ? `<span class="color-dot color-${entry.color}"></span>` : "";
        const labelText = entry.label ? `${escapeHtml(entry.label)} &middot; ` : "";
        return `<div class="progression-divider${entry.unreached ? " unreached" : ""}" data-pts="${entry.pts}" title="Click to edit this waypoint">
        <span class="divider-line"></span>
        ${dot}<span class="divider-label">${labelText}${entry.pts} pts${entry.unreached ? " &middot; not reached yet" : ""}</span>
        <span class="divider-line"></span>
      </div>`;
      }
      const s = entry;
      const canExpand = s.active && !!(s.aa && s.stepRank < s.aa.ranks);
      const key = expandKey(s);
      const expanded = canExpand && expandedSteps.has(key);
      const segClass = s.segmentColor ? ` segment-color-${s.segmentColor}` : "";
      const stepDisp = s.aa ? costDisplayScoped(s.scope, s.className, s.idx, s.stepRank - 1, s.aa.costs[s.stepRank - 1]) : { isGuess: false };
      const totalIsEstimate = s.blendedCumulative !== s.cumulative;
      const totalTitle = totalIsEstimate ? `${s.cumulative} confirmed + ${s.blendedCumulative - s.cumulative} estimated.` : "";
      const warnTitles = [];
      if (s.prereqWarn) warnTitles.push("Prerequisite not yet trained at this point in the sequence.");
      if (s.classCapWarn) warnTitles.push(`Exceeds the rank ${classRankCapFor(s.aa)} cap for your currently selected classes.`);
      if (s.classEligibilityWarn) warnTitles.push(`Requires one of: ${s.aa.eligibleClasses.join(", ")}.`);
      const rowWarn = warnTitles.length > 0;
      const inactiveWarnTitle = s.active ? "" : `Not one of your current 3 classes \u2014 swap ${s.classesLabel || ""} back in to keep training this.`;
      const row = `<div class="progression-row${rowWarn ? " prereq-warn-row" : ""}${s.active ? "" : " inactive"}${segClass}" draggable="true" data-index="${s.index}" data-key="${key}">
      <span class="drag-handle" title="Drag to reorder" aria-hidden="true">&#8942;&#8942;</span>
      <span class="step-num">${s.visiblePos}</span>
      <span class="step-info">
        <span class="step-name${s.owned ? " owned" : ""}">${escapeHtml(s.name)} <span class="step-rank">rank ${s.stepRank}</span></span>
        <span class="step-cat${classBadgeClass(s)}">${escapeHtml(s.label)}</span>
      </span>
      ${rowWarn ? `<span class="step-warn" title="${escapeHtml(warnTitles.join(" "))}">&#9888;</span>` : ""}
      ${!s.active ? `<span class="step-warn step-inactive-warn" title="${escapeHtml(inactiveWarnTitle)}">&#9888;</span>` : ""}
      <span class="step-cost">
        <span class="cost-this${stepDisp.isGuess ? ` is-estimate tier-${stepDisp.confidence}` : ""}"${stepDisp.isGuess ? ` title="${escapeHtml(stepDisp.title)}"` : ""}>+${stepDisp.isGuess ? stepDisp.text : s.stepCost} ${stepDisp.isGuess ? "pt(s)" : `pt${s.stepCost === 1 ? "" : "s"}`}</span>
        <span class="cost-total${totalIsEstimate ? " is-estimate" : ""}"${totalIsEstimate ? ` title="${escapeHtml(totalTitle)}"` : ""}>${totalIsEstimate ? `~${s.blendedCumulative}` : s.cumulative} total</span>
      </span>
      <span class="step-controls" draggable="false">
        <button class="step-btn step-own${s.owned ? " active" : ""}" data-scope="${escapeHtml(s.scope)}" data-classname="${escapeHtml(s.className || "")}" data-idx="${s.idx}" data-rank="${s.stepRank}" title="${s.owned ? "Mark as not yet owned" : "Mark as owned \u2014 you've actually trained this in-game"}">${s.owned ? "&#10003;" : "&#9675;"}</button>
        <button class="step-btn" data-move="up" data-index="${s.index}" ${s.index === steps[0].index ? "disabled" : ""}>&uarr;</button>
        <button class="step-btn" data-move="down" data-index="${s.index}" ${s.index === steps[steps.length - 1].index ? "disabled" : ""}>&darr;</button>
        <button class="step-btn step-expand${expanded ? " active" : ""}" data-key="${key}" ${canExpand ? "" : "disabled"} title="${!s.active ? `Swap ${escapeHtml(s.classesLabel || "")} back into one of your 3 slots to preview this.` : canExpand ? "Preview next rank" : "Already at max rank"}">${expanded ? "&and;" : "&or;"}</button>
        <button class="step-btn step-add" data-category="${s.category || ""}" data-idx="${s.categoryIdx}" ${s.active && s.isLast && s.aa && s.stepRank < s.aa.ranks ? "" : "disabled"} title="${!s.active ? `Swap ${escapeHtml(s.classesLabel || "")} back into one of your 3 slots to keep training this.` : !s.isLast ? "Only this AA's current top rank can be extended here" : s.aa && s.stepRank >= s.aa.ranks ? "Already at max rank" : "Add another rank"}">+</button>
        <button class="step-btn step-remove" data-category="${s.category || ""}" data-idx="${s.categoryIdx}" ${s.active && s.isLast ? "" : "disabled"} title="${!s.active ? `Swap ${escapeHtml(s.classesLabel || "")} back into one of your 3 slots to keep training this.` : !s.isLast ? "Remove this AA's highest rank first" : s.stepRank === 1 ? "Remove this AA from your build" : "Remove this rank"}">${s.stepRank === 1 ? "&times;" : "&minus;"}</button>
        <span class="move-menu-wrap">
          <button class="step-btn step-move${openMoveMenuKey === key ? " active" : ""}" data-key="${key}" title="Move to...">&#8943;</button>
          ${openMoveMenuKey === key ? moveMenuHtml(s, timeline, steps.length) : ""}
        </span>
      </span>
    </div>`;
      if (!expanded) return row;
      return row + nextRankBoxHtml(s.category, s.categoryIdx, s.aa, s.stepRank, " progression-next-rank");
    });
    const focus = progressionFocus();
    el.progressionContent.innerHTML = htmlParts.join("");
    restoreProgressionFocus(focus);
  }
  var STEP_BUTTON_KINDS = ["step-own", "step-expand", "step-add", "step-remove", "step-move"];
  function progressionFocus() {
    const active = document.activeElement;
    const row = active && active.closest && active.closest(".progression-row");
    if (!row || !el.progressionContent.contains(row)) return null;
    const btn = active.closest(".step-btn");
    const kind = !btn ? null : btn.getAttribute("data-move") || STEP_BUTTON_KINDS.find((k) => btn.classList.contains(k));
    return { key: row.getAttribute("data-key"), index: parseInt(row.getAttribute("data-index"), 10), kind };
  }
  function restoreProgressionFocus(focus) {
    if (!focus) return;
    const rows = Array.from(el.progressionContent.querySelectorAll(".progression-row"));
    const row = rows.find((r) => r.getAttribute("data-key") === focus.key) || rows[Math.min(focus.index, rows.length - 1)];
    if (!row) return;
    const selector = focus.kind === "up" || focus.kind === "down" ? `.step-btn[data-move="${focus.kind}"]` : `.${focus.kind}`;
    const same = focus.kind ? row.querySelector(selector) : null;
    const target = same && !same.disabled ? same : row.querySelector(".step-btn:not([disabled])");
    if (target) target.focus();
  }
  function wireProgressionRowEvents() {
    el.progressionContent.addEventListener("click", (e) => {
      const moveBtn = e.target.closest(".step-btn[data-move]");
      if (moveBtn) {
        if (moveBtn.disabled) return;
        const idx = parseInt(moveBtn.getAttribute("data-index"), 10);
        const dir = moveBtn.getAttribute("data-move") === "up" ? -1 : 1;
        moveProgressionEntry(idx, dir);
        return;
      }
      const expandBtn = e.target.closest(".step-expand");
      if (expandBtn) {
        if (expandBtn.disabled) return;
        const key = expandBtn.getAttribute("data-key");
        if (expandedSteps.has(key)) expandedSteps.delete(key);
        else expandedSteps.add(key);
        renderProgression();
        return;
      }
      const moveTriggerBtn = e.target.closest(".step-move");
      if (moveTriggerBtn) {
        e.stopPropagation();
        const key = moveTriggerBtn.getAttribute("data-key");
        openMoveMenuKey = openMoveMenuKey === key ? null : key;
        renderProgression();
        return;
      }
      const moveItemBtn = e.target.closest(".move-menu-item");
      if (moveItemBtn) {
        if (moveItemBtn.disabled) return;
        e.stopPropagation();
        const fromIndex = parseInt(moveItemBtn.getAttribute("data-from-index"), 10);
        const targetPos = parseInt(moveItemBtn.getAttribute("data-target-pos"), 10);
        const anchored = moveItemBtn.getAttribute("data-anchored") === "1";
        openMoveMenuKey = null;
        moveToVisiblePosition(fromIndex, targetPos, anchored);
        return;
      }
      const moveGoBtn = e.target.closest(".move-menu-go");
      if (moveGoBtn) {
        e.stopPropagation();
        const fromIndex = parseInt(moveGoBtn.getAttribute("data-from-index"), 10);
        const input = moveGoBtn.parentElement.querySelector(".move-menu-position-input");
        const raw = parseInt(input.value, 10);
        const clamped = Math.max(1, Math.min(state.purchaseOrder.length, Number.isFinite(raw) ? raw : 1));
        openMoveMenuKey = null;
        moveToVisiblePosition(fromIndex, clamped, false);
        return;
      }
      const addBtn = e.target.closest(".step-add");
      if (addBtn) {
        if (addBtn.disabled) return;
        const category = addBtn.getAttribute("data-category");
        const idx = parseInt(addBtn.getAttribute("data-idx"), 10);
        applyAttempt(attemptIncrement(category, idx));
        return;
      }
      const removeBtn = e.target.closest(".step-remove");
      if (removeBtn) {
        if (removeBtn.disabled) return;
        const category = removeBtn.getAttribute("data-category");
        const idx = parseInt(removeBtn.getAttribute("data-idx"), 10);
        applyAttempt(attemptDecrement(category, idx));
        return;
      }
      const ownBtn = e.target.closest(".step-own");
      if (ownBtn) {
        const scope = ownBtn.getAttribute("data-scope");
        const className = ownBtn.getAttribute("data-classname") || null;
        const idx = parseInt(ownBtn.getAttribute("data-idx"), 10);
        const rank = parseInt(ownBtn.getAttribute("data-rank"), 10);
        const nowOwned = ownBtn.classList.contains("active");
        const newRank = nowOwned ? rank - 1 : rank;
        setOwnedRank(scope, className, idx, newRank <= autoRanksOffsetScoped(scope, className, idx) ? 0 : newRank);
        renderAll();
        return;
      }
      const divider = e.target.closest(".progression-divider");
      if (divider) openWaypointModal(parseInt(divider.getAttribute("data-pts"), 10));
    });
    el.progressionContent.addEventListener("dragstart", (e) => {
      const rowEl = e.target.closest(".progression-row");
      if (!rowEl) return;
      dragSrcIndex = parseInt(rowEl.getAttribute("data-index"), 10);
      dragBaselineWarnCount = countPrereqWarns(computeProgressionSteps());
      dragWarnCacheToIndex = null;
      rowEl.classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
      e.dataTransfer.setData("text/plain", String(dragSrcIndex));
      e.dataTransfer.setData(PROGRESSION_DRAG_TYPE, String(dragSrcIndex));
    });
    el.progressionContent.addEventListener("dragend", (e) => {
      const rowEl = e.target.closest(".progression-row");
      if (!rowEl) return;
      rowEl.classList.remove("dragging");
      clearDragOverMarks();
      dragSrcIndex = null;
    });
    el.progressionContent.addEventListener("dragover", (e) => {
      if (!isOwnDrag(e)) return;
      const rowEl = e.target.closest(".progression-row");
      if (rowEl) {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
        clearDragOverMarks();
        const overIndex = parseInt(rowEl.getAttribute("data-index"), 10);
        if (overIndex === dragSrcIndex) return;
        const rect = rowEl.getBoundingClientRect();
        const before = e.clientY - rect.top < rect.height / 2;
        const toIndex = before ? overIndex : overIndex + 1;
        markDragOver(rowEl, before ? "drag-over-top" : "drag-over-bottom");
        if (dragWouldIntroduceWarn(toIndex)) rowEl.classList.add("drag-warn");
        return;
      }
      const boxEl = e.target.closest(".progression-next-rank");
      if (boxEl) {
        const ownerRow = boxEl.previousElementSibling;
        if (!ownerRow || !ownerRow.classList.contains("progression-row")) return;
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
        clearDragOverMarks();
        const overIndex = parseInt(ownerRow.getAttribute("data-index"), 10);
        if (overIndex === dragSrcIndex) return;
        markDragOver(ownerRow, "drag-over-bottom");
        if (dragWouldIntroduceWarn(overIndex + 1)) ownerRow.classList.add("drag-warn");
        return;
      }
      const divEl = e.target.closest(".progression-divider");
      if (divEl) {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
        clearDragOverMarks();
        const ownerRow = findPrecedingRow(divEl);
        if (!ownerRow) {
          const firstRow = el.progressionContent.querySelector(".progression-row");
          if (firstRow && parseInt(firstRow.getAttribute("data-index"), 10) !== dragSrcIndex) {
            markDragOver(firstRow, "drag-over-top");
            if (dragWouldIntroduceWarn(0)) firstRow.classList.add("drag-warn");
          }
          return;
        }
        const overIndex = parseInt(ownerRow.getAttribute("data-index"), 10);
        if (overIndex === dragSrcIndex) return;
        markDragOver(ownerRow, "drag-over-bottom");
        if (dragWouldIntroduceWarn(overIndex + 1)) ownerRow.classList.add("drag-warn");
      }
    });
    el.progressionContent.addEventListener("drop", (e) => {
      if (!isOwnDrag(e)) return;
      const rowEl = e.target.closest(".progression-row");
      if (rowEl) {
        e.preventDefault();
        const rect = rowEl.getBoundingClientRect();
        const before = e.clientY - rect.top < rect.height / 2;
        const overIndex = parseInt(rowEl.getAttribute("data-index"), 10);
        moveProgressionEntryTo(dragSrcIndex, before ? overIndex : overIndex + 1);
        dragSrcIndex = null;
        stopAutoScroll();
        return;
      }
      const boxEl = e.target.closest(".progression-next-rank");
      if (boxEl) {
        const ownerRow = boxEl.previousElementSibling;
        if (!ownerRow || !ownerRow.classList.contains("progression-row")) return;
        e.preventDefault();
        const overIndex = parseInt(ownerRow.getAttribute("data-index"), 10);
        moveProgressionEntryTo(dragSrcIndex, overIndex + 1);
        dragSrcIndex = null;
        stopAutoScroll();
        return;
      }
      const divEl = e.target.closest(".progression-divider");
      if (divEl) {
        e.preventDefault();
        const ownerRow = findPrecedingRow(divEl);
        const toIndex = ownerRow ? parseInt(ownerRow.getAttribute("data-index"), 10) + 1 : 0;
        moveProgressionEntryTo(dragSrcIndex, toIndex);
        dragSrcIndex = null;
        stopAutoScroll();
      }
    });
  }
  function undoLast() {
    applyAttempt(undoLastMutation());
  }
  function moveProgressionEntry(index, dir) {
    const target = index + dir;
    if (target < 0 || target >= state.purchaseOrder.length) return;
    const a = state.purchaseOrder[index];
    const b = state.purchaseOrder[target];
    const sameAA = a.scope === b.scope && a.idx === b.idx && (a.className || null) === (b.className || null);
    if (sameAA) {
      showToast("Can't reorder different ranks of the same AA.");
      return;
    }
    moveEntry(index, target);
    renderProgression();
  }
  function moveProgressionEntryTo(fromIndex, toIndex) {
    if (toIndex > fromIndex) toIndex -= 1;
    if (fromIndex === toIndex) return;
    moveEntry(fromIndex, toIndex);
    renderProgression();
  }
  function absoluteIndexForVisiblePosition(targetVisiblePos, fromIndex, anchored) {
    const raw = targetVisiblePos <= 1 ? 0 : Math.min(targetVisiblePos - 1, state.purchaseOrder.length - 1);
    return anchored && raw > fromIndex ? raw - 1 : raw;
  }
  function moveToVisiblePosition(fromIndex, targetVisiblePos, anchored) {
    const toIdx = absoluteIndexForVisiblePosition(targetVisiblePos, fromIndex, anchored);
    if (toIdx === fromIndex) return;
    moveEntry(fromIndex, toIdx);
    renderProgression();
  }
  function lastProgressionRow() {
    const rows = el.progressionContent.querySelectorAll(".progression-row");
    return rows.length ? rows[rows.length - 1] : null;
  }
  function isBelowLastRow(e) {
    const last = lastProgressionRow();
    return !!last && e.clientY >= last.getBoundingClientRect().bottom;
  }
  function closeMoveMenu() {
    if (openMoveMenuKey === null) return;
    openMoveMenuKey = null;
    renderProgression();
  }
  function wireProgressionDropZone() {
    document.addEventListener("click", (e) => {
      if (openMoveMenuKey === null) return;
      if (e.target.closest(".move-menu-wrap")) return;
      closeMoveMenu();
    });
    el.progressionWrap.addEventListener("dragover", (e) => {
      if (!isOwnDrag(e)) return;
      updateAutoScroll(e);
    });
    document.addEventListener("dragend", stopAutoScroll);
    el.progressionWrap.addEventListener("dragover", (e) => {
      if (!isOwnDrag(e) || e.target !== el.progressionWrap) return;
      if (!isBelowLastRow(e)) {
        clearDragOverMarks();
        return;
      }
      e.preventDefault();
      e.dataTransfer.dropEffect = "move";
      clearDragOverMarks();
      const last = lastProgressionRow();
      if (last && parseInt(last.getAttribute("data-index"), 10) !== dragSrcIndex) {
        markDragOver(last, "drag-over-bottom");
        if (dragWouldIntroduceWarn(state.purchaseOrder.length)) last.classList.add("drag-warn");
      }
    });
    el.progressionWrap.addEventListener("drop", (e) => {
      if (!isOwnDrag(e) || e.target !== el.progressionWrap) return;
      if (!isBelowLastRow(e)) return;
      e.preventDefault();
      moveProgressionEntryTo(dragSrcIndex, state.purchaseOrder.length);
      dragSrcIndex = null;
      stopAutoScroll();
    });
    el.progressionContent.addEventListener("dragover", (e) => {
      if (!isOwnDrag(e) || e.target !== el.progressionContent) return;
      clearDragOverMarks();
    });
  }
  function populateStaticControls() {
    el.levelInput.max = String(MAX_CHAR_LEVEL);
    el.browseFilter.innerHTML = `<option value="all">All Categories</option><option value="general">General</option><option value="archetype">Archetype</option><option value="special">Special</option><optgroup label="Class">` + CLASS_LIST.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("") + `</optgroup>`;
    if (USER_CHANGELOG[0]) el.versionTag.textContent = `v${USER_CHANGELOG[0].version}`;
    updateVersionDot();
  }
  function updateVersionDot() {
    const current = USER_CHANGELOG[0] && USER_CHANGELOG[0].version;
    if (!current) return;
    let lastSeen = null;
    try {
      lastSeen = localStorage.getItem(LAST_SEEN_VERSION_KEY);
    } catch (e) {
    }
    if (lastSeen === null) {
      try {
        localStorage.setItem(LAST_SEEN_VERSION_KEY, current);
      } catch (e) {
      }
      el.versionTag.classList.remove("unread");
      return;
    }
    el.versionTag.classList.toggle("unread", lastSeen !== current);
  }
  function showToast(msg) {
    el.toast.textContent = msg;
    el.toast.classList.add("show");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => el.toast.classList.remove("show"), Math.min(12e3, 2200 + 50 * String(msg).length));
  }
  function updateChangelogFade() {
    const el2 = el.changelogContent;
    const atBottom = el2.scrollTop + el2.clientHeight >= el2.scrollHeight - 1;
    el.changelogFade.classList.toggle("hidden", atBottom);
  }
  function openChangelogModal() {
    el.changelogContent.innerHTML = USER_CHANGELOG.map((entry) => `
    <div class="changelog-entry">
      <div class="changelog-version">v${escapeHtml(entry.version)} <span class="changelog-date">${escapeHtml(entry.date)}</span></div>
      <ul>${entry.items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </div>`).join("") || '<div class="empty">Nothing here yet.</div>';
    openModal(el.changelogModal, el.closeChangelogBtn);
    el.changelogContent.scrollTop = 0;
    updateChangelogFade();
    el.changelogContent.onscroll = updateChangelogFade;
    el.versionTag.classList.remove("unread");
    if (USER_CHANGELOG[0]) {
      try {
        localStorage.setItem(LAST_SEEN_VERSION_KEY, USER_CHANGELOG[0].version);
      } catch (e) {
      }
    }
  }
  function closeChangelogModal() {
    closeModal(el.changelogModal);
  }
  function renderBuildsList() {
    const builds = listBuilds();
    const activeId = getActiveBuildId();
    el.buildsList.innerHTML = builds.length ? builds.map((b) => `
      <div class="build-row${b.id === activeId ? " active" : ""}">
        <div class="build-info">
          <span class="build-name">${escapeHtml(b.name)}</span>
          <span class="build-meta">${escapeHtml(new Date(b.updatedAt).toLocaleString())}</span>
        </div>
        <div class="build-actions">
          <button class="btn" data-action="load" data-id="${b.id}">Load</button>
          <button class="btn" data-action="rename" data-id="${b.id}">Rename</button>
          <button class="btn danger" data-action="delete" data-id="${b.id}">Delete</button>
        </div>
      </div>`).join("") : '<div class="empty">No saved builds yet \u2014 save your current build below to get started.</div>';
    Array.from(el.buildsList.querySelectorAll("[data-action]")).forEach((btn) => {
      const id = btn.getAttribute("data-id");
      const action = btn.getAttribute("data-action");
      btn.addEventListener("click", () => {
        if (action === "load") {
          const build = builds.find((b) => b.id === id);
          const target = `the build "${build ? build.name : "?"}"`;
          if (!confirmReplaceCurrentBuild("load", target)) return;
          const result = loadBuild(id);
          if (!result) {
            showToast("Couldn't load that build \u2014 it may have been removed.");
            return;
          }
          closeBuildsModal();
          renderAll();
          showToast(`Build loaded${loadIssuesSuffix({ droppedRanks: result.droppedRanks }, result.repaired)}`);
        } else if (action === "rename") {
          const build = builds.find((b) => b.id === id);
          const name = prompt("Rename build:", build ? build.name : "");
          if (name === null) return;
          const trimmed = name.trim();
          if (!trimmed) {
            showToast("Name can't be empty.");
            return;
          }
          const outcome = renameBuild(id, trimmed);
          if (outcome === "collision") {
            showToast(`A build named "${trimmed}" already exists.`);
            return;
          }
          if (outcome === "missing") {
            showToast("Couldn't rename \u2014 that build may have been removed.");
            return;
          }
          renderBuildsList();
          renderTopbar();
          if (outcome === "failed") showToast("Renamed here, but couldn't save it \u2014 local storage may be full or unavailable.");
        } else if (action === "delete") {
          const build = builds.find((b) => b.id === id);
          if (!confirm(`Delete "${build ? build.name : "this build"}"? This can't be undone.`)) return;
          const persisted = deleteBuild(id);
          renderBuildsList();
          renderTopbar();
          if (!persisted) showToast("Deleted here, but couldn't save it \u2014 local storage may be full or unavailable.");
        }
      });
    });
  }
  function openBuildsModal() {
    el.buildSaveName.value = "";
    renderBuildsList();
    openModal(el.buildsModal, el.buildSaveName);
  }
  function closeBuildsModal() {
    closeModal(el.buildsModal);
  }
  function renderOwnedTrackingModal() {
    const activeId = getActiveBuildId();
    const sharing = buildsSharingCurrentOwnedProfile();
    const others = listBuilds().filter((b) => b.id !== activeId);
    el.ownedTrackingStatus.innerHTML = sharing.length ? `Sharing live owned progress with <span class="shared-with">${sharing.map((b) => escapeHtml(b.name)).join(", ")}</span>.` : "Tracking its own independent owned progress right now.";
    el.ownedTrackingBuildSelect.innerHTML = others.length ? others.map((b) => `<option value="${b.id}">${escapeHtml(b.name)}</option>`).join("") : '<option value="">No other saved builds yet</option>';
    el.ownedTrackingBuildSelect.disabled = !others.length;
    el.ownedTrackingLinkBtn.disabled = !others.length;
    el.ownedTrackingMergeBtn.disabled = !others.length;
  }
  function openOwnedTrackingModal() {
    renderOwnedTrackingModal();
    openModal(el.ownedTrackingModal);
  }
  function closeOwnedTrackingModal() {
    closeModal(el.ownedTrackingModal);
  }
  function handleOwnedTrackingLink() {
    const id = el.ownedTrackingBuildSelect.value;
    if (!id) return;
    const name = (listBuilds().find((b) => b.id === id) || {}).name || "that build";
    linkOwnedToBuild(id);
    renderOwnedTrackingModal();
    renderAll();
    showToast(`Now sharing owned progress with "${name}"`);
  }
  function handleOwnedTrackingMerge() {
    const id = el.ownedTrackingBuildSelect.value;
    if (!id) return;
    const name = (listBuilds().find((b) => b.id === id) || {}).name || "that build";
    const result = mergeOwnedFromBuild(id);
    renderOwnedTrackingModal();
    renderAll();
    showToast(result.merged ? `Merged in ${result.merged} owned rank${result.merged === 1 ? "" : "s"} from "${name}"` : `Nothing new to merge in from "${name}"`);
  }
  function handleOwnedTrackingSplit() {
    const split = splitOwnedFromCurrent();
    renderOwnedTrackingModal();
    renderAll();
    showToast(split ? "Now tracking its own independent owned progress" : "Couldn't split \u2014 local storage may be full or unavailable.");
  }
  function openResetModal() {
    el.resetClearOwnedCheckbox.checked = false;
    openModal(el.resetModal, el.cancelResetBtn);
  }
  function closeResetModal() {
    closeModal(el.resetModal);
  }
  function handleConfirmReset() {
    const clearOwnedToo = el.resetClearOwnedCheckbox.checked;
    performReset(clearOwnedToo);
    clearActiveBuild();
    closeResetModal();
    renderAll();
    showToast(clearOwnedToo ? "Build reset" : "Build reset \u2014 owned progress kept");
  }
  function handleBuildSave() {
    const name = el.buildSaveName.value.trim();
    if (!name) {
      showToast("Enter a name for this build.");
      return;
    }
    const id = saveWithNameCheck(name);
    if (id === false) return;
    if (!id) {
      showToast("Couldn't save \u2014 local storage may be full or unavailable.");
      return;
    }
    el.buildSaveName.value = "";
    renderBuildsList();
    renderTopbar();
    showToast(`Saved "${name}"`);
  }

  // src/exportImport.js
  var BUILD_CODE_VERSION = 7;
  var MAX_ENCODED_CODE_LENGTH = 262144;
  var MAX_DECOMPRESSED_BYTES = 4 * 1024 * 1024;
  function pushCompactRank(ids, ranks, scope, className, key, rank) {
    const id = idForKey(scope, className, key);
    if (id != null) {
      ids.push(id);
      ranks.push(rank);
    }
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
  function expandCompactRanks(list, columnar) {
    const ranks = { general: {}, archetype: {}, special: {}, classes: {} };
    let dropped = 0;
    if (!list) return { ranks, dropped };
    const ids = (columnar ? list[0] : list) || [];
    const capped = ids.slice(0, MAX_PURCHASE_ORDER);
    const pairs = columnar ? capped.map((id, i) => [id, list[1][i]]) : capped;
    pairs.forEach(([id, rank]) => {
      const entry = entryForId(id);
      if (!entry) {
        dropped++;
        return;
      }
      if (!Number.isFinite(rank)) return;
      if (entry.scope === "class") {
        ranks.classes[entry.className] = ranks.classes[entry.className] || {};
        ranks.classes[entry.className][entry.key] = rank;
      } else {
        ranks[entry.scope][entry.key] = rank;
      }
    });
    return { ranks, dropped };
  }
  function expandCompactPayload(compact) {
    const isArray = Array.isArray(compact);
    const v = isArray ? compact[0] : compact.v;
    const [c, l, r, p, o, w] = isArray ? compact.slice(1) : [compact.c, compact.l, compact.r, compact.p, compact.o, compact.w];
    const columnar = v >= 4;
    const purchaseOrder = (p || []).slice(0, MAX_PURCHASE_ORDER).map((id) => {
      const entry = entryForId(id);
      return entry ? { scope: entry.scope, className: entry.className, key: entry.key } : null;
    }).filter(Boolean);
    const rankResult = expandCompactRanks(r, columnar);
    const ownedResult = expandCompactRanks(o, columnar);
    return {
      v: SAVE_FORMAT_VERSION,
      selectedClasses: (c || []).map((i) => CLASS_LIST[i]).filter(Boolean),
      charLevel: l,
      // An older share code/link may still carry a `t` (totalPoints) field,
      // from before the point cap was removed - simply never read into
      // anything here, same graceful-ignore as any unrecognized field.
      ranks: rankResult.ranks,
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
      owned: ownedResult.ranks,
      // Not part of the build shape applyLoaded understands - read separately
      // by the import/share-link callers and folded into their own
      // droppedRanks count, since an id unresolved here never reaches
      // deserializeRanks (state.js) to be counted there.
      decodeDropped: rankResult.dropped + ownedResult.dropped
    };
  }
  async function decompress(bytes, format) {
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream(format));
    const reader = stream.getReader();
    const chunks = [];
    let total = 0;
    for (; ; ) {
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
    chunks.forEach((c) => {
      out.set(c, offset);
      offset += c.byteLength;
    });
    return out;
  }
  var V5_MAGIC = 229;
  var V5_BITS = {
    version: 4,
    idMode: 1,
    classSlot: 5,
    level: 6,
    id: 9,
    count: 9,
    rank: 5,
    rankDelta: 6,
    poCount: 11,
    deltaCount: 9,
    wpCount: 8,
    pts: 17,
    color: 4,
    labelLen: 8
  };
  var V6_BITS = { deltaCount: 8, color: 3 };
  var V5_CLASS_NONE = 31;
  function bitWriter() {
    const bits = [];
    return {
      put(value, width) {
        bits.push((value >>> 0).toString(2).padStart(width, "0").slice(-width));
      },
      putBits(str) {
        bits.push(str);
      },
      bytes() {
        let s = bits.join("");
        s += "0".repeat((8 - s.length % 8) % 8);
        const out = new Uint8Array(s.length / 8);
        for (let i = 0; i < out.length; i++) out[i] = parseInt(s.slice(i * 8, i * 8 + 8), 2);
        return out;
      }
    };
  }
  function bitReader(bytes, startByte) {
    let pos = startByte * 8;
    const total = bytes.length * 8;
    function bit(i) {
      return bytes[i >>> 3] >>> 7 - (i & 7) & 1;
    }
    return {
      take(width) {
        if (pos + width > total) throw new Error("build code truncated");
        let v = 0;
        for (let i = 0; i < width; i++) v = v << 1 | bit(pos + i);
        pos += width;
        return v >>> 0;
      },
      // bitWriter.put stores a negative value's low `width` bits (two's
      // complement), so a signed field must sign-extend on read the same way,
      // or a negative value comes back as a large positive one.
      takeSigned(width) {
        const raw = this.take(width);
        const half = 1 << width - 1;
        return raw >= half ? raw - (half << 1) : raw;
      },
      alignedByteOffset() {
        return pos + 7 >>> 3;
      }
    };
  }
  function crc16(bytes, end) {
    let crc = 65535;
    for (let i = 0; i < end; i++) {
      crc ^= bytes[i] << 8;
      for (let b = 0; b < 8; b++) crc = crc & 32768 ? (crc << 1 ^ 4129) & 65535 : crc << 1 & 65535;
    }
    return crc & 65535;
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
  function indexWidth(n) {
    return Math.max(1, 32 - Math.clz32(Math.max(1, n - 1)));
  }
  function packV5(idMode) {
    const [plannedIds, plannedRanks] = compactRanksFor(state.ranks);
    const [ownedIds, ownedRanks] = compactRanksFor(state.owned);
    const planned = /* @__PURE__ */ new Map();
    plannedIds.forEach((id, i) => planned.set(id, plannedRanks[i]));
    const owned = /* @__PURE__ */ new Map();
    ownedIds.forEach((id, i) => owned.set(id, ownedRanks[i]));
    const ids = Array.from(planned.keys()).sort((a, b) => a - b);
    const slot = /* @__PURE__ */ new Map();
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
      const present = new Array(hi + 1).fill("0");
      ids.forEach((id) => {
        present[id] = "1";
      });
      w.putBits(present.join(""));
    } else {
      w.put(ids.length, V5_BITS.count);
      ids.forEach((id) => w.put(id, V5_BITS.id));
    }
    ids.forEach((id) => w.put(planned.get(id), V5_BITS.rank));
    const po = serializePurchaseOrder(state.purchaseOrder).map((e) => idForKey(e.scope, e.className, e.key)).filter((id) => id != null && slot.has(id));
    w.put(po.length, V5_BITS.poCount);
    const poWidth = indexWidth(ids.length);
    po.forEach((id) => w.put(slot.get(id), poWidth));
    const ownedList = ids.filter((id) => owned.has(id));
    w.putBits(ids.map((id) => owned.has(id) ? "1" : "0").join(""));
    const diffs = [];
    ownedList.forEach((id, i) => {
      if (owned.get(id) !== planned.get(id)) diffs.push([i, planned.get(id) - owned.get(id)]);
    });
    const diffWidth = indexWidth(ownedList.length);
    w.put(diffs.length, V5_BITS.deltaCount);
    diffs.forEach(([i, d]) => {
      w.put(i, diffWidth);
      w.put(d, V5_BITS.rankDelta);
    });
    const ownedOnly = Array.from(owned.keys()).filter((id) => !planned.has(id)).sort((a, b) => a - b);
    w.put(ownedOnly.length, V5_BITS.count);
    ownedOnly.forEach((id) => {
      w.put(id, V5_BITS.id);
      w.put(owned.get(id), V5_BITS.rank);
    });
    const labels = [];
    w.put(state.waypoints.length, V5_BITS.wpCount);
    state.waypoints.forEach((wp) => {
      w.put(wp.pts, V5_BITS.pts);
      const ci = WAYPOINT_COLORS.findIndex((c) => c.key === wp.color);
      w.put(ci < 0 ? 0 : ci + 1, V5_BITS.color);
      const bytes = new TextEncoder().encode(wp.label || "");
      w.put(bytes.length, V5_BITS.labelLen);
      labels.push(bytes);
    });
    const head = w.bytes();
    const labelLen = labels.reduce((n, b) => n + b.length, 0);
    const out = new Uint8Array(1 + head.length + labelLen + 2);
    out[0] = V5_MAGIC;
    out.set(head, 1);
    let at = 1 + head.length;
    labels.forEach((b) => {
      out.set(b, at);
      at += b.length;
    });
    const crc = crc16(out, at);
    out[at] = crc >>> 8;
    out[at + 1] = crc & 255;
    return out;
  }
  function expandBinaryPayload(bytes) {
    if (bytes.length < 4) throw new Error("build code truncated");
    const end = bytes.length - 2;
    const want = bytes[end] << 8 | bytes[end + 1];
    if (crc16(bytes, end) !== want) throw new Error("build code failed its checksum");
    const r = bitReader(bytes, 1);
    const v = r.take(V5_BITS.version);
    if (v < 5 || v > 7) throw new Error(`unsupported binary build code version ${v}`);
    const widths = v >= 7 ? V5_BITS : { ...V5_BITS, ...V6_BITS };
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
      bits.forEach((b, i) => {
        if (b) ids.push(i);
      });
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
      ownedRanks.push(plannedRanks[i]);
    });
    const deltaCount = r.take(widths.deltaCount);
    const diffWidth = indexWidth(ownedIds.length);
    for (let k = 0; k < deltaCount; k++) {
      const i = r.take(diffWidth);
      if (v >= 6) {
        const d = r.takeSigned(V5_BITS.rankDelta);
        if (i < ownedRanks.length) ownedRanks[i] -= d;
      } else {
        const raw = r.take(V5_BITS.rank);
        if (i < ownedRanks.length) ownedRanks[i] = ownedRanks[i] - raw & 31;
      }
    }
    if (v >= 7) {
      const ownedOnlyCount = r.take(V5_BITS.count);
      for (let k = 0; k < ownedOnlyCount; k++) {
        ownedIds.push(r.take(V5_BITS.id));
        ownedRanks.push(r.take(V5_BITS.rank));
      }
    }
    const wpCount = r.take(V5_BITS.wpCount);
    const wpMeta = [];
    for (let i = 0; i < wpCount; i++) {
      wpMeta.push({
        pts: r.take(V5_BITS.pts),
        color: r.take(widths.color),
        len: r.take(V5_BITS.labelLen)
      });
    }
    let at = r.alignedByteOffset();
    const waypoints = wpMeta.map((m) => {
      const slice = bytes.subarray(at, at + m.len);
      if (at + m.len > end) throw new Error("build code truncated");
      at += m.len;
      return [
        m.pts,
        m.len ? new TextDecoder().decode(slice) : null,
        m.color === 0 ? null : (WAYPOINT_COLORS[m.color - 1] || {}).key || null
      ];
    });
    const purchaseOrder = poIdx.map((i) => {
      const entry = entryForId(ids[i]);
      return entry ? { scope: entry.scope, className: entry.className, key: entry.key } : null;
    }).filter(Boolean);
    const rankResult = expandCompactRanks([ids, plannedRanks], true);
    const ownedResult = expandCompactRanks([ownedIds, ownedRanks], true);
    return {
      v: SAVE_FORMAT_VERSION,
      selectedClasses,
      charLevel,
      ranks: rankResult.ranks,
      purchaseOrder,
      waypoints,
      owned: ownedResult.ranks,
      // See expandCompactPayload's own decodeDropped - same reasoning, an
      // unresolved id here (an AA removed since encoding, or a crafted id
      // that never existed but still passes the CRC) never reaches
      // deserializeRanks to be counted.
      decodeDropped: rankResult.dropped + ownedResult.dropped
    };
  }
  async function encodeBuildCode() {
    const bitmap = packV5(0);
    const explicit = packV5(1);
    return bytesToBase64(bitmap.length <= explicit.length ? bitmap : explicit);
  }
  var GZIP_MAGIC_0 = 31;
  var GZIP_MAGIC_1 = 139;
  async function decodeBuildCode(code) {
    if (code.length > MAX_ENCODED_CODE_LENGTH) throw new Error("build code exceeds the size limit");
    const bytes = base64ToBytes(code);
    let binaryError = null;
    if (bytes.length && bytes[0] === V5_MAGIC) {
      try {
        return expandBinaryPayload(bytes);
      } catch (e) {
        binaryError = e;
      }
    }
    try {
      return await decodeJsonBuildCode(bytes);
    } catch (e) {
      throw binaryError || e;
    }
  }
  async function decodeJsonBuildCode(bytes) {
    let jsonBytes;
    if (bytes.length >= 2 && bytes[0] === GZIP_MAGIC_0 && bytes[1] === GZIP_MAGIC_1) {
      jsonBytes = await decompress(bytes, "gzip");
    } else {
      try {
        jsonBytes = await decompress(bytes, "deflate-raw");
      } catch (e) {
        jsonBytes = bytes;
      }
    }
    const parsed = JSON.parse(new TextDecoder().decode(jsonBytes));
    const isCompact = Array.isArray(parsed) ? parsed[0] >= 2 : !!parsed && parsed.v === 2 && !looksLikeBuildPayload(parsed);
    if (isCompact) return expandCompactPayload(parsed);
    if (!looksLikeBuildPayload(parsed)) throw new Error("decoded payload isn't a recognizable build");
    return parsed;
  }
  function looksLikeBuildPayload(parsed) {
    return !!parsed && typeof parsed === "object" && !Array.isArray(parsed) && (Array.isArray(parsed.selectedClasses) || parsed.ranks && typeof parsed.ranks === "object" || Array.isArray(parsed.purchaseOrder));
  }
  function toBase64Url(b64) {
    return b64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }
  function fromBase64Url(b64url) {
    let b64 = b64url.replace(/-/g, "+").replace(/_/g, "/");
    while (b64.length % 4) b64 += "=";
    return b64;
  }
  async function buildShareUrl() {
    const url = new URL(window.location.href);
    url.search = "";
    url.hash = "";
    url.searchParams.set("build", toBase64Url(await encodeBuildCode()));
    return url.toString();
  }
  async function applySharedBuildFromUrl(localLoadResult) {
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
      const proceed = confirmReplaceCurrentBuild("load", "the shared build from this link", {
        extraRisk,
        trustMatch: !isActiveBuildTheImportedSlot()
      });
      if (proceed) {
        const { result, repaired, ownedOutcome } = applyImportedBuild(json);
        const savedId = saveImportedBuild();
        notice = savedId ? `Loaded shared build from link \u2014 saved as "Imported Build" in Builds${loadIssuesSuffix(result, repaired)}${ownedNoticeSuffix(ownedOutcome)}` : `Loaded shared build from link, but couldn't save it to Builds \u2014 local storage may be full or unavailable${loadIssuesSuffix(result, repaired)}${ownedNoticeSuffix(ownedOutcome)}`;
        applied = true;
      }
    } else {
      notice = "That share link's build data looks invalid";
    }
    stripBuildParam();
    return { applied, notice };
  }
  function stripBuildParam() {
    const cleanUrl = new URL(window.location.href);
    cleanUrl.searchParams.delete("build");
    window.history.replaceState({}, "", cleanUrl.toString());
  }
  function applyImportedBuild(json) {
    const before = {
      selectedClasses: state.selectedClasses,
      charLevel: state.charLevel,
      ranks: state.ranks,
      purchaseOrder: state.purchaseOrder,
      waypoints: state.waypoints,
      owned: state.owned,
      ownedProfileId: state.ownedProfileId
    };
    try {
      const result = applyLoaded(json);
      state.selectedNode = null;
      clearLastMutation();
      clearActiveBuild();
      const repaired = reconcilePurchaseOrderCounts();
      const ownedOutcome = maybeImportOwned(json);
      result.droppedRanks += ownedOutcome.dropped + safeDecodeDropped(json);
      saveLocal();
      return { result, repaired, ownedOutcome };
    } catch (e) {
      Object.assign(state, before);
      throw e;
    }
  }
  async function buildExportText() {
    const spent = spentPoints();
    const owned = ownedPoints();
    const lines = [];
    lines.push("EverQuest Legends - AA Build");
    lines.push(`Classes: ${state.selectedClasses.join(" / ")}`);
    lines.push(`Points Owned: ${owned}`);
    lines.push(`Points Planned: ${spent}`);
    lines.push(`Exported: ${(/* @__PURE__ */ new Date()).toLocaleString()}`);
    lines.push("");
    AA_CATEGORY_KEYS.forEach((catKey) => {
      const list = getList(catKey);
      const spentAAs = list.map((aa, idx) => ({ aa, rank: effectiveRank(catKey, idx) })).filter((x) => x.rank > 0);
      if (!spentAAs.length) return;
      lines.push(`== ${labelFor(catKey)} ==`);
      spentAAs.forEach(({ aa, rank }) => lines.push(`  ${aa.name}: rank ${rank}/${aa.ranks}${aa.auto ? " (auto-granted)" : ""}`));
      lines.push("");
    });
    otherClassesWithPicks().forEach((className) => {
      lines.push(`== ${className} AA (not one of your current 3 classes) ==`);
      picksForClass(className).forEach(({ aa, rank }) => lines.push(`  ${aa.name}: rank ${rank}/${aa.ranks}`));
      lines.push("");
    });
    if (state.purchaseOrder.length) {
      lines.push("== Progression (pick order) ==");
      computeProgressionTimeline(computeProgressionSteps()).forEach((entry) => {
        if (entry.type === "divider") {
          const labelPart = entry.label ? ` \xB7 ${entry.label}` : "";
          const reachedNote = entry.unreached ? " (not reached yet)" : "";
          lines.push(`  --- ${entry.pts} pts${labelPart} ---${reachedNote}`);
          return;
        }
        const s = entry;
        const maxRank = s.aa ? `/${s.aa.ranks}` : "";
        const suffix = s.active ? "" : " (not one of your current 3 classes)";
        const ownedSuffix = s.owned ? " [OWNED]" : "";
        const stepDisp = s.aa ? costDisplayScoped(s.scope, s.className, s.idx, s.stepRank - 1, s.aa.costs[s.stepRank - 1]) : { isGuess: false };
        const costText = stepDisp.isGuess ? stepDisp.text : s.stepCost;
        const costUnit = stepDisp.isGuess ? "pt(s)" : `pt${s.stepCost === 1 ? "" : "s"}`;
        const totalText = s.blendedCumulative !== s.cumulative ? `~${s.blendedCumulative}` : s.cumulative;
        lines.push(`  ${s.index + 1}. ${s.name} rank ${s.stepRank}${maxRank} \u2014 ${costText} ${costUnit}, ${totalText} total${suffix}${ownedSuffix}`);
      });
      lines.push("");
    }
    lines.push(`BUILD_CODE:${await encodeBuildCode()}`);
    return lines.join("\n");
  }
  async function openExportModal() {
    el.exportText.value = "Generating\u2026";
    el.shareLinkInput.value = "";
    openModal(el.exportModal, el.exportText);
    await regenerateExportContent();
  }
  var exportGeneration = 0;
  async function regenerateExportContent() {
    const generation = ++exportGeneration;
    const [text, url] = await Promise.all([buildExportText(), buildShareUrl()]);
    if (generation !== exportGeneration) return;
    el.exportText.value = text;
    el.shareLinkInput.value = url;
    el.exportText.focus();
    el.exportText.select();
  }
  function closeExportModal() {
    closeModal(el.exportModal);
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
      showToast("Couldn't copy automatically \u2014 select and copy manually.");
    }
  }
  function copyExportText() {
    copyFrom(el.exportText, el.exportText.value);
  }
  function copyShareLink() {
    copyFrom(el.shareLinkInput, el.shareLinkInput.value);
  }
  function saveExportAsTxt() {
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
  var CODE_LINE = /^(?:[A-Za-z0-9+/=_-]|%[0-9A-Fa-f]{2})+$/;
  var BUILD_CODE_START = /BUILD_CODE:\s*([A-Za-z0-9+/=_-]+)/;
  var BUILD_PARAM_START = /[?&]build=((?:[A-Za-z0-9+/=_-]|%[0-9A-Fa-f]{2})+)/;
  var WRAP_WIDTH = 60;
  function codeFromLine(lines, i, pattern) {
    const m = lines[i].match(pattern);
    if (!m) return null;
    let code = m[1];
    let line = lines[i];
    const runsToEnd = m.index + m[0].length === line.length;
    while (runsToEnd && line.length >= WRAP_WIDTH && i + 1 < lines.length && CODE_LINE.test(lines[i + 1])) {
      i++;
      line = lines[i];
      code += line;
    }
    return code;
  }
  function extractBuildCode(text) {
    const lines = text.split(/\r?\n/).map((line) => line.replace(/^\s*(?:>\s?)+/, "").trim());
    for (let i = 0; i < lines.length; i++) {
      const code = codeFromLine(lines, i, BUILD_CODE_START);
      if (code) return code;
    }
    for (let i = 0; i < lines.length; i++) {
      const raw = codeFromLine(lines, i, BUILD_PARAM_START);
      if (!raw) continue;
      try {
        return decodeURIComponent(raw);
      } catch (e) {
        return raw;
      }
    }
    const compact = lines.join("").replace(/^[^A-Za-z0-9+/_-]+|[^A-Za-z0-9+/=_-]+$/g, "");
    if (compact.length > 10 && /^[A-Za-z0-9_+/-]+={0,2}$/.test(compact)) return compact;
    return null;
  }
  function maybeImportOwned(json) {
    const hadOwned = payloadOwnedHasContent(json.owned);
    const result = adoptImportedOwnedAsNewProfile(hadOwned ? json.owned : {});
    return { dropped: result.dropped, hadOwned, saved: result.saved };
  }
  function ownedNoticeSuffix(ownedOutcome) {
    if (!ownedOutcome.saved) return " \u2014 couldn't set up its owned tracking, local storage may be full or unavailable";
    if (!ownedOutcome.hadOwned) return "";
    return " \u2014 owned progress included (tracked separately from your existing progress)";
  }
  function safeDecodeDropped(json) {
    return typeof json.decodeDropped === "number" && Number.isFinite(json.decodeDropped) ? json.decodeDropped : 0;
  }
  async function importBuildFromText(text) {
    const code = extractBuildCode(text);
    if (!code) {
      showToast("No build code found in that text");
      return false;
    }
    let json;
    try {
      json = await decodeBuildCode(fromBase64Url(code));
    } catch (e) {
      showToast("Failed to read build text");
      return false;
    }
    if (!confirmReplaceCurrentBuild("import", "this build")) return false;
    try {
      const { result, repaired, ownedOutcome } = applyImportedBuild(json);
      renderAll();
      showToast(`Build imported${loadIssuesSuffix(result, repaired)}${ownedNoticeSuffix(ownedOutcome)}`);
      return true;
    } catch (e) {
      showToast("Failed to read build text");
      return false;
    }
  }
  function openImportModal() {
    el.importText.value = "";
    openModal(el.importModal, el.importText);
  }
  function closeImportModal() {
    closeModal(el.importModal);
  }
  async function doImport() {
    const text = el.importText.value.trim();
    if (!text) {
      showToast("Paste build text first");
      return;
    }
    if (await importBuildFromText(text)) closeImportModal();
  }

  // src/events.js
  function wireEvents() {
    window.addEventListener("storage", (e) => {
      if (e.key === BUILDS_INDEX_KEY) dropCachedIndex();
      if (e.key === ownedStorageKeyFor(state.ownedProfileId)) {
        refreshOwnedFromStorage();
        renderAll();
      }
    });
    el.classSelects.forEach((sel, i) => {
      let stepBase = null;
      sel.addEventListener("keydown", () => {
        if (!stepBase) stepBase = state.selectedClasses.slice();
      });
      sel.addEventListener("pointerdown", () => {
        stepBase = null;
      });
      sel.addEventListener("blur", () => {
        stepBase = null;
      });
      sel.addEventListener("change", () => {
        const base = stepBase || state.selectedClasses;
        const next = base.slice();
        next[i] = sel.value;
        const dupSlot = base.findIndex((c, j) => j !== i && c === sel.value);
        if (dupSlot >= 0) next[dupSlot] = base[i];
        if (next.every((c, j) => c === state.selectedClasses[j])) return;
        CLASS_SLOT_KEYS.forEach((key, j) => {
          if (state.activeTab === key && next[j] !== state.selectedClasses[j]) state.selectedNode = null;
        });
        state.selectedClasses = next;
        saveLocal();
        renderAll();
      });
    });
    el.levelInput.addEventListener("change", () => {
      const v = parseInt(el.levelInput.value, 10);
      state.charLevel = isNaN(v) ? state.charLevel : Math.max(1, Math.min(MAX_CHAR_LEVEL, v));
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
    el.exportModal.addEventListener("click", (e) => {
      if (e.target === el.exportModal) closeExportModal();
    });
    document.addEventListener("keydown", trapModalFocus);
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
    el.changelogModal.addEventListener("click", (e) => {
      if (e.target === el.changelogModal) closeChangelogModal();
    });
    el.buildsBtn.addEventListener("click", openBuildsModal);
    el.closeBuildsBtn.addEventListener("click", closeBuildsModal);
    el.buildsModal.addEventListener("click", (e) => {
      if (e.target === el.buildsModal) closeBuildsModal();
    });
    el.buildSaveBtn.addEventListener("click", handleBuildSave);
    el.buildSaveName.addEventListener("keydown", (e) => {
      if (e.key === "Enter") handleBuildSave();
    });
    el.importBtn.addEventListener("click", openImportModal);
    el.loadImportFileBtn.addEventListener("click", () => el.importFile.click());
    el.importFile.addEventListener("change", () => {
      const file = el.importFile.files[0];
      if (!file) return;
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
      reader.onerror = () => showToast("Couldn't read that file.");
      reader.readAsText(file);
      el.importFile.value = "";
    });
    el.doImportBtn.addEventListener("click", doImport);
    el.closeImportBtn.addEventListener("click", closeImportModal);
    el.importModal.addEventListener("click", (e) => {
      if (e.target === el.importModal) closeImportModal();
    });
    el.resetBtn.addEventListener("click", openResetModal);
    el.cancelResetBtn.addEventListener("click", closeResetModal);
    el.confirmResetBtn.addEventListener("click", handleConfirmReset);
    el.resetModal.addEventListener("click", (e) => {
      if (e.target === el.resetModal) closeResetModal();
    });
    el.clearOwnedBtn.addEventListener("click", () => {
      if (el.clearOwnedBtn.disabled) return;
      const ok = confirm("Clear owned progress for this build's tracking? This can't be undone, and won't affect your planned picks. If this build shares tracking with another (see Manage tracking\u2026), that one is cleared too.");
      if (!ok) return;
      clearAllOwned();
      renderAll();
      showToast("Owned progress cleared");
    });
    el.manageOwnedTrackingBtn.addEventListener("click", openOwnedTrackingModal);
    el.closeOwnedTrackingBtn.addEventListener("click", closeOwnedTrackingModal);
    el.ownedTrackingModal.addEventListener("click", (e) => {
      if (e.target === el.ownedTrackingModal) closeOwnedTrackingModal();
    });
    el.ownedTrackingLinkBtn.addEventListener("click", handleOwnedTrackingLink);
    el.ownedTrackingMergeBtn.addEventListener("click", handleOwnedTrackingMerge);
    el.ownedTrackingSplitBtn.addEventListener("click", handleOwnedTrackingSplit);
    el.addWaypointBtn.addEventListener("click", () => openWaypointModal());
    el.cancelWaypointBtn.addEventListener("click", closeWaypointModal);
    el.saveWaypointBtn.addEventListener("click", handleSaveWaypoint);
    el.deleteWaypointBtn.addEventListener("click", handleDeleteWaypoint);
    el.waypointModal.addEventListener("click", (e) => {
      if (e.target === el.waypointModal) closeWaypointModal();
    });
    el.waypointLabelInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") handleSaveWaypoint();
    });
    el.waypointPtsInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") handleSaveWaypoint();
    });
    el.dismissBannerBtn.addEventListener("click", () => {
      el.disclaimerBanner.classList.add("hidden");
      try {
        localStorage.setItem(DISCLAIMER_DISMISSED_KEY, "1");
      } catch (e) {
      }
    });
    el.undoLastBtn.addEventListener("click", undoLast);
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
    wireProgressionRowEvents();
    wireBrowseClickDelegation();
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
    el.browseUnownedToggle.addEventListener("click", () => {
      state.browseUnownedOnly = !state.browseUnownedOnly;
      el.browseUnownedToggle.classList.toggle("active", state.browseUnownedOnly);
      renderBrowse();
    });
    el.showHiddenToggle.addEventListener("click", () => {
      state.showHidden = !state.showHidden;
      renderAll();
    });
  }

  // src/main.js
  async function init() {
    cacheDom();
    populateStaticControls();
    migrateLegacyOwnedProfile();
    migrateStaleBuildSlots();
    const rawLocal = loadLocal();
    const localResult = applyLoaded(rawLocal);
    state.ownedProfileId = ownedProfileIdOr(rawLocal && rawLocal.ownedProfileId);
    const ownedResult = loadAndApplyOwned(rawLocal);
    localResult.droppedRanks += ownedResult.droppedOwned;
    loadAndApplyHidden();
    let shared;
    try {
      shared = await applySharedBuildFromUrl(localResult);
    } catch (e) {
      stripBuildParam();
      shared = { applied: false, notice: "That share link's build data looks invalid" };
    }
    wireEvents();
    cleanupStaleStorageKeys();
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
    const repaired = reconcilePurchaseOrderCounts();
    if (repaired) {
      notices.push(`${repaired} pick${repaired === 1 ? "'s" : "s'"} purchase history was out of sync and ${repaired === 1 ? "was" : "were"} repaired`);
    }
    if (!shared.applied && repaired > 0 && !localResult.droppedRanks) saveLocal();
    const invalidated = findInvalidatedPicks();
    if (invalidated.length) {
      const n = invalidated.length;
      notices.push(`${n} pick${n === 1 ? "" : "s"} no longer meet${n === 1 ? "s" : ""} its requirements \u2014 check the highlighted AAs`);
    }
    if (notices.length) {
      showToast(notices.join("; "));
    }
    renderAll();
  }
  document.addEventListener("DOMContentLoaded", init);
})();
