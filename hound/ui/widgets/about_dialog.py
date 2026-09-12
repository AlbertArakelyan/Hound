from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from hound import __version__
from hound.ui import style


class AboutDialog(QDialog):
    """The small window behind the i button on the home screen."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("About Hound")
        self.setModal(True)
        self.setFixedSize(340, 210)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(8)

        title = QLabel("👻 Hound")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        version = QLabel(f"Version {__version__}")
        version.setStyleSheet(f"color: {style.accent(0.95)}; font-weight: bold;")

        tagline = QLabel("Local-first penetration testing toolkit")
        tagline.setWordWrap(True)
        tagline.setStyleSheet(f"color: {style.muted()};")

        license_note = QLabel("GPL-3.0")
        license_note.setStyleSheet(f"color: {style.muted(0.8)};")

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(tagline)
        layout.addSpacing(4)
        layout.addWidget(license_note)
        layout.addStretch()
        layout.addLayout(self._build_buttons())

    def _build_buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addStretch()

        close = QPushButton("Close")
        close.setStyleSheet(style.quiet_button_style())
        close.setFixedWidth(90)
        close.clicked.connect(self.accept)
        close.setDefault(True)

        row.addWidget(close)
        return row

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        super().keyPressEvent(event)
