# EQL AA Calculator

A talent-calculator-style planner for [EverQuest Legends](https://eqlwiki.com/Alternate_Advancement) Alternate Advancement (AA) builds. Unofficial fan-made tool, not affiliated with the game.

**Live:** https://aacalc.abnotus.com

## Features

- Pick up to 3 classes (EQL's tri-class combo system) and spend points across General, Archetype, Class, and Special AAs
- Prerequisite, level, and affordability checks before you can spend a point
- **Browse All AAs** — a searchable reference independent of your current build
- **Build Summary** — everything you've picked, grouped by category
- **Progression** tab — tracks the order you spent points in, reorderable, with per-step/running-total cost, add/remove controls, and single-level undo
- Export/import a build as text, or via a shareable URL (open the link, the build loads automatically)
- Auto-granted AAs (free, level-gated abilities) are applied automatically
- Responsive layout, keyboard-accessible AA selection

## Data source

All AA data (costs, effects, ranks, prerequisites) is scraped from [eqlwiki.com/Alternate_Advancement](https://eqlwiki.com/Alternate_Advancement). Values marked `?` are undocumented on the wiki itself and treated as 0 until confirmed. The dataset will be re-scraped as the wiki fills in during beta.

## Running locally

No build tools, no server — just open `index.html` in a browser.

## Development

The app logic is authored as real ES modules under `src/` (`state.js`, `logic.js`, `dom.js`, `render.js`, `exportImport.js`, `events.js`, `main.js`). Native ES modules don't work over `file://` in Chrome, and this app is deliberately built to run by just double-clicking `index.html` with no local server — so `build_minify.py` assembles the `src/` modules back into a single classic script and minifies it, which is what `index.html` actually loads.

To make a change:

1. Edit files under `src/` (app logic), `data.src.js` (AA data), or `styles.css`.
2. Run `python build_minify.py`. This regenerates `app.src.js` (assembled, readable — generated, don't edit directly), `app.js`/`data.js` (minified, what ships), and re-stamps `index.html` with a cache-busting version hash.
3. Open `index.html` to test.

## Deployment

Hosted on GitHub Pages, served from `main` on every push.
