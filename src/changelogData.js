// Curated, user-facing changelog — features and dataset changes worth telling
// players about. Internal refactors/architecture/bug-fixes-that-were-never-
// visible don't belong here; git log is the record for those. Newest first;
// add a new entry at the top whenever a user-relevant change ships.
export const USER_CHANGELOG = [
  {
    version: "1.4.0",
    date: "2026-07-18",
    items: [
      "New: mark AAs as owned on the Progression tab (the checkmark next to a step) to track what you've actually trained in-game, separate from what you're just planning — owned steps show a strikethrough, and marking/unmarking is undoable.",
      "Reset Build now keeps your owned AAs by default instead of wiping everything, with a checkbox to clear owned progress too if you really want a clean slate.",
      "Owned progress is left out of exported text and share links by default (it's personal, not part of the plan you're sharing) — check \"Include owned progress\" in the Export modal to share it anyway. Named Build slots always keep it, since those are your own saved snapshots."
    ]
  },
  {
    version: "1.3.0",
    date: "2026-07-17",
    items: [
      "New: Builds — save named snapshots of your build and switch between them from the topbar, handy for comparing class combos or planning alternate paths side by side.",
      "Opening a share link or importing text now offers to save your current build first if it isn't already backed up, instead of just warning it'll be replaced. A share link's build is also auto-saved to a reusable \"Imported Build\" slot so it's easy to find again later.",
      "Progression tab: Undo Last now covers reordering too, not just adding/removing a rank — drag or arrow-move a step by mistake and Undo Last puts it back."
    ]
  },
  {
    version: "1.2.1",
    date: "2026-07-16",
    items: [
      "Locked AAs in the tree now show whether they're blocked by a missing prerequisite (amber border + REQ badge) or just a level requirement, instead of looking identical either way.",
      "Browse view now flags a prerequisite you haven't met yet, matching the side panel.",
      "Progression tab: dragging a step shows an amber indicator if that drop would leave its own prerequisite unmet, and out-of-order steps are now dimmed for visibility, not just marked with ⚠."
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
      "Much shorter share links and export codes — a heavily-built character's link is now roughly a tenth of its old length. Links and codes you already have saved or shared still work.",
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
