# UI

This package is the only place allowed to import PyQt6 outside a tool's page and worker.

## What lives here

- `app.py` builds the `QApplication`.
- `main_window.py` owns navigation: a `QStackedWidget` holding the home screen and one
  page per tool, built lazily on first open and then kept.
- `home.py` renders the tool cards. It reads `hound.tools.registry` and must never import
  a specific tool.
- `widgets/` holds pieces shared by every tool: `tool_card.py` and `tool_page.py`.

## Rules

- Anything two tools would both need goes in `widgets/`, not copied into each tool.
- `ToolPage` is the shell every tool page subclasses. It provides the back button, the
  title, `add_content()`, and a `shutdown()` hook. Extend it rather than rebuilding a
  header in a tool.
- `MainWindow.closeEvent` calls `shutdown()` on every built page. Any page that starts a
  thread must override it, otherwise quitting mid run aborts the process.
- Keep widget construction in small `_build_*` methods that return the widget. Long
  `__init__` bodies are the thing to avoid.
- No blocking work in this layer. No `requests`, no `subprocess`, no `time.sleep`.
