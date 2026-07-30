# ohermes-hub — 100 feature ideas

Brainstorm only. Nothing here is planned or scheduled — pick whatever you
want and say so, and I'll build just that. Organized in 10 categories of 10,
with the requested "new pages/top nav tabs" category first and expanded to
20 since that's what was asked for specifically (100 total either way).

## A. New top-level pages / nav tabs (20)

1. **`/timeline`** — a year-by-year scroll of every repo's first commit, framed as "history of what got built when."
2. **`/stack`** — an expanded version of the current Uses page, with real version numbers and a line on why each tool was picked.
3. **`/now`** — a "now page" (a known personal-site convention): what's actively being worked on right now, updated by hand, not auto-generated.
4. **`/blog`** — longer write-ups about specific builds (e.g. "how the DNS-01 Caddy fix actually happened" — real content, not filler).
5. **`/uptime`** — a public status page for which self-hosted services are currently reachable (health checks only, never the PIN-gated content itself).
6. **`/contact`** — a simple contact page or link list, if you ever want people to reach you.
7. **`/vrchat`** — a dedicated page just for the VRChat-related repos (VRCatAPI, VR-Chat-Links, etc.) — there are enough of them to earn their own section.
8. **`/gaming`** — dedicated page for gaming-community projects (DXRULES, AI_SMF_CODE, and anything else in that vein).
9. **`/archive`** — retired/deprecated projects, clearly labeled as no longer maintained — still only real GitHub repos.
10. **`/api-docs`** — public docs for the hub's own `/api/` endpoints, in case you ever want others consuming them.
11. **`/credits`** — attribution page for third-party resources/libraries used across projects.
12. **`/press`** — placeholder for any write-ups, screenshots, or videos of your projects, populated only once real media exists.
13. **`/tools`** — quick links to any *intentionally public* internal tool from one of your repos, kept clearly separate from PIN-gated ones.
14. **`/year-in-review`** — an auto-generated annual retrospective from real GitHub commit data.
15. **`/wishlist`** — distinct from "Ideas" — a short public list of tools/hardware/collaborations you're looking for.
16. **`/talks`** — slides/recordings, if you ever present about any of this.
17. **`/license`** — a page explaining licensing across repos, since it's already mixed (e.g. smart-bulb-dashboard is noncommercial, others aren't).
18. **`/health`** (JSON) — a machine-readable status endpoint for external uptime monitors.
19. **`/roadmap`** — a public high-level direction page, distinct from the task-shaped "Ideas" board.
20. **Custom `/404`** — an on-brand not-found page instead of nginx's default.

## B. Project grid & discovery (10)

21. Sort toggle: most stars / most recent / alphabetical.
22. "Random project" button.
23. Compact list view as an alternative to the current card grid.
24. Per-card mini activity sparkline (commits over the last 90 days).
25. License badge per card, pulled live from GitHub's license API.
26. Primary-language color strip per card (GitHub-style).
27. "Similar projects" cross-links based on shared tags.
28. Manually-pinned "featured" slot at the top of the grid (still real repos only).
29. Project detail page (`/projects/<repo>`) with the full README rendered.
30. Live open-issues count badge per card.

## C. Changelog & activity (10)

31. Filter the changelog by a specific project.
32. Group entries by day instead of a flat list.
33. Show commit diff stats (+/− lines) per entry.
34. Optional weekly digest, sent to you only.
35. GitHub-style contribution heatmap across all repos combined.
36. Distinguish release/tag events from regular commits.
37. Real pagination instead of a hard 30-entry cap.
38. GitHub webhooks for near-instant updates instead of the 10-minute poll cache.
39. Per-project changelog widget, embeddable on that project's own GitHub Pages site.
40. Full-text search across commit messages.

## D. Visual & interaction polish (10)

