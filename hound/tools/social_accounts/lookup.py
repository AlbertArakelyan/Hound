"""The lookup engine. No Qt here, so it can be tested without a display."""

import concurrent.futures as cf
import random
import re
import threading
import time
from collections.abc import Callable, Sequence
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from hound.tools.social_accounts.models import Result, Status
from hound.tools.social_accounts.sites import SITES, Site

DEFAULT_TIMEOUT = 10.0
DEFAULT_WORKERS = 12

BLOCKED_CODES = {401, 403, 405, 429, 500, 502, 503}

USER_AGENTS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
)


def build_session() -> requests.Session:
    """One session per worker thread: connection pooling plus a light retry policy."""
    session = requests.Session()
    retry = Retry(total=2, backoff_factor=0.4,
                  status_forcelist=(500, 502, 503, 504),
                  allowed_methods=frozenset(["GET"]))
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return session


def _classify(site: Site, code: int, body: str) -> tuple[Status, str]:
    if code in BLOCKED_CODES:
        return Status.UNKNOWN, "blocked or rate limited"

    if site.method == "status":
        if code == 200:
            return Status.FOUND, ""
        if code in (404, 410):
            return Status.NOT_FOUND, ""
        return Status.UNKNOWN, f"unexpected status {code}"

    if site.method == "error_text":
        if code == 404:
            return Status.NOT_FOUND, ""
        # The marker shows up only when the profile is missing.
        missing = site.text in body
        return (Status.NOT_FOUND, "") if missing else (Status.FOUND, "")

    # success_text
    return (Status.FOUND, "") if site.text in body else (Status.NOT_FOUND, "")


def check_site(site: Site, username: str, session: requests.Session,
               timeout: float = DEFAULT_TIMEOUT) -> Result:
    safe = quote(username, safe="")
    profile_url = site.url.format(safe)
    probe_url = (site.probe_url or site.url).format(safe)

    if site.regex and not re.match(site.regex, username):
        return Result(site.name, username, profile_url, Status.NOT_FOUND,
                      note="username invalid for this site")

    start = time.perf_counter()
    try:
        # Status checks never read the body, so stream=True drops the connection
        # as soon as the headers are in.
        need_body = site.method in ("error_text", "success_text")
        response = session.get(probe_url, timeout=timeout, allow_redirects=True,
                               stream=not need_body)
        body = response.text if need_body else ""
        code = response.status_code
        response.close()
    except requests.RequestException as exc:
        return Result(site.name, username, profile_url, Status.UNKNOWN,
                      elapsed=time.perf_counter() - start, note=type(exc).__name__)

    status, note = _classify(site, code, body)
    return Result(site.name, username, profile_url, status, code,
                  time.perf_counter() - start, note)


def scan(username: str, sites: Sequence[Site] = SITES, *,
         workers: int = DEFAULT_WORKERS, timeout: float = DEFAULT_TIMEOUT,
         on_result: Callable[[Result], None] | None = None,
         should_stop: Callable[[], bool] | None = None) -> list[Result]:
    """Check every site concurrently. on_result fires as each answer arrives.

    should_stop is checked before each request. Requests already in flight still
    finish, so stopping is not instant.
    """
    results: list[Result] = []
    local = threading.local()

    def worker(site: Site) -> Result | None:
        if should_stop is not None and should_stop():
            return None
        if not hasattr(local, "session"):
            local.session = build_session()
        return check_site(site, username, local.session, timeout)

    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(worker, site) for site in sites]
        for future in cf.as_completed(futures):
            result = future.result()
            if result is None:
                continue
            results.append(result)
            if on_result is not None:
                on_result(result)

    results.sort(key=lambda r: r.site.lower())
    return results
