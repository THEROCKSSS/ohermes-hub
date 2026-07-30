# ohermes-hub — implementation roadmap

Written from a full page-by-page screenshot audit (2026-07-30) of every
route on the live site, cross-checked against `/api/*` responses and the
actual DOM. Distinct from `FEATURE_IDEAS.md` (the 100-item brainstorm,
nothing scheduled) and `roadmap.html` (the public-facing, hand-written
summary) — this is the concrete, phased build plan those feed into.

Ordered by risk/impact: fix what's actively wrong before adding what's new.

## Phase 0 — Bugs found and fixed this session

Already shipped, listed here for the record:

1. **Tools page linked a now-private repo.** `tools.html` hardcodes its
   three cards separately from `projects.json`; it still linked
   `github.com/THEROCKSSS/VRCATAPI` after that repo went private in the
   GitHub visibility sweep earlier today. Card removed.
2. **Mobile search box rendered 260px tall.** `#search { flex: 1 1 260px }`
   sets a *horizontal* flex-basis for the desktop row layout. Once
   `section.controls` switches to `flex-direction: column` under
   `@media (max-width: 640px)`, that same `260px` becomes a *height*
   instead — the search input ballooned into a quarter of the page with a
   huge dead-space gap above the project grid. Fixed with a mobile-only
   `flex-basis: auto` override.
3. **A cold cache poisons live data for the full 10-minute TTL.**
   `/api/projects` and `/api/changelog` already had a "keep serving the
   last known-good snapshot" fallback for when a refresh fails — but only
   once a good snapshot existed. On a fresh container start (no prior
   cache yet), a single transient GitHub failure — rate limit, or just a
   slow network moment — got cached as the empty/degraded result for the
   *entire* 10 minutes, with no faster retry. Reproduced live twice during
   this session's container rebuilds. Fixed: a cold-start failure now
   retries in 30s instead of 600s, matching the already-correct behavior
   for a warm cache.
4. **Blog page was tagged `LIVE DATA`.** It's hand-written content from a
   static `blog.json`, same as Talks/Wishlist/Roadmap/Stack/Tools — all of
   which correctly say `NON-LIVE DATA`. Blog was the one inconsistent
   page. Relabeled.
5. **`projects.json` was stale after the GitHub privacy sweep** — synced
   to the 4 repos still public, `self-hosted-project-hub` added.
6. **Mobile nav tap targets** — nav links and the "More" toggle now render
   as real button-shaped tap targets instead of bare crammed text (carried
   over from an already-completed but uncommitted change, committed this
   session).

## Phase 1 — Reliability hardening (do next, before anything visual)

The rate-limit fragility above is a symptom of a bigger gap: this hub is
one bad GitHub API window away from silently degrading in front of a real
visitor.

1. **Move to an authenticated GitHub token for the backend.** The
   unauthenticated 60 req/hr limit was fully exhausted *by this session's
   own testing* — normal dev iteration, not attack traffic. A
   fine-grained read-only PAT (public-repo metadata scope only, stored the
   same way the `claude-code` Forgejo token is — `.env`, never committed)
   raises this to 5,000 req/hr and removes the fragility entirely. Keep
   the existing "no token, small attack surface" comment in the README
   honest by noting the tradeoff explicitly if this is adopted.
2. **Per-repo stale-fallback, not just per-page.** Today, if 3 of 4 repos'
   GitHub calls succeed and 1 fails, that one repo's card goes fully null
   (`live: false`, no stars/dates/license) even though the *page* overall
   reports `live_data_available: true`. Cache last-known-good per repo
   (keyed by `owner/repo`) instead of only caching the whole response, so
   one flaky repo doesn't blank its own card.
