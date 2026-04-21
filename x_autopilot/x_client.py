"""X API v2 client: OAuth 1.0a session + post/delete for the thread publisher."""
from __future__ import annotations

import os
import re
import time
from typing import Any

from requests_oauthlib import OAuth1Session

API_BASE = "https://api.x.com/2"
TWEETS_URL = f"{API_BASE}/tweets"

_URL_RE = re.compile(r"https?://\S+")
_URL_WEIGHT = 23  # X counts any URL as 23 characters regardless of actual length.


def tweet_length(text: str) -> int:
    """Approximate X's weighted tweet length: URLs count as 23, other chars as 1.

    Ignores the CJK double-weight rule — good enough for English ship posts.
    """
    return len(_URL_RE.sub("x" * _URL_WEIGHT, text))


def build_session() -> OAuth1Session:
    missing = [
        k for k in (
            "X_OAUTH_CONSUMER_KEY",
            "X_OAUTH_CONSUMER_SECRET",
            "X_OAUTH_ACCESS_TOKEN",
            "X_OAUTH_ACCESS_TOKEN_SECRET",
        )
        if not os.getenv(k)
    ]
    if missing:
        raise SystemExit(f"x_client: missing env vars: {', '.join(missing)}")
    return OAuth1Session(
        client_key=os.environ["X_OAUTH_CONSUMER_KEY"],
        client_secret=os.environ["X_OAUTH_CONSUMER_SECRET"],
        resource_owner_key=os.environ["X_OAUTH_ACCESS_TOKEN"],
        resource_owner_secret=os.environ["X_OAUTH_ACCESS_TOKEN_SECRET"],
    )


def post_tweet(
    session: OAuth1Session,
    text: str,
    reply_to: str | None = None,
    retries: int = 1,
) -> str:
    """Post a single tweet, return tweet id. Retries once on 429/5xx."""
    payload: dict[str, Any] = {"text": text}
    if reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to}

    attempt = 0
    while True:
        r = session.post(TWEETS_URL, json=payload, timeout=10)
        if r.status_code in (200, 201):
            tid = r.json().get("data", {}).get("id")
            if not tid:
                raise RuntimeError(f"x_client.post_tweet: response missing id ({r.text})")
            return tid
        if r.status_code in (429, 500, 502, 503, 504) and attempt < retries:
            time.sleep(2 ** attempt)
            attempt += 1
            continue
        raise RuntimeError(f"x_client.post_tweet: HTTP {r.status_code} ({r.text})")


def delete_tweet(session: OAuth1Session, tweet_id: str) -> bool:
    """Best-effort delete. Returns True on success, False on any failure."""
    try:
        r = session.delete(f"{TWEETS_URL}/{tweet_id}", timeout=10)
        return r.status_code in (200, 204)
    except Exception:
        return False
