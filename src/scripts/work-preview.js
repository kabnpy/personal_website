/**
 * Floating hover preview for the work index (desktop fine-pointer only).
 */

const specimenList = document.querySelector('.specimen-list');
const workPreview = document.getElementById('work-preview');

if (specimenList && workPreview && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
  let activeRow = null;

  const positionPreview = (clientX, clientY) => {
    const pad = 20;
    const width = workPreview.offsetWidth || 352;
    const height = workPreview.offsetHeight || 220;
    const x = Math.min(Math.max(pad, clientX + 24), window.innerWidth - width - pad);
    const y = Math.min(Math.max(pad, clientY - height / 2), window.innerHeight - height - pad);
    workPreview.style.transform = `translate3d(${x}px, ${y}px, 0)`;
  };

  const populatePreview = (row) => {
    const index = row.querySelector('.specimen-row__index')?.textContent?.trim() ?? '';
    const title = row.querySelector('.specimen-row__title')?.textContent?.trim() ?? '';
    const year = row.querySelector('.specimen-row__year')?.textContent?.trim() ?? '';
    const desc = row.querySelector('.specimen-row__desc')?.textContent?.trim() ?? '';
    const meta = row.querySelector('.specimen-meta');

    workPreview.replaceChildren();

    const header = document.createElement('div');
    header.className = 'work-preview__header';
    const indexEl = document.createElement('span');
    indexEl.className = 'mono-label text-muted';
    indexEl.textContent = index;
    const yearEl = document.createElement('span');
    yearEl.className = 'mono-label text-muted';
    yearEl.textContent = year;
    header.append(indexEl, yearEl);

    const titleEl = document.createElement('p');
    titleEl.className = 'work-preview__title';
    titleEl.textContent = title;

    const descEl = document.createElement('p');
    descEl.className = 'work-preview__desc';
    descEl.textContent = desc;

    workPreview.append(header, titleEl, descEl);

    if (meta) {
      const metaClone = meta.cloneNode(true);
      if (metaClone instanceof HTMLElement) {
        metaClone.className = 'work-preview__meta';
        workPreview.append(metaClone);
      }
    }
  };

  const hidePreview = () => {
    activeRow = null;
    workPreview.dataset.visible = 'false';
  };

  specimenList.addEventListener('pointermove', (e) => {
    const target = e.target instanceof Element ? e.target : null;
    const summary = target?.closest('.specimen-row__summary');
    const row = summary?.closest('.specimen-row');

    if (!(row instanceof HTMLDetailsElement) || row.open) {
      hidePreview();
      return;
    }

    const wasHidden = workPreview.dataset.visible !== 'true';

    if (row !== activeRow) {
      activeRow = row;
      populatePreview(row);
    }

    if (wasHidden) {
      workPreview.dataset.snap = 'true';
      positionPreview(e.clientX, e.clientY);
      void workPreview.offsetWidth;
      delete workPreview.dataset.snap;
    } else {
      positionPreview(e.clientX, e.clientY);
    }

    workPreview.dataset.visible = 'true';
  });

  specimenList.addEventListener('pointerleave', hidePreview);
  specimenList.addEventListener('click', hidePreview);
}
