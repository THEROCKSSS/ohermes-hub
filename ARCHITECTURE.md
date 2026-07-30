# Architecture

What owns what, and how data actually flows. See `README.md` for what the
site does user-facing; `AGENTS.md` for conventions and how-to-add-X; this
file is the data-flow map neither of those owns.

## The three services

```
┌─────────────────┐      /api/*       ┌──────────────┐
│  hub-frontend    │ ────────────────▶│   hub-api    │
│  nginx + static  │                   │   FastAPI    │
│  HTML/CSS/JS     │◀──── JSON ────────│              │
└──────────────────┘                   └──────┬───────┘
        │                                      │
        │ optional sub-path proxies            │ GitHub REST API
        │ (docs, forgejo, etc. --              │ (public, unauthenticated)
        │  see nginx.conf)                     ▼
        ▼                              ┌──────────────┐
┌──────────────────┐                   │  GitHub.com  │
│ other local       │                  └──────────────┘
│ services on host   │
│ (via host.docker   │
│  .internal)         │
└──────────────────┘

┌──────────────────┐   reads/writes JSON files directly (no HTTP)
│  mcp-server/       │──────────────────────────────────┐
│  server.py          │                                   │
│  (stdio, run by     │                                   ▼
│   Claude Code)       │                          backend/*.json
└──────────────────┘                          (same files hub-api reads)
```

`hub-frontend` and `hub-api` only ever talk over the Docker Compose network
(`hub-api` has no published host port — only nginx can reach it). The MCP
server is a *third*, independent process, not part of the Docker Compose
stack at all — it's launched by Claude Code as a local subprocess (stdio
transport) and writes straight to the same JSON files `hub-api` reads from
disk. There is no HTTP path between the MCP server and the backend; they're
decoupled by sharing a filesystem, not an API.

## Data flow per content type

**Live, GitHub-sourced** (`projects.json` → `/api/projects`, `/api/changelog`,
`/api/changelog.rss`): curated JSON (repo/owner/name/description/tags, hand-
maintained) gets enriched at request time with live GitHub API data (stars,
license, open issues, commit activity, README text), cached in-memory for
10 minutes. On a failed refresh, the cache serves its last-known-good result
rather than overwriting it with an empty one — see `main.py`'s `get_projects`/
`get_changelog` for the actual logic; this was a real bug found and fixed
during development (GitHub's 60 req/hr unauthenticated rate limit is easy to
exhaust with combined testing).

**Hand-curated, MCP-writable** (`wishlist.json`, `talks.json`, `press.json`,
`blog.json`, `ideas.json` → their matching `/api/*` endpoints): plain JSON
arrays, no GitHub calls, no cache (reads are cheap local file reads). Two
write paths exist for these, both ending at the same files:
1. Manually edit the JSON file directly, restart `hub-api`.
2. The MCP server's two-phase `draft_*` / `publish_draft` tool pair (see
   `mcp-server/server.py` and its README) — `draft_*` stages an entry in
   `backend/_pending_drafts.json` (never touches the real file), and
   `publish_draft` is the only thing that appends to the real file. The
   logger skills (`skills/*-logger`) drive this second path.

**Real-time health checks** (`LOCAL_SERVICES` in `main.py` → `/api/uptime`):
actual HTTP requests (not just TCP port checks) against other local
services you list, reachable via `host.docker.internal` since `hub-api`
needs `extra_hosts: host-gateway` for this (see `docker-compose.yml`).
60-second cache — meant to feel closer to real-time than the 10-minute
GitHub-data cache.

## Frontend rendering pattern

Every page follows the same shape: static HTML shell with empty
`<div id="...-slot">` placeholders, `js/partials.js` fetches
`partials/nav.html` / `partials/footer.html` and injects them (one source
of truth for navigation instead of duplicating it across ~20 pages), then
a page-specific inline `<script>` (or `js/app.js` for the homepage) fetches
its own `/api/*` endpoint and renders the result.

**The one rule that matters most in this whole codebase**: rendering never
uses `innerHTML` on anything that came from an API response. Every dynamic
element is built with `document.createElement` + `.textContent`. This is
what makes a malicious repo description, README, or commit message
structurally incapable of injecting HTML/script into the page — there is no
call site where that content is ever parsed as markup, so there is no XSS
vector to find, not "we sanitize it" but "the render path can't do it."
Grep for `innerHTML` before merging any new page; if it appears anywhere in
`frontend/public/js/` or an inline `<script>`, that's a regression.

## Docker layout

Two Compose services (`docker-compose.yml`):
- `hub-api` — `python:3.12-slim`, no published port.
- `hub-frontend` — `nginx:alpine`, `127.0.0.1:8500:80` (loopback-only —
  deliberate; see `README.md`'s "Going beyond localhost").

`frontend/Dockerfile` copies `nginx.conf` to `/etc/nginx/conf.d/default.conf`
and `frontend/public/` to the web root — kept as two separate `COPY`
instructions (not one blanket `COPY .`) specifically because an earlier
`.dockerignore`-based attempt to exclude `Dockerfile`/`nginx.conf` from the
web root *also* hid `nginx.conf` from the Dockerfile's own explicit `COPY`
step (`.dockerignore` scopes the whole build context, not one instruction).
The current layout (`frontend/public/` as the only thing that ever gets
`COPY`'d wholesale) sidesteps that class of bug entirely.

## Known pitfalls already hit once (don't re-discover these)

- **A self-signed cert's SAN list can silently block real ACME issuance**
  for the same domain if it's deployed behind Caddy with DNS-01 — see the
  `caddy-dns-duck` skill (separate project) for the full story; not
  something this repo's own code does, but relevant if you ever put this
  hub behind a real domain.
- **GitHub's unauthenticated rate limit (60 req/hr per IP) is easy to
  exhaust** during combined curl-loop testing + browser automation +
  rebuilding from scratch in the same hour. The cache's stale-on-failure
  behavior (see above) exists specifically because this happened during
  development.
- **`docker compose down`/`up` on the whole stack can restart containers
  you'd intentionally stopped**, if this project ever shares a Compose file
  with other services (it currently doesn't, but watch for this if you add
  more services later).
