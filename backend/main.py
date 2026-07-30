import base64
import json
import time
from pathlib import Path

import httpx
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

PROJECTS_FILE = Path(__file__).parent / "projects.json"
WISHLIST_FILE = Path(__file__).parent / "wishlist.json"
TALKS_FILE = Path(__file__).parent / "talks.json"
PRESS_FILE = Path(__file__).parent / "press.json"
BLOG_FILE = Path(__file__).parent / "blog.json"
IDEAS_FILE = Path(__file__).parent / "ideas.json"
CACHE_TTL_SECONDS = 600  # 10 minutes -- keeps us well under GitHub's
                          # unauthenticated 60 req/hr rate limit even on
                          # repeated page loads.
GITHUB_API = "https://api.github.com"

# Known local services this hub fronts or sits alongside, for the real
# uptime/health check -- reachable via host.docker.internal since this
# container needs host-gateway access (see docker-compose.yml).
LOCAL_SERVICES = [
    {"name": "movie-list-gate", "url": "http://host.docker.internal:8199/login"},
    {"name": "movie-list-api-gate", "url": "http://host.docker.internal:8124/"},
    {"name": "forgejo", "url": "http://host.docker.internal:3000/"},
    {"name": "dxrp-docs", "url": "http://host.docker.internal:8099/"},
    {"name": "personal-docker-umbrella", "url": "http://host.docker.internal:8108/"},
]

app = FastAPI(title="ohermes-hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],  # same-origin only; frontend is served by the same nginx
    allow_methods=["GET"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


_cache = {
    "projects": None, "projects_ts": 0,
    "changelog": None, "changelog_ts": 0,
    "uptime": None, "uptime_ts": 0,
    "readme": {},  # repo -> (result_dict, timestamp)
}
UPTIME_CACHE_TTL = 60  # uptime should feel closer to real-time than the 10-min project cache
DEGRADED_RETRY_SECONDS = 30  # if a refresh comes back fully empty (e.g. rate-limited),
                              # retry soon instead of waiting the full cache TTL
README_CACHE_TTL = 3600  # READMEs change rarely; also gives resilience during a
                          # GitHub rate-limit window, same reasoning as /api/projects


def load_curated_projects():
    with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


async def fetch_repo_live_data(client: httpx.AsyncClient, owner: str, repo: str):
    """Best-effort live enrichment. Returns None on any failure so the caller
    can fall back to curated-only data instead of breaking the whole page."""
    try:
        resp = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}", timeout=5.0)
        if resp.status_code != 200:
            return None
        data = resp.json()
        license_info = data.get("license") or {}
        return {
            "stars": data.get("stargazers_count", 0),
            "pushed_at": data.get("pushed_at"),
            "created_at": data.get("created_at"),
            "html_url": data.get("html_url"),
            "language": data.get("language"),
            "open_issues": data.get("open_issues_count", 0),
            "license": license_info.get("spdx_id"),  # None / "NOASSERTION" / "MIT" / etc.
        }
    except httpx.HTTPError:
        return None


async def fetch_commit_sparkline(client: httpx.AsyncClient, owner: str, repo: str):
    """Weekly commit counts for the last ~90 days (last 13 weeks of GitHub's
    52-week stats/commit_activity). Returns [] if GitHub hasn't cached stats
    for this repo yet (202) or on any failure -- never breaks the page."""
    try:
        resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/stats/commit_activity", timeout=5.0
        )
        if resp.status_code != 200:
            return []
        weeks = resp.json()
        if not isinstance(weeks, list):
            return []
        return [w.get("total", 0) for w in weeks[-13:]]
    except httpx.HTTPError:
        return []


