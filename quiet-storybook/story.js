/* Progressive enhancement: without JavaScript, the complete story stays readable. */
(() => {
  'use strict';
  const scenes = [...document.querySelectorAll('.scene')];
  const previous = document.querySelector('#previous');
  const next = document.querySelector('#next');
  const position = document.querySelector('#position');
  let current = 0;

  function show(index, navigate = false) {
    current = Math.max(0, Math.min(scenes.length - 1, index));
    scenes.forEach((scene, i) => { scene.hidden = i !== current; });
    previous.disabled = current === 0;
    next.textContent = current === scenes.length - 1 ? '처음으로 ↶' : '다음 →';
    next.setAttribute('aria-label', current === scenes.length - 1 ? '첫 장면으로 돌아가기' : '다음 장면');
    position.textContent = `${current + 1} / ${scenes.length} · ${scenes[current].querySelector('h2').textContent}`;
    // Keep keyboard focus visible if the previous control becomes disabled.
    if (previous.disabled && document.activeElement === previous) next.focus();
    if (navigate && window.matchMedia('(max-width: 740px)').matches) {
      document.querySelector('#story').scrollIntoView({ block: 'start', behavior: 'auto' });
    }
  }
  previous.addEventListener('click', () => show(current - 1, true));
  next.addEventListener('click', () => show(current === scenes.length - 1 ? 0 : current + 1, true));
  document.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || event.repeat) return;
    if (event.target.closest('input, textarea, select, [contenteditable="true"], summary')) return;
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      show(current + (event.key === 'ArrowRight' ? 1 : -1), true);
    }
  });
  show(0);
  document.querySelector('.turns').hidden = false;
  document.querySelector('.keyboard').hidden = false;
})();
