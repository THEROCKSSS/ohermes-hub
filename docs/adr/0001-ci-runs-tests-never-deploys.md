# CI runs tests, never deploys

Phase 6 adds GitHub Actions to run the test suite and build both Docker
images on every push and PR, but deliberately stops there: deployment stays
a manual `docker compose up -d --build` on Owen's own machine. The hub runs
on self-hosted hardware behind Caddy and Tailscale with no registry and no
inbound path a runner could reach, so "deploy" here means touching a
personal machine — worth keeping as an explicit human action rather than
something a merge can trigger.

## Consequences

A green CI run means the code is sound, not that the live site has changed;
the two can drift until someone deploys. That gap is accepted, and is why
the deploy step is documented in `CLAUDE.md` rather than automated away.
Revisit if the hub ever moves to hosting a runner could actually reach.
