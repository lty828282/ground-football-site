#!/usr/bin/env python3
"""명언 카드(legend-quotes) 배경으로 쓸 '종목별 무료 스톡 사진'을 Pexels에서 1장씩 받아
assets/img/cardnews/legend-quotes-<K>.jpg 로 저장한다.

특정 실존 선수가 아닌, 종목에 어울리는 역동적 액션/실루엣 사진만 사용(저작권·초상권 안전).
사진 저작자 크레딧을 legend-quotes-credits.txt 로 남기고 로그에도 출력.

필요: PEXELS_API_KEY, Pillow
"""
import os, sys, json, urllib.parse, urllib.request, pathlib
from PIL import Image
import io

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (os.environ.get("PEXELS_API_KEY") or "").strip()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"
DEST = ROOT / "assets" / "img" / "cardnews"
TARGET_W, TARGET_H = 1080, 1350   # 4:5

# 카드 인덱스(0=표지 …) → 검색어 후보(첫 결과부터 사용). 특정 선수 아님, 종목 매칭.
QUERIES = {
    0: ["soccer stadium floodlights night", "football stadium lights", "soccer stadium crowd"],
    1: ["soccer player action", "football player kicking", "soccer player field"],       # 펠레
    2: ["soccer player dribbling", "football dribble action", "soccer player ball control"],  # 메시
    3: ["soccer free kick", "football player shooting", "soccer player silhouette sunset"],    # 호날두
    4: ["basketball player dunk", "basketball slam dunk action", "basketball player jump"],     # 조던
    5: ["boxing gloves dark", "boxer training silhouette", "boxing ring dramatic"],             # 알리
    6: ["basketball player shooting", "basketball action court", "basketball player silhouette"],# 코비
}


def search(query):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({
        "query": query, "per_page": 5, "orientation": "portrait", "size": "large"})
    req = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("photos") or []


def download(u):
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()


def cover_crop(data):
    im = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = im.size
    scale = max(TARGET_W / w, TARGET_H / h)
    nw, nh = int(w * scale + 0.5), int(h * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = (nw - TARGET_W) // 2
    top = (nh - TARGET_H) // 2
    return im.crop((left, top, left + TARGET_W, top + TARGET_H))


def main():
    if not KEY:
        print("PEXELS_API_KEY 없음", file=sys.stderr); sys.exit(1)
    only = None
    if len(sys.argv) > 1 and sys.argv[1].strip():
        only = {int(x) for x in sys.argv[1].split(",") if x.strip()}
    DEST.mkdir(parents=True, exist_ok=True)
    credits = []
    for k, qs in QUERIES.items():
        if only is not None and k not in only:
            continue
        photo = None
        for q in qs:
            photos = search(q)
            if photos:
                photo = photos[0]
                used_q = q
                break
        if not photo:
            print(f"  ✗ card{k}: 결과 없음"); continue
        src = photo["src"].get("portrait") or photo["src"].get("large") or photo["src"]["original"]
        img = cover_crop(download(src))
        out = DEST / f"legend-quotes-{k}.jpg"
        img.save(out, quality=88, optimize=True)
        cr = f'{photo.get("photographer","?")} / Pexels'
        credits.append(cr)
        print(f"  ✓ card{k} ({used_q}) ← {photo.get('url')}  by {cr}  → {out.relative_to(ROOT)}")
    # 크레딧 저장(중복 제거, 순서 유지)
    uniq = list(dict.fromkeys(credits))
    (DEST / "legend-quotes-credits.txt").write_text("\n".join(uniq) + "\n", encoding="utf-8")
    print("\nCREDITS:", " · ".join(uniq))
    print(f"RESULT: {len(credits)}장 저장")


if __name__ == "__main__":
    main()
