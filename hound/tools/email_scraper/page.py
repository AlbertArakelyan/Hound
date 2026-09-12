from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QWidget,
)

from hound.tools.email_scraper.models import PageStatus, PageVisit
from hound.tools.email_scraper.scrape_worker import ScrapeWorker
from hound.ui import style
from hound.ui.widgets.panel import Panel
from hound.ui.widgets.tool_page import ToolPage

TITLE = "Email Scraper"
ICON = "✉️"

STATUS_COLORS = {
    PageStatus.VISITED: style.MUTED,
    PageStatus.FAILED: style.UNKNOWN,
    PageStatus.SKIPPED: style.MUTED,
}


class EmailScraperPage(ToolPage):
    def __init__(self) -> None:
        super().__init__(TITLE, ICON)

        self._worker: ScrapeWorker | None = None
        self._emails: list[str] = []

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
        self._url.setStyleSheet(style.input_style())
        self._url.returnPressed.connect(self._start)

        self._max_pages = QSpinBox()
        self._max_pages.setRange(1, 1000)
        self._max_pages.setValue(100)
        self._max_pages.setPrefix("max ")
        self._max_pages.setSuffix(" pages")
        self._max_pages.setFixedWidth(150)
        self._max_pages.setStyleSheet(style.input_style())

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
        self._start_button.setStyleSheet(style.primary_button_style())
        self._start_button.setFixedWidth(110)
        self._start_button.clicked.connect(self._start)

        self._stop_button = QPushButton("Stop")
        self._stop_button.setStyleSheet(style.quiet_button_style())
        self._stop_button.setFixedWidth(110)
        self._stop_button.setEnabled(False)
        self._stop_button.clicked.connect(self._stop)

        self._status = QLabel("Enter a URL to start.")
        self._status.setStyleSheet(f"color: {style.muted()};")

        layout.addWidget(self._start_button)
        layout.addWidget(self._stop_button)
        layout.addWidget(self._status, 1)
        return row

    def _build_results(self) -> QWidget:
        self._emails_panel = Panel("Emails", "No emails yet.")
        self._copy_button = QPushButton("Copy all")
        self._copy_button.setStyleSheet(style.quiet_button_style())
        self._copy_button.setEnabled(False)
        self._copy_button.clicked.connect(self._copy_all)
        self._emails_panel.add_action(self._copy_button)

        self._log_panel = Panel("Crawl log", "Pages will be listed here.")

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background-color: rgba({style.MUTED}, 0.30); }}"
            f"QSplitter::handle:horizontal {{ width: 1px; margin: 0 8px; }}"
        )
        splitter.addWidget(self._emails_panel)
        splitter.addWidget(self._log_panel)
        splitter.setSizes([600, 600])
        return splitter

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

        self._emails.clear()
        self._emails_panel.clear()
        self._emails_panel.set_heading("Emails")
        self._log_panel.clear()
        self._copy_button.setEnabled(False)
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
        self._emails.append(address)
        label = QLabel(address)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setContentsMargins(0, 3, 0, 3)
        self._emails_panel.add_row(label)
        self._emails_panel.set_heading(f"Emails ({len(self._emails)})")
        self._copy_button.setEnabled(True)

    def _add_page(self, visit: PageVisit) -> None:
        suffix = f"  ({visit.note})" if visit.note else ""
        label = QLabel(f"[{visit.index}] {visit.url}{suffix}")
        label.setContentsMargins(0, 3, 0, 3)
        label.setStyleSheet(f"color: rgba({STATUS_COLORS[visit.status]}, 1.0);")
        self._log_panel.add_row(label)

    def _copy_all(self) -> None:
        QApplication.clipboard().setText("\n".join(self._emails))
        self._copy_button.setText("Copied")

    def _on_finished(self, emails: int, pages: int, elapsed: float) -> None:
        self._status.setText(f"{emails} emails from {pages} pages, {elapsed:.1f}s")

    def _on_worker_done(self) -> None:
        self._worker = None
        self._start_button.setEnabled(True)
        self._stop_button.setEnabled(False)
        self._copy_button.setText("Copy all")

    def shutdown(self) -> None:
        if self._worker is not None:
            self._worker.stop()
            self._worker.wait(5000)
