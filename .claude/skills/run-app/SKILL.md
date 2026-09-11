---
name: run-app
description: Run or verify the Hound desktop app, including headless checks of GUI wiring. Use when asked to run, start, launch, or screenshot the app, or to confirm a GUI change actually works.
---

# Run and verify Hound

## Run it for real

```bash
.venv/bin/python main.py
```

This opens a window, so it blocks until closed. Do not run it without a timeout in a
non interactive session.

It needs the system package `libxcb-cursor0`. Without it Qt aborts with
"Could not load the Qt platform plugin xcb". That package needs sudo, so ask the user to
install it rather than trying yourself.

## Verify without a display

This is the normal way to check a change. It runs the real widgets with Qt's offscreen
backend.

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python - <<'PY' 2>&1 | grep -v propagateSizeHints
from PyQt6.QtWidgets import QApplication
from hound.ui.main_window import MainWindow
from hound.tools.registry import TOOLS

app = QApplication(["test"])
window = MainWindow()
window.show()

stack = window.centralWidget()
window._open_tool(TOOLS[0])
page = stack.currentWidget()
print("page:", type(page).__name__)
window.close()
PY
```

The `propagateSizeHints` line is noise from the offscreen backend, not a problem.

## Rules for these checks

- Stub the network. Replace the engine function in the worker module, for example
  `search_worker.scan = fake_scan`, and return canned results. Do not hit live sites to
  test UI wiring.
- After starting a worker, call `page._worker.wait(5000)` then `app.processEvents()`, or
  the signals never arrive and the check proves nothing.
- Test the engine separately with a fake session object. It has no Qt imports, so it
  needs no display and no network.
- Close the window at the end. A `QThread` destroyed while running aborts the process.

## Report honestly

Say what you actually ran. An offscreen check does not prove the window looks right, only
that the wiring holds. If you never saw a real window, say so.
