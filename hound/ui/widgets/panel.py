from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from hound.ui import style


class Panel(QWidget):
    """A titled, scrolling list of rows.

    Both tool pages show results this way. Rows go in with add_row(), and the empty
    message shows whenever there are none.
    """

    def __init__(self, heading: str, empty_text: str = "") -> None:
        super().__init__()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        self._heading = QLabel(heading)
        self._heading.setStyleSheet("font-weight: bold;")

        # Fixed height, so a panel with an action button in its heading still lines up
        # with a panel without one.
        heading_bar = QWidget()
        heading_bar.setFixedHeight(32)
        self.heading_row = QHBoxLayout(heading_bar)
        self.heading_row.setContentsMargins(0, 0, 0, 0)
        self.heading_row.setSpacing(8)
        self.heading_row.addWidget(self._heading)
        self.heading_row.addStretch()
        outer.addWidget(heading_bar)

        self._rows = QVBoxLayout()
        self._rows.setContentsMargins(14, 12, 14, 12)
        self._rows.setSpacing(0)
        self._rows.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._empty = QLabel(empty_text)
        self._empty.setStyleSheet(f"color: {style.muted(0.85)};")
        self._empty.setVisible(bool(empty_text))
        self._rows.addWidget(self._empty)

        container = QWidget()
        container.setLayout(self._rows)

        area = QScrollArea()
        area.setObjectName("Panel")
        area.setStyleSheet(style.panel_style("Panel"))
        area.setWidgetResizable(True)
        area.setWidget(container)
        area.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(area, 1)

    def set_heading(self, text: str) -> None:
        self._heading.setText(text)

    def add_action(self, widget: QWidget) -> None:
        """Put a control on the right of the heading, such as Copy all."""
        self.heading_row.addWidget(widget)

    def add_row(self, widget: QWidget) -> None:
        self._empty.setVisible(False)
        self._rows.addWidget(widget)

    def row_count(self) -> int:
        # The empty label is always in the layout, so it does not count.
        return self._rows.count() - 1

    def clear(self) -> None:
        while self._rows.count() > 1:
            item = self._rows.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._empty.setVisible(bool(self._empty.text()))
