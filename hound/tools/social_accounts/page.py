from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from hound.tools.social_accounts.models import Result, Status
from hound.tools.social_accounts.result_row import ResultRow
from hound.tools.social_accounts.search_worker import SearchWorker
from hound.tools.social_accounts.sites import SITES
from hound.ui.widgets.tool_page import ToolPage

TITLE = "Social Account Discovery"


class SocialAccountsPage(ToolPage):
    def __init__(self) -> None:
        super().__init__(TITLE)

        self._worker: SearchWorker | None = None
        self._rows: list[tuple[ResultRow, Result]] = []

        self.add_content(self._build_search_bar())
        self.add_content(self._build_status_line())
        self.add_content(self._build_results_area(), 1)

    # Layout ---------------------------------------------------------------

    def _build_search_bar(self) -> QWidget:
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Username")
        self._input.setClearButtonEnabled(True)
        self._input.returnPressed.connect(self._start_search)

        self._search_button = QPushButton("Search")
        self._search_button.setFixedWidth(100)
        self._search_button.clicked.connect(self._start_search)

        self._found_only = QCheckBox("Found only")
        self._found_only.toggled.connect(self._apply_filter)

        layout.addWidget(self._input, 1)
        layout.addWidget(self._search_button)
        layout.addWidget(self._found_only)
        return bar

    def _build_status_line(self) -> QWidget:
        self._status = QLabel(f"{len(SITES)} sites ready.")
        self._status.setStyleSheet("color: #9a9a9a;")
        return self._status

    def _build_results_area(self) -> QWidget:
        self._results_layout = QVBoxLayout()
        self._results_layout.setContentsMargins(0, 0, 0, 0)
        self._results_layout.setSpacing(2)
        self._results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        container = QWidget()
        container.setLayout(self._results_layout)

        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(container)
        return area

    # Search ---------------------------------------------------------------

    def _start_search(self) -> None:
        username = self._input.text().strip()
        if not username:
            self._status.setText("Enter a username first.")
            return
        if self._worker is not None:
            return

        self._clear_results()
        self._search_button.setEnabled(False)
        self._status.setText(f"Scanning {len(SITES)} sites for {username} ...")

        self._worker = SearchWorker(username)
        self._worker.result_ready.connect(self._add_result)
        self._worker.search_finished.connect(self._on_finished)
        self._worker.finished.connect(self._on_worker_done)
        self._worker.start()

    def _add_result(self, result: Result) -> None:
        row = ResultRow(result)
        row.setVisible(self._passes_filter(result))
        self._rows.append((row, result))
        self._results_layout.addWidget(row)

    def _on_finished(self, found: int, unknown: int, elapsed: float) -> None:
        self._status.setText(f"{found} found, {unknown} unknown, {elapsed:.1f}s")

    def _on_worker_done(self) -> None:
        self._worker = None
        self._search_button.setEnabled(True)

    def shutdown(self) -> None:
        if self._worker is not None:
            self._worker.stop()
            self._worker.wait(3000)

    # Filtering ------------------------------------------------------------

    def _passes_filter(self, result: Result) -> bool:
        return not self._found_only.isChecked() or result.status is Status.FOUND

    def _apply_filter(self) -> None:
        for row, result in self._rows:
            row.setVisible(self._passes_filter(result))

    def _clear_results(self) -> None:
        for row, _ in self._rows:
            row.setParent(None)
            row.deleteLater()
        self._rows.clear()
