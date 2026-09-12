from dataclasses import dataclass
from enum import Enum


class PageStatus(str, Enum):
    VISITED = "visited"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class PageVisit:
    """What happened with one page of the crawl."""

    index: int
    url: str
    status: PageStatus
    new_emails: int = 0
    note: str = ""


@dataclass(frozen=True)
class CrawlSummary:
    emails: tuple[str, ...]
    pages: int
    stopped: bool
