from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Result:
    """One site's answer about one username."""

    site: str
    username: str
    url: str
    status: Status
    http_code: int | None = None
    elapsed: float = 0.0
    note: str = ""
