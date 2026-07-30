---
name: ohermes-press-logger
description: "Publish a write-up of completed model-test or workflow-experiment results to ohermes-hub's public Press page. Trigger: a testing/experiment task has actually concluded with real results worth sharing -- what was tried, what happened, what it changes. Drafts the write-up from real results and confirms before publishing."
---

# ohermes Press logger

Owen's own framing: Press is "for when we're done testing models and wanna
post the results... things we've done with particular models and how [it]
can help workflows." A results write-up, published once real results exist
— not a progress update, not a plan.

## When this actually applies

- A model test, benchmark, or workflow experiment has genuinely concluded
  with a real outcome — a comparison result, a workflow change that
  measurably helped, a finding worth other people reading.
- **Does not apply** mid-experiment, or to routine work that isn't itself
  the subject of the test (don't write a press post about every session —
  this is for the results themselves).

## Workflow

Uses the `ohermes-hub-content` MCP server's tools (see
`mcp-server/README.md` in the ohermes-hub project) instead of editing
`press.json` by hand.

1. **Let the test/experiment actually finish first.** The write-up is
   built from real output — actual numbers, actual before/after, actual
   observed behavior — never from an expected or hoped-for result.
2. **Call `draft_press_post`:**
   ```
   draft_press_post(
     title="Specific, honest title -- what was tested/built, not a headline",
     summary="One or two sentences: what was tried and the real outcome.",
     body="The actual write-up -- what was tested, what happened, what changed as a result. Plain text (rendered as-is, not markdown-parsed on the page -- keep formatting simple: blank-line paragraph breaks, no headers/bold syntax)."
   )
   ```
   Ground every claim in something that actually happened this session or a
   prior logged one — if a number or result isn't confidently known, say so
   in the text rather than smoothing it over. This only stages the entry —
   it does not publish anything yet.
3. **Show Owen the full drafted write-up (the tool's return value) and
   confirm before publishing.** This is the most public-facing of the
   logging skills — treat the bar for "ready to publish" accordingly. A
   terse "yes"/"go" is enough once the draft is shown in full.
4. **On confirmation, call `publish_draft(draft_id)`** — writes the entry
   to the real `press.json` the backend serves. If Owen says no or wants
   edits, call `discard_draft(draft_id)` and re-draft rather than publishing
   something not yet approved.

## What NOT to publish

- Results that reveal exploitable details about a private/PIN-gated
  system's current weaknesses (same rule as Roadmap/Talks).
- A "results" post before the test has actually concluded.
- Anything Owen hasn't confirmed — this is the one most worth getting
  explicit sign-off on, every time, no exceptions for "it seemed obviously
  fine to post."
