#!/usr/bin/env python3
# 카드뉴스 자동 발행 스크립트 (인스타 캐러셀 스타일 · 풀사진 배경)
#
# 하는 일 (하루 1회):
#   1. assets/data/cardnews-queue.json 의 queue 맨 앞에서 카드뉴스 1편을 꺼낸다
#   2. Pexels API로 주제에 맞는 무료 축구 사진을 슬라이드 수만큼 받아
#      assets/img/cardnews/<slug>-0.jpg ... 로 저장(슬라이드마다 다른 사진)
#   3. pages/cardnews-<slug>.html 페이지를 인스타 캐러셀 템플릿으로 생성
#   4. pages/guides.html 의 카드뉴스 목록(마커 사이)을 다시 만들어 새 글을 노출
#   5. 발행한 항목을 queue → published(맨 앞)로 옮겨 저장
#
# 사전 준비:
#   - GitHub 저장소 Secrets 에 PEXELS_API_KEY 등록 (https://www.pexels.com/api/ 무료 발급)
#   - 로컬 실행 예:  export PEXELS_API_KEY="..." ; python3 scripts/publish_cardnews.py
#
# 옵션:
#   --dry-run   실제 파일/큐를 바꾸지 않고 생성 결과만 /tmp 에 써서 미리보기
#   --no-photo  사진 없이 발행(단색 배경). API 키가 없거나 실패해도 자동 적용됨
#
# 참고: Pexels 라이선스는 상업적 사용 무료·출처 표기 의무 없음(표기는 권장). 애드센스 사이트에 안전.

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_PATH = os.path.join(ROOT, "assets", "data", "cardnews-queue.json")
GUIDES_PATH = os.path.join(ROOT, "pages", "guides.html")
PAGES_DIR = os.path.join(ROOT, "pages")
IMG_DIR = os.path.join(ROOT, "assets", "img", "cardnews")

PEXELS_API_KEY = (os.environ.get("PEXELS_API_KEY") or "").strip()
# Cloudflare(에러 1010)가 기본 파이썬 UA를 차단하므로 브라우저 UA 사용
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"

# 카드 위에 들어가는 브랜딩(그라운드 유소년)
HANDLE = "groundyouth.com"
WORDMARK = "GROUND YOUTH"

# 주제별 디자인 컨셉(스킨). queue 항목의 "concept" 로 선택.
#   cls    : 카드에 붙는 테마 클래스("" 는 기본 그린)
#   photo  : 기본적으로 사진 배경을 쓸지(False 면 플랫 배경+피치 모티프, Pexels 불필요)
#   series : 카드 좌상단 시리즈 라벨 기본값(항목 "series" 로 덮어쓰기 가능)
CONCEPTS = {
    "green":    {"cls": "",             "photo": True,  "series": "GROUND YOUTH CLASS"},
    "navy":     {"cls": "cnx-navy",     "photo": True,  "series": "MINDSET NOTE"},
    "tactics":  {"cls": "cnx-tactics",  "photo": True,  "series": "TACTICS NOTE"},
    "training": {"cls": "cnx-training", "photo": True,  "series": "TRAINING CLASS"},
    "match":    {"cls": "cnx-match",    "photo": True,  "series": "MATCH ANALYSIS"},
    "insight":  {"cls": "cnx-insight",  "photo": True,  "series": "SCOUTING INSIGHT", "frame": True,
                 "rails": ("DEFINE · DEVELOP · DELIVER", "YOUTH · GROWTH · FUTURE")},
}

# 축구 아이콘 스프라이트(페이지 기준 상대경로). 라벨은 큐에서 지정.
ICON_SPRITE = "../assets/img/football-icons.svg"

LIST_START = "<!-- CARDNEWS_LIST:START"
LIST_END = "<!-- CARDNEWS_LIST:END -->"


