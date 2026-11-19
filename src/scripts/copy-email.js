/**
 * Click-to-copy email links with mailto fallback and polite aria-live feedback.
 */

const copyEmailLinks = document.querySelectorAll('[data-copy-email]');

if (copyEmailLinks.length > 0 && navigator.clipboard?.writeText) {
  let liveRegion = null;

  const announce = (message) => {
    if (!liveRegion) {
      liveRegion = document.createElement('span');
      liveRegion.setAttribute('aria-live', 'polite');
      liveRegion.style.cssText =
        'position:fixed;inline-size:1px;block-size:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap;';
      document.body.append(liveRegion);
    }
    liveRegion.textContent = '';
    requestAnimationFrame(() => {
      liveRegion.textContent = message;
    });
  };

  for (const link of copyEmailLinks) {
    if (!(link instanceof HTMLAnchorElement)) continue;
    let resetTimer = null;
    const originalText = link.textContent?.trim() ?? '';

    link.addEventListener('click', async (e) => {
      const email = link.dataset.copyEmail;
      if (!email) return;

      e.preventDefault();
      try {
        await navigator.clipboard.writeText(email);
        link.textContent = 'copied';
        announce(`Copied ${email} to clipboard`);

        clearTimeout(resetTimer);
        resetTimer = setTimeout(() => {
          link.textContent = originalText;
        }, 1800);
      } catch {
        window.location.href = link.href;
      }
    });
  }
}
