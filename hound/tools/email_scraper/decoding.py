"""Pull out email addresses that are not in the HTML as plain text.

Cloudflare's email obfuscation is the common case. It replaces the address with a hex
blob and decodes it in the browser, so a plain regex over the page finds nothing.
"""

import re

# <span class="__cf_email__" data-cfemail="8ceae9...">
CF_ATTR_RE = re.compile(r'data-cfemail="([0-9a-fA-F]{4,})"')
# <a href="/cdn-cgi/l/email-protection#5f393a...">
CF_LINK_RE = re.compile(r'/cdn-cgi/l/email-protection#([0-9a-fA-F]{4,})')

CF_PROTECTION_PATH = "/cdn-cgi/l/email-protection"


def decode_cfemail(blob: str) -> str | None:
    """Decode one Cloudflare blob. The first byte is the XOR key for the rest.

    The result is a candidate, not a verified address. The caller decides whether it
    looks like an email, so a malformed blob cannot inject junk into the results.
    """
    try:
        return "".join(
            chr(int(blob[i:i + 2], 16) ^ int(blob[:2], 16))
            for i in range(2, len(blob), 2)
        )
    except ValueError:
        return None


def find_obfuscated(html: str) -> list[str]:
    """Candidate addresses hidden behind Cloudflare obfuscation in this page."""
    candidates = []
    for pattern in (CF_ATTR_RE, CF_LINK_RE):
        for blob in pattern.findall(html):
            decoded = decode_cfemail(blob)
            if decoded:
                candidates.append(decoded)
    return candidates
