/**
 * Controls the looping monochrome shadow video overlay.
 * Respects prefers-reduced-motion and tab visibility.
 */

const video = document.getElementById('shadow-video');
const shadowsBtn = document.getElementById('shadows-toggle');

if (video instanceof HTMLVideoElement && shadowsBtn) {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let shadowsOn = true;

  const syncShadows = () => {
    shadowsBtn.setAttribute('aria-pressed', String(shadowsOn));
    video.dataset.hidden = String(!shadowsOn);

    if (shadowsOn && !reducedMotion.matches && !document.hidden) {
      video.play().catch(() => {});
    } else {
      video.pause();
    }
  };

  syncShadows();

  shadowsBtn.addEventListener('click', () => {
    shadowsOn = !shadowsOn;
    syncShadows();
  });

  document.addEventListener('visibilitychange', syncShadows);
  reducedMotion.addEventListener('change', syncShadows);
}
