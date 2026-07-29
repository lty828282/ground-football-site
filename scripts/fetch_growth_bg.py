#!/usr/bin/env python3
"""성장 카드뉴스(growth) 배경 사진 7장을 Pexels에서 받아
assets/img/cardnews/growth-<K>.jpg (1080x1350) 로 저장. 필요: PEXELS_API_KEY, Pillow."""
import os, sys, json, urllib.parse, urllib.request, pathlib, io
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (os.environ.get("PEXELS_API_KEY") or "").strip()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"
DEST = ROOT / "assets" / "img" / "cardnews"
TW, TH = 1080, 1350

# 카드 인덱스 → 검색어 후보(첫 결과부터). 특정 실존인물 아님, 일반 스톡.
QUERIES = {
    0: ["kids playing soccer sunset", "child soccer field", "youth football sunset"],   # 표지
    1: ["parent and child outdoors", "family child park", "father son outdoors"],       # 메시지
    2: ["child sleeping peacefully", "kid sleeping bed", "child asleep"],                # 수면
    3: ["healthy food children table", "milk eggs healthy breakfast", "kids healthy meal"], # 영양
    4: ["kid playing soccer field", "boy football training", "child running soccer"],     # 운동
    5: ["children playing outdoors sunlight", "kids running park sun", "child outdoor sun"], # 햇빛
    6: ["youth soccer team sunset", "child soccer silhouette", "football kid sunset"],    # 마무리
}


def search(q):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": q, "per_page": 5, "orientation": "portrait", "size": "large"})
    req = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("photos") or []


def download(u):
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()


def cover(data):
    im = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = im.size
    s = max(TW / w, TH / h)
    nw, nh = int(w * s + .5), int(h * s + .5)
    im = im.resize((nw, nh), Image.LANCZOS)
    l, t = (nw - TW) // 2, (nh - TH) // 2
    return im.crop((l, t, l + TW, t + TH))


def main():
    if not KEY:
        sys.exit("PEXELS_API_KEY 없음")
    only = {int(x) for x in sys.argv[1].split(",")} if len(sys.argv) > 1 and sys.argv[1].strip() else None
    DEST.mkdir(parents=True, exist_ok=True)
    creds = []
    for k, qs in QUERIES.items():
        if only is not None and k not in only:
            continue
        photo = None
        for q in qs:
            ps = search(q)
            if ps:
                photo = ps[0]; used = q; break
        if not photo:
            print(f"  ✗ growth-{k}: 결과 없음"); continue
        src = photo["src"].get("portrait") or photo["src"].get("large") or photo["src"]["original"]
        cover(download(src)).save(DEST / f"growth-{k}.jpg", quality=88, optimize=True)
        creds.append(f'{photo.get("photographer","?")} / Pexels')
        print(f"  ✓ growth-{k} ({used}) by {creds[-1]}")
    print("CREDITS:", " · ".join(dict.fromkeys(creds)))
    print("DONE")


if __name__ == "__main__":
    main()
