async function renderRankingPage() {
  const rankings = await fetchRankings();
  document.getElementById('ranking-rows-full').innerHTML = rankings.map(renderRankingRow).join('');
}

document.addEventListener('DOMContentLoaded', renderRankingPage);
