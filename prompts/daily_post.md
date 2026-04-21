# Daily draft task

Draft one X post (or a short thread, max 5 posts) for today.

## Context you have access to

- `VOICE_PROMPT_PATH` — the builder's voice guide. Follow it exactly.
- The current working directory may contain sibling project folders
  (`../claude-code-*`). Peek at their READMEs if you need today's ship topic.
- The prompt already contains the last 7 days of drafts as a
  "do not repeat" block — scan it before choosing today's angle.

## What you output

A markdown file at `drafts/{YYYY-MM-DD}.md` with this exact shape:

```
---
date: 2026-04-21
intent: ship_announcement   # or build_log / teardown / question
status: draft                # never "approved" — human sets that
---

<post 1 text, ≤ 280 chars>

---

<post 2 text, if thread>
```

One post per `---` block. Frontmatter is required. Do not exceed 5 blocks.

## Self-check before writing

1. Did you read the voice guide?
2. Did you check recent posts so this isn't a repeat?
3. Is every number in the draft real and verifiable?
4. Is the CTA a repo link (if this is a ship post)?

If any answer is no, fix it before writing the file.
