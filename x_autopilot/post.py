"""Post an approved draft to X. Dry-run by default.

Safety model:
- Refuses any draft whose frontmatter status is not `approved`.
- Dry-run is the default. `--publish` must be passed explicitly.
- Each `---`-separated block in the body becomes one post. If there is more
  than one block, subsequent posts are sent as replies to form a thread.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from x_autopilot.x_client import build_session, delete_tweet, post_tweet, tweet_length

ROOT = Path(__file__).resolve().parent.parent
MAX_POST_CHARS = 280


def parse_draft(path: Path) -> tuple[dict[str, str], list[str]]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated frontmatter")

    fm: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()

    body = text[end + 5:].strip()
    blocks = [b.strip() for b in body.split("\n---\n") if b.strip()]
    return fm, blocks


def validate(fm: dict[str, str], blocks: list[str]) -> None:
    if fm.get("status") != "approved":
        raise SystemExit(
            f"post.py: draft status is '{fm.get('status')}', not 'approved'. "
            f"Run: python -m x_autopilot.approve <draft>"
        )
    if not blocks:
        raise SystemExit("post.py: draft body is empty.")
    for i, block in enumerate(blocks, 1):
        weighted = tweet_length(block)
        if weighted > MAX_POST_CHARS:
            raise SystemExit(
                f"post.py: block {i} is {weighted} weighted chars (max {MAX_POST_CHARS})."
            )
    if len(blocks) > 5:
        raise SystemExit(f"post.py: {len(blocks)} blocks exceeds max thread length of 5.")


def publish(blocks: list[str]) -> list[str]:
    """Post blocks as a thread. On any failure, roll back already-posted blocks."""
    session = build_session()
    ids: list[str] = []
    try:
        for i, block in enumerate(blocks, 1):
            reply_to = ids[-1] if ids else None
            ids.append(post_tweet(session, block, reply_to=reply_to))
    except RuntimeError as e:
        if ids:
            print(
                f"post.py: publish failed on block {len(ids) + 1}; "
                f"rolling back {len(ids)} already-posted tweet(s).",
                file=sys.stderr,
            )
            for tid in reversed(ids):
                ok = delete_tweet(session, tid)
                status = "ok" if ok else "FAILED (manual cleanup: https://x.com/i/status/" + tid + ")"
                print(f"  rollback {tid}: {status}", file=sys.stderr)
        raise SystemExit(f"post.py: publish failed: {e}")
    return ids


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="Post an approved draft to X.")
    parser.add_argument("draft", type=Path)
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Actually hit the X API. Without this flag, runs in dry-run mode.",
    )
    args = parser.parse_args()

    fm, blocks = parse_draft(args.draft)
    validate(fm, blocks)

    if not args.publish:
        print("post.py: DRY RUN. Would post the following blocks:")
        for i, block in enumerate(blocks, 1):
            print(f"\n--- block {i} ({tweet_length(block)} weighted / {len(block)} raw chars) ---")
            print(block)
        print("\npost.py: rerun with --publish to actually ship.")
        return

    ids = publish(blocks)
    handle = os.getenv("X_HANDLE", "example_user")
    print("post.py: shipped.")
    for tid in ids:
        print(f"  https://x.com/{handle}/status/{tid}")


if __name__ == "__main__":
    main()
