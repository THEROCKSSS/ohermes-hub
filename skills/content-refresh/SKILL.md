---
name: ohermes-hub-content-refresh
description: "Keep an ohermes-hub-style project index's curated content current -- check for new public repos to add, stale/removed repos to drop, and outdated descriptions to rewrite. Use periodically, or whenever new projects get pushed to GitHub and should show up on the hub."
---

# ohermes-hub: content refresh

`backend/projects.json` is hand-curated on purpose (see the hard rule below)
— it doesn't auto-discover repos, so it drifts out of date as new things get
built and pushed. This skill is the periodic maintenance pass that catches
that drift.

## The hard rule, unchanged from how this project started

**Never add a repo to `projects.json` unless it's already public on
GitHub.** If a new project isn't posted yet, it doesn't go on the hub —
full stop, no exceptions without explicit sign-off from whoever owns the
site. This is true for every step below.

## 1. Check for new public repos not yet listed

```bash
gh repo list <your-username> --limit 100 --json name,description,isPrivate,updatedAt \
  --jq '.[] | select(.isPrivate == false) | .name'
```

Diff that list against the `repo` field of every entry in `projects.json`.
Anything public and missing is a candidate to add.

## 2. For each new candidate, check it actually has something to say

Don't add a repo just because it exists — check it has real content first:

```bash
gh api "repos/<owner>/<repo>/readme" --jq '.content' | base64 -d | head -c 500
gh api "repos/<owner>/<repo>/contents/" --jq '.[].name'
```

If the README is empty/near-empty and the file listing is just
`.gitignore`/`LICENSE`/nothing substantive, it's not ready to list — same
judgment call made when this hub was first built (several repos were
deliberately left off for exactly this reason). Skip it, don't force a
description out of nothing.

## 3. Write the description from the actual README, not the GitHub one-liner

GitHub's repo `description` field is often blank or terse. Read the real
README and summarize what it *actually does* in one honest sentence — this
is the same standard the rest of the curated list already holds to. Never
invent capabilities the README doesn't support.

## 4. Add the entry

```json
{
  "repo": "exact-repo-name",
  "owner": "your-github-username",
  "name": "Display Name",
  "description": "One accurate sentence, grounded in the real README.",
  "tags": ["PrimaryLanguage", "category"]
}
```

## 5. Check for repos that should come OUT

A repo goes private, gets deleted, or gets renamed — any of those break its
entry silently (the live-enrichment fetch just starts failing for that one
repo, degrading to `"live": false` for it specifically, which is easy to
miss since the rest of the page still works fine). Spot-check:

```bash
for repo in $(jq -r '.[].repo' backend/projects.json); do
  owner=$(jq -r --arg r "$repo" '.[] | select(.repo==$r) | .owner' backend/projects.json)
  status=$(gh api "repos/$owner/$repo" --silent -o /dev/null -w "%{http_code}" 2>&1 || echo "FAIL")
  echo "$repo: $status"
done
```

Anything that fails or comes back private: remove the entry, or move it to
an `/archive` page if the project has a real one, per the
`ohermes-hub-full-stack-setup` skill's page list.

## 6. Verify the refresh actually took effect

The backend caches aggressively (10 minutes on `/api/projects`, and — after
a resilience fix made during this project's own review pass — it now
deliberately keeps serving the last known-good snapshot if a refresh comes
back empty, rather than clobbering good data with a failed one). That means
editing `projects.json` alone isn't enough to see the change immediately:

```bash
docker compose restart hub-api   # clears the in-memory cache
curl -s http://localhost:8500/api/projects | jq '.projects[] | .repo'
```

Confirm the new repo appears and any removed one doesn't, before considering
the refresh done.

## When to actually run this

There's no cron job here by design — this is a "when you remember, or when
you just pushed something new" skill, not a background service. If you want
it automatic, that's a separate, later decision (a scheduled task calling
the checks above), not something this skill assumes you want.
