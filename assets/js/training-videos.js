// 추천 훈련 영상 라이브러리 — training-videos.json 을 읽어 카드 그리드로 렌더.
(async function () {
  const BASE = (typeof SITE_BASE !== 'undefined' && SITE_BASE) ? SITE_BASE : '/';
  const grid = document.getElementById('vid-grid');
  const filters = document.getElementById('vid-filters');
  if (!grid) return;

  let data;
  try {
    const res = await fetch(BASE + 'assets/data/training-videos.json');
    data = await res.json();
  } catch (e) {
    grid.innerHTML = '<div class="empty-state">영상 목록을 불러오지 못했습니다.</div>';
    return;
  }

  const videos = data.videos || [];
  const cats = ['전체'].concat(data.categories || []);
  let active = '전체';

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function thumb(v) {
    return 'https://i.ytimg.com/vi/' + encodeURIComponent(v.id) + '/hqdefault.jpg';
  }

  function render() {
    const list = active === '전체' ? videos : videos.filter((v) => v.cat === active);
    grid.innerHTML = list.map(function (v) {
      const vert = v.short ? ' vert' : '';
      const t = esc(v.title);
      return (
        '<div class="vid-card">' +
          '<button class="vid-thumb' + vert + '" data-id="' + esc(v.id) + '" aria-label="영상 재생: ' + t + '">' +
            '<img loading="lazy" src="' + thumb(v) + '" alt="' + t + '">' +
            '<span class="vid-play"></span>' +
          '</button>' +
          '<div class="vid-meta">' +
            '<span class="vid-tag">' + esc(v.cat) + '</span>' +
            '<h3 class="vid-title">' + t + '</h3>' +
            '<p class="vid-note">' + esc(v.note || '') + '</p>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }

  function renderFilters() {
    if (!filters) return;
    filters.innerHTML = cats.map(function (c) {
      return '<button class="vid-chip' + (c === active ? ' on' : '') + '" data-cat="' + c + '">' + c + '</button>';
    }).join('');
  }

  // 클릭 재생: 썸네일 → iframe 교체 (성능을 위한 lite-embed)
  grid.addEventListener('click', function (e) {
    const btn = e.target.closest('.vid-thumb');
    if (!btn) return;
    const id = btn.getAttribute('data-id');
    const ifr = document.createElement('iframe');
    ifr.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
    ifr.title = '훈련 영상';
    ifr.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    ifr.allowFullscreen = true;
    btn.innerHTML = '';
    btn.appendChild(ifr);
  });

  if (filters) {
    filters.addEventListener('click', function (e) {
      const chip = e.target.closest('.vid-chip');
      if (!chip) return;
      active = chip.getAttribute('data-cat');
      renderFilters();
      render();
    });
  }

  renderFilters();
  render();
})();