def load_queue():
    with open(QUEUE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_queue(data):
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def fetch_photos(query, slug, count, dry_run=False):
    """Pexels 에서 사진을 받아 슬라이드 수(count)만큼 매핑. (relpath 리스트, 촬영자 리스트) 반환."""
    if not PEXELS_API_KEY:
        print("  · PEXELS_API_KEY 없음 → 사진 없이 발행", file=sys.stderr)
        return [], []

    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({
        "query": query,
        "per_page": min(80, max(count + 6, 15)),
        "orientation": "portrait",
        "size": "medium",
    })
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_API_KEY, "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            payload = json.load(res)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
        print("  · Pexels 검색 실패(%s) → 사진 없이 발행" % e, file=sys.stderr)
        return [], []

    photos = payload.get("photos") or []
    if not photos:
        print("  · '%s' 검색 결과 없음 → 사진 없이 발행" % query, file=sys.stderr)
        return [], []

    dest_dir = IMG_DIR if not dry_run else "/tmp"
    os.makedirs(dest_dir, exist_ok=True)

    n_unique = min(count, len(photos))
    files, credits = [], []
    for k in range(n_unique):
        src = photos[k].get("src") or {}
        img_url = src.get("large2x") or src.get("large") or src.get("portrait") or src.get("original")
        if not img_url:
            continue
        fn = "%s-%d.jpg" % (slug, k)
        try:
            ireq = urllib.request.Request(img_url, headers={"User-Agent": UA})
            with urllib.request.urlopen(ireq, timeout=60) as res:
                data = res.read()
            with open(os.path.join(dest_dir, fn), "wb") as f:
                f.write(data)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            print("  · 사진 다운로드 실패(%s)" % e, file=sys.stderr)
            continue
        files.append("../assets/img/cardnews/%s" % fn)
        credits.append(photos[k].get("photographer") or "Pexels")

    if not files:
        return [], []
    # 슬라이드 수만큼 순환 매핑(사진이 부족하면 앞에서부터 재사용)
    mapped = [files[i % len(files)] for i in range(count)]
    print("  · 사진 %d장 저장 (검색어: %s)" % (len(files), query))
    return mapped, credits


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def esc_br(s):
    return "<br>".join(esc(p) for p in (s or "").split("<br>"))


def fmt(s):
    """<br> 유지, HTML 이스케이프, **강조** → 포인트색 span."""
    out = []
    for part in (s or "").split("<br>"):
        p = esc(part)
        p = re.sub(r"\*\*(.+?)\*\*", r'<span class="cnx-hl">\1</span>', p)
        out.append(p)
    return "<br>".join(out)


def _dots(total, active):
    return ('<div class="cnx-dots">'
            + "".join('<i class="on"></i>' if i == active else "<i></i>" for i in range(total))
            + "</div>")


def _icon_grid(icons):
    if not icons:
        return ""
    cells = []
    for it in icons:
        cells.append(
            '          <div class="cnx-ic"><div class="box">'
            '<svg class="fi"><use href="%s#%s"></use></svg></div><small>%s</small></div>'
            % (ICON_SPRITE, esc(it.get("icon", "star")), fmt(it.get("label", "")))
        )
    return '\n        <div class="cnx-icongrid">\n' + "\n".join(cells) + "\n        </div>"


def _card_open(ctx, img):
    cls = "cnx-card" + (" " + ctx["cls"] if ctx["cls"] else "")
    cls += " cnx-flat" if ctx["flat"] else " cnx-photo"
    style = "" if (ctx["flat"] or not img) else ' style="background-image:url(\'%s\')"' % img
    extra = ""
    if ctx["flat"]:
        extra += '\n      <div class="cnx-motif"></div>'
    if ctx.get("frame"):
        extra += '\n      <div class="cnx-frame"></div>'
    for pos, txt in zip(("l", "r"), ctx.get("rails") or ()):
        extra += '\n      <div class="cnx-rail %s">%s</div>' % (pos, esc(txt))
    return '    <div class="%s"%s>%s' % (cls, style, extra)


def _top(ctx):
    return ('      <div class="cnx-top">\n'
            '        <span class="cnx-series"><i class="cnx-bar"></i>%s</span>\n'
            '        <span class="cnx-handle">%s</span>\n'
            '      </div>' % (esc(ctx["series"]), esc(HANDLE)))


def _bottom(total, active):
    return ('      <div class="cnx-bottom">\n'
            '        %s\n'
            '        <div class="cnx-mark">%s</div>\n'
            '      </div>' % (_dots(total, active), WORDMARK))


def _cover_card(entry, ctx, img, total):
    cta = entry.get("coverCta") or "저장해두고 다음 편도 확인하세요"
    main = ('      <div class="cnx-main">\n'
            '        <div class="cnx-kicker">%s</div>\n'
            '        <h2 class="cnx-title cnx-hook">%s</h2>\n'
            '        <span class="cnx-underline"></span>\n'
            '        <div class="cnx-sub">%s</div>\n'
            '        <div class="cnx-cta">%s</div>\n'
            '      </div>' % (fmt(entry.get("kicker", ctx["series"])), fmt(entry["coverTitle"]),
                              fmt(entry["coverSub"]), fmt(cta)))
    return "%s\n%s\n%s\n%s\n    </div>" % (_card_open(ctx, img), _top(ctx), main, _bottom(total, 0))


def _content_card(entry, ctx, card, number, img, total, active):
    main = ('      <div class="cnx-main">\n'
            '        <span class="cnx-tick"></span>\n'
            '        <div class="cnx-no">%02d</div>\n'
            '        <h2 class="cnx-title">%s</h2>\n'
            '        <p class="cnx-body">%s</p>%s\n'
            '      </div>' % (number, fmt(card["title"]), fmt(card["body"]), _icon_grid(card.get("icons"))))
    return "%s\n%s\n%s\n%s\n    </div>" % (_card_open(ctx, img), _top(ctx), main, _bottom(total, active))


def _closing_card(entry, ctx, img, total):
    cta = entry.get("closingCta") or ("팔로우하고 다음 카드뉴스 받아보세요 · %s" % HANDLE)
    quote = ""
    if entry.get("quote"):
        quote = '        <div class="cnx-quote"><span>%s</span></div>\n' % fmt(entry["quote"])
    main = ('      <div class="cnx-main">\n'
            '        <h2 class="cnx-title">%s</h2>\n'
            '        <span class="cnx-underline"></span>\n'
            '%s'
            '        <div class="cnx-sub">%s</div>\n'
            '        <div class="cnx-cta">%s</div>\n'
            '      </div>' % (fmt(entry["closingTitle"]), quote, fmt(entry["closingBody"]), fmt(cta)))
    return "%s\n%s\n%s\n%s\n    </div>" % (_card_open(ctx, img), _top(ctx), main, _bottom(total, total - 1))


def concept_ctx(entry):
    name = entry.get("concept", "green")
    conf = CONCEPTS.get(name, CONCEPTS["green"])
    return {
        "cls": conf["cls"],
        "flat": not bool(entry.get("photo", conf["photo"])),
        "series": entry.get("series") or conf["series"],
        "frame": conf.get("frame", False),
        "rails": conf.get("rails"),
    }


def render_page(entry, photos, credits):
    cards = entry["cards"]
    total = len(cards) + 2  # 커버 + 본문 + 마무리
    ctx = concept_ctx(entry)

    def img_at(i):
        return photos[i] if (photos and i < len(photos)) else None

    slides = [_cover_card(entry, ctx, img_at(0), total)]
    for j, card in enumerate(cards):
        slides.append(_content_card(entry, ctx, card, j + 1, img_at(j + 1), total, j + 1))
    slides.append(_closing_card(entry, ctx, img_at(total - 1), total))

    guide_html = ""
    if entry.get("guideSlug"):
        guide_html = ('\n  <div style="text-align:center;padding:0 20px 40px;">'
                      '<a class="guide-cta" href="/pages/guide-%s.html">📖 글로 자세히 읽기 →</a></div>\n'
                      % esc(entry["guideSlug"]))

    credit_html = ""
    if credits:
        uniq = list(dict.fromkeys(credits))
        credit_html = ('\n  <div class="cn-credit">사진 © %s / <a href="https://www.pexels.com" target="_blank" rel="noopener">Pexels</a></div>\n'
                       % esc(", ".join(uniq)))

    return """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{metaTitle} | 그라운드 유소년</title>
<meta name="description" content="{metaDesc}">
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css">
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>

  <div id="site-header"></div>

  <div class="page-hero">
    <div class="breadcrumb"><a href="/index.html">홈</a> / <a href="/pages/guides.html">가이드</a> / <span>카드뉴스</span></div>
    <h1>{h1} · 카드뉴스</h1>
  </div>

  <div class="cnx-wrap">
    <div class="cnx-hint">📱 각 카드를 이미지로 저장해 공유해 보세요</div>

{slides}
  </div>
{guide}{credit}
  <div id="site-footer"></div>

  <script src="../assets/js/icons.js"></script>
  <script src="../assets/js/render.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.js"></script>
  <script src="../assets/js/supabase-client.js"></script>
  <script src="../assets/js/common.js"></script>
</body>
</html>
""".format(
        metaTitle=esc(entry["metaTitle"]),
        metaDesc=esc(entry["metaDesc"]),
        h1=esc(entry["listTitle"]),
        slides="\n".join(slides),
        guide=guide_html,
        credit=credit_html,
    )


def render_list_item(entry):
    return (
        '      <a class="guide-card" href="/pages/cardnews-{slug}.html">\n'
        '        <div class="gc-top" style="background:{theme}"></div>\n'
        '        <div class="gc-body">\n'
        '          <div class="gc-cat">카드뉴스</div>\n'
        '          <h3>{title}</h3>\n'
        '          <p>{desc}</p>\n'
        '          <div class="gc-more">카드뉴스 보기 →</div>\n'
        '        </div>\n'
        '      </a>'
    ).format(
        slug=entry["slug"],
        theme=entry.get("theme", "#1B4332"),
        title=esc(entry["listTitle"]),
        desc=esc(entry["listDesc"]),
    )


def rewrite_guides_list(published):
    with open(GUIDES_PATH, encoding="utf-8") as f:
        html = f.read()
    start = html.find(LIST_START)
    end = html.find(LIST_END)
    if start == -1 or end == -1:
        raise SystemExit("guides.html 에서 CARDNEWS_LIST 마커를 찾지 못했습니다.")
    start_line_end = html.find("\n", start)
    items = "\n".join(render_list_item(e) for e in published)
    new_html = html[:start_line_end + 1] + items + "\n      " + html[end:]
    with open(GUIDES_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="파일/큐를 바꾸지 않고 미리보기만")
    ap.add_argument("--no-photo", action="store_true", help="사진 없이 발행")
    args = ap.parse_args()

    data = load_queue()
    queue = data.get("queue", [])
    if not queue:
        print("발행할 카드뉴스가 큐에 없습니다. cardnews-queue.json 의 queue 에 항목을 추가하세요.")
        return 0

    entry = queue[0]
    slug = entry["slug"]
    slide_count = len(entry["cards"]) + 2
    ctx = concept_ctx(entry)
    print("발행: %s (%s) · 컨셉 %s · 슬라이드 %d장" % (entry["listTitle"], slug, entry.get("concept", "green"), slide_count))

    photos, credits = ([], [])
    if not args.no_photo and not ctx["flat"]:
        photos, credits = fetch_photos(entry.get("photoQuery", entry["listTitle"]), slug, slide_count, dry_run=args.dry_run)

    page_html = render_page(entry, photos, credits)

    if args.dry_run:
        preview = os.path.join("/tmp", "cardnews-%s.html" % slug)
        with open(preview, "w", encoding="utf-8") as f:
            f.write(page_html)
        print("[dry-run] 페이지 미리보기: %s" % preview)
        print("[dry-run] 큐/목록은 변경하지 않았습니다.")
        return 0

    page_path = os.path.join(PAGES_DIR, "cardnews-%s.html" % slug)
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(page_html)
    print("페이지 생성: pages/cardnews-%s.html" % slug)

    published_item = {
        "slug": slug,
        "generated": True,
        "theme": entry.get("theme", "#1B4332"),
        "listTitle": entry["listTitle"],
        "listDesc": entry["listDesc"],
    }
    if credits:
        published_item["photoCredit"] = list(dict.fromkeys(credits))
    data["published"].insert(0, published_item)
    data["queue"] = queue[1:]
    save_queue(data)

    rewrite_guides_list(data["published"])
    print("가이드 목록 갱신 완료. 남은 큐: %d편" % len(data["queue"]))

    # 새 페이지가 색인되도록 sitemap 갱신
    try:
        import gen_sitemap
        gen_sitemap.main()
    except Exception as e:  # noqa
        print("  · sitemap 갱신 건너뜀(%s)" % e, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
