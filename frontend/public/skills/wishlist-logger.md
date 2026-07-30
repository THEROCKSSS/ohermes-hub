---
name: ohermes-wishlist-logger
description: "Log a real research-for-purchase task to ohermes-hub's public Wishlist page. Trigger: the user asks Claude to research a tool, piece of hardware, or software with buying/acquiring it as the actual goal (not just general curiosity/comparison research). Drafts the entry from the real research findings and confirms before publishing -- never invoke silently."
---

# ohermes Wishlist logger

Owen's own framing: "if I wanna have you like research something and want
to buy it, you'll put it on the wishlist." This is that — a record of real
purchase-research tasks, not a wishlist of invented wants.

## When this actually applies

- Owen asks you to look into buying/acquiring a specific tool, piece of
  hardware, software license, or service.
- **Does not apply** to general technical research that isn't about
  acquiring something (reading docs, comparing free options with no
  purchase intent, debugging).
- If it's ambiguous whether buying is the actual goal, ask rather than
  guess — this publishes to a public site.

## Workflow

Uses the `ohermes-hub-content` MCP server's tools (see
`mcp-server/README.md` in the ohermes-hub project) instead of editing
`wishlist.json` by hand — same confirm-before-publish behavior, just via
the draft/publish tool pair rather than manual file edits.

1. **Do the research normally first.** This skill doesn't change how you
   research — it's what happens after, with the real findings in hand.
2. **Call `draft_wishlist_item`** with what was actually found — real
   prices, real tradeoffs, real recommendation, not filler:
   ```
   draft_wishlist_item(
     item="Exact product/tool name",
     why="One honest sentence: what problem this solves.",
     status="researching",
     notes="Key finding from the actual research -- price point, main tradeoff, or what's blocking a decision."
   )
   ```
   `status` is one of `researching` / `considering` / `bought` / `passed` —
   reflects where the decision actually stands, not "researching" by
   default once a real decision has been made. This only stages the entry
   (in `backend/_pending_drafts.json`) — it does not publish anything yet.
3. **Show Owen the drafted entry (the tool's return value) and ask before
   publishing.** This is a public page — a purchase consideration is a step
   more personal than a project listing, and the confirm-before-publish
   habit already established for this hub's project list applies here too.
   A terse "yes"/"go" is enough once shown the draft.
4. **On confirmation, call `publish_draft(draft_id)`** — this writes the
   entry to the real `wishlist.json` the backend serves. If Owen says no
   or wants changes instead, call `discard_draft(draft_id)` and re-draft.
5. **Update an existing entry instead of duplicating** when the same item
   comes up again with a status change (moved from `researching` to
   `bought`, for instance) — this isn't yet a dedicated MCP tool; edit
   `backend/wishlist.json` directly for that specific case, find it by
   `item` name.

## What NOT to log

- Anything Owen explicitly says is private or not for the public site.
- Research where no real purchase intent exists.
- Prices/specifics you're not confident are accurate — say "notes":
  "price varies, check current listing" rather than a stale or guessed number.
