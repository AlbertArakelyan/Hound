from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class ToolPage(QWidget):
    """Shell every tool page sits in: a back button, a title, and a content area.

    Subclasses add their own widgets with add_content().
    """

    back_requested = pyqtSignal()

    def __init__(self, title: str) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        header = QHBoxLayout()
        back = QPushButton("Back")
        back.setFixedWidth(80)
        back.clicked.connect(self.back_requested.emit)

        heading = QLabel(title)
        heading.setStyleSheet("font-size: 22px; font-weight: bold;")

        header.addWidget(back)
        header.addWidget(heading)
        header.addStretch()
        layout.addLayout(header)

        self._content = QVBoxLayout()
        layout.addLayout(self._content)
        layout.addStretch()

    def add_content(self, widget: QWidget) -> None:
        self._content.addWidget(widget)
