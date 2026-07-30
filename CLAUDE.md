# CLAUDE.md — ohermes-hub

Tool/environment-specific notes only. For what this is and how it's built,
see `README.md`, `ARCHITECTURE.md`, `AGENTS.md` — this file doesn't repeat
them.

## Local commands

```bash
docker compose up -d --build      # rebuild + start both services
docker compose restart hub-api    # clear in-memory caches without a full rebuild
curl -s http://localhost:8500/api/projects   # sanity check after any backend change
```

## Real gotchas already hit in this environment

- **GitHub's unauthenticated rate limit (60 req/hr per IP) is shared across
  everything hitting `api.github.com` from this machine** — heavy testing
  (curl loops, browser automation, rebuilding a scratch copy of this repo)
  can exhaust it within an hour. If `/api/projects` suddenly shows
  `"live_data_available": false` with no other change, check
  `curl -s https://api.github.com/rate_limit` before assuming a code bug.
- **`docker-compose.yml` binds `127.0.0.1:8500`, not `0.0.0.0`** —
  deliberate (loopback-only until you decide to expose it further). Don't
  "fix" this to `0.0.0.0` without checking whether that's actually wanted.
- **Camofox browser automation (if used for verification) has been flaky**
  in this environment — tabs occasionally die mid-session and viewport
  resizing hasn't reliably taken effect. If a browser check fails
  unexpectedly, retry with a fresh tab before assuming the site itself is
  broken.
- **No CHANGELOG.md yet** — this repo has no git commit history at the
  time these docs were written (`git log` returns "no commits yet" on
  `master`). Generate one from real `git log` output once real commits
  exist; don't hand-write history that isn't there.

## Skills that apply directly to this repo

`skills/backend-provider-setup`, `skills/frontend-webpage-setup`,
`skills/full-stack-setup`, `skills/content-refresh` — plus the three MCP-
backed logger skills registered globally (`ohermes-wishlist-logger`,
`ohermes-talks-logger`, `ohermes-press-logger` under `~/.claude/skills/`).
See `AGENTS.md`'s hard rules before touching any content those skills manage.
