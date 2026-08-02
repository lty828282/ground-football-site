#!/usr/bin/env python3
"""훈련 영상 자동 수집 — 키워드별로 유튜브에서 '최근 6개월 이내 · 조회수 상위 3개'를
검색해 assets/data/training-videos.json 에 채운다.

- 카테고리별 검색어(GROUPS)로 search.list(order=viewCount, publishedAfter=6개월전) 호출
- videos.list 로 실제 조회수/업로드일/임베드 가능여부 확인 후 조회수순 상위 N개 선정
- 기존 수동 큐레이션 영상(auto 아님)은 보존, 자동 영상(auto=true)만 새로 교체
- 결과 JSON 을 파일에 쓰고, 동시에 로그에 요약/전체 JSON 출력

필요 환경변수: YOUTUBE_API_KEY
"""
import os, sys, json, datetime, urllib.request, urllib.parse, urllib.error

API_KEY = (os.environ.get("YOUTUBE_API_KEY") or "").strip()
YT = "https://www.googleapis.com/youtube/v3"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "assets", "data", "training-videos.json")

MONTHS6 = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=183)
PUBLISHED_AFTER = MONTHS6.replace(microsecond=0).isoformat().replace("+00:00", "Z")

# 카테고리 = 화면 필터 칩 라벨, queries = 검색 키워드, n = 상위 몇 개
GROUPS = [
    {"cat": "볼감각", "queries": ["유소년 축구 볼 컨트롤 훈련", "축구 볼 감각 훈련",
                                 "축구 퍼스트 터치 훈련", "축구 트래핑 훈련", "볼 리프팅 트래핑 기본기"], "n": 5},
    {"cat": "슛 & 킥", "queries": ["유소년 축구 슛 훈련", "유소년 축구 킥 훈련"], "n": 3},
    {"cat": "드리블", "queries": ["유소년 축구 드리블 훈련"], "n": 3},
    {"cat": "패스", "queries": ["유소년 축구 패스 훈련"], "n": 3},
    {"cat": "리프팅", "queries": ["축구 리프팅 훈련", "축구 저글링 훈련"], "n": 3},
]
# 화면에 표시할 카테고리 순서(수동 '볼감각' 포함)
CATEGORY_ORDER = ["볼감각", "슛 & 킥", "드리블", "패스", "리프팅"]

# 축구 무관 영상 제외(예: '리프팅'=역도, '킥'=격투기 등 동음이의 오검색 방지)
SOCCER_TOKENS = ("축구", "풋살", "유소년", "드리블", "리프팅", "저글링", "패스", "트래핑", "트레핑",
                 "슛", "슈팅", "킥", "볼", "공", "football", "soccer", "futsal")
# 역도/헬스 + 예능/하이라이트/중계 등 '훈련 영상'이 아닌 것 제외
BLOCK_TOKENS = ("데드리프트", "데드리프", "스쿼트", "벤치프레스", "헬스", "웨이트", "보디빌딩",
                "다이어트", "크로스핏", "역도", "태권", "복싱", "무에타이", "격투",
                "예능", "하이라이트", "중계", "몰카", "리액션", "먹방", "브이로그", "vlog",
                "다시보기", "풀경기", "레전드", "매치볼드림", "슈팅스타", "달인")
# 훈련/강습 성격을 우선(제목·채널에 아래 중 하나가 있어야 채택)
TUTORIAL_TOKENS = ("훈련", "드릴", "drill", "기본기", "기초", "배우기", "방법", "레슨", "강습",
                   "클래스", "따라", "tutorial", "how to", "연습", "스킬", "skill", "코칭",
                   "coaching", "practice", "티키타카", "개인기")


def yt(endpoint, params):
    params = dict(params, key=API_KEY)
    url = YT + "/" + endpoint + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        sys.exit(f"유튜브 API 오류 (HTTP {e.code}) [{endpoint}]: {body[:400]}")


