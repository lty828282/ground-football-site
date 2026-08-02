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
  let items = [];
  try {
    const res = await fetch(SITE_BASE + 'assets/data/ticker.json');
    items = await res.json();
  } catch (e) {
    console.error('ticker load failed', e);
    return;
  }
  if (!Array.isArray(items) || !items.length) return;
  const html = items
    .map((t) => {
      const inner = '<b>' + t.label + '</b>' + t.text;
      if (t.url) {
        const href = SITE_BASE + String(t.url).replace(/^\//, '');
        return '<a class="tk" href="' + href + '">' + inner + '</a>';
      }
      return '<span>' + inner + '</span>';
    })
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
  } else if (path.endsWith('/pages/soccer-videos.html')) {
    activeKey = 'soccer-videos';
  } else if (path.endsWith('/pages/gear-videos.html')) {
    activeKey = 'gear-videos';
  } else if (path.endsWith('/pages/training-videos.html')) {
    activeKey = 'tvideos';
  } else if (path.endsWith('/pages/nutrition.html') || path.indexOf('/pages/guide-nutrition') !== -1
             || path.indexOf('/pages/guide-match-meals') !== -1 || path.indexOf('/pages/guide-supplements') !== -1
             || path.indexOf('/pages/guide-snacks') !== -1) {
    activeKey = 'nutrition';
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

// ── SEO 메타 자동 주입(canonical·Open Graph·구조화 데이터) ─────────────
// 정적 head 를 페이지마다 손대지 않아도 되도록, 로드 시 표준 태그를 채운다.
function injectSeo() {
  try {
    const head = document.head;
    const origin = location.origin;
    const url = origin + location.pathname.replace(/index\.html$/, '');
    const title = document.title || '그라운드 유소년';
    const descEl = document.querySelector('meta[name="description"]');
    const desc = descEl ? descEl.content : '유소년 축구 전문 정보 허브 · 그라운드 유소년';
    const ogImg = origin + '/assets/img/brand/profile.png';
    const isArticle = location.pathname.indexOf('/pages/') > -1;

    if (!document.querySelector('link[rel="canonical"]')) {
      const l = document.createElement('link');
      l.rel = 'canonical'; l.href = url; head.appendChild(l);
    }
    const props = [
      ['og:site_name', '그라운드 유소년'],
      ['og:type', isArticle ? 'article' : 'website'],
      ['og:title', title],
      ['og:description', desc],
      ['og:url', url],
      ['og:image', ogImg],
      ['og:locale', 'ko_KR'],
    ];
    props.forEach(([p, v]) => {
      if (document.querySelector(`meta[property="${p}"]`)) return;
      const m = document.createElement('meta');
      m.setAttribute('property', p); m.content = v; head.appendChild(m);
    });
    [['twitter:card', 'summary'], ['twitter:title', title],
     ['twitter:description', desc], ['twitter:image', ogImg]].forEach(([n, v]) => {
      if (document.querySelector(`meta[name="${n}"]`)) return;
      const m = document.createElement('meta');
      m.name = n; m.content = v; head.appendChild(m);
    });
    if (!document.getElementById('ld-org')) {
      const ld = document.createElement('script');
      ld.type = 'application/ld+json'; ld.id = 'ld-org';
      ld.textContent = JSON.stringify({
        '@context': 'https://schema.org',
        '@graph': [
          { '@type': 'Organization', name: '그라운드 유소년', url: origin, logo: ogImg },
          { '@type': 'WebSite', name: '그라운드 유소년', url: origin },
        ],
      });
      head.appendChild(ld);
    }
  } catch (e) {
    console.error('seo inject failed', e);
  }
}

injectSeo();
document.addEventListener('DOMContentLoaded', loadPartials);
