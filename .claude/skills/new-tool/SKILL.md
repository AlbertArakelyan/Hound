---
name: new-tool
description: Add a new tool to Hound (a new card on the home screen plus its own page). Use when asked to add, scaffold, or wire up a tool such as theHarvester, hunter.io, a port scanner, or any new capability that needs its own page.
---

# Add a tool

Read `SPEC.md` first. Every tool is self contained: one directory, Qt free logic, one
registry entry. Adding a tool must not change the home screen.

## Steps

1. Create `hound/tools/<tool_name>/` with `__init__.py`.
2. Write the logic in its own files. No PyQt6 imports in them.
   - `models.py` for the dataclasses and status enum it returns.
   - Engine file named after the job, for example `lookup.py`, `harvest.py`.
   - Any fixed data (site lists, endpoints, wordlists) in its own module so the engine
     does not change when the data does.
3. Write `page.py` with a `ToolPage` subclass from `hound.ui.widgets.tool_page`.
   Build the UI in small `_build_*` methods and add them with `add_content()`.
   Pass the tool's emoji as the second argument so the page matches its card.
   Use `hound.ui.widgets.panel.Panel` for results, and take every colour, input and
   button style from `hound.ui.style`. Write no colours of your own.
4. If the work can take more than an instant, put it in a `QThread` subclass in
   `search_worker.py` (or `<job>_worker.py`). Emit one signal per result so the page
   fills in as answers arrive, and one signal when the run ends.
   Override `shutdown()` on the page to stop and wait for the thread.
5. Register it in `hound/tools/registry.py`: add a lazy factory function plus a
   `ToolSpec` entry in `TOOLS`. The factory imports the page inside the function, which
   is what keeps the registry free of Qt imports.
6. Verify with the `run-app` skill before saying it works.

## Copy the shape of the existing tool

`hound/tools/social_accounts/` is the reference. It shows the split:
`sites.py` (data), `models.py`, `lookup.py` (engine), `search_worker.py` (thread),
`result_row.py` and `page.py` (UI).

## Tools that wrap an external binary

- Find the binary with `shutil.which()`. Never assume it is installed.
- If it is missing, the page says so plainly and disables the run button. Do not raise
  and do not fail silently.
- Stream stdout with `subprocess.Popen` and emit lines as they arrive. Do not block the
  GUI thread waiting for the process to exit.
- Always pass a timeout and kill the process on `shutdown()`.

## Tools that need an API key

- Keys never go in the repo, in defaults, or in commits.
- Read the key from the environment or a local config path that `.gitignore` covers.
- If the key is missing, the page says which key it needs and disables the run button.
- Keep the key out of logs, error text, and results.

## Checklist

- [ ] Logic files import no PyQt6.
- [ ] Page subclasses `ToolPage`, no direct network or subprocess calls in it.
- [ ] Background work runs off the GUI thread and is stopped in `shutdown()`.
- [ ] One `ToolSpec` added, home screen untouched.
- [ ] Card name and description read well, they are user facing text.
