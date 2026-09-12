from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from hound.tools.registry import ToolSpec, TOOLS
from hound.ui.home import HomeScreen


class MainWindow(QMainWindow):
    """Holds the home screen and one page per tool, and switches between them."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Hound")
        self.resize(1280, 720)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._home = HomeScreen(TOOLS)
        self._home.tool_selected.connect(self._open_tool)
        self._stack.addWidget(self._home)

        # Pages are built the first time a tool is opened, then kept.
        self._pages: dict[str, int] = {}

    def _open_tool(self, spec: ToolSpec) -> None:
        if spec.id not in self._pages:
            page = spec.create_page()
            page.back_requested.connect(self._show_home)
            self._pages[spec.id] = self._stack.addWidget(page)
        self._stack.setCurrentIndex(self._pages[spec.id])

    def _show_home(self) -> None:
        self._stack.setCurrentWidget(self._home)

    def closeEvent(self, event: QCloseEvent) -> None:
        for index in self._pages.values():
            self._stack.widget(index).shutdown()
        super().closeEvent(event)
