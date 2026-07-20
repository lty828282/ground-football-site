const EMPTY_ROW =
  '<tr><td colspan="5" class="empty-cell">아직 수집된 채널이 없습니다. sync_youth_channels.py 실행 후 표시됩니다.</td></tr>';

async function renderRankingPage() {
  const channels = await fetchYouthChannels();
  const subsSlot = document.getElementById('youth-subs-rows');
  const recentSlot = document.getElementById('youth-recent-rows');

  if (!channels.length) {
    subsSlot.innerHTML = EMPTY_ROW;
    recentSlot.innerHTML = EMPTY_ROW;
    return;
  }

  const bySubs = channels
    .slice()
    .sort((a, b) => (b.subs_count || 0) - (a.subs_count || 0));
  subsSlot.innerHTML = bySubs.map((ch, i) => renderYouthSubsRow(ch, i + 1)).join('');

  const byRecent = channels
    .filter((ch) => ch.latest_upload_at)
    .sort((a, b) => new Date(b.latest_upload_at) - new Date(a.latest_upload_at))
    .slice(0, 15);
  recentSlot.innerHTML = byRecent.length
    ? byRecent.map((ch, i) => renderYouthRecentRow(ch, i + 1)).join('')
    : EMPTY_ROW;
}

document.addEventListener('DOMContentLoaded', renderRankingPage);
