// 홈 진입 유도 배너(비침투형)
// - 화면을 덮지 않는 우측 하단 슬라이드인 카드(닫기 가능·지연 노출)
// - 목적 ① 인스타 팔로우 유도  ② 새 카드뉴스로 내부 회유(광고 노출↑)
// - 한 번 닫으면 7일간 다시 안 뜸(localStorage), 세션당 1회만
// SEO/애드센스 안전: 콘텐츠를 가리는 전면 팝업이 아니라 작은 배너.

(function () {
  var IG_URL = 'https://www.instagram.com/groundyouth/'; // 인스타 핸들 바뀌면 이 줄만 수정
  var KEY = 'gy_promo_v1';
  var DELAY_MS = 7000;      // 7초 뒤 노출(진입 즉시 아님)
  var COOLDOWN_DAYS = 7;    // 닫은 뒤 재노출까지 대기일

  function base() {
    return (typeof SITE_BASE !== 'undefined' && SITE_BASE) ? SITE_BASE : '/';
  }
  function dismissedRecently() {
    try {
      var v = localStorage.getItem(KEY);
      if (!v) return false;
      var t = parseInt(v, 10);
      if (!t) return false;
      return (Date.now() - t) < COOLDOWN_DAYS * 86400000;
    } catch (e) { return false; }
  }
  function remember() {
    try { localStorage.setItem(KEY, String(Date.now())); } catch (e) {}
  }

  function injectStyle() {
    if (document.getElementById('gy-promo-style')) return;
    var css = ''
      + '.gy-promo{position:fixed;right:20px;bottom:20px;z-index:900;width:330px;max-width:calc(100vw - 32px);'
      + 'background:#12261E;color:#fff;border-radius:16px;overflow:hidden;'
      + 'box-shadow:0 14px 40px rgba(0,0,0,.32);border:1px solid rgba(255,213,79,.25);'
      + 'font-family:Pretendard,-apple-system,"Malgun Gothic",sans-serif;'
      + 'transform:translateY(140%);opacity:0;transition:transform .45s cubic-bezier(.2,.8,.2,1),opacity .45s;}'
      + '.gy-promo.on{transform:translateY(0);opacity:1;}'
      + '.gy-promo .gp-x{position:absolute;top:8px;right:10px;width:26px;height:26px;border:0;cursor:pointer;'
      + 'background:rgba(255,255,255,.12);color:#fff;border-radius:50%;font-size:15px;line-height:26px;text-align:center;padding:0;}'
      + '.gy-promo .gp-x:hover{background:rgba(255,255,255,.22);}'
      + '.gy-promo .gp-head{padding:15px 18px 4px;font-size:12px;font-weight:900;letter-spacing:2px;}'
      + '.gy-promo .gp-head b{color:#fff;} .gy-promo .gp-head i{color:#E8A33D;font-style:normal;}'
      + '.gy-promo .gp-ig{display:flex;align-items:center;gap:12px;padding:8px 18px 14px;}'
      + '.gy-promo .gp-ig .gp-ic{flex:none;width:40px;height:40px;border-radius:12px;'
      + 'background:linear-gradient(45deg,#F58529,#DD2A7B 45%,#8134AF 75%,#515BD4);display:flex;align-items:center;justify-content:center;}'
      + '.gy-promo .gp-ig .gp-ic svg{width:22px;height:22px;fill:#fff;}'
      + '.gy-promo .gp-ig .gp-t{flex:1;font-size:13.5px;line-height:1.4;color:#e7f2ea;}'
      + '.gy-promo .gp-follow{display:block;text-align:center;margin:0 18px 14px;padding:11px 0;border-radius:10px;'
      + 'background:#E8A33D;color:#12261E;font-weight:900;font-size:14.5px;text-decoration:none;}'
      + '.gy-promo .gp-follow:hover{filter:brightness(1.06);}'
      + '.gy-promo .gp-rec{display:flex;align-items:center;gap:12px;padding:12px 16px;text-decoration:none;'
      + 'background:#0d1c16;border-top:1px solid rgba(255,255,255,.08);}'
      + '.gy-promo .gp-rec:hover{background:#0a1712;}'
      + '.gy-promo .gp-rec img{flex:none;width:52px;height:65px;object-fit:cover;border-radius:8px;background:#1B4332;}'
      + '.gy-promo .gp-rec .gp-rt{flex:1;min-width:0;}'
      + '.gy-promo .gp-rec .gp-cap{font-size:11px;font-weight:800;letter-spacing:.5px;color:#7ED957;margin-bottom:3px;}'
      + '.gy-promo .gp-rec .gp-rti{font-size:13.5px;font-weight:700;color:#fff;line-height:1.35;'
      + 'display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}'
      + '.gy-promo .gp-rec .gp-go{flex:none;color:#E8A33D;font-weight:900;font-size:16px;}'
      + '@media(max-width:520px){.gy-promo{right:12px;left:12px;bottom:12px;width:auto;}}';
    var st = document.createElement('style');
    st.id = 'gy-promo-style';
    st.textContent = css;
    document.head.appendChild(st);
  }

  var IG_SVG = '<svg viewBox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.9.07 1.2.06 1.8.25 2.2.42.6.2 1 .46 1.4.9.44.4.7.8.9 1.4.17.4.36 1 .42 2.2.06 1.3.07 1.7.07 4.9s0 3.6-.07 4.9c-.06 1.2-.25 1.8-.42 2.2-.2.6-.46 1-.9 1.4-.4.44-.8.7-1.4.9-.4.17-1 .36-2.2.42-1.3.06-1.7.07-4.9.07s-3.6 0-4.9-.07c-1.2-.06-1.8-.25-2.2-.42-.6-.2-1-.46-1.4-.9-.44-.4-.7-.8-.9-1.4-.17-.4-.36-1-.42-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.07-4.9c.06-1.2.25-1.8.42-2.2.2-.6.46-1 .9-1.4.4-.44.8-.7 1.4-.9.4-.17 1-.36 2.2-.42C8.4 2.2 8.8 2.2 12 2.2zm0 1.8c-3.1 0-3.5 0-4.7.07-.9.04-1.4.2-1.7.32-.43.17-.74.37-1.06.7-.32.32-.52.63-.7 1.06-.12.3-.28.8-.32 1.7C3.25 8.5 3.24 8.9 3.24 12s0 3.5.07 4.7c.04.9.2 1.4.32 1.7.17.43.37.74.7 1.06.32.32.63.52 1.06.7.3.12.8.28 1.7.32 1.2.07 1.6.07 4.7.07s3.5 0 4.7-.07c.9-.04 1.4-.2 1.7-.32.43-.17.74-.37 1.06-.7.32-.32.52-.63.7-1.06.12-.3.28-.8.32-1.7.07-1.2.07-1.6.07-4.7s0-3.5-.07-4.7c-.04-.9-.2-1.4-.32-1.7-.17-.43-.37-.74-.7-1.06-.32-.32-.63-.52-1.06-.7-.3-.12-.8-.28-1.7-.32C15.5 4 15.1 4 12 4zm0 3.06A4.94 4.94 0 1 0 12 16.94 4.94 4.94 0 0 0 12 7.06zm0 8.15A3.2 3.2 0 1 1 12 8.8a3.2 3.2 0 0 1 0 6.4zm6.3-8.35a1.15 1.15 0 1 1-2.3 0 1.15 1.15 0 0 1 2.3 0z"/></svg>';

  function build(rec) {
    injectStyle();
    var wrap = document.createElement('aside');
    wrap.className = 'gy-promo';
    wrap.setAttribute('role', 'complementary');
    wrap.setAttribute('aria-label', '그라운드 유소년 소식 받기');

    var recHtml = '';
    if (rec) {
      var href = base() + 'pages/cardnews-' + rec.slug + '.html';
      var thumb = base() + 'exports/' + rec.slug + '/slide1.jpg';
      recHtml =
        '<a class="gp-rec" href="' + href + '">' +
        '<img src="' + thumb + '" alt="" onerror="this.style.display=\'none\'">' +
        '<span class="gp-rt"><span class="gp-cap">새 카드뉴스</span>' +
        '<span class="gp-rti">' + escapeHtml(rec.listTitle || '카드뉴스 보러가기') + '</span></span>' +
        '<span class="gp-go">→</span></a>';
    }

    wrap.innerHTML =
      '<button class="gp-x" aria-label="닫기">✕</button>' +
      '<div class="gp-head"><b>GROUND</b> <i>YOUTH</i></div>' +
      '<div class="gp-ig">' +
        '<span class="gp-ic">' + IG_SVG + '</span>' +
        '<span class="gp-t">매일 유소년 축구 카드뉴스·릴스를<br>인스타에서 먼저 만나보세요</span>' +
      '</div>' +
      '<a class="gp-follow" href="' + IG_URL + '" target="_blank" rel="noopener">인스타그램 팔로우 →</a>' +
      recHtml;

    document.body.appendChild(wrap);
    requestAnimationFrame(function () { wrap.classList.add('on'); });

    function close() { remember(); wrap.classList.remove('on'); setTimeout(function () { wrap.remove(); }, 450); }
    wrap.querySelector('.gp-x').addEventListener('click', close);
    // 팔로우/추천 클릭도 '봤음'으로 처리(재노출 방지)
    var links = wrap.querySelectorAll('a');
    for (var i = 0; i < links.length; i++) links[i].addEventListener('click', remember);
  }

  function escapeHtml(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function newestCardnews() {
    return fetch(base() + 'assets/data/cardnews-queue.json')
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var pub = (d && d.published) || [];
        return pub.length ? pub[0] : null;   // published[0] = 가장 최신
      })
      .catch(function () { return null; });
  }

  function start() {
    if (dismissedRecently()) return;
    try { if (sessionStorage.getItem(KEY + '_seen')) return; } catch (e) {}
    setTimeout(function () {
      try { sessionStorage.setItem(KEY + '_seen', '1'); } catch (e) {}
      newestCardnews().then(build);
    }, DELAY_MS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
