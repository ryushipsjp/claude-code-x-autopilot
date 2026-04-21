# claude-code-x-autopilot

Founder-grade X (Twitter) autopilot. Built with Claude.

Generates daily X post drafts that match **your** voice — not generic AI slop.
Review in your terminal. Ship with one keystroke. Dry-run by default so nothing
goes out without you.

> Dogfooded on [@ryushipsjp](https://x.com/ryushipsjp) to keep the "ship every Friday"
> manifesto alive without burning a founder's brain on thread-drafting.

## Why

Solo founders lose a whole evening a week just staring at the compose box.
A drafting assistant that actually reads your repo, your recent posts, and
your voice guide takes the first 80% off your plate — you stay in control of
the last 20%.

## Stack

`Claude Agent SDK` (Python) · X API v2 (OAuth 1.0a user context) · approval-gated CLI

> Drafter reads your last 7 days of local drafts as "don't repeat" context —
> no read-timeline API tier required.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# fill in ANTHROPIC_API_KEY and X credentials
```

## Usage

Generate today's draft:

```bash
python -m x_autopilot.draft
# → drafts/2026-04-21.md
```

Review & approve:

```bash
python -m x_autopilot.approve drafts/2026-04-21.md
```

Post (dry-run default — prints what *would* be sent, posts nothing):

```bash
python -m x_autopilot.post drafts/2026-04-21.md
# really ship it:
python -m x_autopilot.post drafts/2026-04-21.md --publish
```

## Safety defaults

- **Dry-run is ON by default** on `post`. Explicit `--publish` flag required.
- **Approval gate** reads the draft file mtime; you must re-save the file
  after reviewing before `post` will accept it.
- **Voice guide is yours.** Edit `prompts/manifesto.md` to match your brand.
  Nothing ships through generic Claude defaults.

## Extend it

Want to post to Bluesky / LinkedIn / a newsletter instead?
Copy `x_autopilot/post.py` → `x_autopilot/post_<sink>.py`, swap the MCP
tool call for your sink's API. Same draft → many channels.

## License

MIT. Fork it. Ship your own.

---

#### Hire me

Custom Claude Code automations for founders and small teams → DM
[@ryushipsjp](https://x.com/ryushipsjp).

---

Shipped by [@ryushipsjp](https://x.com/ryushipsjp) — new Claude Code automation every Friday.
