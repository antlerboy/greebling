(() => {
  'use strict';
  const host = document.getElementById('living-mark');
  const next = document.getElementById('next-mark');
  const pause = document.getElementById('pause-mark');
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  let paused = preference.matches;
  let marks = [];
  let previous = '';

  function syncPlayback() {
    const video = host.querySelector('video');
    pause.disabled = !video;
    pause.textContent = video ? (paused ? 'Play motion' : 'Pause motion') : 'Still drawing';
    if (!video) return;
    if (paused || document.hidden) video.pause();
    else video.play().catch(() => {});
  }

  function showStill(src, description) {
    const image = document.createElement('img');
    image.src = '/' + src;
    image.alt = description;
    image.decoding = 'async';
    host.replaceChildren(image);
    syncPlayback();
  }

  function show(mark) {
    previous = mark.id;
    if (mark.kind !== 'video') {
      showStill(mark.src, mark.description);
      return;
    }
    const video = document.createElement('video');
    video.poster = '/' + mark.poster;
    video.src = '/' + mark.src;
    video.muted = true;
    video.defaultMuted = true;
    video.loop = true;
    video.playsInline = true;
    video.preload = 'metadata';
    video.setAttribute('aria-label', mark.description);
    video.addEventListener('error', () => {
      if (host.contains(video)) showStill(mark.poster, mark.description);
    }, {once: true});
    host.replaceChildren(video);
    syncPlayback();
  }

  function choose(initial = false) {
    const eligible = marks.filter(mark => mark.id !== previous && (!initial || mark.kind === 'video'));
    const pool = eligible.length ? eligible : marks;
    if (!pool.length) return;
    const random = new Uint32Array(1);
    crypto.getRandomValues(random);
    show(pool[random[0] % pool.length]);
  }

  next.addEventListener('click', () => choose());
  pause.addEventListener('click', () => { paused = !paused; syncPlayback(); });
  preference.addEventListener('change', event => { paused = event.matches; syncPlayback(); });
  document.addEventListener('visibilitychange', syncPlayback);
  syncPlayback();
  fetch('/assets/living-marks/manifest.json')
    .then(response => {
      if (!response.ok) throw new Error('The drawings could not be loaded.');
      return response.json();
    })
    .then(data => {
      marks = data.marks.filter(mark => mark.id && mark.src);
      next.disabled = marks.length < 2;
      choose(true);
    })
    .catch(() => { next.disabled = true; });
})();
