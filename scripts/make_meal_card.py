#!/usr/bin/env python3
"""집중형 식단 카드뉴스 생성 — 게시물 하나 = 한 끼 + 간식.

meal-cards.json 의 queue[0] 을 읽어, 각 음식의 Pexels 사진을 받아
클린한 인스타 포스터(1080x1350)로 렌더한다. (healthyyouth 스타일 참고)

필요: PEXELS_API_KEY, Playwright, Pillow
결과: exports/meal-cards/<slug>.png / .jpg
"""
import os, sys, json, urllib.parse, urllib.request, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "data" / "meal-cards.json"
OUT = ROOT / "exports" / "meal-cards"
TMP = pathlib.Path("/tmp/mealimg"); TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
KEY = (os.environ.get("PEXELS_API_KEY") or "").strip()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"


def fetch_food(query, name):
    """Pexels 정사각 음식 사진 1장 → 로컬 경로. 실패 시 None."""
    if not KEY:
        return None
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({
        "query": query, "per_page": 3, "orientation": "square", "size": "medium"})
    req = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            photos = (json.load(r).get("photos") or [])
        if not photos:
            return None
        src = photos[0].get("src") or {}
        iu = src.get("medium") or src.get("large") or src.get("original")
        dst = TMP / (name + ".jpg")
        rq = urllib.request.Request(iu, headers={"User-Agent": UA})
        with urllib.request.urlopen(rq, timeout=40) as resp:
            dst.write_bytes(resp.read())
        return dst.as_uri()
    except Exception as e:
        print(f"  사진 실패({query}): {e}", file=sys.stderr)
        return None


def food_cell(item, big=False):
    uri = item.get("_img")
    style = f"background-image:url('{uri}')" if uri else "background:#dfe6df"
    cls = "cell big" if big else "cell"
    return f"""<div class="{cls}">
      <div class="ph" style="{style}"></div>
      <div class="lb">{item['label']}</div>
      <div class="wh">{item.get('why','')}</div>
    </div>"""


TPL = """<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px;overflow:hidden;
  font-family:-apple-system,'Segoe UI','Apple SD Gothic Neo','Malgun Gothic',sans-serif;}}
.poster{{width:1080px;height:1350px;background:#FAF7EF;display:flex;flex-direction:column;word-break:keep-all;}}
.top{{background:linear-gradient(120deg,#1B4332,#2E7D52);color:#fff;padding:52px 60px 44px;position:relative;}}
.kick{{font-size:24px;font-weight:800;letter-spacing:3px;color:#FFD54F;margin-bottom:12px;}}
.ttl{{font-size:74px;font-weight:900;line-height:1.08;letter-spacing:-1px;}}
.hook{{font-size:30px;font-weight:600;margin-top:18px;color:#eaf4ec;}}
.bar{{height:10px;background:#7ED957;}}
.body{{flex:1;padding:40px 56px 24px;display:flex;flex-direction:column;}}
.sec{{font-size:34px;font-weight:900;color:#14261E;margin:6px 0 22px;display:flex;align-items:center;gap:12px;}}
.sec .pill{{font-size:20px;font-weight:800;color:#fff;background:#2E7D52;border-radius:999px;padding:6px 18px;}}
.sec.snack .pill{{background:#E8A33D;}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:22px;}}
.cell{{background:#fff;border:1px solid #e7e3d7;border-radius:22px;padding:18px 20px;display:flex;align-items:center;gap:18px;}}
.cell .ph{{width:118px;height:118px;border-radius:18px;background-size:cover;background-position:center;flex:none;}}
.cell.big .ph{{width:138px;height:138px;}}
.cell .lb{{font-size:30px;font-weight:900;color:#14261E;white-space:nowrap;}}
.cell .wh{{font-size:19px;color:#5F6F67;margin-top:5px;line-height:1.35;}}
.cell > div:not(.ph){{display:flex;flex-direction:column;flex:1;min-width:0;}}
.snackgrid{{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-bottom:6px;}}
.spacer{{flex:1;min-height:14px;}}
.keys{{display:flex;gap:14px;margin-top:22px;}}
.key{{flex:1;background:#EAF4EC;border-radius:16px;padding:16px 12px;text-align:center;
  font-size:21px;font-weight:800;color:#1B4332;line-height:1.3;}}
.key b{{display:block;color:#2E7D52;font-size:26px;margin-bottom:4px;}}
.foot{{background:#14261E;color:#fff;padding:26px 56px;display:flex;align-items:center;justify-content:space-between;}}
.foot .cta{{font-size:26px;font-weight:800;color:#FFD54F;}}
.foot .brand{{font-size:24px;font-weight:900;letter-spacing:1px;}}
.foot .brand span{{color:#7ED957;}}
</style></head><body>
<div class="poster">
  <div class="top">
    <div class="kick">{kicker}</div>
    <div class="ttl">{title}</div>
    <div class="hook">{hook}</div>
  </div>
  <div class="bar"></div>
  <div class="body">
    <div class="sec"><span class="pill">한 끼</span>{meal_title}</div>
    <div class="grid">{meal_cells}</div>
    <div class="spacer"></div>
    <div class="sec snack"><span class="pill">간식</span>{snack_title}</div>
    <div class="snackgrid">{snack_cells}</div>
    <div class="keys">{keys}</div>
  </div>
  <div class="foot">
    <div class="cta">🔖 저장 · 간식 추천은 프로필 링크</div>
    <div class="brand">GROUND <span>YOUTH</span></div>
  </div>
</div></body></html>"""


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    q = data.get("queue") or []
    if not q:
        print("큐 비어있음"); return
    item = q[0]
    slug = item["slug"]

    for it in item["meal"]["items"] + item["snack"]["items"]:
        it["_img"] = fetch_food(it["query"], slug + "-" + it["label"])

    meal_cells = "".join(food_cell(it) for it in item["meal"]["items"])
    snack_cells = "".join(food_cell(it, big=True) for it in item["snack"]["items"])
    keys = "".join(f'<div class="key"><b>{i+1}</b>{k}</div>'
                   for i, k in enumerate(item.get("keypoints", [])))
    html = TPL.format(kicker=item.get("kicker", ""), title=item["title"], hook=item["hook"],
                      meal_title=item["meal"]["title"], meal_cells=meal_cells,
                      snack_title=item["snack"]["title"], snack_cells=snack_cells, keys=keys)
    hp = TMP / (slug + ".html"); hp.write_text(html, encoding="utf-8")

    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox", "--disable-gpu"])
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        pg.goto(hp.as_uri())
        pg.wait_for_timeout(500)
        png = OUT / (slug + ".png")
        pg.screenshot(path=str(png))
        b.close()
    # 인스타 API용 JPG
    try:
        from PIL import Image
        Image.open(png).convert("RGB").save(OUT / (slug + ".jpg"), quality=90, optimize=True)
    except Exception as e:
        print("jpg 변환 실패:", e)
    print(f"RESULT: {slug} 식단 카드 생성")


if __name__ == "__main__":
    main()
