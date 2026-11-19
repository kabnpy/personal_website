# Coding Standards

## Architecture
- **Static-first Astro**: Ship zero client-side framework JS by default. Use `.astro` components for layout and structure, and small vanilla ES modules in `src/scripts/` for progressive enhancement.
- **Single source of truth**: Shared shell markup (`<head>`, ambient layers, `<header>`, `<footer>`) lives in `src/layouts/BaseLayout.astro`. Structured content (such as projects) lives in `src/data/` rather than being duplicated across HTML and JS.

## CSS (CUBE CSS)
- Maintain native cascade layer order: `reset → base → composition → utilities → blocks → exceptions`.
- Use semantic custom properties (`--color-paper`, `--color-ink`, `--font-sans`, `--font-mono`). Do not name tokens after a visual style they no longer hold.
- Prefer modern CSS (`light-dark()`, `@view-transition`, `:where()`, `clamp()`, `calc()`) with graceful fallbacks where needed.
- Avoid duplicating shared layout/typography rules across sibling classes; group them with `:where(...)`.
- Remove unused selectors, tokens, and `data-*` attributes promptly.

## JavaScript
- Split client scripts by single responsibility (`shadows.js`, `theme.js`, `copy-email.js`, `work-preview.js`).
- Load page-specific scripts only on the pages that need them.
- Always guard DOM queries and browser APIs (`navigator.clipboard`, `document.startViewTransition`, `localStorage`).

## Accessibility
- Respect `prefers-reduced-motion` for animations, video playback, and view transitions.
- Preserve visible `:focus-visible` outlines on all interactive controls.
- Use semantic HTML landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`, `<details>`) and polite `aria-live` announcements for clipboard/status feedback.

## Git Hygiene
- Keep `main` always buildable (`npm run build` must pass).
- Use short-lived branches (`feat/<name>`, `fix/<name>`, `chore/<name>`) and delete them after merging.
- Write concise, atomic commits (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`).
