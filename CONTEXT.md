# ohermes-hub

A public index of the projects that are actually shipped and public. The
organising principle is that nothing on the site is invented: every claim
is either pulled from a real external source or explicitly marked as
hand-written.

## Language

### Data provenance

**Live Data**:
Content sourced from an external API at serve time rather than authored by
hand. Every surface showing it carries a visible `LIVE DATA` marker.
_Avoid_: real-time, dynamic, auto-updating

**Non-Live Data**:
Content written by hand and committed to the repo. Every surface showing it
carries a visible `NON-LIVE DATA` marker. The distinction is a promise to
the reader about where a claim came from, so a page must never be labelled
`LIVE DATA` merely because it is loaded over HTTP from this hub's own API.
_Avoid_: static data, hardcoded, bundled

**Degraded**:
The state where Live Data could not be retrieved and the last known-good
copy is being served instead. Distinct from having no data at all — a
degraded surface is showing something true, just not current.
_Avoid_: stale, cached, failed

### Content

**Curated Project**:
A repo deliberately listed as part of the hub's index. A repo only
qualifies once it is public on GitHub — this is a hard rule, not an
editorial preference, because the whole index is a claim that a reader can
go and read the code.
_Avoid_: listed repo, featured project, portfolio item

**Honest Empty State**:
A section that says plainly that it holds nothing yet, in place of
placeholder or invented content. Preferred over hiding the section
entirely, so the absence itself is visible and truthful.
_Avoid_: placeholder, coming soon, blank state
