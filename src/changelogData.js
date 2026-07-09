// Curated, user-facing changelog — features and dataset changes worth telling
// players about. Internal refactors/architecture/bug-fixes-that-were-never-
// visible don't belong here; git log is the record for those. Newest first;
// add a new entry at the top whenever a user-relevant change ships.
export const USER_CHANGELOG = [
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
