# EQL AA Calculator — Project Conventions

## Changelog entries (`src/changelogData.js`)

Write every entry like a patch note a player would read, not a technical summary:

- Plain, direct sentences. No em-dash chains, no "not X but Y" constructions, no "the whole point of X is Y" framing.
- Describe what changed for the player ("swapping a class no longer wipes its picks"), not the implementation ("added scope/className-based persistence").
- No meta-narration about the development process, prior versions of the code, or why a decision was made internally — that belongs in commit messages, not here.
- Keep it to 1–3 sentences per bullet. If it needs more than that, it's probably two changes, not one.
- A lone data-only fix (a wiki-scrape correction, an internal-only bugfix nobody would notice) does not get its own changelog entry or version bump.

## Code comments

Default to no comment. Only add one when the WHY is genuinely non-obvious — a hidden constraint, a subtle invariant, a workaround for a specific bug, behavior that would surprise a reader. If removing the comment wouldn't confuse a future reader, don't write it.

When a comment is warranted:

- 1–4 sentences, not a paragraph. If a function seems to need a multi-paragraph explanation, that's usually a sign the code itself should be simpler, not that it needs more prose.
- State the invariant or constraint directly. Don't narrate the development process ("originally this worked differently...", "after some investigation...", "this used to be a bug..."), don't recount rejected alternatives, don't reference specific past incidents by name.
- Avoid AI-tell phrasing: heavy em-dash chains, "not X but Y" constructions, "the whole point of X is Y," restating what the code already says in plainer words.
- Don't reference "this fix" / "this feature" / a specific issue — comments should describe the code as it is now, not the history of how it got there. That history belongs in git log / commit messages.

Both of the above apply retroactively too — when touching a file for another reason, feel free to tighten a comment or changelog entry nearby if it reads like the above.

## Versioning

Never self-tag a release. Before creating/moving a git tag or adding an entry to `USER_CHANGELOG`, state the proposed classification and a one-line reason, then wait for confirmation.

Classification (`vX.Y.Z`):
- **Major** (bump `Y`, e.g. 1.6→1.7): a substantial new feature a player would notice and want to read about.
- **Minor** (bump `Z`, e.g. 1.6.3→1.6.4): a smaller enhancement, fix, or extension of an existing feature — most changelog-worthy work lands here.
- **Backlog** (no version bump, no tag, no changelog entry): internal-only work — refactors, comment cleanup, tooling, doc fixes, anything never user-visible.

A data-only correction (a wiki re-scrape confirming/fixing an AA's cost or effect value, with no accompanying feature work) does not get its own changelog entry or version bump — just commit the data fix with a plain commit message. It's fine to fold a "Data correction from a fresh wiki scrape: ..." bullet into a changelog entry that's *already* shipping real feature work in the same version (see 1.6.0/1.6.1 for the pattern), but a data fix alone never justifies a version bump by itself.
