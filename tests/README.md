# Tests

Two kinds, both plain Python scripts (no pytest) — run each file directly and
check its exit code; every one prints `ALL PASS` on success and asserts
loudly on failure.

## Data-independent unit tests

`test_guess_costs_interpolation.py` exercises `wiki-sync/guess_costs.py`'s
core logic (`interpolate_bounded_gaps`, `guess_for_entry`) directly, against
synthetic reference pools rather than the live dataset. No server, no
browser — just:

```
python tests/test_guess_costs_interpolation.py
```

This is deliberately *not* pinned to any AA's current confidence tier: the
whole point of the cost-guessing feature is that a guess resolves away the
moment the wiki confirms the real value, so a test asserting "AA X is
currently medium-confidence" would break the instant the feature does its
job. It tests the algorithm's rules instead (unanimous vs. majority voting,
bounded-vs-trailing interpolation, non-monotonic sibling exclusion, the
manual-guess fallback and its zero-known-ranks edge case) with hand-built
inputs that stay true regardless of what `data.src.js` says on any given day.

## Browser (Playwright) tests

`test_cost_guess.py`, `test_manual_guess.py`, `test_guess_all_tabs.py`,
`test_disclaimer_banner.py`, `test_estimated_total.py` drive the actual app
in a real Chrome instance via [Playwright](https://playwright.dev/python/).

**Prerequisites:**
- `pip install playwright`
- A Chrome/Chromium install on PATH (these launch with `channel="chrome"` —
  the system browser, not a Playwright-managed one, so no `playwright
  install` download step is needed if Chrome is already present)
- The app served locally on port 8743:
  ```
  python -m http.server 8743
  ```
  (run from the repo root, in a separate terminal, before the tests)

Then, from the repo root:

```
python tests/test_cost_guess.py
python tests/test_manual_guess.py
python tests/test_guess_all_tabs.py
python tests/test_disclaimer_banner.py
python tests/test_estimated_total.py
```

A few of these load a hand-crafted or hand-decoded `?build=` share code to
reach a specific scenario (an already-purchased guessed rank, a build with
several unconfirmed-cost ranks already spent, an inactive-class step) rather
than clicking through the UI to build it up live — faster, and pins the
exact scenario being tested instead of leaving it implicit in a sequence of
clicks.

None of these are wired into CI; run them by hand after a change that
touches the cost-guessing feature (`wiki-sync/guess_costs.py`,
`src/costGuesses.js`'s consumers in `src/keys.js`/`src/logic.js`/
`src/render.js`, the disclaimer banner, or the topbar) before rebuilding
and committing.
