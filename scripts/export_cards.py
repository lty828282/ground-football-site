#!/usr/bin/env python3
"""카드뉴스 페이지의 각 카드를 인스타그램용 PNG(1080x1350, 4:5)로 추출한다.

사용법:
    python3 scripts/export_cards.py intro
    python3 scripts/export_cards.py soccer-shoes

러너에서 실제 폰트·사진 그대로 렌더되며, exports/<slug>/slideN.png 로 저장된다.
로컬 샌드박스에는 Playwright가 없으므로 GitHub Actions(export-cards.yml)에서 실행한다.
"""
import sys
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent

# 인스타 세로 규격 1080x1350 = 540x675 @2x
CARD_W = 540
SCALE = 2

# 카드 캡처용 오버라이드: 둥근 모서리·여백·그림자 제거, 폭 고정
INJECT_CSS = """
.cnx-hint,.cnx-hint{display:none!important;}
.cnx-wrap{max-width:none!important;padding:0!important;margin:0!important;}
.cnx-card{
  width:%dpx!important;max-width:none!important;
  border-radius:0!important;margin:0!important;box-shadow:none!important;
}
body{background:#000!important;}
""" % CARD_W


def main():
    if len(sys.argv) < 2:
        print("usage: export_cards.py <slug>")
        sys.exit(1)
    slug = sys.argv[1].strip()
    page_path = ROOT / "pages" / f"cardnews-{slug}.html"
    if not page_path.exists():
        print(f"NOT FOUND: {page_path}")
        sys.exit(1)

    out_dir = ROOT / "exports" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-gpu"])
        page = browser.new_page(
            viewport={"width": CARD_W, "height": 1400},
            device_scale_factor=SCALE,
        )
        page.goto(page_path.as_uri())
        page.add_style_tag(content=INJECT_CSS)
        # 웹폰트·배경 사진 로딩 대기
        page.wait_for_load_state("networkidle")
        try:
            page.evaluate("document.fonts.ready")
        except Exception:
            pass
        page.wait_for_timeout(600)

        cards = page.query_selector_all(".cnx-card")
        n = 0
        for i, card in enumerate(cards, 1):
            card.scroll_into_view_if_needed()
            page.wait_for_timeout(150)
            fp = out_dir / f"slide{i}.png"
            card.screenshot(path=str(fp))
            # 인스타 그래프 API는 JPEG만 허용 → JPG도 함께 저장
            try:
                from PIL import Image
                Image.open(fp).convert("RGB").save(out_dir / f"slide{i}.jpg",
                                                   quality=90, optimize=True)
            except Exception as e:
                print(f"  jpg 변환 실패: {e}")
            n = i
            print(f"saved {fp.relative_to(ROOT)}")
        browser.close()
    print(f"RESULT: {slug} · {n}장 추출")


if __name__ == "__main__":
    main()
