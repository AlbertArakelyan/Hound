# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

This project is a bare skeleton: `main.py` is a hello-world script, and there is no
dependency manifest, test suite, lint config, or git repository yet. There is no
architecture to describe. Regenerate this file once real code exists.

## Environment

Python 3.12.3, with a venv at `.venv` (currently contains only `pip`).

**Always run Python and pip inside this venv.** The user usually starts Claude Code with
the venv already activated, so check first and only activate if needed:

```bash
[ -n "$VIRTUAL_ENV" ] || source .venv/bin/activate
python main.py
```

Because each Bash call starts a fresh shell, `source` does not persist between calls —
either prefix the guard above in each call that runs Python, or invoke the venv
interpreter directly (`.venv/bin/python`, `.venv/bin/pip`).
