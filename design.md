# Design System

Locked tokens for this hub. Every color and font in `frontend/public/css/style.css`
references one of these — no inline OKLCH/hex values, no ad hoc `font-family`
declarations. If a new page needs a color/font not listed here, it's missing
from the system; add it as a named token, don't inline it.

## Genre

Dark, terminal/dev-portfolio aesthetic — deliberately echoes the "dark
terminal aesthetic" of the Cap's Movie List project already listed on this
hub's own grid, for a consistent voice across the ecosystem. Dark is the
default per this workspace's own design preferences (warm dark paper,
light ink), not a redesign decision made per-page.

## Color tokens (OKLCH, `:root` in `style.css`)

| Token | Value | Use |
|---|---|---|
| `--bg` | `oklch(0.16 0.01 260)` | Page background |
| `--paper` | `oklch(0.19 0.012 260)` | Card/panel surfaces |
| `--paper-2` | `oklch(0.23 0.014 260)` | Nested surfaces (tag chips inside cards) |
| `--border` | `oklch(0.32 0.014 260)` | All hairline borders |
| `--ink` | `oklch(0.92 0.01 90)` | Primary text |
| `--ink-dim` | `oklch(0.68 0.012 90)` | Secondary/muted text |
| `--accent` | `oklch(0.78 0.16 150)` | Links, active states, live-data tag |
| `--accent-dim` | `oklch(0.5 0.1 150)` | Hover borders, sparkline bars |
| `--warn` | `oklch(0.75 0.15 60)` | Down/open-issue indicators (never used for anything except a genuine warning state) |
| `--focus` | `oklch(0.8 0.18 150)` | `:focus-visible` outlines only |

No pure `#000` anywhere — `--bg` is a near-black warm dark, per this
workspace's anti-slop rule.

## Typography (2 families, no more)

- `--font-mono` — `ui-monospace` stack. Used for: the brand wordmark, all
  headings, nav, data tags, badges, code-flavored UI chrome. This is what
  gives the site its "terminal" identity — don't introduce a third
  typeface for a new page.
- `--font-body` — system sans stack. Body copy only.
- No italic headers, anywhere (workspace-wide rule) — emphasis in headings
  is carried by the accent color or weight, never `font-style: italic`.

## Components (shared classes, not per-page reinvention)

- `.card` — the one repeating surface unit (project grid, uses/stack page,
  wishlist/talks/press entries all reuse it with content variations, not
  separate card styles).
- `.data-tag` — the `LIVE DATA` / `NON-LIVE DATA` labeling convention
  (workspace-wide rule: explicit beats vague about what's real-time vs.
  static). `.data-tag.live` gets the accent color; the static variant
  stays muted.
- `.tag-chip` — filter pills, `aria-pressed` for active state, never a
  separate "selected" color scheme.
- `.nav-more` — the `<details>/<summary>` overflow menu pattern for the
  nav once it grew past ~6 primary items. Plain HTML, no JS, native
  keyboard support for free.

## Mobile (hard rule, not a per-page decision)

Every new page's CSS goes through a single `@media (max-width: 640px)`
block at the bottom of `style.css` (or an inline `<style>` for a
page-specific component) — **never** modify a base desktop selector to
"also work on mobile." This workspace's standing rule: preserve desktop
layout completely unchanged; all responsive changes are additive overrides
inside the media query, full stop.

## What this file does NOT cover

Page-by-page content/copy — that's each page's own job. Backend/API
design — see `ARCHITECTURE.md`. This is tokens and shared component rules
only.
