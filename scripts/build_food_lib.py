#!/usr/bin/env python3
"""음식 사진 라이브러리 구축 — food-library.json 의 음식마다 여러 장을 Pexels에서 받아
assets/img/food-lib/<slug>/N.jpg 로 저장한다. (식단 카드가 매번 랜덤으로 골라 다양성 확보)

사용:  python3 scripts/build_food_lib.py [slug1,slug2]   (특정 음식만, 생략 시 전체)
필요:  PEXELS_API_KEY
"""
import os, sys, json, urllib.parse, urllib.request, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEF = ROOT / "assets" / "data" / "food-library.json"
LIB = ROOT / "assets" / "img" / "food-lib"
KEY = (os.environ.get("PEXELS_API_KEY") or "").strip()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"


def search(query, need):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({
        "query": query, "per_page": need, "orientation": "square", "size": "medium"})
    req = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return (json.load(r).get("photos") or [])


def main():
    if not KEY:
        print("PEXELS_API_KEY 없음", file=sys.stderr); sys.exit(1)
    with open(DEF, encoding="utf-8") as f:
        cfg = json.load(f)
    per = int(cfg.get("per_food", 5))
    foods = cfg["foods"]
    only = None
    if len(sys.argv) > 1 and sys.argv[1].strip():
        only = {x.strip() for x in sys.argv[1].split(",") if x.strip()}

    for slug, meta in foods.items():
        if only is not None and slug not in only:
            continue
        d = LIB / slug
        d.mkdir(parents=True, exist_ok=True)
        seen, saved = set(), 0
        for q in meta["queries"]:
            if saved >= per:
                break
            try:
                photos = search(q, per)
            except Exception as e:
                print(f"  {slug} 검색 실패({q}): {e}", file=sys.stderr); continue
            for p in photos:
                if saved >= per:
                    break
                pid = p.get("id")
                if pid in seen:
                    continue
                seen.add(pid)
                src = p.get("src") or {}
                iu = src.get("medium") or src.get("large") or src.get("original")
                if not iu:
                    continue
                try:
                    rq = urllib.request.Request(iu, headers={"User-Agent": UA})
                    with urllib.request.urlopen(rq, timeout=40) as resp:
                        (d / f"{saved}.jpg").write_bytes(resp.read())
                    saved += 1
                except Exception as e:
                    print(f"  {slug} 다운로드 실패: {e}", file=sys.stderr)
        print(f"{slug}: {saved}장")
    print("RESULT: 음식 라이브러리 구축 완료")


if __name__ == "__main__":
    main()
