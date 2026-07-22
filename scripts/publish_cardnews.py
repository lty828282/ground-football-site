#!/usr/bin/env python3
# 카드뉴스 자동 발행 스크립트
#
# 하는 일 (하루 1회):
#   1. assets/data/cardnews-queue.json 의 queue 맨 앞에서 카드뉴스 1편을 꺼낸다
#   2. Pexels API로 주제에 맞는 무료 훈련 사진 1장을 받아 assets/img/cardnews/<slug>.jpg 로 저장
#   3. pages/cardnews-<slug>.html 페이지를 템플릿으로 생성
#   4. pages/guides.html 의 카드뉴스 목록(마커 사이)을 다시 만들어 새 글을 노출
#   5. 발행한 항목을 queue → published(맨 앞)로 옮겨 저장
#
# 사전 준비:
#   - GitHub 저장소 Secrets 에 PEXELS_API_KEY 등록 (https://www.pexels.com/api/ 무료 발급)
#   - 로컬 실행 예:
#       export PEXELS_API_KEY="..."
#       python3 scripts/publish_cardnews.py
#
# 옵션:
#   --dry-run   실제 파일/큐를 바꾸지 않고 생성 결과만 /tmp 에 써서 미리보기
#   --no-photo  사진 없이 발행(단색 배경 + 기존 SVG 모티프). API 키가 없거나 실패해도 자동 적용됨
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

# 본문 카드 배경색 순환 팔레트
INNER_COLORS = ["#2E7D52", "#B5651D", "#3A6B8A", "#8A5A16", "#5B7C5A", "#4E6157", "#1B4332"]
CLOSING_COLOR = "#12261E"

LIST_START = "<!-- CARDNEWS_LIST:START"
LIST_END = "<!-- CARDNEWS_LIST:END -->"


def load_queue():
    with open(QUEUE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_queue(data):
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def fetch_photo(query, slug, dry_run=False):
    """Pexels 에서 사진 1장을 받아 저장하고 (상대경로, 크레딧) 반환. 실패 시 (None, None)."""
    if not PEXELS_API_KEY:
        print("  · PEXELS_API_KEY 없음 → 사진 없이 발행", file=sys.stderr)
        return None, None
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({
        "query": query,
        "per_page": 15,
        "orientation": "landscape",
        "size": "medium",
    })
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_API_KEY})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            payload = json.load(res)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
        print("  · Pexels 검색 실패(%s) → 사진 없이 발행" % e, file=sys.stderr)
        return None, None

    photos = payload.get("photos") or []
    if not photos:
        print("  · '%s' 검색 결과 없음 → 사진 없이 발행" % query, file=sys.stderr)
        return None, None

    photo = photos[0]
    src = photo.get("src") or {}
    img_url = src.get("large2x") or src.get("large") or src.get("original")
    if not img_url:
        return None, None

    os.makedirs(IMG_DIR, exist_ok=True)
    dest = os.path.join(IMG_DIR if not dry_run else "/tmp", slug + ".jpg")
    try:
        with urllib.request.urlopen(img_url, timeout=60) as res:
            data = res.read()
        with open(dest, "wb") as f:
            f.write(data)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print("  · 사진 다운로드 실패(%s) → 사진 없이 발행" % e, file=sys.stderr)
        return None, None

    credit = {
        "photographer": photo.get("photographer") or "Pexels",
        "photographer_url": photo.get("photographer_url") or "https://www.pexels.com",
    }
    print("  · 사진 저장: %s (© %s / Pexels)" % (os.path.basename(dest), credit["photographer"]))
    return "../assets/img/cardnews/%s.jpg" % slug, credit


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def esc_br(s):
    """<br> 은 그대로 두고 나머지만 이스케이프."""
    parts = (s or "").split("<br>")
    return "<br>".join(esc(p) for p in parts)


