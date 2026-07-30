---
name: ohermes-hub-full-stack-setup
description: "Stand up a complete ohermes-hub-style project index locally in one pass -- backend provider + frontend webpage + docker-compose, from zero to a working localhost site. Use when you want the whole thing at once instead of doing the backend and frontend skills separately, or as the reference for how the two pieces fit together."
---

# ohermes-hub: full stack, local setup

The combined walkthrough — backend provider + frontend webpage + Compose
wiring, in the order you'd actually build it. This is genuinely local-only:
by the end of this skill you have a working site at `http://localhost:8500/`
and nothing more. Making it reachable over Tailscale or a real domain is a
deliberately separate, later step — don't reach for that until this part
works and you've actually looked at the page in a browser.

If you want the deep detail behind either half, see
`ohermes-hub-backend-provider-setup` and `ohermes-hub-frontend-webpage-setup`
— this skill is the assembly instructions, those are the reference manuals.

## Directory layout

```
your-hub/
  docker-compose.yml
  backend/
    Dockerfile
    requirements.txt
    main.py
    projects.json
  frontend/
    Dockerfile
    nginx.conf
    public/
      index.html
      css/style.css
      js/app.js
      js/partials.js
      partials/nav.html
      partials/footer.html
```

## docker-compose.yml

```yaml
services:
  hub-api:
    build: ./backend
    container_name: hub-api
    restart: unless-stopped
    # No published port -- only hub-frontend talks to it, over the
    # compose network. No secrets/env vars needed if you're using GitHub's
    # public unauthenticated API.

  hub-frontend:
    build: ./frontend
    container_name: hub-frontend
    restart: unless-stopped
    ports:
      - "127.0.0.1:8500:80"   # loopback-only -- deliberate. Not reachable
                               # from your LAN, Tailscale, or the internet
                               # at this stage. That's a later, separate step.
    depends_on:
      - hub-api
```

Binding to `127.0.0.1` (not `0.0.0.0`) is the load-bearing detail here — it
keeps this test build unreachable from anywhere except the machine you're
running it on, until you've actually decided you want it exposed further.

## Build order

1. Write `backend/projects.json` with 2-3 of your own real public repos
   first — don't try to curate your entire GitHub account before you've
   even confirmed the pipeline works end to end.
2. Write `backend/main.py` (see the backend-provider-setup skill for the
   actual implementation pattern — caching, fail-soft GitHub calls, the
   README-allowlist rule).
3. `docker compose build hub-api && docker compose up -d hub-api` — get
   the provider working and `curl`-verified *before* touching the frontend
   at all. Debugging both halves at once is much harder than debugging one.
4. Write the frontend (`index.html`, `app.js`, `nginx.conf` proxying
   `/api/` to `hub-api:8000`) — see the frontend-webpage-setup skill for
   the safe-rendering pattern (never `innerHTML` on API data).
5. `docker compose up -d --build` for the whole stack.

## Verification pass (do this for real, not just "it built")

```bash
docker compose ps                                    # both containers Up
curl -s http://localhost:8500/                        # 200, real HTML
curl -s http://localhost:8500/api/projects | head -c 300   # real GitHub data, not nulls
```

Then actually open `http://localhost:8500/` in a browser. A 200 status code
from curl proves nginx served *something* — it doesn't prove the page's
JavaScript ran without a console error, or that the fetch to `/api/projects`
actually resolved. Check the browser console at least once.

## A hidden/gated area, if you want one

If part of your setup should stay behind a PIN or auth gate that this
public hub deliberately doesn't advertise: run that gated service on its
own port (not a sub-path of this hub — if the gated app's own login/logout
routes are hardcoded to its own root, as most simple auth-gate setups are,
mounting it at a sub-path breaks its redirects). Then link to it from
somewhere unobtrusive (a small unlabeled footer glyph, for instance) with
the href set client-side based on the current hostname, so the link
resolves correctly whether you're testing on `localhost`, your LAN IP, or
eventually a real domain — one piece of code, no hardcoded hostname to
update later:

```js
const link = document.getElementById("secret-entry");
const GATED_SERVICE_PORT = 8108; // whatever port your gated service publishes
link.href = `${location.protocol}//${location.hostname}:${GATED_SERVICE_PORT}/`;
```

## What this skill deliberately does NOT cover

- Getting a real TLS certificate (that's a Caddy + DNS-01 problem — see the
  `caddy-dns-duck` skill if you have one, or research DNS-01 challenges
  separately)
- Exposing this over Tailscale (`tailscale serve`) or the public internet
  (`tailscale funnel`, or a router port-forward) — deliberately out of
  scope here. Get it right on `localhost` first.
- Picking a real domain / dynamic DNS provider

Those are all real, separate pieces of work — folding them in here would
make "did my local setup actually work" much harder to answer cleanly.
