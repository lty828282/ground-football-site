async function renderNews() {
  const articles = await fetchNews(12);
  const list = document.getElementById('news-list');

  if (!articles.length) {
    list.innerHTML = '<div class="empty-state">아직 수집된 기사가 없습니다. 잠시 후 다시 확인해주세요.</div>';
    return;
  }

  list.innerHTML = articles.map(renderNewsRow).join('');

  const fetched = articles[0].fetched_at;
  if (fetched) {
    document.getElementById('news-updated').textContent = '마지막 갱신: ' + timeAgo(fetched);
  }
}

document.addEventListener('DOMContentLoaded', renderNews);
