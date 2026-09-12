"""Runs the scan off the GUI thread and reports each result as it arrives."""

import time

from PySide6.QtCore import QThread, Signal

from hound.tools.social_accounts.lookup import scan
from hound.tools.social_accounts.models import Result, Status
from hound.tools.social_accounts.sites import SITES


class SearchWorker(QThread):
    result_ready = Signal(object)
    search_finished = Signal(int, int, float)

    def __init__(self, username: str) -> None:
        super().__init__()
        self._username = username
        self._stopped = False

    def stop(self) -> None:
        self._stopped = True

    def run(self) -> None:
        started = time.perf_counter()
        found = unknown = 0

        def on_result(result: Result) -> None:
            nonlocal found, unknown
            if self._stopped:
                return
            if result.status is Status.FOUND:
                found += 1
            elif result.status is Status.UNKNOWN:
                unknown += 1
            self.result_ready.emit(result)

        scan(self._username, SITES, on_result=on_result,
             should_stop=lambda: self._stopped)

        if not self._stopped:
            self.search_finished.emit(found, unknown, time.perf_counter() - started)
