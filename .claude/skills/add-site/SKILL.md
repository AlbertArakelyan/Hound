---
name: add-site
description: Add or fix a site in the social account search list. Use when asked to support a new social network, or when a site reports wrong results (false found, false not found, or always unknown).
---

# Add a site to the social account search

The list lives in `hound/tools/social_accounts/sites.py`. It is data only. Adding a site
must not change `lookup.py`.

## Pick the detection method

Check by hand first with a username you know exists and one you know does not.

```bash
.venv/bin/python -c "
import requests
for u in ('torvalds', 'zzz-no-such-user-zzz'):
    r = requests.get('https://example.com/{}'.format(u), timeout=10)
    print(u, r.status_code, len(r.text))
"
```

- Different status codes, 200 and 404: use `method='status'`, the default.
- Always 200, and the missing page has a marker string: use `method='error_text'` with
  that marker in `text`.
- Always 200, and only the real page has a marker: use `method='success_text'`.

Pick a marker that is stable, not a page title or a stray word that could appear in
someone's bio.

## Optional fields

- `probe_url`: a cheap JSON endpoint to request, while `url` stays the human profile link
  shown in results. Use it when the HTML page is heavy or renders client side.
- `regex`: the site's username rules. Saves a request when the input cannot be valid
  there anyway.

## Verify

Run the engine, not the GUI:

```bash
.venv/bin/python -c "
from hound.tools.social_accounts.lookup import check_site, build_session
from hound.tools.social_accounts.sites import SITES
site = next(s for s in SITES if s.name == 'NewSite')
session = build_session()
for u in ('torvalds', 'zzz-no-such-user-zzz'):
    print(check_site(site, u, session))
"
```

A known username must come back `found` and a nonsense one `not_found`. If both agree,
the method or the marker is wrong.

## Do not guess

A site that blocks us or rate limits must report `unknown`, never `not_found`. If you
cannot tell the two apart, leave it `unknown` and say so. A wrong `not_found` is worse
than no answer.
