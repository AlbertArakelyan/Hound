"""Runs the crawl off the GUI thread and reports pages and emails as they arrive."""

import time

from PyQt6.QtCore import QThread, pyqtSignal

from hound.tools.email_scraper.models import PageVisit
from hound.tools.email_scraper.scraper import crawl


class ScrapeWorker(QThread):
    page_visited = pyqtSignal(object)
    email_found = pyqtSignal(str)
    crawl_finished = pyqtSignal(int, int, float)

    def __init__(self, url: str, max_pages: int, same_domain: bool) -> None:
        super().__init__()
        self._url = url
        self._max_pages = max_pages
        self._same_domain = same_domain
        self._stopped = False

    def stop(self) -> None:
        self._stopped = True

    def run(self) -> None:
        started = time.perf_counter()
        emails = 0

        def on_page(visit: PageVisit) -> None:
            if not self._stopped:
                self.page_visited.emit(visit)

        def on_email(address: str) -> None:
            nonlocal emails
            emails += 1
            if not self._stopped:
                self.email_found.emit(address)

        summary = crawl(self._url,
                        max_pages=self._max_pages,
                        same_domain=self._same_domain,
                        on_page=on_page,
                        on_email=on_email,
                        should_stop=lambda: self._stopped)

        self.crawl_finished.emit(emails, summary.pages, time.perf_counter() - started)