41. Light/dark toggle (currently dark-only, by design, but toggleable is cheap).
42. Scroll-triggered fade-in on cards.
43. Animated counter for total stars/commits in the hero.
44. Real favicon (currently unset).
45. Open Graph preview image for link shares.
46. Skeleton loading states instead of plain "Loading…" text.
47. Smooth anchor-scroll for the nav tabs.
48. Command palette (Cmd/Ctrl+K) to jump to any project or page instantly.
49. A subtle terminal-cursor-blink accent, echoing Cap's Movie List's aesthetic.
50. A print stylesheet so `/uses` or `/stack` looks clean exported to PDF.

## E. Data, stats & live badges (10)

51. Combined star count across every listed repo, shown in the hero.
52. Aggregate "lines of code" stat via GitHub's languages API.
53. Per-repo contributor count (honestly showing 1 where that's true).
54. Repo age (`created_at`) alongside last-pushed.
55. Fork count badge.
56. CI/Actions status badge, for any repo that has workflows.
57. "Projects shipped this year" counter.
58. Language breakdown chart across the whole portfolio.
59. Live GitHub API rate-limit-remaining indicator (for your own visibility, not public-facing).
60. Per-repo dependency count, only if it'd actually be meaningful.

## F. Search, filter & navigation (10)

61. Keyboard shortcuts (`/` to focus search, `Esc` to clear).
62. URL-persisted filters, so a filtered view is shareable via link.
63. Sticky nav bar on scroll.
64. Mobile hamburger menu once the nav grows past ~5 tabs.
65. `sitemap.xml` for search engines.
66. Fuzzy (typo-tolerant) search instead of exact substring match.
67. Search across changelog messages too, not just project name/description.
68. "Recently viewed" project shortcut (client-side only, localStorage).
69. Tag cloud visualization instead of a flat chip list.
70. Breadcrumb for any page that ends up nested (e.g. `/projects/<repo>`).

## G. Content & writing (10)

71. Per-project "why I built this" blurb, separate from the GitHub description.
72. Build-log posts tied to specific commits/milestones.
73. A "lessons learned" tag on changelog entries for genuinely notable fixes (tonight's DNS-01 saga would qualify).
74. Opt-in screenshots/GIFs embedded per project card.
75. A short bio/about blurb in the homepage hero.
76. FAQ page for common questions about the setup.
77. Inline markdown-rendered README preview on hover/click.
78. Auto cross-post changelog entries to the Forgejo issue tracker.
79. Optional "currently reading/learning" mini-section.
80. A hand-written or auto-drafted monthly recap page.

## H. Integrations (10)

81. Merge Forgejo activity into the same changelog feed, not just GitHub.
82. A Tailscale-only "internal" view with extra detail visible only over the tailnet.
83. Discord webhook posting new changelog entries to a channel.
84. Real uptime-monitor integration (e.g. a self-hosted Uptime Kuma) instead of a hand-rolled `/uptime` page.
85. Optional GitHub Sponsors / Ko-fi link (off by default).
86. Live VRChat API status widget on `/vrchat`, using your own VRCatAPI project.
87. A small "currently trending" TMDB widget on the homepage, sourced from Cap's Movie List.
88. Auto-generated OG images per project card.
89. GitHub push webhooks instead of polling, for true real-time updates.
90. Cross-links from relevant project cards to the `caddy-dns-duck` skill or other relevant skills.

## I. Personalization & accessibility (10)

91. Respect `prefers-reduced-motion` for any animation added later.
92. High-contrast mode toggle.
93. Font-size adjuster.
94. Remembered filter/search state across visits (localStorage).
95. Full-content RSS feed for the changelog, not just titles.
96. Formal keyboard-only navigability audit (tab order, focus rings).
97. Screen-reader landmark regions (`<main>`, `<nav>`, ARIA labels) throughout.
98. Locale/language toggle, listed for completeness even if unlikely to matter.
99. "Copy link to this project" button per card.
100. A tiny "hub last updated" note on `/uses` or `/stack` — meta, but honest.

---

Say which ones (by number, category, or just describe them) and I'll build
those specifically — nothing here gets implemented on its own.