@app.get("/api/projects")
async def get_projects():
    now = time.time()
    if _cache["projects"] is not None and (now - _cache["projects_ts"]) < CACHE_TTL_SECONDS:
        return _cache["projects"]

    curated = load_curated_projects()
    enriched = []
    live_data_available = False

    async with httpx.AsyncClient(headers={"Accept": "application/vnd.github+json"}) as client:
        for entry in curated:
            live = await fetch_repo_live_data(client, entry["owner"], entry["repo"])
            item = dict(entry)
            if live:
                live_data_available = True
                item["stars"] = live["stars"]
                item["pushed_at"] = live["pushed_at"]
                item["created_at"] = live["created_at"]
                item["github_url"] = live["html_url"]
                item["open_issues"] = live["open_issues"]
                item["license"] = live["license"]
                item["live"] = True
                item["sparkline"] = await fetch_commit_sparkline(client, entry["owner"], entry["repo"])
            else:
                item["stars"] = None
                item["pushed_at"] = None
                item["created_at"] = None
                item["github_url"] = f"https://github.com/{entry['owner']}/{entry['repo']}"
                item["open_issues"] = None
                item["license"] = None
                item["live"] = False
                item["sparkline"] = []
            enriched.append(item)

    if live_data_available:
        enriched.sort(key=lambda x: x["pushed_at"] or "", reverse=True)

    result = {
        "generated_at": int(now),
        "live_data_available": live_data_available,
        "projects": enriched,
    }

    if not live_data_available:
        # Every single live fetch failed this round (most likely GitHub's
        # rate limit, or a cold-start race right after container startup).
        # If we have a prior good snapshot, keep serving it instead of
        # clobbering it with an all-empty result. Either way, retry soon
        # rather than waiting out the full cache TTL -- this state should
        # self-heal once the rate limit window resets or the race clears.
        if _cache["projects"] is None:
            _cache["projects"] = result
        _cache["projects_ts"] = now - CACHE_TTL_SECONDS + DEGRADED_RETRY_SECONDS
        return _cache["projects"]

    _cache["projects"] = result
    _cache["projects_ts"] = now
    return result


@app.get("/api/projects/{repo}/readme")
async def get_project_readme(repo: str):
    """Raw README text for a curated repo, proxied server-side so the
    frontend never needs its own GitHub calls. Displayed as plain text on
    the client (not markdown-rendered) -- deliberately, to avoid any HTML
    injection risk from repo content."""
    curated = load_curated_projects()
    match = next((p for p in curated if p["repo"] == repo), None)
    if not match:
        return Response(status_code=404, content="Unknown project")

    now = time.time()
    cached = _cache["readme"].get(repo)
    if cached and (now - cached[1]) < README_CACHE_TTL:
        return cached[0]

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GITHUB_API}/repos/{match['owner']}/{match['repo']}/readme",
                headers={"Accept": "application/vnd.github+json"},
                timeout=5.0,
            )
            if resp.status_code != 200:
                # Serve a stale-but-real cached README over a fresh "unavailable"
                # if we have one -- same reasoning as /api/projects.
                if cached:
                    return cached[0]
                return {"available": False, "content": ""}
            data = resp.json()
            content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
            result = {"available": True, "content": content}
            _cache["readme"][repo] = (result, now)
            return result
    except httpx.HTTPError:
        if cached:
            return cached[0]
        return {"available": False, "content": ""}


async def fetch_changelog_entries():
    curated = load_curated_projects()
    entries = []
    async with httpx.AsyncClient(headers={"Accept": "application/vnd.github+json"}) as client:
        for entry in curated:
            try:
                resp = await client.get(
                    f"{GITHUB_API}/repos/{entry['owner']}/{entry['repo']}/commits",
                    params={"per_page": 3},
                    timeout=5.0,
                )
                if resp.status_code != 200:
                    continue
                for commit in resp.json():
                    entries.append({
                        "repo": entry["name"],
                        "repo_url": f"https://github.com/{entry['owner']}/{entry['repo']}",
                        "message": commit["commit"]["message"].split("\n")[0][:200],
                        "date": commit["commit"]["author"]["date"],
                        "sha": commit["sha"][:7],
                        "commit_url": commit["html_url"],
                    })
            except (httpx.HTTPError, KeyError, TypeError):
                continue
    entries.sort(key=lambda x: x["date"], reverse=True)
    return entries[:30]


