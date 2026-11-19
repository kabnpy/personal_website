/**
 * 2-state color theme toggle (system default vs. opposite override).
 * Syncs across tabs via localStorage and animates via View Transitions when allowed.
 */

const themeBtn = document.getElementById('theme-toggle');
const themeLabel = document.getElementById('theme-toggle-label');
const colorSchemeMeta = document.querySelector('meta[name="color-scheme"]');

if (themeBtn && themeLabel && colorSchemeMeta instanceof HTMLMetaElement) {
  const STORAGE_KEY = 'color-scheme';
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

  const parseScheme = (value) => (value === 'light' || value === 'dark' ? value : null);
  const getSystemScheme = () => (prefersDark.matches ? 'dark' : 'light');
  const getStoredScheme = () => parseScheme(colorSchemeMeta.content);

  const renderTheme = (stored) => {
    colorSchemeMeta.content = stored ?? 'light dark';
    const resolved = stored ?? getSystemScheme();
    const label = resolved === 'dark' ? 'Dark' : 'Light';
    const nextLabel = resolved === 'dark' ? 'light' : 'dark';
    themeLabel.textContent = label;
    themeBtn.setAttribute('aria-label', `Switch to ${nextLabel} theme`);
  };

  renderTheme(getStoredScheme());

  themeBtn.addEventListener('click', () => {
    const current = getStoredScheme() ?? getSystemScheme();
    const target = current === 'dark' ? 'light' : 'dark';
    const shouldPersist = target !== getSystemScheme();

    try {
      if (shouldPersist) {
        localStorage.setItem(STORAGE_KEY, target);
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    } catch {}

    const applyTheme = () => renderTheme(shouldPersist ? target : null);
    const allowMotion = window.matchMedia('(prefers-reduced-motion: no-preference)').matches;

    if (allowMotion && typeof document.startViewTransition === 'function') {
      document.startViewTransition(applyTheme);
    } else {
      applyTheme();
    }
  });

  window.addEventListener('storage', (e) => {
    if (e.key !== STORAGE_KEY) return;
    renderTheme(parseScheme(e.newValue));
  });

  prefersDark.addEventListener('change', () => {
    if (!getStoredScheme()) {
      renderTheme(null);
    }
  });
}
