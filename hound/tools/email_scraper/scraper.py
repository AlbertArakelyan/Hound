"""The crawl engine. No Qt here, so it can be tested without a display.

Ported from examples/email-scarper.py: breadth first from a starting URL, pulling
every email address out of the page text as it goes.
"""

import random
import re
import urllib.parse
from collections import deque
from collections.abc import Callable

import requests
from bs4 import BeautifulSoup

from hound.tools.email_scraper.decoding import CF_PROTECTION_PATH, find_obfuscated
from hound.tools.email_scraper.models import CrawlSummary, PageStatus, PageVisit

DEFAULT_MAX_PAGES = 100
DEFAULT_TIMEOUT = 10.0

EMAIL_RE = re.compile(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", re.I)

# Anchors that are not pages to fetch.
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "#")

USER_AGENTS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
)


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return session


def _resolve(link: str, base_url: str, path: str) -> str:
    """Turn an anchor href into an absolute URL, the way the script does.

    The fragment is dropped, so /page and /page#section are the same request.
    """
    link = link.split("#", 1)[0]
    if not link:
        return ""
    if link.startswith("/"):
        return base_url + link
    if not link.startswith("http"):
        return path + link
    return link


def crawl(start_url: str, *,
          max_pages: int = DEFAULT_MAX_PAGES,
          timeout: float = DEFAULT_TIMEOUT,
          same_domain: bool = True,
          on_page: Callable[[PageVisit], None] | None = None,
          on_email: Callable[[str], None] | None = None,
          should_stop: Callable[[], bool] | None = None) -> CrawlSummary:
    """Walk the site from start_url and collect the emails found on each page.

    on_page fires once per page, on_email once per address not seen before.
    should_stop is checked before each request, so stopping takes effect after the
    request in flight returns.
    """
    pending: deque[str] = deque([start_url])
    visited: set[str] = set()
    emails: set[str] = set()

    start_host = urllib.parse.urlsplit(start_url).netloc
    session = build_session()
    count = 0
    stopped = False

    while pending and count < max_pages:
        if should_stop is not None and should_stop():
            stopped = True
            break

        url = pending.popleft()
        visited.add(url)
        count += 1

        parts = urllib.parse.urlsplit(url)
        base_url = f"{parts.scheme}://{parts.netloc}"
        path = url[:url.rfind("/") + 1] if "/" in parts.path else url

        try:
            response = session.get(url, timeout=timeout)
        except requests.RequestException as exc:
            _emit_page(on_page, count, url, PageStatus.FAILED, 0, type(exc).__name__)
            continue

        found_here = 0
        for address in EMAIL_RE.findall(response.text):
            found_here += _record(address, emails, on_email)

        # Addresses the page hides from a plain text scan. A decoded blob is only a
        # candidate, so it has to look like an address before it counts.
        for candidate in find_obfuscated(response.text):
            if EMAIL_RE.fullmatch(candidate):
                found_here += _record(candidate, emails, on_email)

        soup = BeautifulSoup(response.text, features="lxml")
        for anchor in soup.find_all("a"):
            href = anchor.attrs.get("href", "")
            if not href:
                continue

            if href.lower().startswith(SKIP_SCHEMES):
                # A mailto: is not a page, but the address in it still counts.
                if href.lower().startswith("mailto:"):
                    for address in EMAIL_RE.findall(href):
                        found_here += _record(address, emails, on_email)
                continue

            if CF_PROTECTION_PATH in href:
                # Already harvested above, and it is not a real page.
                continue

            link = _resolve(href, base_url, path)
            if not link or link in visited or link in pending:
                continue
            if same_domain and urllib.parse.urlsplit(link).netloc != start_host:
                continue
            pending.append(link)

        _emit_page(on_page, count, url, PageStatus.VISITED, found_here)

    return CrawlSummary(tuple(sorted(emails)), count, stopped)


def _record(address: str, emails: set[str], on_email) -> int:
    """Add an address if it is new. Returns 1 when it was."""
    address = address.lower()
    if address in emails:
        return 0
    emails.add(address)
    if on_email is not None:
        on_email(address)
    return 1


def _emit_page(on_page, index: int, url: str, status: PageStatus,
               new_emails: int, note: str = "") -> None:
    if on_page is not None:
        on_page(PageVisit(index, url, status, new_emails, note))
