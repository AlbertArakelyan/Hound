from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout

from hound.tools.registry import ToolSpec


class ToolCard(QFrame):
    """One clickable card on the home screen."""

    clicked = pyqtSignal(object)

    def __init__(self, spec: ToolSpec) -> None:
        super().__init__()
        self._spec = spec

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(320, 140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        name = QLabel(spec.name)
        name.setStyleSheet("font-size: 16px; font-weight: bold;")

        description = QLabel(spec.description)
        description.setWordWrap(True)

        layout.addWidget(name)
        layout.addWidget(description)
        layout.addStretch()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._spec)
