"""Approval gate: flip a draft's frontmatter status to `approved`.

The poster refuses to publish any draft whose status is not `approved`.
This script is deliberately trivial — the real review is you reading the
file in your editor before you run it.
"""
from __future__ import annotations

import sys
from pathlib import Path


def approve(path: Path) -> int:
    if not path.exists():
        print(f"approve.py: {path} does not exist.", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        print("approve.py: draft has no frontmatter. Aborting.", file=sys.stderr)
        return 1

    end = text.find("\n---\n", 4)
    if end == -1:
        print("approve.py: frontmatter terminator not found. Aborting.", file=sys.stderr)
        return 1

    frontmatter = text[4:end]
    body = text[end + 5:]

    new_lines = []
    saw_status = False
    for line in frontmatter.splitlines():
        if line.startswith("status:"):
            new_lines.append("status: approved")
            saw_status = True
        else:
            new_lines.append(line)
    if not saw_status:
        new_lines.append("status: approved")

    rebuilt = "---\n" + "\n".join(new_lines) + "\n---\n" + body
    path.write_text(rebuilt, encoding="utf-8")
    print(f"approve.py: {path} marked approved.")
    return 0


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: python -m x_autopilot.approve <draft.md>", file=sys.stderr)
        sys.exit(2)
    sys.exit(approve(Path(sys.argv[1])))


if __name__ == "__main__":
    main()
