#!/usr/bin/env python3
"""
hound — username enumeration across public web profiles (a small Sherlock clone).

It asks each site's public profile URL whether a username exists, using one of
three detection strategies, and reports found / not found / unknown.

Examples:
    python hound.py torvalds
    python hound.py torvalds janedoe --found-only
    python hound.py torvalds --only GitHub Reddit --timeout 5
    python hound.py torvalds --json out.json --csv out.csv
    python hound.py --list-sites

Requires: requests   ->   pip install requests
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass, asdict
from typing import Optional
from urllib.parse import quote

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:  # pragma: no cover
    sys.exit("hound needs 'requests'. Install it with:  pip install requests")


# --------------------------------------------------------------------------- #
# Site registry
# --------------------------------------------------------------------------- #
# method:
#   "status"        -> 200 means the profile exists, 404 means it doesn't
#   "error_text"    -> page is always 200; the marker string appears only when
#                      the profile is MISSING
#   "success_text"  -> page is always 200; the marker string appears only when
#                      the profile EXISTS
#
# probe_url lets you hit a cheap JSON endpoint while still showing the human
# profile URL in the results.
# regex skips sites whose username rules the input can't satisfy anyway.


@dataclass(frozen=True)
class Site:
    name: str
    url: str
    method: str = "status"
    probe_url: Optional[str] = None
    text: Optional[str] = None
    regex: Optional[str] = None


SITES: list[Site] = [
    Site("GitHub", "https://github.com/{}",
         regex=r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$"),
    Site("GitLab", "https://gitlab.com/{}"),
    Site("Bitbucket", "https://bitbucket.org/{}/"),
    Site("Reddit", "https://www.reddit.com/user/{}",
         probe_url="https://www.reddit.com/user/{}/about.json"),
    Site("Hacker News", "https://news.ycombinator.com/user?id={}",
         method="error_text", text="No such user."),
    Site("Medium", "https://medium.com/@{}"),
    Site("Dev.to", "https://dev.to/{}"),
    Site("Telegram", "https://t.me/{}",
         method="success_text", text="tgme_page_title"),
    Site("Instagram", "https://www.instagram.com/{}/"),
    Site("TikTok", "https://www.tiktok.com/@{}"),
    Site("YouTube", "https://www.youtube.com/@{}"),
    Site("Steam", "https://steamcommunity.com/id/{}",
         method="error_text", text="The specified profile could not be found"),
    Site("SoundCloud", "https://soundcloud.com/{}"),
    Site("Vimeo", "https://vimeo.com/{}"),
    Site("Flickr", "https://www.flickr.com/people/{}"),
    Site("Kaggle", "https://www.kaggle.com/{}"),
    Site("Docker Hub", "https://hub.docker.com/u/{}",
         probe_url="https://hub.docker.com/v2/users/{}/"),
    Site("npm", "https://www.npmjs.com/~{}"),
    Site("PyPI", "https://pypi.org/user/{}/"),
    Site("Replit", "https://replit.com/@{}"),
    Site("Keybase", "https://keybase.io/{}"),
    Site("Mastodon", "https://mastodon.social/@{}"),
    Site("Last.fm", "https://www.last.fm/user/{}"),
    Site("Chess.com", "https://www.chess.com/member/{}",
         probe_url="https://api.chess.com/pub/player/{}"),
    Site("Patreon", "https://www.patreon.com/{}"),
    Site("About.me", "https://about.me/{}"),
    Site("Wikipedia", "https://en.wikipedia.org/wiki/Special:CentralAuth/{}",
         method="error_text", text="There is no global account"),
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
]

FOUND, NOT_FOUND, UNKNOWN = "found", "not_found", "unknown"
BLOCKED_CODES = {401, 403, 405, 429, 500, 502, 503}


# --------------------------------------------------------------------------- #
# Core
# --------------------------------------------------------------------------- #

@dataclass
class Result:
    site: str
    username: str
    url: str
    status: str
    http_code: Optional[int] = None
    elapsed: float = 0.0
    note: str = ""


def build_session(proxy: Optional[str]) -> requests.Session:
    """One session per worker: connection pooling + a light retry policy."""
    s = requests.Session()
    retry = Retry(total=2, backoff_factor=0.4,
                  status_forcelist=(500, 502, 503, 504),
                  allowed_methods=frozenset(["GET"]))
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    if proxy:
        s.proxies = {"http": proxy, "https": proxy}
    return s


def check_site(site: Site, username: str, session: requests.Session,
               timeout: float, delay: float) -> Result:
    safe = quote(username, safe="")
    profile_url = site.url.format(safe)
    probe_url = (site.probe_url or site.url).format(safe)

    if site.regex and not re.match(site.regex, username):
        return Result(site.name, username, profile_url, NOT_FOUND,
                      note="username invalid for this site")

    if delay:
        time.sleep(random.uniform(0, delay))

    start = time.perf_counter()
    try:
        # For pure status checks we never touch the body, so stream=True lets us
        # drop the connection as soon as the headers are in.
        need_body = site.method in ("error_text", "success_text")
        r = session.get(probe_url, timeout=timeout, allow_redirects=True,
                        stream=not need_body)
        body = r.text if need_body else ""
        code = r.status_code
        r.close()
    except requests.RequestException as exc:
        return Result(site.name, username, profile_url, UNKNOWN,
                      elapsed=time.perf_counter() - start,
                      note=type(exc).__name__)

    elapsed = time.perf_counter() - start

    if site.method == "status":
        if code == 200:
            status, note = FOUND, ""
        elif code in (404, 410):
            status, note = NOT_FOUND, ""
        elif code in BLOCKED_CODES:
            status, note = UNKNOWN, "blocked or rate limited"
        else:
            status, note = UNKNOWN, f"unexpected status {code}"
    elif site.method == "error_text":
        if code in BLOCKED_CODES:
            status, note = UNKNOWN, "blocked or rate limited"
        elif code == 404:
            status, note = NOT_FOUND, ""
        else:
            found = site.text not in body
            status, note = (FOUND, "") if found else (NOT_FOUND, "")
    else:  # success_text
        if code in BLOCKED_CODES:
            status, note = UNKNOWN, "blocked or rate limited"
        else:
            found = site.text in body
            status, note = (FOUND, "") if found else (NOT_FOUND, "")

    return Result(site.name, username, profile_url, status, code, elapsed, note)


def scan(username: str, sites: list[Site], workers: int, timeout: float,
         delay: float, proxy: Optional[str], on_result) -> list[Result]:
    results: list[Result] = []
    local = __import__("threading").local()

    def worker(site: Site) -> Result:
        if not hasattr(local, "session"):
            local.session = build_session(proxy)
        return check_site(site, username, local.session, timeout, delay)

    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(worker, s): s for s in sites}
        for fut in cf.as_completed(futures):
            res = fut.result()
            results.append(res)
            on_result(res)

    results.sort(key=lambda r: r.site.lower())
    return results


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #

class C:
    GREEN = RED = YELLOW = GREY = BOLD = RESET = ""

    @classmethod
    def enable(cls):
        cls.GREEN, cls.RED, cls.YELLOW = "\033[32m", "\033[31m", "\033[33m"
        cls.GREY, cls.BOLD, cls.RESET = "\033[90m", "\033[1m", "\033[0m"


def render(res: Result, found_only: bool) -> Optional[str]:
    if found_only and res.status != FOUND:
        return None
    if res.status == FOUND:
        mark, color, detail = "+", C.GREEN, res.url
    elif res.status == NOT_FOUND:
        mark, color, detail = "-", C.RED, "not found"
    else:
        mark, color, detail = "?", C.YELLOW, res.note or "unknown"
    return f"{color}[{mark}]{C.RESET} {res.site:<14} {C.GREY}{detail}{C.RESET}"


def write_json(path: str, results: list[Result]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([asdict(r) for r in results], fh, indent=2)


def write_csv(path: str, results: list[Result]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(asdict(results[0]).keys()))
        w.writeheader()
        w.writerows(asdict(r) for r in results)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="hound",
        description="Check which sites have a public profile for a username.")
    p.add_argument("usernames", nargs="*", help="one or more usernames")
    p.add_argument("--only", nargs="+", metavar="SITE", help="scan only these sites")
    p.add_argument("--exclude", nargs="+", metavar="SITE", help="skip these sites")
    p.add_argument("--timeout", type=float, default=10.0, help="per-request seconds (default 10)")
    p.add_argument("--workers", type=int, default=12, help="concurrent requests (default 12)")
    p.add_argument("--delay", type=float, default=0.0,
                   help="random 0..N second jitter before each request")
    p.add_argument("--proxy", help="e.g. socks5h://127.0.0.1:9050")
    p.add_argument("--found-only", action="store_true", help="print hits only")
    p.add_argument("--json", metavar="FILE", help="write results as JSON")
    p.add_argument("--csv", metavar="FILE", help="write results as CSV")
    p.add_argument("--no-color", action="store_true")
    p.add_argument("--list-sites", action="store_true", help="print supported sites and exit")
    return p.parse_args(argv)


def select_sites(args) -> list[Site]:
    sites = SITES
    if args.only:
        wanted = {s.lower() for s in args.only}
        sites = [s for s in sites if s.name.lower() in wanted]
    if args.exclude:
        skip = {s.lower() for s in args.exclude}
        sites = [s for s in sites if s.name.lower() not in skip]
    return sites


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.list_sites:
        for s in SITES:
            print(f"{s.name:<14} {s.url}")
        return 0

    if not args.usernames:
        print("error: give at least one username (or --list-sites)", file=sys.stderr)
        return 2

    if not args.no_color and sys.stdout.isatty() and os.name != "nt":
        C.enable()

    sites = select_sites(args)
    if not sites:
        print("error: no sites left after filtering", file=sys.stderr)
        return 2

    all_results: list[Result] = []
    for username in args.usernames:
        print(f"\n{C.BOLD}>> {username}{C.RESET}  ({len(sites)} sites)")
        started = time.perf_counter()

        def emit(res: Result) -> None:
            line = render(res, args.found_only)
            if line:
                print(line)

        results = scan(username, sites, args.workers, args.timeout,
                       args.delay, args.proxy, emit)
        all_results.extend(results)

        hits = sum(r.status == FOUND for r in results)
        unsure = sum(r.status == UNKNOWN for r in results)
        print(f"{C.GREY}-- {hits} found, {unsure} unknown, "
              f"{time.perf_counter() - started:.1f}s{C.RESET}")

    if args.json:
        write_json(args.json, all_results)
        print(f"{C.GREY}wrote {args.json}{C.RESET}")
    if args.csv and all_results:
        write_csv(args.csv, all_results)
        print(f"{C.GREY}wrote {args.csv}{C.RESET}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
