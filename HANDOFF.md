# HANDOFF — ohermes-hub

## Current state (2026-07-30)

### Just completed: public-IP redaction in the blog

The first (and currently only) blog post, `dns01-caddy-fix`, contained the
home network's **real public IP** in a quoted Let's Encrypt error line. It
was published to the live site and pushed to the public GitHub repo.

Two separate problems were fixed in one pass:

1. **Privacy leak** — the literal IP was removed from `backend/blog.json`
   and replaced with the placeholder `<the public IP the domain resolves
   to>`.
2. **Factual error** — the post asserted that the IP was "Let's Encrypt's
   own validator." It was not. In an ACME `Timeout during connect` error,
   Let's Encrypt names **the address it tried to reach** (i.e. the domain's
   own A record), not the validator's address. The surrounding narrative,
   which reasoned about "that validator's IP range," was rewritten to match
   what the log actually said. The root-cause conclusion (inbound 80/443
   blocked upstream, DNS-01 as the fix) is unchanged and still correct.

The same misattribution was corrected in the `caddy-dns-duck` skill at
`~/.claude/skills/caddy-dns-duck/SKILL.md` (local only — that skill is not
among the 7 published under `frontend/public/skills/`).

Verified: `curl -s http://localhost:8500/api/blog` no longer contains the
IP, and serves the corrected wording. `hub-api` was rebuilt.

### Outstanding — needs an explicit decision

The IP remains readable in **public git history** on
`github.com/THEROCKSSS/ohermes-hub`, in the initial commit `a86580d`
(`backend/blog.json`). Removing it from history requires a rewrite plus a
force-push to both `origin` and `forgejo`. That has not been done — it is
destructive and outward-facing, so it is being left for Owen to approve.

Mitigating factor: the exposed address is **stale**. The connection is on a
dynamic IP and has since changed, so the published value no longer points
at this network.

### Also noted, not acted on

`.git/config` has the Forgejo push token embedded in plaintext in the
remote URL. Local-only and not pushed, but worth moving to a credential
helper or `~/.claude/.env` at some point.

## Next up

- Owen's request: harden the Docker containers so a container compromise
  does not become host access. See the hardening plan — `docker-compose.yml`
  currently runs both services as root with no capability drop, no
  `read_only`, no resource limits, and grants both `host.docker.internal`
  via `host-gateway`.
- Owen's original question (still open): an inventory of how many blog
  posts could be written from previous sessions. 41 session transcripts
  exist under `~/.claude/projects/`; only 1 session retrospective has been
  written, and `session-retrospectives/INDEX.md` was never updated with it.
