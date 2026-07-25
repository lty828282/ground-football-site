// 영상 피드 렌더 — window.FEED_CONFIG = { data: 'assets/data/xxx.json' } 를 읽어
// 단일(videos) 또는 섹션(sections) 형태를 카드 그리드로 렌더. 클릭 시 유튜브 임베드 재생.
(async function () {
  const BASE = (typeof SITE_BASE !== 'undefined' && SITE_BASE) ? SITE_BASE : '/';
  const cfg = window.FEED_CONFIG || {};
  const root = document.getElementById('feed-root');
  if (!root || !cfg.data) return;

  let data;
  try {
    data = await (await fetch(BASE + cfg.data)).json();
  } catch (e) {
    root.innerHTML = '<div class="empty-state">영상을 불러오지 못했습니다.</div>';
    return;
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function card(v) {
    const vert = v.short ? ' vert' : '';
    const t = esc(v.title);
    return (
      '<div class="vid-card">' +
        '<button class="vid-thumb' + vert + '" data-id="' + esc(v.id) + '" aria-label="영상 재생: ' + t + '">' +
          '<img loading="lazy" src="https://i.ytimg.com/vi/' + encodeURIComponent(v.id) + '/hqdefault.jpg" alt="' + t + '">' +
          '<span class="vid-play"></span>' +
        '</button>' +
        '<div class="vid-meta">' +
          (v.tag ? '<span class="vid-tag">' + esc(v.tag) + '</span>' : '') +
          '<h3 class="vid-title">' + t + '</h3>' +
          '<p class="vid-note">' + esc(v.note || '') + '</p>' +
        '</div>' +
      '</div>'
    );
  }

  function grid(vs) {
    if (!vs || !vs.length) return '<div class="empty-state">최근 일주일 이내 영상을 찾지 못했습니다. 곧 업데이트됩니다.</div>';
    return '<div class="vid-grid">' + vs.map(card).join('') + '</div>';
  }

  const upd = document.getElementById('feed-updated');
  if (upd && data.updated) upd.textContent = '업데이트: ' + data.updated;

  if (Array.isArray(data.sections)) {
    root.innerHTML = data.sections.map(function (s) {
      return '<h2 class="feed-sec">' + esc(s.label) + '</h2>' + grid(s.videos);
    }).join('');
  } else {
    root.innerHTML = grid(data.videos);
  }

  // 썸네일 클릭 → iframe 교체(lite-embed)
  root.addEventListener('click', function (e) {
    const btn = e.target.closest('.vid-thumb');
    if (!btn) return;
    const id = btn.getAttribute('data-id');
    const ifr = document.createElement('iframe');
    ifr.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
    ifr.title = '영상';
    ifr.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    ifr.allowFullscreen = true;
    btn.innerHTML = '';
    btn.appendChild(ifr);
  });
})();
