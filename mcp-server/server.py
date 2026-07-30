"""
ohermes-hub content MCP server.

Exposes tools to draft new Wishlist/Talks/Press/Blog/Ideas entries for the
hub. Every write is two-phase on purpose: draft_* stages an entry and
returns a draft_id; publish_draft actually writes it to the file the
backend serves. This mirrors the same confirm-before-publish rule already
used by the wishlist/talks/press logger skills -- an MCP tool has no
built-in way to pause and wait for a human, so the enforcement is
behavioral: every draft_* and publish_draft tool description below
instructs the calling agent explicitly, and publish_draft must never be
called immediately after draft_* without the human actually seeing the
draft and confirming it first.

Deliberately does NOT expose an "add_project" or "add_tool" tool. Projects
are governed by the stricter GitHub-first rule (see the content-refresh
skill) -- only real, already-public GitHub repos belong there, and that
curation judgment call shouldn't be something an MCP tool call can bypass.

Configuration: set OHERMES_HUB_DATA_DIR to the backend/ directory containing
wishlist.json, talks.json, press.json, blog.json, ideas.json. Defaults to
../backend relative to this file, which is correct for this repo's own
layout.
"""

import json
import os
import uuid
from datetime import date
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DATA_DIR = Path(os.environ.get("OHERMES_HUB_DATA_DIR", Path(__file__).parent.parent / "backend"))
PENDING_FILE = DATA_DIR / "_pending_drafts.json"

FILES = {
    "wishlist": DATA_DIR / "wishlist.json",
    "talk": DATA_DIR / "talks.json",
    "press": DATA_DIR / "press.json",
    "blog": DATA_DIR / "blog.json",
    "idea": DATA_DIR / "ideas.json",
}

mcp = FastMCP("ohermes-hub-content")


def _load_list(path: Path) -> list:
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def _save_list(path: Path, entries: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _pending_dict() -> dict:
    if not PENDING_FILE.exists():
        return {}
    try:
        with open(PENDING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def _save_pending(pending: dict) -> None:
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(pending, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _stage(kind: str, entry: dict) -> dict:
    pending = _pending_dict()
    draft_id = uuid.uuid4().hex[:8]
    pending[draft_id] = {"kind": kind, "entry": entry}
    _save_pending(pending)
    return {"draft_id": draft_id, "kind": kind, "entry": entry,
            "next_step": "Show this draft to the user in full and get their explicit yes/no before calling publish_draft. Do not call publish_draft automatically."}


@mcp.tool()
def draft_wishlist_item(item: str, why: str, status: str = "researching", notes: str = "") -> dict:
    """Draft a Wishlist entry (a tool/hardware/software actually being
    researched with buying it as the real goal). Does NOT publish -- returns
    a draft_id. status is one of: researching, considering, bought, passed.
    Show the draft to the user and get explicit confirmation before calling
    publish_draft. Never invoke this for research that has no real purchase
    intent."""
    entry = {"date": str(date.today()), "item": item, "why": why, "status": status, "notes": notes}
    return _stage("wishlist", entry)


@mcp.tool()
def draft_talk(topic: str, summary: str, tags: list[str] | None = None) -> dict:
    """Draft a Talks entry -- a real, substantive discussion or exploration
    of an idea, model, or technology that just happened (not a passing
    mention). Does NOT publish -- returns a draft_id. Show the draft to the
    user and get explicit confirmation before calling publish_draft."""
    entry = {"date": str(date.today()), "topic": topic, "summary": summary, "tags": tags or []}
    return _stage("talk", entry)


@mcp.tool()
def draft_press_post(title: str, summary: str, body: str) -> dict:
    """Draft a Press entry -- results from a model test or workflow
    experiment that has actually concluded. body is plain text (paragraph
    breaks as blank lines); never markdown or HTML, since the page renders
    it as plain text on purpose. Does NOT publish -- returns a draft_id.
    Show the FULL draft to the user and get explicit confirmation before
    calling publish_draft. This is the most public-facing of the content
    types -- do not skip the confirmation step for any reason."""
    entry = {"date": str(date.today()), "title": title, "summary": summary, "body": body}
    return _stage("press", entry)


@mcp.tool()
def draft_blog_post(title: str, summary: str, body: str, slug: str | None = None) -> dict:
    """Draft a Blog entry -- a longer write-up about a specific build or
    fix. body is plain text (paragraph breaks as blank lines). slug is
    optional; auto-generated from the title if omitted. Does NOT publish --
    returns a draft_id. Show the draft to the user and get explicit
    confirmation before calling publish_draft."""
    if not slug:
        slug = "".join(c.lower() if c.isalnum() else "-" for c in title).strip("-")
        while "--" in slug:
            slug = slug.replace("--", "-")
    entry = {"date": str(date.today()), "slug": slug, "title": title, "summary": summary, "body": body}
    return _stage("blog", entry)


@mcp.tool()
def draft_idea(name: str, description: str) -> dict:
    """Draft an Ideas-board entry -- something being considered but not yet
    built, shown clearly separated from the real shipped-project grid.
    This is NOT for real projects (those need to already be public on
    GitHub and go through the content-refresh skill instead) -- only for
    genuine not-yet-real ideas. Does NOT publish -- returns a draft_id. Show
    the draft to the user and get explicit confirmation before calling
    publish_draft."""
    entry = {"name": name, "description": description}
    return _stage("idea", entry)


@mcp.tool()
def list_pending_drafts() -> list:
    """List every drafted entry awaiting human confirmation, across all
    content types. Use this to check what's queued before publishing or
    discarding."""
    pending = _pending_dict()
    return [{"draft_id": k, **v} for k, v in pending.items()]


@mcp.tool()
def publish_draft(draft_id: str) -> dict:
    """Publish a previously-drafted entry to the live site. ONLY call this
    after the human has explicitly confirmed, in this conversation, that
    they want this specific draft published. Never call this immediately
    after draft_* without that confirmation actually happening."""
    pending = _pending_dict()
    staged = pending.get(draft_id)
    if not staged:
        return {"error": f"No pending draft with id {draft_id}. Call list_pending_drafts to see what's queued."}

    kind = staged["kind"]
    entry = staged["entry"]
    path = FILES[kind]
    entries = _load_list(path)
    entries.append(entry)
    _save_list(path, entries)

    del pending[draft_id]
    _save_pending(pending)

    return {"published": True, "kind": kind, "entry": entry,
            "note": "Rebuild/restart hub-api (docker compose restart hub-api) for the change to show up if the backend caches this content type."}


@mcp.tool()
def discard_draft(draft_id: str) -> dict:
    """Discard a pending draft without publishing it."""
    pending = _pending_dict()
    if draft_id not in pending:
        return {"error": f"No pending draft with id {draft_id}."}
    del pending[draft_id]
    _save_pending(pending)
    return {"discarded": draft_id}


if __name__ == "__main__":
    mcp.run(transport="stdio")
