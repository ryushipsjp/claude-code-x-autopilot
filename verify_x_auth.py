"""OAuth 1.0a credential check. Calls GET /2/users/me, prints only status + handle match.

Never prints token values, full response body, or signed headers.
Exit codes: 0 = pass, 1 = handle mismatch, 2 = missing env, 3 = API error.
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session

load_dotenv(Path(__file__).parent / ".env")

REQUIRED = [
    "X_OAUTH_CONSUMER_KEY",
    "X_OAUTH_CONSUMER_SECRET",
    "X_OAUTH_ACCESS_TOKEN",
    "X_OAUTH_ACCESS_TOKEN_SECRET",
    "X_HANDLE",
]
missing = [k for k in REQUIRED if not os.getenv(k)]
if missing:
    print(f"FAIL missing={missing}")
    sys.exit(2)

session = OAuth1Session(
    client_key=os.environ["X_OAUTH_CONSUMER_KEY"],
    client_secret=os.environ["X_OAUTH_CONSUMER_SECRET"],
    resource_owner_key=os.environ["X_OAUTH_ACCESS_TOKEN"],
    resource_owner_secret=os.environ["X_OAUTH_ACCESS_TOKEN_SECRET"],
)

r = session.get("https://api.twitter.com/2/users/me", timeout=10)
print(f"HTTP {r.status_code}  rate-remaining={r.headers.get('x-rate-limit-remaining', 'n/a')}")

if r.status_code == 200:
    data = r.json().get("data", {})
    returned = (data.get("username") or "").lower()
    expected = os.environ["X_HANDLE"].lstrip("@").lower()
    match = returned == expected
    print(f"handle: returned={returned!r} expected={expected!r} match={match}")
    sys.exit(0 if match else 1)

try:
    err = r.json()
    title = err.get("title") or (err.get("errors") or [{}])[0].get("code") or err.get("detail")
except Exception:
    title = "(unparseable)"
print(f"error-title: {title}")
sys.exit(3)
