# ohermes-hub

Public project index — intended to eventually become the root page at
`ohermes.duckdns.org`, replacing what's currently DXRP docs there (DXRP docs
moves to `/docs`, not removed).

**Status: local testing only.** Not wired into the real `custom-domains`
Caddyfile yet. Nothing here touches production until it's been reviewed and
explicitly approved.

## Test it locally

```
docker compose up -d --build
```

Then open **http://localhost:8500/**.

## What's on it

- **Project grid** — every public (non-private) repo under
  `github.com/THEROCKSSS` that has real content to describe, pulled live
  from GitHub's API (star count, last-pushed date) with a 10-minute cache.
  Search + tag filter, both client-side.
- **"Now building"** — whichever listed repo was pushed to most recently.
- **Changelog** — recent commits across every listed repo, live from GitHub,
  plus an RSS feed at `/api/changelog.rss`.
- **Ideas board** — deliberately empty right now. This board only ever lists
  ideas once they're posted on GitHub — nothing fabricated, nothing queued
  that isn't real yet.
- **Hidden footer link** — a small unlabeled `·` in the footer that goes
  straight to personal-docker-umbrella's PIN page, on its own port (umbrella
  services need their own port rather than a sub-path — their login/unlock
  routes are hardcoded absolute paths at their own root, same reason
  `movie-list-gate` needs its own port). The link's target is set client-side
  based on whatever hostname the page is currently being viewed from, so it
  resolves correctly whether you're on localhost, the Tailscale IP, or
  eventually `ohermes.duckdns.org`.
- **Grid controls** — sort (recent/stars/alphabetical), random-project jump,
  compact/card view toggle, per-card commit sparkline (13-week, live), license
  and open-issues badges, language-color dot, "similar projects" cross-links.
- **Project detail pages** (`/project.html?repo=...`) — full README, shown as
  plain text (never markdown-rendered) so repo content can never inject HTML.
- **16 additional pages**, reachable from the nav's primary tabs (Projects,
  Changelog, Ideas, Now, Blog, Stack) or the "More" dropdown (Timeline,
  Year in Review, Roadmap, Archive, Uptime, API Docs, Credits, License,
  Wishlist, Talks, Press, Tools, Contact) — real/live data where available,
  honest empty states everywhere else (Archive, Press, Tools, Wishlist,
  Talks, Roadmap have nothing fabricated in them, by design).
- **`/uptime`** — real health checks (not just port pings — actual HTTP
  requests) against the other self-hosted services on this machine.
- **A real blog post** — a genuine account of tonight's DNS-01 Caddy fix,
  not filler.

## Curating the project list

Edit `backend/projects.json`. Each entry needs `repo`, `owner`, `name`,
`description`, and `tags`. **Only add a repo here if it's already public on
GitHub** — this is a hard rule, not a style preference. Descriptions should
be grounded in the repo's actual README/content, not invented.

## Architecture

- `frontend/public/` — static HTML/CSS/vanilla JS, served by nginx. No build
  step, no framework. All API-sourced content is rendered via
  `textContent`/`createElement`, never `innerHTML`, to stay safe against a
  compromised or malicious repo description reaching the page unsanitized.
  `partials/nav.html` and `partials/footer.html` are fetched and injected by
  `js/partials.js` on every page — one source of truth for the nav instead
  of duplicating it across ~19 pages.
- `backend/` — a tiny FastAPI service that proxies and caches GitHub's
  public, **unauthenticated** API (no token needed or stored anywhere —
  keeps the attack surface small on a public-facing site). 10-minute cache
  on project/changelog data, 60-second cache on uptime checks.

## Before this goes to production

1. You test it locally and say it's good.
2. `custom-domains/Caddyfile`'s `ohermes.duckdns.org:8443` root block gets
   pointed at this hub instead of `dxrp-docs`, and a new `/docs` route gets
   added pointing at `dxrp-docs` (already-working DNS-01 cert covers this —
   no new cert work needed, see the `caddy-dns-duck` skill).
3. Re-verify the secret-entry footer link, `/docs`, and `/forgejo/` all
   still resolve correctly once real Caddy is in the chain instead of this
   project's own local nginx.