def search_ids(q):
    data = yt("search", {
        "part": "snippet", "q": q, "type": "video", "order": "viewCount",
        "maxResults": 40, "publishedAfter": PUBLISHED_AFTER,
        "relevanceLanguage": "ko", "regionCode": "KR",
        "videoEmbeddable": "true", "safeSearch": "strict",
    })
    return [it["id"]["videoId"] for it in data.get("items", []) if it.get("id", {}).get("videoId")]


def video_details(ids):
    out = {}
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        data = yt("videos", {"part": "snippet,statistics,status,contentDetails",
                             "id": ",".join(batch), "maxResults": 50})
        for it in data.get("items", []):
            out[it["id"]] = it
    return out


def fmt_views(n):
    n = int(n)
    if n >= 10000:
        v = n / 10000
        return (f"{v:.1f}".rstrip("0").rstrip(".")) + "만"
    if n >= 1000:
        return f"{n/1000:.1f}".rstrip("0").rstrip(".") + "천"
    return str(n)


def parse_dur_seconds(iso):
    # PT#H#M#S → 초
    import re
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mnt, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mnt * 60 + s


def pick_group(g, seen):
    cand = []
    for q in g["queries"]:
        cand += search_ids(q)
    # 중복 제거(순서 유지)
    cand = list(dict.fromkeys(cand))
    det = video_details(cand)
    rows = []
    for vid in cand:
        it = det.get(vid)
        if not it or vid in seen:
            continue
        st = it.get("status", {})
        if not st.get("embeddable", True) or st.get("privacyStatus") != "public":
            continue
        pub = it["snippet"].get("publishedAt", "")
        if pub < PUBLISHED_AFTER:      # 6개월 이내 재확인
            continue
        hay = (it["snippet"]["title"] + " " + it["snippet"]["channelTitle"]).lower()
        if any(b.lower() in hay for b in BLOCK_TOKENS):   # 축구 무관(역도)·예능·하이라이트 제외
            continue
        if not any(s.lower() in hay for s in SOCCER_TOKENS):  # 축구 관련성 필수
            continue
        if not any(t.lower() in hay for t in TUTORIAL_TOKENS):  # 훈련/강습 성격 필수
            continue
        dur = parse_dur_seconds(it.get("contentDetails", {}).get("duration"))
        if dur and dur <= 70:      # 숏츠 제외(롱폼만) — 목록 카드 크기 통일
            continue
        views = int(it.get("statistics", {}).get("viewCount", 0))
        rows.append({"id": vid, "views": views, "pub": pub,
                     "title": it["snippet"]["title"].strip(),
                     "channel": it["snippet"]["channelTitle"].strip()})
    rows.sort(key=lambda r: r["views"], reverse=True)
    chosen = rows[:g["n"]]
    for r in chosen:
        seen.add(r["id"])
    return chosen


def main():
    if not API_KEY:
        sys.exit("환경변수 YOUTUBE_API_KEY 가 필요합니다.")
    print(f"기준일(6개월 이내) publishedAfter = {PUBLISHED_AFTER}\n")

    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    manual = [v for v in data.get("videos", []) if not v.get("auto")]

    auto = []
    seen = set(v["id"] for v in manual)
    for g in GROUPS:
        chosen = pick_group(g, seen)
        print(f"[{g['cat']}] {' / '.join(g['queries'])} → {len(chosen)}개")
        for r in chosen:
            ym = r["pub"][:7].replace("-", ".")
            note = f"조회수 {fmt_views(r['views'])} · {ym} · {r['channel']}"
            print(f"    - {r['id']}  ({fmt_views(r['views'])}, {ym})  {r['title'][:50]}")
            vobj = {"id": r["id"], "title": r["title"], "cat": g["cat"], "note": note, "auto": True}
            auto.append(vobj)

    data["categories"] = CATEGORY_ORDER
    data["videos"] = manual + auto
    data["updated"] = datetime.date.today().isoformat()

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"\n완료: 수동 {len(manual)}개 + 자동 {len(auto)}개 = {len(data['videos'])}개")
    print("\n===== FULL JSON =====")
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
