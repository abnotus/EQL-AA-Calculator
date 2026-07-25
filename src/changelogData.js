// Curated, user-facing changelog — features and dataset changes worth telling
// players about. Internal refactors/architecture/bug-fixes-that-were-never-
// visible don't belong here; git log is the record for those. Newest first;
// add a new entry at the top whenever a user-relevant change ships.
export const USER_CHANGELOG = [
  {
    version: "1.8.0",
    date: "2026-07-25",
    items: [
      "New: swapping a class no longer wipes its picks. They move to a new Other Classes tab instead of disappearing, grouped by class with their own subtotal, and still count toward your Points Spent total. Swap the class back in and everything's exactly as you left it. (Points Spent is now a lifetime total across every class you've used — Progression's own running total still only tracks your current 3, so don't be surprised if the two numbers don't match.)",
      "Reset Build and Clear Owned now cover every class you've used, not just your current 3 — matching how they already worked for your active classes.",
      "Progression rows now show a small colored badge for which of your 3 classes each one belongs to."
    ]
  },
  {
    version: "1.7.0",
    date: "2026-07-25",
    items: [
      "New: Hide an AA you don't care about — a Hide/Unhide toggle in the side panel and on each Browse card tucks it out of the tree, Browse All AAs, and search. A \"Show Hidden\" toggle brings hidden AAs back whenever you want. Hiding is purely a display preference: it never affects your build, an AA you've already spent points on always stays visible, and it's not saved to exports or share links."
    ]
  },
  {
    version: "1.6.5",
    date: "2026-07-25",
    items: [
      "Progression tab: dragging a row near the top or bottom of the list now auto-scrolls it, speeding up the closer you get to the edge — no more pre-scrolling to where you want to drop before you can start."
    ]
  },
  {
    version: "1.6.4",
    date: "2026-07-22",
    items: [
      "New: class-based rank caps are now enforced. Steadfast Will is the current example — capped at rank 6 unless one of your 3 classes is Warrior, Paladin, Shadow Knight (rank 8), or Ranger (rank 7). Tri-class combines rather than switches, so any one of your 3 classes qualifying is enough.",
      "A rank that a later class swap puts out of reach is never stripped — it stays exactly as trained, flagged the same way a stale prerequisite already is, with the out-of-reach portion of its progress bar shown dimmed. Swap back to a qualifying class and the warning clears automatically."
    ]
  },
  {
    version: "1.6.3",
    date: "2026-07-21",
    items: [
      "Fixed: a purchased rank with an estimated cost showed \"0 pt(s)\" in the plain-text export instead of its \"~N\" estimate, even though the tree, side panel, and Progression tab all showed the real guess.",
      "Fixed: Progression's own running point total used to freeze through any purchased rank with an estimated cost. It now blends estimates into the total the same way the topbar already does, and the plain-text export matches it exactly. Affordability still only ever counts confirmed costs."
    ]
  },
  {
    version: "1.6.2",
    date: "2026-07-19",
    items: [
      "Removed the \"Total AA Points\" field and the cap it enforced — the topbar now just shows points spent, with no ceiling to set or bump into. Waypoints already cover marking a point total worth planning around.",
      "When Points Spent includes estimates, the confirmed/estimated breakdown now lives in a tooltip on hover instead of a second number next to it."
    ]
  },
  {
    version: "1.6.1",
    date: "2026-07-19",
    items: [
      "New: pattern-inferred estimates now cover effect values too, not just costs — a \"?\" like the one in \"Increases your critical hit chance by 1/?/5/10%\" can now show a guess, wherever descriptions appear. Same confidence tiers and tooltips as cost estimates; still just a display hint.",
      "Data correction from a fresh wiki scrape: Packrat's ranks 2 and 3 weight-reduction values are now confirmed (10% and 15%).",
      "Hand-picked estimates now fill in the rest of the currently undocumented effect values — Adamant Will, the crafting Mastery AAs, the Innate line, Packrat's remaining ranks, and a few others — marked with their own \"very low\" confidence tier."
    ]
  },
  {
    version: "1.6.0",
    date: "2026-07-18",
    items: [
      "New: undocumented per-rank costs (shown as \"?\" on the wiki) can now show a pattern-inferred estimate instead, wherever a cost appears — the tree, side panel, Browse All AAs, and Progression. Marked with a ~ and color-coded by confidence, with a tooltip explaining what it's based on. Always a cross-check against similar, fully-documented AAs, never a guess from one AA's numbers alone.",
      "An estimate is shown for reference only and never affects point totals or affordability — the moment the wiki documents the real cost, that takes over automatically. If you've already purchased a rank like that, the topbar's Points Spent turns blue and blends the estimate in, with the breakdown in its tooltip.",
      "Data corrections from a fresh wiki scrape: Combat Fury and Combat Stability both had a previously-undocumented rank confirmed, and Packrat gained several confirmed ranks too.",
      "A handful of costs no comparable AA could cross-check now show a hand-picked estimate instead, marked with its own \"very low\" confidence tier."
    ]
  },
  {
    version: "1.5.0",
    date: "2026-07-18",
    items: [
      "New: Waypoints on the Progression tab. Mark a point total worth returning to (with an optional name, like \"Level 20\" or \"Turn-in gear\") and it shows up as a labeled divider right where your training order crosses it. Give it a color to make that stretch of steps stand out — color-code your whole plan into stages at a glance. Click a chip or divider to edit it later.",
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
      "Reset Build now keeps your owned AAs by default instead of wiping everything, with a checkbox to clear them too if you want a clean slate. A separate \"Clear Owned\" button clears owned progress on its own, without touching your plan.",
      "Owned progress is tracked per character, not per plan, so switching between Builds or opening a share link never touches it. It's left out of exported text and share links by default — a checkbox opts in, for moving it to another browser or sharing it. Importing a build with owned data asks first, since it would otherwise overwrite your own."
    ]
  },
  {
    version: "1.3.0",
    date: "2026-07-17",
    items: [
      "New: Builds — save named snapshots of your build and switch between them from the topbar. Handy for comparing class combos or planning alternate paths side by side.",
      "Opening a share link or importing text now offers to save your current build first, instead of just warning it'll be replaced. A share link's build is also auto-saved to a reusable \"Imported Build\" slot so it's easy to find again later.",
      "Progression tab: Undo Last now covers reordering too, not just adding or removing a rank — drag or arrow-move a step by mistake and Undo Last puts it back."
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
