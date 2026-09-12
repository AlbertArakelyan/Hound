"""One line in the results list."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from hound.tools.social_accounts.models import Result, Status
from hound.ui import style

BADGES = {
    Status.FOUND: ("+", style.FOUND),
    Status.NOT_FOUND: ("-", style.MUTED),
    Status.UNKNOWN: ("?", style.UNKNOWN),
}


class ResultRow(QWidget):
    def __init__(self, result: Result) -> None:
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(12)

        layout.addWidget(self._build_badge(result))
        layout.addWidget(self._build_name(result))
        layout.addWidget(self._build_detail(result), 1)

    def _build_badge(self, result: Result) -> QLabel:
        symbol, color = BADGES[result.status]
        badge = QLabel(symbol)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedSize(22, 20)
        badge.setStyleSheet(
            f"color: rgba({color}, 1.0);"
            f"background-color: rgba({color}, 0.15);"
            f"border-radius: 5px;"
            f"font-weight: bold;"
        )
        return badge

    def _build_name(self, result: Result) -> QLabel:
        name = QLabel(result.site)
        name.setFixedWidth(140)
        if result.status is not Status.FOUND:
            name.setStyleSheet(f"color: {style.muted(0.85)};")
        return name

    def _build_detail(self, result: Result) -> QLabel:
        if result.status is Status.FOUND:
            link = QLabel(style.link(result.url))
            link.setOpenExternalLinks(True)
            link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            return link

        text = result.note or (
            "not found" if result.status is Status.NOT_FOUND else "unknown"
        )
        label = QLabel(text)
        label.setStyleSheet(f"color: {style.muted(0.85)};")
        return label
