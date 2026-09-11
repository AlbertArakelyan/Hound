# Social account discovery

Given a username, ask each site whether a public profile exists. Ported from the
Hound-CLI reference script.

## Files

| file | job | Qt |
|---|---|---|
| `sites.py` | the site list, data only | no |
| `models.py` | `Status` enum, `Result` dataclass | no |
| `lookup.py` | session, `check_site`, concurrent `scan` | no |
| `search_worker.py` | `QThread` wrapper, one signal per result | yes |
| `result_row.py` | one row: mark, site name, link | yes |
| `page.py` | input, search button, filter, scrolling list | yes |

To add or fix a site, use the `add-site` skill. Do not change `lookup.py` for it.

## Detection

Three methods, chosen per site in `sites.py`:

- `status`: 200 means found, 404 or 410 means not found.
- `error_text`: page is always 200, the marker appears only when the profile is missing.
- `success_text`: page is always 200, the marker appears only when it exists.

Anything in `BLOCKED_CODES` is `unknown`, never `not_found`. Same for a request that
raises. Reporting a blocked site as not found is the worst bug this tool can have, so
keep that distinction intact.

## Concurrency

`scan` uses a thread pool with one `requests.Session` per worker thread, and calls
`on_result` as each answer lands. `SearchWorker` turns that into a Qt signal so rows
appear progressively. `should_stop` is checked before each request, so stopping is not
instant, requests already in flight still finish.

## Testing

Test `lookup.py` with a fake session object that returns a canned status code and body.
Test the page with `search_worker.scan` replaced by a stub. Never hit live sites to test
UI wiring. See the `run-app` skill.
