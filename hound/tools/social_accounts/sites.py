"""The site list. Data only, so sites can be added without touching the engine."""

from dataclasses import dataclass
from typing import Literal

# status        200 means the profile exists, 404 means it does not
# error_text    page is always 200, the marker appears only when the profile is MISSING
# success_text  page is always 200, the marker appears only when the profile EXISTS
Method = Literal["status", "error_text", "success_text"]


@dataclass(frozen=True)
class Site:
    name: str
    url: str
    method: Method = "status"
    # Lets us hit a cheap JSON endpoint while still showing the human profile URL.
    probe_url: str | None = None
    text: str | None = None
    # Skips sites whose username rules the input cannot satisfy anyway.
    regex: str | None = None


SITES: tuple[Site, ...] = (
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
)
