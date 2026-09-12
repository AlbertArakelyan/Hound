from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from hound.tools.email_scraper.models import PageStatus, PageVisit
from hound.tools.email_scraper.scrape_worker import ScrapeWorker
from hound.ui.widgets.tool_page import ToolPage

TITLE = "Email Scraper"

STATUS_COLORS = {
    PageStatus.VISITED: "#9a9a9a",
    PageStatus.FAILED: "#c98a1b",
    PageStatus.SKIPPED: "#9a9a9a",
}


class EmailScraperPage(ToolPage):
    def __init__(self) -> None:
        super().__init__(TITLE)

        self._worker: ScrapeWorker | None = None

        self.add_content(self._build_target_row())
        self.add_content(self._build_control_row())
        self.add_content(self._build_results(), 1)

    # Layout ---------------------------------------------------------------

    def _build_target_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._url = QLineEdit()
        self._url.setPlaceholderText("https://example.com")
        self._url.setClearButtonEnabled(True)
        self._url.returnPressed.connect(self._start)

        self._max_pages = QSpinBox()
        self._max_pages.setRange(1, 1000)
        self._max_pages.setValue(100)
        self._max_pages.setPrefix("max ")
        self._max_pages.setSuffix(" pages")
        self._max_pages.setFixedWidth(140)

        self._same_domain = QCheckBox("Stay on this domain")
        self._same_domain.setChecked(True)

        layout.addWidget(self._url, 1)
        layout.addWidget(self._max_pages)
        layout.addWidget(self._same_domain)
        return row

    def _build_control_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._start_button = QPushButton("Start")
        self._start_button.setFixedWidth(100)
        self._start_button.clicked.connect(self._start)

        self._stop_button = QPushButton("Stop")
        self._stop_button.setFixedWidth(100)
        self._stop_button.setEnabled(False)
        self._stop_button.clicked.connect(self._stop)

        self._status = QLabel("Enter a URL to start.")
        self._status.setStyleSheet("color: #9a9a9a;")

        layout.addWidget(self._start_button)
        layout.addWidget(self._stop_button)
        layout.addWidget(self._status, 1)
        return row

    def _build_results(self) -> QWidget:
        self._emails_layout, emails_pane = self._build_pane("Emails")
        self._log_layout, log_pane = self._build_pane("Crawl log")

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(emails_pane)
        splitter.addWidget(log_pane)
        splitter.setSizes([600, 600])
        return splitter

    def _build_pane(self, heading: str) -> tuple[QVBoxLayout, QWidget]:
        pane = QWidget()
        outer = QVBoxLayout(pane)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        label = QLabel(heading)
        label.setStyleSheet("font-weight: bold;")
        outer.addWidget(label)

        rows = QVBoxLayout()
        rows.setContentsMargins(0, 0, 0, 0)
        rows.setSpacing(2)
        rows.setAlignment(Qt.AlignmentFlag.AlignTop)

        container = QWidget()
        container.setLayout(rows)

        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(container)
        outer.addWidget(area, 1)
        return rows, pane

    # Crawl ----------------------------------------------------------------

    def _start(self) -> None:
        url = self._url.text().strip()
        if not url:
            self._status.setText("Enter a URL first.")
            return
        if self._worker is not None:
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            self._url.setText(url)

        self._clear(self._emails_layout)
        self._clear(self._log_layout)
        self._start_button.setEnabled(False)
        self._stop_button.setEnabled(True)
        self._status.setText(f"Crawling {url} ...")

        self._worker = ScrapeWorker(url, self._max_pages.value(),
                                    self._same_domain.isChecked())
        self._worker.page_visited.connect(self._add_page)
        self._worker.email_found.connect(self._add_email)
        self._worker.crawl_finished.connect(self._on_finished)
        self._worker.finished.connect(self._on_worker_done)
        self._worker.start()

    def _stop(self) -> None:
        if self._worker is not None:
            self._worker.stop()
            self._status.setText("Stopping, waiting for the last request ...")

    def _add_email(self, address: str) -> None:
        label = QLabel(address)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._emails_layout.addWidget(label)

    def _add_page(self, visit: PageVisit) -> None:
        suffix = f"  ({visit.note})" if visit.note else ""
        label = QLabel(f"[{visit.index}] {visit.url}{suffix}")
        label.setStyleSheet(f"color: {STATUS_COLORS[visit.status]};")
        self._log_layout.addWidget(label)

    def _on_finished(self, emails: int, pages: int, elapsed: float) -> None:
        self._status.setText(f"{emails} emails from {pages} pages, {elapsed:.1f}s")

    def _on_worker_done(self) -> None:
        self._worker = None
        self._start_button.setEnabled(True)
        self._stop_button.setEnabled(False)

    def shutdown(self) -> None:
        if self._worker is not None:
            self._worker.stop()
            self._worker.wait(5000)

    # Helpers --------------------------------------------------------------

    def _clear(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
