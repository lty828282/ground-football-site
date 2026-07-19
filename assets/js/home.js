async function renderHome() {
  const posts = await fetchPosts();

  const popular = posts
    .filter((p) => p.popular)
    .sort((a, b) => a.rank - b.rank);

  const feedSlot = document.getElementById('popular-feed');
  if (popular.length) {
    const main = renderFeedMain(popular[0]);
    const rows = popular.slice(1).map((p) => renderFeedRow(p, pad2(p.rank))).join('');
    feedSlot.innerHTML = main + '<div class="feed-list">' + rows + '</div>';
  } else {
    feedSlot.innerHTML = '<div class="empty-state">아직 인기글이 없습니다.</div>';
  }

  const news = await fetchNews(4);
  document.getElementById('home-news').innerHTML = news.length
    ? news.map(renderNewsRow).join('')
    : '<div class="empty-state">아직 수집된 기사가 없습니다.</div>';

  const trainingVideos = await fetchVideos('training');
  const topTraining = trainingVideos.sort((a, b) => b.view_count - a.view_count).slice(0, 3);
  document.getElementById('training-cards').innerHTML = topTraining.length
    ? topTraining.map(renderVideoCard).join('')
    : '<div class="empty-state">아직 수집된 영상이 없습니다.</div>';

  const rankings = await fetchRankings();
  document.getElementById('ranking-rows').innerHTML = rankings.slice(0, 5).map(renderRankingRow).join('');
}

document.addEventListener('DOMContentLoaded', renderHome);
