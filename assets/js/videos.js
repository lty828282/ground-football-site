const SECTION_META = {
  training: { label: '축구 훈련', desc: '축구 훈련·스킬·트레이닝 인기 영상과 최신 영상 (한글·영어 검색)' },
  youth: { label: '유소년 축구', desc: '유소년 축구 관련 인기 영상과 최신 영상' },
  review: { label: '축구화 리뷰', desc: '축구화 리뷰 인기 영상과 최신 영상 (한글·영어 검색)' }
};

async function renderVideos() {
  const params = new URLSearchParams(window.location.search);
  const section = params.get('section') || 'training';
  const meta = SECTION_META[section] || SECTION_META.training;

  document.title = meta.label + ' — 그라운드';
  document.getElementById('crumb-label').textContent = meta.label;
  document.getElementById('videos-title').textContent = meta.label;
  document.getElementById('videos-desc').textContent = meta.desc;

  const videos = await fetchVideos(section);
  const topSlot = document.getElementById('top-videos');
  const recentSlot = document.getElementById('recent-videos');

  if (!videos.length) {
    const empty = '<div class="empty-state">아직 수집된 영상이 없습니다. 잠시 후 다시 확인해주세요.</div>';
    topSlot.innerHTML = empty;
    recentSlot.innerHTML = empty;
    return;
  }

  const byViews = videos.slice().sort((a, b) => b.view_count - a.view_count).slice(0, 10);
  const topIds = new Set(byViews.map((v) => v.video_id));
  const byRecent = videos
    .filter((v) => !topIds.has(v.video_id))
    .sort((a, b) => new Date(b.published_at) - new Date(a.published_at))
    .slice(0, 10);

  topSlot.innerHTML = byViews.map(renderVideoCard).join('');
  recentSlot.innerHTML = byRecent.length
    ? byRecent.map(renderVideoCard).join('')
    : '<div class="empty-state">최근 업로드 영상이 없습니다.</div>';

  const fetched = videos[0].fetched_at;
  if (fetched) {
    document.getElementById('videos-updated').textContent = '마지막 갱신: ' + timeAgo(fetched);
  }
}

document.addEventListener('DOMContentLoaded', renderVideos);
