// 경기 결과 렌더 — match-results.json 을 읽어 대회별 표로 표시.
(async function () {
  const BASE = (typeof SITE_BASE !== 'undefined' && SITE_BASE) ? SITE_BASE : '/';
  const wrap = document.getElementById('rs-wrap');
  if (!wrap) return;

  let data;
  try {
    const res = await fetch(BASE + 'assets/data/match-results.json');
    data = await res.json();
  } catch (e) {
    wrap.innerHTML = '<div class="empty-state">경기 결과를 불러오지 못했습니다.</div>';
    return;
  }

  const upd = document.getElementById('rs-updated');
  if (upd && data.updated) upd.textContent = '업데이트: ' + data.updated;

  const tours = data.tournaments || [];
  if (!tours.length) {
    wrap.innerHTML = '<div class="empty-state">등록된 경기 결과가 없습니다.</div>';
    return;
  }

  function scoreCell(m) {
    if (m.status === '예정' || m.hs == null || m.as == null) {
      return '<span class="rs-vs">vs</span>';
    }
    const hw = m.hs > m.as, aw = m.as > m.hs;
    return '<span class="rs-score"><b class="' + (hw ? 'win' : '') + '">' + m.hs +
      '</b> : <b class="' + (aw ? 'win' : '') + '">' + m.as + '</b></span>';
  }

  function statusBadge(s) {
    const cls = s === '종료' ? 'done' : (s === '진행' ? 'live' : 'soon');
    return '<span class="rs-badge ' + cls + '">' + (s || '') + '</span>';
  }

  wrap.innerHTML = tours.map(function (t) {
    // 날짜별 그룹
    const byDate = {};
    (t.matches || []).forEach(function (m) { (byDate[m.date] = byDate[m.date] || []).push(m); });
    const dates = Object.keys(byDate).sort();
    const groups = dates.map(function (d) {
      const rows = byDate[d].map(function (m) {
        return '<tr>' +
          '<td class="rs-round">' + (m.round || '') + '</td>' +
          '<td class="rs-home">' + m.home + '</td>' +
          '<td class="rs-sc">' + scoreCell(m) + '</td>' +
          '<td class="rs-away">' + m.away + '</td>' +
          '<td class="rs-st">' + statusBadge(m.status) + '</td>' +
        '</tr>';
      }).join('');
      return '<div class="rs-date">' + d + '</div>' +
        '<div class="table-scroll"><table class="rs-table"><tbody>' + rows + '</tbody></table></div>';
    }).join('');

    const src = t.source_url
      ? '<a href="' + t.source_url + '" target="_blank" rel="noopener nofollow">' + (t.source || '출처') + ' ↗</a>'
      : (t.source || '');
    return '<section class="rs-tour">' +
      '<div class="rs-tour-head">' +
        '<h2>' + t.name + '</h2>' +
        '<div class="rs-meta">' + [t.region, t.division].filter(Boolean).join(' · ') +
        (src ? ' <span class="rs-src">· 출처: ' + src + '</span>' : '') + '</div>' +
      '</div>' + groups +
    '</section>';
  }).join('');
})();
