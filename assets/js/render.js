function renderCard(post) {
  return (
    '<a class="card" href="/pages/article.html?id=' + post.id + '">' +
      '<div class="card-thumb">' + thumbHtml(post) + '</div>' +
      '<div class="card-body">' +
        '<div class="tag">' + post.tag + '</div>' +
        '<h3>' + post.title + '</h3>' +
        '<div class="card-meta"><span>조회 ' + formatViews(post.views) + '</span><span>댓글 ' + post.comments + '</span></div>' +
      '</div>' +
    '</a>'
  );
}

function renderFeedMain(post) {
  return (
    '<a class="feed-main" href="/pages/article.html?id=' + post.id + '">' +
      thumbHtml(post) +
      '<div class="feed-body">' +
        '<span class="rank-badge">01</span>' +
        '<h3>' + post.title + '</h3>' +
        '<p>' + post.excerpt + '</p>' +
      '</div>' +
    '</a>'
  );
}

function renderFeedRow(post, rankLabel) {
  const meta = post.video
    ? '조회 ' + formatViews(post.views) + ' · ' + post.duration + ' 영상'
    : '조회 ' + formatViews(post.views) + ' · ' + post.tag;
  return (
    '<a class="feed-row" href="/pages/article.html?id=' + post.id + '">' +
      '<span class="rank-badge">' + rankLabel + '</span>' +
      thumbHtml(post, { sm: true }) +
      '<div class="row-text"><h4>' + post.title + '</h4><span>' + meta + '</span></div>' +
    '</a>'
  );
}

function renderRankingRow(item) {
  const deltaClass = item.delta >= 0 ? 'delta-up' : 'delta-down';
  const arrow = item.delta >= 0 ? '▲' : '▼';
  const deltaText = Math.abs(item.delta).toFixed(1) + '%';
  return (
    '<tr>' +
      '<td>' + item.rank + '</td>' +
      '<td class="ch-name">' + ytChip() + item.name + '</td>' +
      '<td>' + item.subs + '</td>' +
      '<td class="' + deltaClass + '">' + arrow + ' ' + deltaText + '</td>' +
      '<td>' + item.category + '</td>' +
    '</tr>'
  );
}

function pad2(n) {
  return String(n).padStart(2, '0');
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function timeAgo(iso) {
  if (!iso) return '';
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return Math.max(1, Math.floor(diff / 60000)) + '분 전';
  if (h < 24) return h + '시간 전';
  const d = Math.floor(h / 24);
  if (d < 30) return d + '일 전';
  return new Date(iso).toISOString().slice(0, 10);
}

function renderNewsRow(article) {
  return (
    '<a class="news-row" href="' + escapeHtml(article.link) + '" target="_blank" rel="noopener">' +
      '<div class="news-text">' +
        '<h3>' + escapeHtml(article.title) + '</h3>' +
        '<p>' + escapeHtml(article.summary) + '</p>' +
        '<div class="news-meta">' +
          '<span>' + escapeHtml(article.source || '출처 미상') + '</span>' +
          '<span>' + timeAgo(article.published_at) + '</span>' +
          '<span class="news-outlink">원문 보기 ↗</span>' +
        '</div>' +
      '</div>' +
    '</a>'
  );
}

function renderVideoCard(v) {
  return (
    '<a class="card video-card" href="https://www.youtube.com/watch?v=' + escapeHtml(v.video_id) + '" target="_blank" rel="noopener">' +
      '<div class="video-thumb"><img src="' + escapeHtml(v.thumbnail_url) + '" alt="" loading="lazy">' +
        '<div class="play-badge">' + PLAY_BADGE_SVG + '</div>' +
      '</div>' +
      '<div class="card-body">' +
        '<h3>' + escapeHtml(v.title) + '</h3>' +
        '<div class="card-meta"><span>' + escapeHtml(v.channel_title) + '</span>' +
        '<span>조회 ' + formatViews(v.view_count) + '</span>' +
        '<span>' + timeAgo(v.published_at) + '</span></div>' +
      '</div>' +
    '</a>'
  );
}
