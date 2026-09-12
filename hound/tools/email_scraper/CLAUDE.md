# Email Scraper

Crawl a site breadth first from a starting URL and collect the email addresses in the
page text. Ported from `examples/email-scarper.py`.

This is not theHarvester. It is only that script's crawler.

## Files

| file | job | Qt |
|---|---|---|
| `models.py` | `PageStatus`, `PageVisit`, `CrawlSummary` | no |
| `scraper.py` | the crawl engine | no |
| `scrape_worker.py` | `QThread` wrapper, one signal per page and per email | yes |
| `page.py` | URL input, controls, emails pane and crawl log | yes |

## How the crawl works

A `deque` of pending URLs, a `set` of visited ones, a `set` of emails. Each page is
fetched once, scanned with `EMAIL_RE`, then its anchors are resolved and queued.

Link resolution follows the script: `/path` joins to scheme and netloc, a bare relative
link joins to the current directory, anything starting with `http` is taken as is.

`same_domain` defaults to True and compares `urlsplit(...).netloc` against the starting
host. The script followed every link, including off site ones. Keep the default on,
crawling third parties is outside what the user asked to test.

`mailto:`, `tel:`, `javascript:` and `#` anchors are never fetched. A `mailto:` still
gives up its address. Fragments are stripped when resolving, so `/page` and
`/page#section` are one request.

## Obfuscated addresses

Many sites never put the address in the HTML. `decoding.py` handles the common case,
Cloudflare email obfuscation, which stores the address as a hex blob in
`data-cfemail="..."` or in a `/cdn-cgi/l/email-protection#...` link and decodes it in
the browser. A plain regex over the page finds nothing on those sites.

`decode_cfemail` returns a candidate, not a verified address. `scraper.py` checks it
against `EMAIL_RE` before recording, so a malformed blob cannot inject junk.

If a site shows an email in the browser but the crawl finds none, fetch the page and
look for how it is hidden before touching the regex. It is usually another obfuscation
scheme, or the address is rendered by JavaScript and is not in the HTML at all.

## Rules

- Every request needs a timeout. Without one a dead host hangs the worker thread.
- Catch `requests.RequestException`, not single subclasses. A page that fails is a
  `PageVisit` with `PageStatus.FAILED` and the exception name as the note, never a
  crash that kills the run.
- `should_stop` is checked before each request, so a stop takes effect after the request
  in flight returns. Say that in the UI rather than pretending it is instant.
- Addresses are lowercased before dedupe, so `Sales@x.com` and `sales@x.com` are one.

## Testing

Stub `requests.Session.get` with canned HTML by replacing `scraper.build_session`. Test
the page with `scrape_worker.crawl` replaced. Do not crawl live sites to test wiring.
See the `run-app` skill.
