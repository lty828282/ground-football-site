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

const POPULAR_WINDOWS = [
  { days: 1, label: '최근 24시간 기준' },
  { days: 3, label: '최근 3일 기준' },
  { days: 7, label: '최근 일주일 기준' },
  { days: 30, label: '최근 한 달 기준' },
];

// 최근 일주일 이내 영상 중 인기순으로 뽑되, 모자라면 기간을 넓혀가며 채운다
function pickWeeklyPopular(videos, count) {
  const WINDOWS_DAYS = [7, 14, 30];
  for (const days of WINDOWS_DAYS) {
    const cutoff = Date.now() - days * 86400000;
    const pool = videos.filter(
      (v) => v.published_at && new Date(v.published_at).getTime() >= cutoff
    );
    if (pool.length >= count) {
      return pool.sort((a, b) => b.view_count - a.view_count).slice(0, count);
    }
  }
  return videos.slice().sort((a, b) => b.view_count - a.view_count).slice(0, count);
}

// 최근 하루 영상 중 인기순으로 뽑되, 영상이 모자라면 기간을 넓혀가며 채운다
function pickRecentPopular(allVideos, count) {
  for (const w of POPULAR_WINDOWS) {
    const cutoff = Date.now() - w.days * 86400000;
    const pool = allVideos.filter(
      (v) => v.published_at && new Date(v.published_at).getTime() >= cutoff
    );
    if (pool.length >= count) {
      return {
        videos: pool.sort((a, b) => b.view_count - a.view_count).slice(0, count),
        label: w.label,
      };
    }
  }
  return {
    videos: allVideos.slice().sort((a, b) => b.view_count - a.view_count).slice(0, count),
    label: '전체 기간 기준',
  };
}

function renderPopularFeed(allVideos, news) {
  const feedSlot = document.getElementById('popular-feed');
  const picked = pickRecentPopular(allVideos, 3);
  const note = document.getElementById('popular-window-note');
  if (note) note.textContent = picked.label;
  const topNews = news.slice(0, 2);
  const items = picked.videos.map(videoToFeedItem).concat(topNews.map(newsToFeedItem));

  if (!items.length) {
    feedSlot.innerHTML = '<div class="empty-state">아직 인기 콘텐츠가 없습니다.</div>';
    return;
  }

  const main = renderPopularMain(items[0]);
  const rows = items.slice(1).map((item, i) => renderPopularRow(item, pad2(i + 2))).join('');
  feedSlot.innerHTML = main + '<div class="feed-list">' + rows + '</div>';
}

async function renderHome() {
  const [trainingVideos, youthVideos, reviewVideos, news, channels] = await Promise.all([
    fetchVideos('training'),
    fetchVideos('youth'),
    fetchVideos('review'),
    fetchNews(4),
    fetchYouthChannels(),
  ]);

  renderPopularFeed(youthVideos.concat(trainingVideos, reviewVideos), news);

  document.getElementById('home-news').innerHTML = news.length
    ? news.map(renderNewsRow).join('')
    : '<div class="empty-state">아직 수집된 기사가 없습니다.</div>';

  const topYouth = pickWeeklyPopular(youthVideos, 3);
  document.getElementById('youth-cards').innerHTML = topYouth.length
    ? topYouth.map(renderVideoCard).join('')
    : '<div class="empty-state">아직 수집된 영상이 없습니다.</div>';

  const topChannels = channels
    .slice()
    .sort((a, b) => (b.subs_count || 0) - (a.subs_count || 0))
    .slice(0, 5);
  document.getElementById('ranking-rows').innerHTML = topChannels.length
    ? topChannels.map((ch, i) => renderYouthSubsRow(ch, i + 1)).join('')
    : '<tr><td colspan="5" class="empty-cell">아직 수집된 채널이 없습니다.</td></tr>';
}

document.addEventListener('DOMContentLoaded', renderHome);
