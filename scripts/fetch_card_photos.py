#!/usr/bin/env python3
"""카드뉴스 카드별 사진 후보를 Pexels에서 여러 장 받아 컨택트 시트로 만든다.

각 카드에 어울리는 사진을 고르기 위해, 카드별 검색어로 후보 N장을 받아
exports/photo-candidates/<slug>/card<K>/ 에 저장하고, 한눈에 보는 시트도 만든다.

사용:  python3 scripts/fetch_card_photos.py home-training
필요:  PEXELS_API_KEY, Pillow
"""
import os, sys, json, urllib.parse, urllib.request, urllib.error, pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (os.environ.get("PEXELS_API_KEY") or "").strip()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"

# 카드 인덱스(파일 home-training-<K>.jpg 기준) → 검색어 후보
CARD_QUERIES = {
    "home-training": {
        2: ["soccer boy dribbling", "kid dribbling football", "child soccer dribble ball"],
        3: ["soccer ball against wall", "boy kicking football wall", "kid soccer wall"],
        4: ["soccer training cones", "football agility cones", "soccer cone drill kids"],
        5: ["soccer juggling ball", "football keepie uppie", "boy juggling soccer"],
        6: ["kid soccer training", "child football practice", "youth soccer drill"],
    }
}

PER_CARD = 8


def _font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def search(query, need):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({
        "query": query, "per_page": need, "orientation": "portrait", "size": "medium"})
    req = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return (json.load(r).get("photos") or [])


def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "home-training"
    if not KEY:
        print("PEXELS_API_KEY 없음", file=sys.stderr); sys.exit(1)
    cards = CARD_QUERIES.get(slug)
    if not cards:
        print("정의된 검색어 없음:", slug, file=sys.stderr); sys.exit(1)

    out = ROOT / "exports" / "photo-candidates" / slug
    out.mkdir(parents=True, exist_ok=True)

    for k, queries in cards.items():
        cdir = out / f"card{k}"
        cdir.mkdir(exist_ok=True)
        seen, saved = set(), []
        for q in queries:
            if len(saved) >= PER_CARD:
                break
            try:
                photos = search(q, PER_CARD)
            except Exception as e:
                print(f"  검색 실패({q}): {e}", file=sys.stderr); continue
            for p in photos:
                if len(saved) >= PER_CARD:
                    break
                pid = p.get("id")
                if pid in seen:
                    continue
                seen.add(pid)
                src = (p.get("src") or {})
                iu = src.get("large") or src.get("portrait") or src.get("original")
                if not iu:
                    continue
                try:
                    rq = urllib.request.Request(iu, headers={"User-Agent": UA})
                    with urllib.request.urlopen(rq, timeout=40) as resp:
                        data = resp.read()
                    fp = cdir / f"{len(saved)}.jpg"
                    fp.write_bytes(data)
                    saved.append(fp)
                except Exception as e:
                    print(f"  다운로드 실패: {e}", file=sys.stderr)
        # 컨택트 시트 (4열, 번호 라벨)
        make_sheet(saved, out / f"card{k}_sheet.jpg", f"card{k}")
        print(f"card{k}: {len(saved)}장")
    print("RESULT: 후보 수집 완료")


def make_sheet(files, dst, label):
    if not files:
        return
    cols, tw, th, pad = 4, 320, 400, 10
    rows = (len(files) + cols - 1) // cols
    W = cols * tw + (cols + 1) * pad
    H = rows * th + (rows + 1) * pad + 40
    sheet = Image.new("RGB", (W, H), (24, 32, 28))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 8), f"{label} 후보 (번호로 선택)", font=_font(24), fill=(255, 255, 255))
    for i, fp in enumerate(files):
        try:
            im = Image.open(fp).convert("RGB")
        except Exception:
            continue
        im = im.resize((tw, th))
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad)
        y = 40 + pad + r * (th + pad)
        sheet.paste(im, (x, y))
        # 번호 배지
        d.rectangle([x, y, x + 46, y + 40], fill=(232, 163, 61))
        d.text((x + 12, y + 4), str(i), font=_font(30), fill=(20, 20, 20))
    sheet.save(dst, quality=88)


if __name__ == "__main__":
    main()
