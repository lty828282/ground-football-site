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

function popularThumb(item, opts) {
  opts = opts || {};
  const sizeClass = opts.sm ? ' -sm' : '';
  if (item.thumb) {
    const badgeStyle = opts.sm ? ' style="width:18px;height:18px;bottom:5px;right:5px;"' : '';
    return (
      '<div class="photo-thumb photo-thumb-img' + sizeClass + '">' +
        '<img src="' + escapeHtml(item.thumb) + '" alt="" loading="lazy">' +
        '<div class="play-badge"' + badgeStyle + '>' + PLAY_BADGE_SVG + '</div>' +
      '</div>'
    );
  }
  return '<div class="photo-thumb' + sizeClass + '">' + iconSvg('chart') + '</div>';
}

function renderPopularMain(item) {
  return (
    '<a class="feed-main" href="' + escapeHtml(item.href) + '" target="_blank" rel="noopener">' +
      popularThumb(item) +
      '<div class="feed-body">' +
        '<span class="rank-badge">01</span>' +
        '<h3>' + escapeHtml(item.title) + '</h3>' +
        '<p>' + escapeHtml(item.excerpt) + '</p>' +
      '</div>' +
    '</a>'
  );
}

function renderPopularRow(item, rankLabel) {
  return (
    '<a class="feed-row" href="' + escapeHtml(item.href) + '" target="_blank" rel="noopener">' +
      '<span class="rank-badge">' + rankLabel + '</span>' +
      popularThumb(item, { sm: true }) +
      '<div class="row-text"><h4>' + escapeHtml(item.title) + '</h4><span>' + escapeHtml(item.meta) + '</span></div>' +
    '</a>'
  );
}

function channelUrl(ch) {
  return ch.handle
    ? 'https://www.youtube.com/' + ch.handle
    : 'https://www.youtube.com/channel/' + ch.channel_id;
}

function channelCell(ch) {
  const avatar = ch.thumbnail_url
    ? '<img class="ch-avatar" src="' + escapeHtml(ch.thumbnail_url) + '" alt="" loading="lazy">'
    : ytChip();
  const pin = ch.is_pinned ? '<span class="pin-chip">고정</span>' : '';
  return (
    '<td class="ch-name"><a class="ch-cell" href="' + escapeHtml(channelUrl(ch)) + '" target="_blank" rel="noopener">' +
      avatar + escapeHtml(ch.name) + pin +
    '</a></td>'
  );
}

function renderYouthSubsRow(ch, rank) {
  return (
    '<tr>' +
      '<td>' + rank + '</td>' +
      channelCell(ch) +
      '<td>' + formatViews(ch.subs_count || 0) + '</td>' +
      '<td>' + (ch.latest_upload_at ? timeAgo(ch.latest_upload_at) : '—') + '</td>' +
      '<td><a class="ch-link" href="' + escapeHtml(channelUrl(ch)) + '" target="_blank" rel="noopener">바로가기 ↗</a></td>' +
    '</tr>'
  );
}

function renderYouthRecentRow(ch, rank) {
  const videoHref = ch.latest_video_id
    ? 'https://www.youtube.com/watch?v=' + encodeURIComponent(ch.latest_video_id)
    : channelUrl(ch);
  return (
    '<tr>' +
      '<td>' + rank + '</td>' +
      channelCell(ch) +
      '<td><a class="ch-video" href="' + escapeHtml(videoHref) + '" target="_blank" rel="noopener">' +
        escapeHtml(ch.latest_video_title || '최근 영상') + ' ↗</a></td>' +
      '<td>' + timeAgo(ch.latest_upload_at) + '</td>' +
      '<td>' + formatViews(ch.subs_count || 0) + '</td>' +
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
