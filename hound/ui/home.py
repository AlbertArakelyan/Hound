from collections.abc import Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from hound.tools.registry import ToolSpec
from hound.ui import style
from hound.ui.widgets.about_dialog import AboutDialog
from hound.ui.widgets.tool_card import ToolCard

COLUMNS = 3
BUTTON_SIZE = 28


class HomeScreen(QWidget):
    """Lists the registered tools as cards. Knows nothing about any single tool."""

    tool_selected = Signal(object)

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

    def _build_header(self) -> QHBoxLayout:
        title = QLabel("👻 Hound")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        subtitle = QLabel("Local-first penetration testing toolkit")
        subtitle.setStyleSheet(f"color: {style.muted()};")

        text = QVBoxLayout()
        text.setSpacing(4)
        text.addWidget(title)
        text.addWidget(subtitle)

        header = QHBoxLayout()
        header.addLayout(text)
        header.addStretch()
        # Top aligned, so it sits level with the title rather than with the
        # middle of the two line block.
        header.addWidget(self._build_about_button(),
                         alignment=Qt.AlignmentFlag.AlignTop)
        return header

    def _build_about_button(self) -> QPushButton:
        button = QPushButton("i")
        button.setToolTip("About Hound")
        button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        button.setStyleSheet(style.round_button_style(BUTTON_SIZE))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(self._show_about)
        return button

    def _show_about(self) -> None:
        AboutDialog(self).exec()
