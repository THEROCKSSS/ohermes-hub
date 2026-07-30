---
name: ohermes-hub-backend-provider-setup
description: "Build the data-provider backend (hub-api) for an ohermes-hub-style project hub -- a small FastAPI service that pulls, caches, and serves your public GitHub repo data. Local-only setup, no domain/Tailscale/DuckDNS required. Use when you want your own project-index site's backend, or want to understand how the live GitHub-data layer works before touching the frontend."
---

# ohermes-hub: backend / provider setup

This builds the **data provider** — a tiny FastAPI service that reads a
curated list of your own public GitHub repos, enriches it with live data
(stars, license, open issues, commit activity) from GitHub's public API, and
serves it as JSON for a frontend to consume. No GitHub token required, no
paid API, no auth of any kind. Purely local — this skill does not touch
Tailscale, DuckDNS, or any real domain.

## What you end up with

A container (or a plain `uvicorn` process) listening on port 8000 with these
endpoints:

- `GET /api/projects` — your curated repo list + live GitHub enrichment
- `GET /api/projects/{repo}/readme` — raw README text for one repo
- `GET /api/changelog` — recent commits across all your repos
- `GET /api/changelog.rss` — the same, as an RSS feed
- `GET /api/uptime` — real HTTP health checks against other local services you name
- `GET /api/health` / `GET /api/status` — liveness checks for the provider itself

## 1. Curate your project list

Create `projects.json` — one entry per public GitHub repo you want to show.
**Only list repos that are already public on GitHub.** Don't invent
descriptions; base them on the repo's actual README.

```json
[
  {
    "repo": "my-repo-name",
    "owner": "your-github-username",
    "name": "Display Name",
    "description": "One honest sentence about what it actually does.",
    "tags": ["Python", "cli-tool"]
  }
]
```

## 2. The provider itself

`main.py` — a FastAPI app. The core pattern worth understanding, not just
copying:

- **Use GitHub's public, unauthenticated REST API** (`https://api.github.com`).
  No token needed for public repo data. This keeps the service's attack
  surface small (nothing to leak) and avoids needing any secret at all.
- **Cache aggressively.** GitHub's unauthenticated rate limit is 60
  requests/hour *per IP*. A 10-minute in-memory cache on `/api/projects` and
  `/api/changelog` keeps you well under that even with real visitor traffic.
  A 60-second cache is fine for `/api/uptime` since that's meant to feel
  closer to real-time.
- **Fail soft, never fail loud.** Every GitHub call should be wrapped so a
  single repo's API hiccup (rate limit, GitHub outage, a repo you deleted)
  degrades that one field to `null`/empty instead of crashing the whole
  endpoint. Nobody should see a 500 because one repo's stats endpoint
  returned a temporary 202.
- **Security headers even on an API.** Add `X-Frame-Options: DENY`,
  `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer` as
  middleware — cheap, and matters the moment this is public.
- **The commit-activity sparkline data** comes from GitHub's
  `/repos/{owner}/{repo}/stats/commit_activity` endpoint — it can return
  `202 Accepted` on the very first request for a repo GitHub hasn't cached
  stats for yet. Treat that as "no data yet," not an error.
- **README fetching should be allowlisted.** Only serve README content for
  repos actually in your curated `projects.json` — reject anything else with
  a 404. This is what stops the endpoint from becoming an open proxy for
  arbitrary GitHub repos.
- **Render nothing as HTML server-side.** This service only ever returns
  JSON, RSS-as-XML, or raw text — never generates HTML from repo content.
  That job (and the injection risk that comes with it) belongs to the
  frontend skill, which handles it by never using `innerHTML`.

`requirements.txt`:
```
fastapi==0.115.0
uvicorn[standard]==0.30.6
httpx==0.27.2
```

`Dockerfile`:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py projects.json ./
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 3. Run it standalone (no frontend needed yet)

```bash
docker build -t my-hub-backend .
docker run --rm -p 8000:8000 my-hub-backend
```

Or without Docker at all:
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 4. Verify it actually works

```bash
curl -s http://localhost:8000/api/status
curl -s http://localhost:8000/api/projects | head -c 500
```

You should see real data — actual star counts, actual `pushed_at`
timestamps — not placeholders. If `live_data_available` comes back `false`
in the `/api/projects` response, GitHub's API calls are failing (check your
network, or whether you've been rate-limited from too much testing in a
short window).

## If you want real uptime checks against your OTHER local services

Add an `extra_hosts: ["host.docker.internal:host-gateway"]` entry to
whatever container runs this (Docker Desktop) so it can reach services
published on your host machine, and list them in the provider's known-services
config, e.g. `http://host.docker.internal:<port>`. Each check should be a
real HTTP request (not just a TCP port check) with a short timeout (4-5s) so
one dead service doesn't stall the whole `/api/uptime` response.

## Next step

Once this is running and `curl`-verified, move to the
`ohermes-hub-frontend-webpage-setup` skill to build the page that actually
displays this data.
