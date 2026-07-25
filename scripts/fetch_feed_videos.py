#!/usr/bin/env python3
"""상단 메뉴용 영상 피드 수집 — 최근 1주일 이내 · 조회수 상위 영상을 유튜브에서 받아
assets/data/soccer-videos.json (축구 영상, 10개) 와
assets/data/gear-videos.json (축구화&축구용품, 섹션별 10개) 를 만든다.

필요 환경변수: YOUTUBE_API_KEY
"""
import os, sys, json, datetime, urllib.request, urllib.parse, urllib.error

API_KEY = (os.environ.get("YOUTUBE_API_KEY") or "").strip()
YT = "https://www.googleapis.com/youtube/v3"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "assets", "data")

NOW = datetime.datetime.now(datetime.timezone.utc)
WEEK_AGO = (NOW - datetime.timedelta(days=7)).replace(microsecond=0).isoformat().replace("+00:00", "Z")

# 축구 영상: 단일 피드
SOCCER = {"out": "soccer-videos.json", "title": "축구 영상",
          "tag": "축구", "queries": ["축구"], "n": 10}

# 축구화 & 축구용품: 섹션 2개
GEAR = {"out": "gear-videos.json", "title": "축구화 & 축구용품",
        "sections": [
            {"label": "축구화 리뷰 & 추천", "tag": "축구화",
             "queries": ["축구화 리뷰", "풋살화 리뷰", "유소년 축구화"], "n": 10},
            {"label": "축구 용품 리뷰 & 추천", "tag": "용품",
             "queries": ["축구 용품 리뷰", "축구 용품 추천", "축구용품 리뷰", "축구용품 추천",
                         "축구 장비 리뷰", "풋살 용품 추천"], "n": 10},
        ]}


def yt(endpoint, params):
    params = dict(params, key=API_KEY)
    url = YT + "/" + endpoint + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"유튜브 API 오류 (HTTP {e.code}) [{endpoint}]: {e.read().decode('utf-8','replace')[:400]}")


def search_ids(q):
    data = yt("search", {"part": "snippet", "q": q, "type": "video", "order": "viewCount",
                         "maxResults": 25, "publishedAfter": WEEK_AGO,
                         "relevanceLanguage": "ko", "regionCode": "KR",
                         "videoEmbeddable": "true", "safeSearch": "strict"})
    return [it["id"]["videoId"] for it in data.get("items", []) if it.get("id", {}).get("videoId")]


def details(ids):
    out = {}
    for i in range(0, len(ids), 50):
        data = yt("videos", {"part": "snippet,statistics,status,contentDetails",
                             "id": ",".join(ids[i:i + 50]), "maxResults": 50})
        for it in data.get("items", []):
            out[it["id"]] = it
    return out


def fmt_views(n):
    n = int(n)
    if n >= 10000:
        return f"{n/10000:.1f}".rstrip("0").rstrip(".") + "만"
    if n >= 1000:
        return f"{n/1000:.1f}".rstrip("0").rstrip(".") + "천"
    return str(n)


def days_ago(pub):
    try:
        d = datetime.datetime.fromisoformat(pub.replace("Z", "+00:00"))
        n = (NOW - d).days
        return "오늘" if n <= 0 else f"{n}일 전"
    except Exception:
        return ""


def is_short(iso):
    import re
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return False
    h, mnt, s = (int(x) if x else 0 for x in m.groups())
    return (h * 3600 + mnt * 60 + s) <= 65


def pick(queries, n, tag, seen):
    cand = []
    for q in queries:
        cand += search_ids(q)
    cand = list(dict.fromkeys(cand))
    det = details(cand)
    rows = []
    for vid in cand:
        it = det.get(vid)
        if not it or vid in seen:
            continue
        st = it.get("status", {})
        if not st.get("embeddable", True) or st.get("privacyStatus") != "public":
            continue
        if it["snippet"].get("publishedAt", "") < WEEK_AGO:   # 1주일 이내 재확인
            continue
        views = int(it.get("statistics", {}).get("viewCount", 0))
        rows.append({"id": vid, "views": views,
                     "pub": it["snippet"].get("publishedAt", ""),
                     "title": it["snippet"]["title"].strip(),
                     "channel": it["snippet"]["channelTitle"].strip(),
                     "short": is_short(it.get("contentDetails", {}).get("duration"))})
    rows.sort(key=lambda r: r["views"], reverse=True)
    chosen = rows[:n]
    out = []
    for r in chosen:
        seen.add(r["id"])
        note = f"조회수 {fmt_views(r['views'])} · {days_ago(r['pub'])} · {r['channel']}"
        v = {"id": r["id"], "title": r["title"], "tag": tag, "note": note}
        if r["short"]:
            v["short"] = True
        out.append(v)
    return out


def main():
    if not API_KEY:
        sys.exit("환경변수 YOUTUBE_API_KEY 가 필요합니다.")
    print(f"publishedAfter(1주일 이내) = {WEEK_AGO}\n")
    today = datetime.date.today().isoformat()

    # 축구 영상
    seen = set()
    vids = pick(SOCCER["queries"], SOCCER["n"], SOCCER["tag"], seen)
    soccer = {"title": SOCCER["title"], "updated": today, "videos": vids}
    with open(os.path.join(DATA, SOCCER["out"]), "w", encoding="utf-8") as f:
        json.dump(soccer, f, ensure_ascii=False, indent=2); f.write("\n")
    print(f"[축구 영상] {len(vids)}개")
    for v in vids:
        print("   ", v["id"], "|", v["note"], "|", v["title"][:50])

    # 축구화 & 축구용품
    seen = set()
    sections = []
    for sec in GEAR["sections"]:
        vs = pick(sec["queries"], sec["n"], sec["tag"], seen)
        sections.append({"label": sec["label"], "videos": vs})
        print(f"\n[{sec['label']}] {len(vs)}개")
        for v in vs:
            print("   ", v["id"], "|", v["note"], "|", v["title"][:50])
    gear = {"title": GEAR["title"], "updated": today, "sections": sections}
    with open(os.path.join(DATA, GEAR["out"]), "w", encoding="utf-8") as f:
        json.dump(gear, f, ensure_ascii=False, indent=2); f.write("\n")

    print("\n완료")


if __name__ == "__main__":
    main()
