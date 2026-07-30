# ohermes-hub content MCP server

Exposes tools to draft (and, after confirmation, publish) new entries to
this hub's Wishlist, Talks, Press, Blog, and Ideas pages.

## Install

```bash
pip install -r requirements.txt
```

## Register with Claude Code

```bash
claude mcp add ohermes-hub-content -- python /full/path/to/mcp-server/server.py
```

Or point `OHERMES_HUB_DATA_DIR` at a different `backend/` directory if this
server is running against a different deployment than the one it lives
next to:

```bash
claude mcp add ohermes-hub-content --env OHERMES_HUB_DATA_DIR=/path/to/backend -- python /full/path/to/mcp-server/server.py
```

## Tools

- `draft_wishlist_item(item, why, status, notes)`
- `draft_talk(topic, summary, tags)`
- `draft_press_post(title, summary, body)`
- `draft_blog_post(title, summary, body, slug)`
- `draft_idea(name, description)`
- `list_pending_drafts()`
- `publish_draft(draft_id)`
- `discard_draft(draft_id)`

Every `draft_*` tool stages an entry in `backend/_pending_drafts.json` and
returns a `draft_id` — it does **not** touch the live content files. Nothing
reaches the actual site until `publish_draft` is called, and every tool's
own description instructs the calling agent to only do that after a human
has explicitly confirmed the draft. This is a behavioral contract enforced
by the tool descriptions, not a technical lock — MCP has no native "pause
for human approval" primitive.

After `publish_draft`, restart the backend container so the change is
picked up if that content type is cached:
```bash
docker compose restart hub-api
```
(Wishlist/Talks/Press/Blog/Ideas reads are uncached in this project, so this
is optional today — included for forward-compatibility if that changes.)

## What's deliberately not here

No `add_project` or `add_tool`. The project list is governed by a stricter
rule — only real, already-public GitHub repos, verified via the
`ohermes-hub-content-refresh` skill's process — and that curation judgment
call shouldn't be something an MCP tool call can bypass.
