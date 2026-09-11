# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Early skeleton. `main.py` opens a 1280x720 PyQt6 window showing "Hello, World!".
No tests or lint config yet. Update this file once there is real architecture.

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

## Writing style

This applies to everything a human reads: README files, code comments, commit messages,
docs, and chat replies.

- Keep it short and precise. Cut anything that does not add information.
- Plain words a person would actually say.
- No em dashes. Use a comma, a period, or parentheses.
- No lectures, no filler, no restating the request back.
- No hedging or padding phrases like "it's worth noting" or "in order to".
