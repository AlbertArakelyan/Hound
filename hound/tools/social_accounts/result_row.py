"""One line in the results list."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from hound.tools.social_accounts.models import Result, Status

MARKS = {
    Status.FOUND: ("+", "#2e9e4f"),
    Status.NOT_FOUND: ("-", "#9a9a9a"),
    Status.UNKNOWN: ("?", "#c98a1b"),
}


class ResultRow(QWidget):
    def __init__(self, result: Result) -> None:
        super().__init__()

        symbol, color = MARKS[result.status]

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(12)

        mark = QLabel(f"[{symbol}]")
        mark.setStyleSheet(f"color: {color}; font-weight: bold;")
        mark.setFixedWidth(28)

        name = QLabel(result.site)
        name.setFixedWidth(140)

        layout.addWidget(mark)
        layout.addWidget(name)
        layout.addWidget(self._detail(result), 1)

    def _detail(self, result: Result) -> QLabel:
        if result.status is Status.FOUND:
            link = QLabel(f'<a href="{result.url}">{result.url}</a>')
            link.setOpenExternalLinks(True)
            link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            return link

        text = result.note or ("not found" if result.status is Status.NOT_FOUND else "unknown")
        label = QLabel(text)
        label.setStyleSheet("color: #9a9a9a;")
        return label
