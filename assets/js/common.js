async function loadPartials() {
  const headerSlot = document.getElementById('site-header');
  const footerSlot = document.getElementById('site-footer');

  if (headerSlot) {
    const res = await fetch('/partials/header.html');
    headerSlot.innerHTML = await res.text();
    try {
      await initTicker();
    } catch (e) {
      console.error('ticker init failed', e);
    }
    initSearch();
    highlightActiveNav();
  }
  if (footerSlot) {
    const res = await fetch('/partials/footer.html');
    footerSlot.innerHTML = await res.text();
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
    window.location.href = '/pages/search.html?q=' + encodeURIComponent(q);
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
  const res = await fetch('/assets/data/categories.json');
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
