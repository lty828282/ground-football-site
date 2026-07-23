// '/pages/...' 처럼 루트 기준으로 적힌 링크를 실제 배포 경로에 맞게 고쳐준다
function rewriteRootLinks(scope) {
  scope.querySelectorAll('a[href^="/"]').forEach((a) => {
    const href = a.getAttribute('href');
    if (!href.startsWith('//')) a.setAttribute('href', SITE_BASE + href.slice(1));
  });
}

async function loadPartials() {
  const headerSlot = document.getElementById('site-header');
  const footerSlot = document.getElementById('site-footer');
  rewriteRootLinks(document);

  if (headerSlot) {
    const res = await fetch(SITE_BASE + 'partials/header.html');
    headerSlot.innerHTML = await res.text();
    rewriteRootLinks(headerSlot);
    try {
      await initTicker();
    } catch (e) {
      console.error('ticker init failed', e);
    }
    initSearch();
    highlightActiveNav();
  }
  if (footerSlot) {
    const res = await fetch(SITE_BASE + 'partials/footer.html');
    footerSlot.innerHTML = await res.text();
    rewriteRootLinks(footerSlot);
  }
}

async function initTicker() {
  const track = document.getElementById('ticker-track');
  if (!track) return;
  const { data, error } = await supabaseClient
    .from('ticker_items')
    .select('label, text')
    .order('sort_order', { ascending: true });
  if (error) {
    console.error('ticker load failed', error);
    return;
  }
  const html = data
    .map((t) => '<span><b>' + t.label + '</b>' + t.text + '</span>')
    .join('');
  track.innerHTML = html + html;
}

function initSearch() {
  const form = document.getElementById('nav-search-form');
  const input = document.getElementById('nav-search-input');
  if (!form) return;
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const q = input.value.trim();
    if (!q) return;
    window.location.href = SITE_BASE + 'pages/search.html?q=' + encodeURIComponent(q);
  });
}

function highlightActiveNav() {
  const params = new URLSearchParams(window.location.search);
  const path = window.location.pathname;
  let activeKey = null;

  if (path.endsWith('/pages/ranking.html')) {
    activeKey = 'ranking';
  } else if (path.endsWith('/pages/news.html')) {
    activeKey = 'news';
  } else if (path.indexOf('/pages/guide') !== -1 || path.indexOf('/pages/cardnews') !== -1) {
    activeKey = 'guides';
  } else if (path.endsWith('/pages/videos.html')) {
    activeKey = params.get('section');
  } else if (path.endsWith('/pages/category.html')) {
    activeKey = params.get('cat');
  }

  if (!activeKey) return;
  const link = document.querySelector('.nav-links a[data-nav="' + activeKey + '"]');
  if (link) link.classList.add('active');
}

async function fetchPosts() {
  const { data, error } = await supabaseClient
    .from('posts')
    .select('id, category, categoryLabel:category_label, tag, title, excerpt, content, icon, video, duration, views, comments, date, popular, rank');
  if (error) {
    console.error('posts load failed', error);
    return [];
  }
  return data;
}

async function fetchYouthChannels() {
  const { data, error } = await supabaseClient
    .from('youth_channels')
    .select('*');
  if (error) {
    console.error('youth channels load failed', error);
    return [];
  }
  return data;
}

async function fetchCategories() {
  const res = await fetch(SITE_BASE + 'assets/data/categories.json');
  return res.json();
}

async function fetchNews(limit) {
  let query = supabaseClient
    .from('news_articles')
    .select('*')
    .order('published_at', { ascending: false });
  if (limit) query = query.limit(limit);
  const { data, error } = await query;
  if (error) {
    console.error('news load failed', error);
    return [];
  }
  return data;
}

async function fetchVideos(section) {
  const { data, error } = await supabaseClient
    .from('videos')
    .select('*')
    .eq('section', section);
  if (error) {
    console.error('videos load failed', error);
    return [];
  }
  return data;
}

document.addEventListener('DOMContentLoaded', loadPartials);
