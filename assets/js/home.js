function videoToFeedItem(v) {
  return {
    title: v.title,
    excerpt: v.channel_title + ' 채널 · 조회 ' + formatViews(v.view_count) + '회',
    meta: '조회 ' + formatViews(v.view_count) + ' · ' + v.channel_title,
    href: 'https://www.youtube.com/watch?v=' + v.video_id,
    thumb: v.thumbnail_url,
  };
}

function newsToFeedItem(n) {
  return {
    title: n.title,
    excerpt: n.summary,
    meta: (n.source || '출처 미상') + ' · ' + timeAgo(n.published_at),
    href: n.link,
    thumb: null,
  };
}

function renderPopularFeed(allVideos, news) {
  const feedSlot = document.getElementById('popular-feed');
  const topVideos = allVideos.slice().sort((a, b) => b.view_count - a.view_count).slice(0, 3);
  const topNews = news.slice(0, 2);
  const items = topVideos.map(videoToFeedItem).concat(topNews.map(newsToFeedItem));

  if (!items.length) {
    feedSlot.innerHTML = '<div class="empty-state">아직 인기 콘텐츠가 없습니다.</div>';
    return;
  }

  const main = renderPopularMain(items[0]);
  const rows = items.slice(1).map((item, i) => renderPopularRow(item, pad2(i + 2))).join('');
  feedSlot.innerHTML = main + '<div class="feed-list">' + rows + '</div>';
}

async function renderHome() {
  const [trainingVideos, youthVideos, reviewVideos, news, rankings] = await Promise.all([
    fetchVideos('training'),
    fetchVideos('youth'),
    fetchVideos('review'),
    fetchNews(4),
    fetchRankings(),
  ]);

  renderPopularFeed(trainingVideos.concat(youthVideos, reviewVideos), news);

  document.getElementById('home-news').innerHTML = news.length
    ? news.map(renderNewsRow).join('')
    : '<div class="empty-state">아직 수집된 기사가 없습니다.</div>';

  const topTraining = trainingVideos.slice().sort((a, b) => b.view_count - a.view_count).slice(0, 3);
  document.getElementById('training-cards').innerHTML = topTraining.length
    ? topTraining.map(renderVideoCard).join('')
    : '<div class="empty-state">아직 수집된 영상이 없습니다.</div>';

  document.getElementById('ranking-rows').innerHTML = rankings.slice(0, 5).map(renderRankingRow).join('');
}

document.addEventListener('DOMContentLoaded', renderHome);
