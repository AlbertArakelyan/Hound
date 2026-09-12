from collections.abc import Sequence

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from hound.tools.registry import ToolSpec
from hound.ui.widgets.tool_card import ToolCard

COLUMNS = 3


class HomeScreen(QWidget):
    """Lists the registered tools as cards. Knows nothing about any single tool."""

    tool_selected = pyqtSignal(object)

    def __init__(self, tools: Sequence[ToolSpec]) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        layout.addLayout(self._build_header())

        grid = QGridLayout()
        grid.setSpacing(16)
        for index, spec in enumerate(tools):
            card = ToolCard(spec)
            card.clicked.connect(self.tool_selected.emit)
            grid.addWidget(card, index // COLUMNS, index % COLUMNS)
        # Keeps the cards their own size instead of spreading across the window.
        grid.setColumnStretch(COLUMNS, 1)
        layout.addLayout(grid)

        layout.addStretch()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def _build_header(self) -> QVBoxLayout:
        header = QVBoxLayout()
        header.setSpacing(4)

        title = QLabel("👻 Hound")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        subtitle = QLabel("Local-first penetration testing toolkit")
        subtitle.setStyleSheet("color: rgba(127, 127, 127, 1.0);")

        header.addWidget(title)
        header.addWidget(subtitle)
        return header
