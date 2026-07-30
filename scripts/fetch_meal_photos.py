#!/usr/bin/env python3
"""식단 카드뉴스(meal-plan)용 음식 사진을 Pexels에서 받아
assets/img/cardnews/meal/<key>.jpg (정사각 480x480) 로 저장.

특정 인물 아님, 음식 스톡만 사용. 필요: PEXELS_API_KEY, Pillow.
"""
import os, sys, json, urllib.parse, urllib.request, pathlib, io
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (os.environ.get("PEXELS_API_KEY") or "").strip()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"
DEST = ROOT / "assets" / "img" / "cardnews" / "meal"
SZ = 480

# key → 검색어 후보(첫 결과부터). 메뉴 내용을 최대한 살린 음식 사진.
QUERIES = {
    "toast": ["whole grain toast breakfast", "wheat toast bread", "toast breakfast plate"],
    "egg":   ["boiled eggs plate", "boiled egg halves", "eggs breakfast"],
    "milk":  ["glass of milk", "milk glass wooden table", "fresh milk glass"],
    "fruit": ["fresh cut fruit plate", "sliced fruit bowl", "assorted fruit plate"],
    "rice":  ["plate of white rice", "white steamed rice closeup", "sushi rice white"],
    "fish":  ["grilled salmon fillet plate", "grilled fish dish", "cooked fish fillet"],
    "veg":   ["steamed broccoli florets", "assorted fresh vegetables", "grilled vegetables plate"],
    "soup":  ["miso soup bowl", "vegetable soup bowl top view", "bowl of soup closeup"],
    "tofu":  ["tofu cubes dish", "fresh tofu block", "tofu plate"],
    "chicken": ["grilled chicken breast plate", "cooked chicken breast", "grilled chicken dish"],
    "stew":  ["korean stew hot pot", "soybean paste stew", "korean soup stew"],
    "nuts":  ["mixed nuts bowl", "assorted nuts wooden", "bowl of nuts"],
}


def search(q):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": q, "per_page": 4, "orientation": "square", "size": "medium"})
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
    s = max(SZ / w, SZ / h)
    nw, nh = int(w * s + .5), int(h * s + .5)
    im = im.resize((nw, nh), Image.LANCZOS)
    l, t = (nw - SZ) // 2, (nh - SZ) // 2
    return im.crop((l, t, l + SZ, t + SZ))


def main():
    if not KEY:
        sys.exit("PEXELS_API_KEY 없음")
    only = {x for x in sys.argv[1].split(",")} if len(sys.argv) > 1 and sys.argv[1].strip() else None
    DEST.mkdir(parents=True, exist_ok=True)
    creds = []
    for key, qs in QUERIES.items():
        if only is not None and key not in only:
            continue
        saved = False
        for q in qs:
            if saved:
                break
            for photo in search(q):
                s = photo.get("src") or {}
                # medium 변형은 간혹 422 → large/original 우선
                for variant in ("large", "original", "large2x", "medium"):
                    u = s.get(variant)
                    if not u:
                        continue
                    try:
                        cover(download(u)).save(DEST / f"{key}.jpg", quality=86, optimize=True)
                    except Exception as e:
                        print(f"    · {key} {variant} 실패: {e}", file=sys.stderr); continue
                    creds.append(f'{photo.get("photographer","?")} / Pexels')
                    print(f"  ✓ meal/{key} ({q}) by {creds[-1]}")
                    saved = True
                    break
                if saved:
                    break
        if not saved:
            print(f"  ✗ {key}: 사진 실패")
    print("CREDITS:", " · ".join(dict.fromkeys(creds)))
    print("DONE")


if __name__ == "__main__":
    main()
