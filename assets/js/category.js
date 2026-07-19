async function renderCategory() {
  const params = new URLSearchParams(window.location.search);
  const cat = params.get('cat') || 'info';

  const [posts, categories] = await Promise.all([fetchPosts(), fetchCategories()]);
  const meta = categories[cat] || { label: '카테고리', desc: '' };

  document.title = meta.label + ' — 그라운드';
  document.getElementById('crumb-label').textContent = meta.label;
  document.getElementById('cat-title').textContent = meta.label;
  document.getElementById('cat-desc').textContent = meta.desc;

  let list;
  if (cat === 'popular') {
    list = posts.slice().sort((a, b) => b.views - a.views).slice(0, 12);
  } else {
    list = posts
      .filter((p) => p.category === cat)
      .sort((a, b) => new Date(b.date) - new Date(a.date));
  }

  document.getElementById('cat-count').textContent = '총 ' + list.length + '건';

  const grid = document.getElementById('cat-cards');
  grid.innerHTML = list.length
    ? list.map(renderCard).join('')
    : '<div class="empty-state">아직 게시글이 없습니다.</div>';
}

document.addEventListener('DOMContentLoaded', renderCategory);
