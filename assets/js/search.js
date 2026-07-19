async function renderSearch() {
  const params = new URLSearchParams(window.location.search);
  const q = (params.get('q') || '').trim();

  document.getElementById('search-title').textContent = q ? '"' + q + '" 검색 결과' : '검색 결과';
  document.title = (q ? q + ' 검색' : '검색') + ' — 그라운드';

  const input = document.getElementById('nav-search-input');
  const setInput = () => { if (input) input.value = q; };
  const headerReady = new MutationObserver(() => {
    const el = document.getElementById('nav-search-input');
    if (el) { el.value = q; headerReady.disconnect(); }
  });
  headerReady.observe(document.getElementById('site-header'), { childList: true, subtree: true });

  if (!q) {
    document.getElementById('search-count').textContent = '';
    document.getElementById('search-cards').innerHTML = '<div class="empty-state">검색어를 입력해주세요.</div>';
    return;
  }

  const posts = await fetchPosts();
  const needle = q.toLowerCase();
  const results = posts.filter((p) =>
    p.title.toLowerCase().includes(needle) ||
    p.excerpt.toLowerCase().includes(needle) ||
    p.tag.toLowerCase().includes(needle) ||
    p.categoryLabel.toLowerCase().includes(needle)
  );

  document.getElementById('search-count').textContent = '총 ' + results.length + '건';
  document.getElementById('search-cards').innerHTML = results.length
    ? results.map(renderCard).join('')
    : '<div class="empty-state">일치하는 게시글이 없습니다.</div>';
}

document.addEventListener('DOMContentLoaded', renderSearch);
