from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from hound.tools.registry import ToolSpec

ACCENT = "124, 92, 255"

# Greys are given as alpha over the theme background, so the card reads the same
# whether the system theme is light or dark.
CARD_STYLE = f"""
#ToolCard {{
    background-color: rgba(127, 127, 127, 0.07);
    border: 1px solid rgba(127, 127, 127, 0.28);
    border-radius: 12px;
}}
#ToolCard:hover {{
    background-color: rgba({ACCENT}, 0.10);
    border: 1px solid rgba({ACCENT}, 0.70);
}}
"""


class ToolCard(QFrame):
    """One clickable card on the home screen."""

    clicked = pyqtSignal(object)

    def __init__(self, spec: ToolSpec) -> None:
        super().__init__()
        self._spec = spec

        self.setObjectName("ToolCard")
        self.setStyleSheet(CARD_STYLE)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(320, 150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        layout.addLayout(self._build_heading())
        layout.addWidget(self._build_description(), 1)
        layout.addWidget(self._build_hint())

    def _build_heading(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        if self._spec.icon:
            icon = QLabel(self._spec.icon)
            icon.setStyleSheet("font-size: 20px;")
            row.addWidget(icon)

        name = QLabel(self._spec.name)
        name.setStyleSheet("font-size: 16px; font-weight: bold;")
        row.addWidget(name, 1)
        return row

    def _build_description(self) -> QLabel:
        description = QLabel(self._spec.description)
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignTop)
        description.setStyleSheet("color: rgba(127, 127, 127, 1.0);")
        return description

    def _build_hint(self) -> QLabel:
        hint = QLabel("Open")
        hint.setStyleSheet(f"color: rgba({ACCENT}, 0.95); font-size: 12px;")
        return hint

    def showEvent(self, event) -> None:
        # Labels must not eat the mouse, or the card loses its hover state and a
        # click on the text does nothing.
        for label in self.findChildren(QLabel):
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        super().showEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._spec)
