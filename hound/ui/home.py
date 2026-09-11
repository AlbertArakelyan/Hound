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

        title = QLabel("Hound")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(16)
        for index, spec in enumerate(tools):
            card = ToolCard(spec)
            card.clicked.connect(self.tool_selected.emit)
            grid.addWidget(card, index // COLUMNS, index % COLUMNS)
        layout.addLayout(grid)

        layout.addStretch()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