3. **Fix content drift**: Smart Bulb Dashboard's card description says
   "97 features"; its own README says "159 working features." The
   `skills.html` copy for `ohermes-hub-content-refresh` still says
   "this hub's real 13-project list" (it's 4 now). Both are exactly the
   kind of staleness the hub's own philosophy ("nothing fabricated") is
   built to avoid — worth a pass now that they've been spotted.

## Phase 2 — Real uptime history (the flagship ask)

Today's `/uptime` is a live snapshot only: a green/red dot and a
millisecond figure, recomputed fresh on every page load, nothing
persisted. It cannot answer "was this down last night" or "for how long."
This phase makes it a real status page:

1. **Background poller, not request-time-only checks.** Add a lightweight
   asyncio background task in `hub-api` that hits each `LOCAL_SERVICES`
   URL on a fixed interval (e.g. 60s, matching the existing
   `UPTIME_CACHE_TTL`) and appends `{service, timestamp, up, latency_ms}`
   to a small local store.
2. **Storage: SQLite, not a new service.** A single `uptime.db` file
   (stdlib `sqlite3`, no new container) with one append-only table is
   enough at this scale and keeps the "no shared runtime between
   containers" property from `stack.html` intact. Retain e.g. 90 days,
   prune older rows on write.
3. **`/api/uptime/history?service=X&days=N`** — new endpoint returning the
   check rows for a service, plus derived stats: uptime % over 24h/7d/30d,
   longest incident, current streak.
4. **Visual: a day-segmented status bar per service** (the GitHub-status /
   UptimeRobot pattern) — one thin vertical segment per day, colored by
   that day's worst status, hoverable for exact downtime windows. Rows
   that currently show only a dot + ms gain this bar underneath.
5. **Incident list**: "down 2026-07-29 03:14–03:22 (8m)" style entries,
   derived from consecutive `up: false` rows, newest first — same honest,
   derived-not-invented data pattern the rest of the site already follows.
6. **Keep `/api/health` and `/api/status` as-is** — those are for external
   monitors hitting *this hub*, unrelated to the services-it-fronts page.
7. Once this works, `roadmap.html`'s existing "Integrations" line ("a real
   uptime-monitor backend instead of hand-rolled health checks") should be
   moved from "Under consideration" to "Shipped."

This is self-contained — no new container, no new external dependency,
consistent with everything else in `stack.html`.

## Phase 3 — Changelog depth

The changelog is real and live, but flat and uncapped-feeling:

1. Per-project filter (client-side, data's already there).
2. Group entries by day instead of one long flat list.
3. Real pagination past the current hard 30-entry cap.
4. Distinguish tagged releases from regular commits (GitHub's releases API,
   one more cached call per repo).

## Phase 4 — Visual & interaction polish

Lower risk, lower urgency than Phases 1–3, worth batching together:

1. Skeleton loading states instead of plain "Loading…" text on
   first paint (most visible on a cold cache — directly related to Phase 1).
2. Command palette (Cmd/Ctrl+K) to jump to any project/page.
3. Keyboard shortcuts (`/` to focus search, `Esc` to clear).
4. URL-persisted filters so a filtered/sorted view is shareable.

## Phase 5 — Accessibility & Forgejo integration

1. Screen-reader landmark regions (`<main>`, `<nav>`, ARIA labels) —
   currently unaudited.
2. Keyboard-only nav audit (tab order, focus rings).
3. `prefers-reduced-motion` respected for any animation added in Phase 4.
4. Now that a Forgejo mirror exists (`claude-code/ohermes-hub`), merge
   Forgejo activity into the same changelog feed per `roadmap.html`'s own
   "Integrations" line — real cross-platform activity, not just GitHub.

## Phase 6 — Testing & CI

This project currently has **zero tests and zero CI** — no `tests/` dir, no
`.github/workflows/`, nothing in `requirements.txt` beyond fastapi/uvicorn/
httpx. It's a live public service with no safety net; today's session found
three real bugs by hand that a test suite would have caught or prevented
from regressing.

1. **pytest suite over all 7 `/api/*` routes** — `/api/projects`,
   `/api/projects/{repo}/readme`, `/api/changelog`, `/api/changelog.rss`,
   `/api/uptime`, `/api/health`, `/api/status`. Contract shape + happy/sad
   paths. Generate via the `api-test-suite` skill, then review by hand.
2. **Explicit regression tests for the two cache bugs fixed in Phase 0** —
   the important one: a cold cache (no prior snapshot) plus a failing
   GitHub call must schedule a retry ~30s out, *not* poison the cache for
   the full 600s TTL. This is the bug that bit twice in one session; it
   should be impossible to reintroduce silently.
3. **Mock GitHub, don't call it.** Tests must not hit `api.github.com` —
   the unauthenticated 60 req/hr budget was exhausted by manual testing
   alone this session, and a CI run that burns it would be worse. Stub the
   httpx client so rate-limit/failure paths are directly exercisable.
4. **GitHub Actions workflow** — run the test suite and `docker compose
   build` both images on every push and PR. The build step matters
   independently: it catches Dockerfile/dependency breakage that tests
   alone won't.
5. **No auto-deploy step.** Deploy is a manual `docker compose up -d
   --build` on Owen's own hardware and stays that way — see
   `docs/adr/0001-ci-runs-tests-never-deploys.md`.

## Phase 7 — Content & Integrations

The remaining "Content & writing" and non-uptime "Integrations" items from
`FEATURE_IDEAS.md`. Most of these are about *getting more real content onto
the site automatically* rather than hand-writing it.

1. **Per-project "why I built this" blurbs**, separate from the GitHub
   description — the one thing the GitHub API genuinely can't provide.
2. **Build-log posts tied to specific commits/milestones**, extending the
   existing `blog.json` pattern.
3. **Auto cross-post new changelog entries to Forgejo issues.** Note this
   is the *opposite direction* from Phase 5's item 4 (which pulls Forgejo
   activity *into* the changelog feed) — easy to confuse, worth keeping
   straight when either is picked up.
4. **Discord webhook** posting new changelog entries to a channel.
5. **Auto-generated OG preview images per project card**, for link shares.
6. **GitHub push webhooks instead of the 10-minute poll.** Doubles as
   rate-limit relief and complements Phase 1 — near-real-time updates and
   far fewer API calls.

**Blocked on repo visibility** (do not build until/unless the underlying
repos go public again — all four went private in the 2026-07-30 sweep):

- `/vrchat` page and its live VRChat API status widget — needs `VRCATAPI`.
- TMDB "currently trending" homepage widget — needs `Cap-s-Movie-List`.
- `/gaming` page — needs `DXRULES` / `AI_SMF_CODE`.

Listing these as blocked rather than dropping them, since visibility is a
one-command change if that ever flips back.

## Phase 8 — Data & Personalization

The remaining stats and personalization items. Lower-stakes, mostly
mechanical, batchable in one pass.

1. **Combined star count** across every listed repo, and a "projects
   shipped this year" counter, in the homepage hero.
2. **Aggregate language breakdown chart** across the whole portfolio, via
   GitHub's languages API.
3. **Fork count, contributor count, and repo age** (`created_at`) badges —
   contributor count shown honestly as 1 where that's the truth.
4. **Font-size adjuster and high-contrast toggle.** Accessibility-adjacent
   to Phase 5, but these are user-facing *controls* rather than semantic
   markup — kept here deliberately so Phase 5 stays a focused a11y pass.
5. **Live GitHub rate-limit-remaining indicator.** Directly motivated by
   burning through the full 60 req/hr budget during this session's testing
   with no visibility into it until things silently degraded. Most useful
   before Phase 1's token work lands, and still useful after.
6. **"Hub last updated" note** — meta, but honest.

---

## Suggested working order

The phase numbers are filing order, not priority. Issues #2–#6 were already
filed before Phase 6 was identified, and renumbering live issues for
cosmetics isn't worth it. Recommended actual order:

1. **Phase 1** (reliability) — the hub is one bad GitHub window from
   degrading in front of a visitor.
2. **Phase 6** (testing & CI) — lock in Phase 0's and Phase 1's fixes
   before building anything new on top of them.
3. **Phase 2** (uptime history) — the flagship feature ask.
4. **Phases 3, 4, 5, 7, 8** — in whatever order suits; no hard
   dependencies between them.

---

Nothing past Phase 0 is built yet. Say which phase (or which numbered item
inside one) to start on and that's what gets built — same rule as
`FEATURE_IDEAS.md`.