def render_page(entry, photo_rel, credit):
    slug = entry["slug"]
    theme = entry.get("theme", "#1B4332")
    kicker = esc(entry.get("kicker", "GROUND YOUTH"))

    if photo_rel:
        cover_open = ('    <div class="cn-card cover cn-photo" '
                      'style="background-color:%s;background-image:url(\'%s\')">' % (theme, photo_rel))
    else:
        cover_open = '    <div class="cn-card cover" style="background:%s">' % theme

    cards_html = []
    cards_html.append(cover_open)
    cards_html.append('      <div class="cn-kicker">%s</div>' % kicker)
    cards_html.append('      <h2>%s</h2>' % esc_br(entry["coverTitle"]))
    cards_html.append('      <p>%s</p>' % esc_br(entry["coverSub"]))
    cards_html.append('      <div class="cn-brand">그라<em>운</em>드 유소년</div>')
    cards_html.append('    </div>')

    inner_palette = [c for c in INNER_COLORS if c != theme] or INNER_COLORS
    for i, card in enumerate(entry["cards"]):
        color = inner_palette[i % len(inner_palette)]
        cards_html.append('')
        cards_html.append('    <div class="cn-card" style="background:%s">' % color)
        cards_html.append('      <div class="cn-no">%02d</div>' % (i + 1))
        cards_html.append('      <h2>%s</h2>' % esc_br(card["title"]))
        cards_html.append('      <p>%s</p>' % esc_br(card["body"]))
        cards_html.append('      <div class="cn-brand">그라<em>운</em>드 유소년</div>')
        cards_html.append('    </div>')

    cards_html.append('')
    cards_html.append('    <div class="cn-card" style="background:%s">' % CLOSING_COLOR)
    cards_html.append('      <div class="cn-kicker">기억하세요</div>')
    cards_html.append('      <h2>%s</h2>' % esc_br(entry["closingTitle"]))
    cards_html.append('      <p>%s</p>' % esc_br(entry["closingBody"]))
    cards_html.append('      <div class="cn-brand">그라<em>운</em>드 유소년 · groundyouth.com</div>')
    cards_html.append('    </div>')

    credit_html = ""
    if photo_rel and credit:
        credit_html = ('\n  <div class="cn-credit">사진 © <a href="%s" target="_blank" rel="noopener">%s</a> / Pexels</div>\n'
                       % (esc(credit["photographer_url"]), esc(credit["photographer"])))

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

  <div class="cardnews">
    <div class="cn-hint">📱 각 카드를 이미지로 저장해 공유해 보세요</div>

{cards}
  </div>
{credit}
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
        cards="\n".join(cards_html),
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
    # 마커 라인의 끝(개행)까지 포함해 교체
    start_line_end = html.find("\n", start)
    items = "\n".join(render_list_item(e) for e in published)
    new_block = (
        html[:start_line_end + 1]
        + items + "\n"
        + "      " + html[end:]
    )
    with open(GUIDES_PATH, "w", encoding="utf-8") as f:
        f.write(new_block)


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
    print("발행: %s (%s)" % (entry["listTitle"], slug))

    photo_rel, credit = (None, None)
    if not args.no_photo:
        photo_rel, credit = fetch_photo(entry.get("photoQuery", entry["listTitle"]), slug, dry_run=args.dry_run)

    page_html = render_page(entry, photo_rel, credit)

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

    # 발행 완료 항목을 목록용 최소 정보로 published 맨 앞에 추가
    published_item = {
        "slug": slug,
        "generated": True,
        "theme": entry.get("theme", "#1B4332"),
        "listTitle": entry["listTitle"],
        "listDesc": entry["listDesc"],
    }
    if credit:
        published_item["photoCredit"] = credit
    data["published"].insert(0, published_item)
    data["queue"] = queue[1:]
    save_queue(data)

    rewrite_guides_list(data["published"])
    print("가이드 목록 갱신 완료. 남은 큐: %d편" % len(data["queue"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
