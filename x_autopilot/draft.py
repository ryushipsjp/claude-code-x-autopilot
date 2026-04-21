"""Generate today's X post draft using Claude Agent SDK."""
from __future__ import annotations

import os
import re
import sys
from datetime import date
from pathlib import Path

import anyio
from dotenv import dotenv_values, load_dotenv

from claude_agent_sdk import ClaudeAgentOptions, query

ROOT = Path(__file__).resolve().parent.parent
DRAFT_FILENAME_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")


def _load_recent_drafts(drafts_dir: Path, today: str, days: int = 7) -> list[dict[str, str]]:
    """Newest-first list of {date, body} for prior drafts. Excludes today's file."""
    if not drafts_dir.exists():
        return []
    records: list[dict[str, str]] = []
    for p in sorted(drafts_dir.iterdir(), reverse=True):
        m = DRAFT_FILENAME_PATTERN.match(p.name)
        if not m:
            continue
        draft_date = m.group(1)
        if draft_date == today:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if text.startswith("---\n"):
            end = text.find("\n---\n", 4)
            if end != -1:
                text = text[end + 5:]
        records.append({"date": draft_date, "body": text.strip()})
        if len(records) >= days:
            break
    return records


def _format_recent(recent: list[dict[str, str]]) -> str:
    if not recent:
        return "_(no prior drafts — this is the first one)_"
    lines = []
    for r in recent:
        body = r["body"].replace("\n", " ").strip()
        if len(body) > 280:
            body = body[:277] + "..."
        lines.append(f"- {r['date']}: {body}")
    return "\n".join(lines)


def build_prompt(today: str, handle: str, recent: list[dict[str, str]]) -> str:
    voice_path = ROOT / os.getenv("VOICE_PROMPT_PATH", "prompts/manifesto.md")
    task_path = ROOT / "prompts" / "daily_post.md"
    voice = voice_path.read_text(encoding="utf-8")
    task = task_path.read_text(encoding="utf-8")
    return (
        f"Today is {today}. You are drafting for @{handle}.\n\n"
        f"# Voice guide\n{voice}\n\n"
        f"# Recent drafts (newest first — do not repeat topics or phrasing)\n"
        f"{_format_recent(recent)}\n\n"
        f"# Task\n{task}\n\n"
        f"Write the draft file to drafts/{today}.md using the Write tool.\n"
        f"Do not print the draft to stdout. Do not create any other files."
    )


async def run() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    env_file = dotenv_values(ROOT / ".env")
    load_dotenv(ROOT / ".env", override=True)
    if not env_file.get("ANTHROPIC_API_KEY"):
        os.environ.pop("ANTHROPIC_API_KEY", None)
    today = date.today().isoformat()
    handle = os.getenv("X_HANDLE", "example_user")
    recent = _load_recent_drafts(ROOT / "drafts", today)
    print(f"draft.py: {len(recent)} prior draft(s) loaded as context.")

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write"],
        disallowed_tools=[
            "Bash",
            "PowerShell",
            "Edit",
            "NotebookEdit",
            "Task",
            "WebFetch",
            "WebSearch",
        ],
        permission_mode="acceptEdits",
        model="claude-sonnet-4-6",
    )

    async for message in query(prompt=build_prompt(today, handle, recent), options=options):
        print(message)

    out_path = ROOT / "drafts" / f"{today}.md"
    if not out_path.exists():
        print(f"draft.py: expected {out_path} to be written, but it is missing.", file=sys.stderr)
        return 1
    print(f"draft.py: wrote {out_path}")
    return 0


def main() -> None:
    sys.exit(anyio.run(run))


if __name__ == "__main__":
    main()
