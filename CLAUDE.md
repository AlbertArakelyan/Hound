# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Read `SPEC.md` for what Hound is and where it is going. The home screen lists tools as
cards, and the first tool, social account discovery, works. No test suite or lint config
yet.

Nested guidance lives next to the code it governs: `hound/ui/CLAUDE.md`,
`hound/tools/CLAUDE.md`, and `hound/tools/social_accounts/CLAUDE.md`.

Project skills: `new-tool` to add a tool, `add-site` to add or fix a site in the social
search, `run-app` to run or verify the GUI. The `architecture-guard` agent checks the
layering rules.

## Environment

Python 3.12.3, venv at `.venv`. Dependencies in `requirements.txt`.

Always run Python and pip inside the venv. The user usually starts Claude Code with it
already activated, so check before activating:

```bash
[ -n "$VIRTUAL_ENV" ] || source .venv/bin/activate
python main.py
```

Each Bash call starts a fresh shell, so `source` does not carry over between calls.
Either repeat the guard above, or call `.venv/bin/python` and `.venv/bin/pip` directly.

Running the app needs the system package `libxcb-cursor0`. Without it Qt aborts with
"Could not load the Qt platform plugin xcb".

## Examples

`examples/` holds reference scripts, not part of the app. They are CLI scripts written
against their own assumptions, so do not run them, import them, or treat them as
something to keep working. Never add `examples/` to the venv, the requirements, or the
registry.

Read them to see how a tool should work, then port the logic into
`hound/tools/<tool>/` following the rules below. `examples/social-accounts.py` is what
the social account search was ported from.

## Git

Never commit unless I ask for it explicitly. Leave changes in the working tree and say
what is uncommitted. The same goes for pushing, branching, amending, and reverting.

Commit messages are `type(branch number): what you did`, for example
`feat(1): add Email Scraper tool`. The `commit` skill has the types and the rules.

## Architecture

This project will grow. Keep it clean from the start.

- One responsibility per file and per directory. If a name needs "and", split it.
- Keep UI, business logic, and I/O separate. Widgets should not talk to the network,
  the filesystem, or a database directly.
- Dependencies point inward. Core logic must not import UI or framework code, so it
  stays testable without Qt.
- Put new code in the module that owns that concern. Do not grow `main.py`, it should
  only wire things together and start the app.
- Refactor when a file stops being obvious, not later. Move code instead of duplicating it.

## Writing style

This applies to everything a human reads: README files, code comments, commit messages,
docs, and chat replies.

- Keep it short and precise. Cut anything that does not add information.
- Plain words a person would actually say.
- No em dashes. Use a comma, a period, or parentheses.
- No lectures, no filler, no restating the request back.
- No hedging or padding phrases like "it's worth noting" or "in order to".
