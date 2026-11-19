/**
 * Controls the looping monochrome shadow video overlay.
 * Respects prefers-reduced-motion and tab visibility.
 */

const video = document.getElementById('shadow-video');
const shadowsBtn = document.getElementById('shadows-toggle');

if (video instanceof HTMLVideoElement && shadowsBtn) {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let isEnabled = !reducedMotion.matches;

  const syncShadows = () => {
    shadowsBtn.setAttribute('aria-pressed', String(isEnabled));
    video.dataset.paused = String(!isEnabled);

    if (isEnabled && !document.hidden) {
      video.play().catch(() => {});
    } else {
      video.pause();
    }
  };

  syncShadows();

  shadowsBtn.addEventListener('click', () => {
    isEnabled = !isEnabled;
    syncShadows();
  });

  document.addEventListener('visibilitychange', syncShadows);

  reducedMotion.addEventListener('change', (e) => {
    isEnabled = !e.matches;
    syncShadows();
  });
}
