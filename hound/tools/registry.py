from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    """What a tool tells the app about itself.

    create_page imports its page lazily, so this module stays free of Qt imports.
    """

    id: str
    name: str
    description: str
    create_page: Callable[[], Any]
    # Shown on the card. One emoji, optional.
    icon: str = ""


def _social_accounts_page() -> Any:
    from hound.tools.social_accounts.page import SocialAccountsPage

    return SocialAccountsPage()


def _email_scraper_page() -> Any:
    from hound.tools.email_scraper.page import EmailScraperPage

    return EmailScraperPage()


TOOLS: tuple[ToolSpec, ...] = (
    ToolSpec(
        id="social-accounts",
        name="Social Account Discovery",
        description="Find social media accounts that use a given username.",
        create_page=_social_accounts_page,
        icon="🔎",
    ),
    ToolSpec(
        id="email-scraper",
        name="Email Scraper",
        description="Crawl a site and collect the email addresses it exposes.",
        create_page=_email_scraper_page,
        icon="✉️",
    ),
)