@app.get("/api/changelog")
async def get_changelog():
    now = time.time()
    if _cache["changelog"] is not None and (now - _cache["changelog_ts"]) < CACHE_TTL_SECONDS:
        return _cache["changelog"]

    entries = await fetch_changelog_entries()
    if not entries:
        # Same reasoning as /api/projects: an empty refresh (rate limit,
        # transient GitHub failure, or a cold-start race) shouldn't blank
        # out a previously good feed, and shouldn't poison a cold cache
        # for the full TTL either -- retry soon either way.
        if _cache["changelog"] is None:
            _cache["changelog"] = {"generated_at": int(now), "live": False, "entries": []}
        _cache["changelog_ts"] = now - CACHE_TTL_SECONDS + DEGRADED_RETRY_SECONDS
        return _cache["changelog"]

    result = {"generated_at": int(now), "live": True, "entries": entries}
    _cache["changelog"] = result
    _cache["changelog_ts"] = now
    return result


@app.get("/api/changelog.rss")
async def get_changelog_rss():
    # Reuses get_changelog()'s own cache + stale-on-failure logic instead of
    # duplicating the fetch here (duplicating it was a real bug: this used
    # to independently overwrite the shared cache with its own fetch,
    # bypassing the "don't clobber good data with an empty refresh" fix above).
    data = await get_changelog()
    entries = data["entries"]

    items = []
    for e in entries:
        title = _xml_escape(f"{e['repo']}: {e['message']}")
        link = _xml_escape(e["commit_url"])
        items.append(
            f"<item><title>{title}</title><link>{link}</link>"
            f"<guid>{link}</guid><pubDate>{e['date']}</pubDate></item>"
        )

    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel>'
        "<title>ohermes.duckdns.org — Changelog</title>"
        "<link>https://ohermes.duckdns.org/</link>"
        "<description>Recent commits across active projects</description>"
        + "".join(items)
        + "</channel></rss>"
    )
    return Response(content=rss, media_type="application/rss+xml")


def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


async def check_service(client: httpx.AsyncClient, service: dict):
    start = time.time()
    try:
        resp = await client.get(service["url"], timeout=4.0, follow_redirects=True)
        ok = resp.status_code < 500  # a login/redirect page (2xx/3xx/401/403) still means "up"
        return {"name": service["name"], "up": ok, "status_code": resp.status_code,
                "latency_ms": round((time.time() - start) * 1000)}
    except httpx.HTTPError:
        return {"name": service["name"], "up": False, "status_code": None,
                "latency_ms": None}


@app.get("/api/uptime")
async def get_uptime():
    now = time.time()
    if _cache["uptime"] is not None and (now - _cache["uptime_ts"]) < UPTIME_CACHE_TTL:
        return _cache["uptime"]

    async with httpx.AsyncClient() as client:
        results = [await check_service(client, s) for s in LOCAL_SERVICES]

    result = {"generated_at": int(now), "services": results}
    _cache["uptime"] = result
    _cache["uptime_ts"] = now
    return result


@app.get("/api/status")
async def get_status():
    return {"ok": True, "time": int(time.time())}


@app.get("/api/health")
async def get_health():
    """Machine-readable status for external uptime monitors -- distinct
    from /api/uptime, which reports on the *other* local services this hub
    links to; this one reports on the hub itself."""
    return {
        "ok": True,
        "service": "ohermes-hub",
        "time": int(time.time()),
        "projects_cache_age_s": int(time.time() - _cache["projects_ts"]) if _cache["projects_ts"] else None,
    }


def _load_json_list(path: Path):
    """Wishlist/talks/press are all hand-edited local JSON, not GitHub-sourced
    -- no live enrichment, no cache needed, just read the file. Newest first."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        entries = []
    return sorted(entries, key=lambda e: e.get("date", ""), reverse=True)


@app.get("/api/wishlist")
async def get_wishlist():
    return {"entries": _load_json_list(WISHLIST_FILE)}


@app.get("/api/talks")
async def get_talks():
    return {"entries": _load_json_list(TALKS_FILE)}


@app.get("/api/press")
async def get_press():
    return {"entries": _load_json_list(PRESS_FILE)}


@app.get("/api/blog")
async def get_blog():
    return {"entries": _load_json_list(BLOG_FILE)}


@app.get("/api/blog/{slug}")
async def get_blog_post(slug: str):
    entries = _load_json_list(BLOG_FILE)
    match = next((e for e in entries if e.get("slug") == slug), None)
    if not match:
        return Response(status_code=404, content="Unknown post")
    return match


@app.get("/api/ideas")
async def get_ideas():
    return {"entries": _load_json_list(IDEAS_FILE)}
