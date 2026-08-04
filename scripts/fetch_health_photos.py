#!/usr/bin/env python3
"""건강·영양 심화 글에 넣을 가로형 사진을 Pexels에서 받아
assets/img/health/<key>.jpg (1200x720) 로 저장. 필요: PEXELS_API_KEY, Pillow.
저작자 크레딧을 로그로 출력(각 글에 표기)."""
import os, sys, json, urllib.parse, urllib.request, pathlib, io
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (os.environ.get("PEXELS_API_KEY") or "").strip()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"
DEST = ROOT / "assets" / "img" / "health"
TW, TH = 1200, 720

QUERIES = {
    "hydration-hero": ["child drinking water sport", "kid drinking water bottle", "athlete drinking water"],
    "hydration-sweat": ["water bottle sports field", "soccer water bottle grass", "sports drink bottle"],
    "bones-hero": ["glass of milk on wooden table", "milk pouring into glass", "glass of milk white background"],
    "bones-sun": ["children playing outdoors sunlight", "kids running park sunny", "child outdoor sunshine"],
    "iron-hero": ["red meat cooked plate", "grilled beef steak plate", "cooked meat protein plate"],
    "iron-greens": ["spinach leafy greens", "cooked spinach bowl", "green vegetables iron"],
}


def search(q):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": q, "per_page": 5, "orientation": "landscape", "size": "large"})
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
                for variant in ("large", "original", "large2x", "medium"):
                    u = s.get(variant)
                    if not u:
                        continue
                    try:
                        cover(download(u)).save(DEST / f"{key}.jpg", quality=85, optimize=True)
                    except Exception as e:
                        print(f"    · {key} {variant} 실패: {e}", file=sys.stderr); continue
                    who = photo.get("photographer", "?")
                    creds.append(f'{key}: {who} / Pexels')
                    print(f"  ✓ health/{key} ({q}) by {who}")
                    saved = True
                    break
                if saved:
                    break
        if not saved:
            print(f"  ✗ {key}: 실패")
    print("CREDITS:")
    for c in creds:
        print("   ", c)
    print("DONE")


if __name__ == "__main__":
    main()
