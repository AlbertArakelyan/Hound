# Tools

One directory per tool. A tool owns its logic, its data, and its page, and nothing
outside its own directory except the registry entry.

To add one, use the `new-tool` skill. `social_accounts/` is the reference shape.

## Registry

`registry.py` is the only file the app reads to learn what tools exist. Rules:

- It imports no PySide6. Page imports go inside the `_*_page()` factory functions, so
  opening the app does not import every page.
- A `ToolSpec` carries `id`, `name`, `description`, `create_page`, and an optional
  `icon`. The `name`, `description` and `icon` are shown on the home screen card, so
  write them for a person. The icon is one emoji, and the card works without it.
- Adding a tool means one new factory plus one new `TOOLS` entry. Nothing else.

## Inside a tool

- Logic files import no PySide6, so they can be tested with no display and no network.
- Fixed data (site lists, endpoints, wordlists) lives in its own module, separate from
  the engine that reads it.
- `page.py` holds the UI only. It does not open sockets or spawn processes itself, it
  drives a worker.
- Never import another tool. Shared code belongs in `hound/ui/widgets/` for widgets, or a
  shared module if it is logic.
