from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from hound.ui import style


class ToolPage(QWidget):
    """Shell every tool page sits in: a back button, a title, and a content area.

    Subclasses add their own widgets with add_content().
    """

    back_requested = Signal()

    def __init__(self, title: str, icon: str = "") -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        layout.addLayout(self._build_header(title, icon))

        self._content = QVBoxLayout()
        self._content.setSpacing(16)
        layout.addLayout(self._content, 1)

    def _build_header(self, title: str, icon: str) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(16)

        back = QPushButton("← Back")
        back.setStyleSheet(style.quiet_button_style())
        back.setFixedWidth(90)
        back.clicked.connect(self.back_requested.emit)
        header.addWidget(back)

        if icon:
            emoji = QLabel(icon)
            emoji.setStyleSheet("font-size: 20px;")
            header.addWidget(emoji)

        heading = QLabel(title)
        heading.setStyleSheet("font-size: 22px; font-weight: bold;")
        header.addWidget(heading)

        header.addStretch()
        return header

    def add_content(self, widget: QWidget, stretch: int = 0) -> None:
        self._content.addWidget(widget, stretch)

    def shutdown(self) -> None:
        """Called before the app closes. Override to stop background work."""
