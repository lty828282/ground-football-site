async function renderArticle() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');
  const root = document.getElementById('article-root');

  const posts = await fetchPosts();
  const post = posts.find((p) => p.id === id);

  if (!post) {
    root.innerHTML = '<div class="empty-state">게시글을 찾을 수 없습니다. <a href="/index.html">홈으로 돌아가기</a></div>';
    return;
  }

  document.title = post.title + ' — 그라운드';

  const catUrl = '/pages/category.html?cat=' + post.category;
  const paragraphs = post.content.map((p) => '<p>' + p + '</p>').join('');
  const durationText = post.video ? ' · 영상 ' + post.duration : '';

  root.innerHTML =
    '<div class="breadcrumb"><a href="/index.html">홈</a> / <a href="' + catUrl + '">' + post.categoryLabel + '</a></div>' +
    '<div class="article-tag">' + post.tag + '</div>' +
    '<h1 class="article-title">' + post.title + '</h1>' +
    '<div class="article-meta"><span>' + post.date + '</span><span>조회 ' + formatViews(post.views) + '</span><span>댓글 ' + post.comments + durationText + '</span></div>' +
    '<div class="article-hero-thumb">' + thumbHtml(post) + '</div>' +
    '<div class="article-body">' + paragraphs + '</div>' +
    '<div class="related-wrap" id="related-wrap"></div>';

  const related = posts
    .filter((p) => p.category === post.category && p.id !== post.id)
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 3);

  if (related.length) {
    document.getElementById('related-wrap').innerHTML =
      '<h2>' + post.categoryLabel + ' 관련 글</h2>' +
      '<div class="card-grid">' + related.map(renderCard).join('') + '</div>';
  }
}

document.addEventListener('DOMContentLoaded', renderArticle);
