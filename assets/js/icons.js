// 사이트 루트 경로 (로컬 서버에서는 '/', GitHub Pages에서는 '/저장소이름/')
// icons.js가 {루트}assets/js/에 있는 것을 이용해 어느 호스팅에서든 자동 계산된다.
const SITE_BASE = new URL('../../', document.currentScript.src).pathname;

const ICONS = {
  ball: '<circle cx="12" cy="12" r="8.5"/><path d="M12 6.2l3 2-1.1 3.2h-3.8L9 8.2z"/><path d="M12 14.7l3.4 2.5M9 14.7l-3 2.8M6 9.4l-3-.9M18 9.4l3-.9"/>',
  boot: '<path d="M12 3l6 16H6L12 3z"/><path d="M9 13h6M8 16.5h8"/>',
  chart: '<path d="M4 12h16M4 6h10M4 18h13"/>',
  video: '<rect x="3.5" y="6" width="17" height="12" rx="2"/><path d="M9.5 10.3v5.4l5-2.7z" fill="#fff" stroke="none"/>',
  person: '<circle cx="9" cy="8" r="3"/><path d="M4 19c0-3 2.2-5 5-5s5 2 5 5"/><path d="M16 9l2 2 3-4"/>',
  zigzag: '<path d="M4 16c4 0 4-8 8-8s4 8 8 8"/><circle cx="20" cy="8" r="1.4" fill="#fff" stroke="none"/>'
};

const PLAY_BADGE_SVG = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';

function iconSvg(key) {
  const inner = ICONS[key] || ICONS.ball;
  return '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.4">' + inner + '</svg>';
}

function thumbHtml(post, opts) {
  opts = opts || {};
  const sizeClass = opts.sm ? ' -sm' : '';
  const badgeStyle = opts.sm ? ' style="width:18px;height:18px;bottom:5px;right:5px;"' : '';
  const badge = post.video
    ? '<div class="play-badge"' + badgeStyle + '>' + PLAY_BADGE_SVG + '</div>'
    : '';
  return '<div class="photo-thumb' + sizeClass + '">' + iconSvg(post.icon) + badge + '</div>';
}

function ytChip() {
  return '<span class="yt-chip">' + PLAY_BADGE_SVG + '</span>';
}

function formatViews(n) {
  if (n >= 10000) return (n / 10000).toFixed(1).replace(/\.0$/, '') + '만';
  if (n >= 1000) return (n / 1000).toFixed(1).replace(/\.0$/, '') + '천';
  return String(n);
}
