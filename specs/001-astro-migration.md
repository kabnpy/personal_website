# Spec 001: Astro Migration

## Goal
Migrate the static two-page site from `prototype/` into a maintainable **Astro** project at the repository root, eliminating duplicated page chrome and separating client-side behaviors, while preserving exact visual and behavioral parity.

## Requirements
1. **Shared Layout (`src/layouts/BaseLayout.astro`)**
   - Renders `<head>` (charset, viewport, `color-scheme` meta, FOUC-prevention inline script, SVG favicon, Google Fonts `Geist` + `JetBrains Mono`, global CSS).
   - Renders `AmbientLayers` as a fixed sibling outside `.frame`, and `SiteHeader`, `<slot />`, and `SiteFooter` inside `.frame`.
2. **Components (`src/components/`)**
   - `AmbientLayers.astro`: `#shadow-video` (`/shadows.mp4`) and `.ambient-layer--grain`.
   - `SiteHeader.astro`: Brand mark on home (`/`), `← Home` link on inner pages, and primary nav (`Work` with `aria-current="page"` when active).
   - `SiteFooter.astro`: Studio label, `Say hello` copy-email link (supporting `chrome-link` vs `chrome-highlight` via prop), `Shadows` toggle, and `Theme` toggle.
   - `SpecimenRow.astro`: `<details class="specimen-row reveal">` driven by structured project data, with `--reveal-order` CSS variable.
   - `WorkPreview.astro`: `<aside id="work-preview" class="work-preview" aria-hidden="true"></aside>`.
3. **Structured Data (`src/data/work.json`)**
   - Holds all 6 projects (`index`, `title`, `discipline`, `year`, `description`, `meta` key/value pairs).
4. **Client Scripts (`src/scripts/`)**
   - `shadows.js`: Looping video toggle respecting `prefers-reduced-motion` and `visibilitychange`.
   - `theme.js`: Light/dark toggle with `localStorage`, `storage` event sync, and `document.startViewTransition`.
   - `copy-email.js`: Click-to-copy email with `mailto:` fallback and polite `aria-live` announcement.
   - `work-preview.js`: Floating hover preview loaded only on `/work`.
5. **Pages & Assets**
   - `/` (`src/pages/index.astro`) and `/work` (`src/pages/work.astro`).
   - `public/shadows.mp4` copied from `prototype/shadows.mp4`.
   - `prototype/` removed once `npm run build` succeeds and parity is verified.

## Out of Scope
- Adding new pages, backend routes, or UI frameworks (React/Vue/Svelte).
- Changing the visual design or Blender pipeline.
