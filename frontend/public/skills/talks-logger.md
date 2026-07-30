---
name: ohermes-talks-logger
description: "Log a real, substantive discussion or exploration of an idea, model, or particular technology to ohermes-hub's public Talks page. Trigger: a genuine back-and-forth exploration happened (not a one-line mention) -- discussing how a model behaves, weighing an architectural idea, comparing approaches to a problem. Drafts the entry and confirms before publishing."
---

# ohermes Talks logger

Owen's own framing: Talks is "kind of like the ideas -- they're just being
talked about... talks about particular things or models." Not formal
presentations (that's what the page used to mean before this correction) —
a running record of real discussions that had actual substance.

## When this actually applies

- A genuine exploration happened: comparing two models' behavior on
  something real, working through an architectural tradeoff, digging into
  why a particular technology behaves the way it does.
- **Does not apply** to routine task execution, or a passing one-line
  mention of a model/tool with no actual discussion attached.
- The bar is "would this be worth someone else reading," not "did we say
  a model's name."

## Workflow

Uses the `ohermes-hub-content` MCP server's tools (see
`mcp-server/README.md` in the ohermes-hub project) instead of editing
`talks.json` by hand.

1. **Let the discussion actually happen first** — this skill logs a
   discussion that occurred, it doesn't manufacture one.
2. **Call `draft_talk`** summarizing the real substance — the actual
   question explored and what was concluded (or left open, if it was left
   open; don't invent a tidy conclusion that didn't happen):
   ```
   draft_talk(
     topic="Short, specific topic -- not just a model name",
     summary="What was actually discussed and what came of it, in 2-4 honest sentences.",
     tags=["relevant", "tags"]
   )
   ```
   This only stages the entry — it does not publish anything yet.
3. **Show Owen the drafted entry (the tool's return value) and confirm
   before publishing** — same confirm-before-publish habit as the rest of
   this hub. A terse "yes"/"go" is enough.
4. **On confirmation, call `publish_draft(draft_id)`** — writes the entry
   to the real `talks.json` the backend serves. If Owen says no, call
   `discard_draft(draft_id)` instead.

## What NOT to log

- Anything that reveals details about a private/PIN-gated project's
  internals, security posture, or unreleased plans — same exclusion that
  already applies to the Roadmap page.
- A discussion that didn't actually happen, logged just to populate the
  page. An empty Talks page is a true statement; a padded one isn't.
