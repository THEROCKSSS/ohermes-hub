# Agent Conventions

For data flow and *why* things are shaped this way, see `ARCHITECTURE.md` —
this file covers conventions and how-to-add-X workflows, not the underlying
design.

## Repo structure (summary — see ARCHITECTURE.md for the data-flow diagram)

```
backend/            FastAPI service + JSON data files
  main.py
  projects.json      curated repo list (hand-maintained)
  wishlist.json talks.json press.json blog.json ideas.json
                     MCP-writable content, plain arrays
frontend/
  nginx.conf, Dockerfile
  public/            everything served -- keep this the ONLY thing the
                     Dockerfile COPYs wholesale (see ARCHITECTURE.md's
                     .dockerignore pitfall)
    partials/        nav.html, footer.html -- single source of truth
    js/              partials.js, app.js, secret-entry.js
    skills/          servable copies of the *.md skill files (raw markdown,
                     downloadable from the live site's /skills.html)
mcp-server/          standalone MCP server, not part of docker-compose
skills/              the actual skill source files (SKILL.md format)
```

## Hard rules (violating any of these is a regression, not a style choice)

1. **Never list a project in `projects.json` that isn't already public on
   GitHub.** No exceptions without explicit human sign-off for a specific
   case. This is a content-integrity rule, not a technical one — nothing
   enforces it in code, so it depends on whoever edits that file (human or
   agent) actually following it.
2. **Never render API-sourced content with `innerHTML`.** Every dynamic
   element uses `document.createElement` + `.textContent`. See
   `ARCHITECTURE.md`'s rendering-pattern section for why this matters.
3. **MCP `publish_draft` only after human confirmation, every time.** The
   `draft_*` tools stage content; nothing reaches a real `.json` file
   until `publish_draft` is called, and that should only happen after a
   human has actually seen the draft and said yes — in whatever
   conversation is driving the MCP client. This is enforced by the tool
   descriptions, not a technical lock (MCP has no native pause-for-human
   primitive).
4. **Empty states are honest, not padded.** If a page has nothing real to
   show (Archive, Press, Wishlist, Talks with no entries yet), it says so
   plainly. Never fill an empty page with invented placeholder content to
   avoid it looking sparse.
5. **A Roadmap/Talks/Press entry never reveals exploitable details** about
   a private/PIN-gated system's current security posture. If a real
   finding is sensitive, note that it exists without the specifics that
   would help someone exploit it.

## How to add a new page

1. Copy the shape of an existing simple page (e.g. `now.html`) — nav-slot/
   footer-slot placeholders, a `<section class="hero">`, then content.
2. If it needs live data, add a backend endpoint (`main.py`) and fetch it
   client-side the same way every other page does (see any of
   `wishlist.html`/`talks.html`/`uptime.html` for the pattern — fetch,
   build DOM nodes, never `innerHTML`).
3. Add a link in `frontend/public/partials/nav.html` — decide whether it
   belongs in the primary nav (5-6 items max before it gets unwieldy) or
   the `<details class="nav-more">` dropdown.
4. Rebuild: `docker compose up -d --build`.

## How to add a new real project to the grid

Don't hand-edit `projects.json` ad hoc — follow the `*-content-refresh`
skill's actual process (checking the repo is public, has real README
content, isn't already stale/removed elsewhere). It exists specifically so
this doesn't drift into "add whatever seems relevant."

## How to add a new MCP-writable content type (beyond wishlist/talks/press/blog/ideas)

1. Add `<name>.json` (empty array) to `backend/`.
2. Add `GET /api/<name>` to `main.py` using the existing `_load_json_list`
   helper — don't write a new loader from scratch.
3. Add a `draft_<name>` tool to `mcp-server/server.py`, following the exact
   shape of the existing `draft_*` tools (stage via `_stage`, never write
   directly) — `publish_draft`/`discard_draft`/`list_pending_drafts` are
   already generic across all kinds, no changes needed there.
4. Build the frontend page the same way as `wishlist.html`/`talks.html`.

## Verification checklist before calling any change here "done"

- [ ] `grep -rn "innerHTML" frontend/public/` returns nothing new
- [ ] `docker compose up -d --build` succeeds, both containers show `Up`
- [ ] The actual endpoint/page was hit with `curl` (or a real browser) —
      a successful build is not the same as a working feature
- [ ] If `projects.json` changed: every entry's repo is confirmed public
      (`gh api repos/<owner>/<repo>` returns 200, not 404/private)
- [ ] If an MCP tool changed: tested by calling it directly as a plain
      Python function first (`python -c "import server; ..."`), not just
      assumed correct from reading the code
