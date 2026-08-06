# 홈페이지 '실시간 인기' 영상 동기화 스크립트
#
# 하는 일:
#   1. 유튜브에서 섹션별(youth·training·review) 최근 인기 영상을 검색
#   2. 각 영상의 조회수/게시일/채널명/썸네일을 수집
#   3. Supabase videos 테이블에 upsert (video_id 기준 merge)
#   4. 오래된(기본 45일 초과) 영상은 정리해 첫 화면이 늘 최신으로 유지되게 함
#
# 배경: 홈 '실시간 인기' 피드와 '이번 주 인기' 카드는 Supabase videos 테이블을
#       읽는다(assets/js/home.js → fetchVideos). 이 테이블을 매일 갱신하지 않으면
#       recency 창(24h·3일·7일·30일)에 걸리는 영상이 없어 전체기간 1위 영상만
#       계속 노출된다 → "첫 화면 동영상이 며칠째 그대로"인 원인.
#
# 사전 준비:
#   - supabase/news_videos_schema.sql 의 videos 테이블이 있어야 함
#   - 환경변수:
#       export YOUTUBE_API_KEY="유튜브 Data API v3 키"
#       export SUPABASE_SERVICE_ROLE_KEY="Supabase service_role 키"
#       python3 supabase/sync_home_videos.py
#
# 쿼터 참고: search.list는 호출당 100유닛. 섹션 3개 → 약 300유닛/일. 기본 1만 쿼터로 충분.

import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://sbskumlrahpilikudfjd.supabase.co").strip()
SUPABASE_SERVICE_ROLE_KEY = (os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
YOUTUBE_API_KEY = (os.environ.get("YOUTUBE_API_KEY") or "").strip()

YT_BASE = "https://www.googleapis.com/youtube/v3"

# 섹션별 검색어(홈 피드 = youth+training+review 를 합쳐 최신·인기순 노출)
SECTIONS = [
    {"section": "youth",    "query": "유소년 축구"},
    {"section": "training", "query": "축구 훈련 드리블"},
    {"section": "review",   "query": "축구화 리뷰"},
]
PER_SECTION = 12          # 섹션별 상위 N개 저장
RECENT_DAYS = 30          # 검색 대상: 최근 N일 이내 게시
PRUNE_DAYS = 45           # videos 테이블에서 이보다 오래된 행은 삭제


def yt_get(endpoint, params):
    params = dict(params, key=YOUTUBE_API_KEY)
    url = YT_BASE + "/" + endpoint + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        reason = ""
        try:
            reason = json.loads(body)["error"]["errors"][0].get("reason", "")
        except (ValueError, KeyError, IndexError):
            pass
        hints = {
            "badRequest": "유튜브 API 키가 잘못되었습니다. 키 값을 다시 확인하세요.",
            "keyInvalid": "유튜브 API 키가 잘못되었습니다. 키 값을 다시 확인하세요.",
            "accessNotConfigured": "이 키의 Google Cloud 프로젝트에서 'YouTube Data API v3'가 활성화되어 있지 않습니다.",
            "quotaExceeded": "유튜브 API 일일 쿼터를 초과했습니다. 내일 다시 시도하세요.",
            "forbidden": "유튜브 API 접근이 거부되었습니다. 키 제한 설정을 확인하세요.",
        }
        hint = hints.get(reason, body[:300])
        sys.exit(f"유튜브 API 오류 (HTTP {e.code}, {reason or '원인 미상'}): {hint}")


def search_video_ids(query, published_after):
    data = yt_get("search", {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "maxResults": 25,
        "publishedAfter": published_after,
        "relevanceLanguage": "ko",
        "regionCode": "KR",
    })
    ids = []
    for item in data.get("items", []):
        vid = item.get("id", {}).get("videoId")
        if vid and vid not in ids:
            ids.append(vid)
    return ids


def fetch_video_rows(video_ids, section):
    rows = []
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        data = yt_get("videos", {
            "part": "snippet,statistics",
            "id": ",".join(batch),
            "maxResults": 50,
        })
        for item in data.get("items", []):
            sn = item.get("snippet", {})
            st = item.get("statistics", {})
            thumbs = sn.get("thumbnails", {})
            thumb = (thumbs.get("medium") or thumbs.get("high") or thumbs.get("default") or {}).get("url")
            if not (sn.get("title") and thumb and sn.get("publishedAt")):
                continue
            rows.append({
                "video_id": item["id"],
                "section": section,
                "title": sn["title"],
                "channel_title": sn.get("channelTitle", ""),
                "thumbnail_url": thumb,
                "view_count": int(st.get("viewCount", 0)),
                "published_at": sn["publishedAt"],
                "fetched_at": now,
            })
    # 조회수 상위 PER_SECTION개만 저장
    rows.sort(key=lambda r: r["view_count"], reverse=True)
    return rows[:PER_SECTION]


def upsert_videos(rows):
    url = SUPABASE_URL + "/rest/v1/videos?on_conflict=video_id"
    body = json.dumps(rows).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": "Bearer " + SUPABASE_SERVICE_ROLE_KEY,
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            res.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        if e.code in (401, 403):
            sys.exit(f"Supabase 인증 오류 (HTTP {e.code}): service_role 키를 확인하세요.\n상세: {detail}")
        if e.code == 404 or "PGRST205" in detail or "does not exist" in detail:
            sys.exit(f"Supabase에 videos 테이블이 없습니다 (HTTP {e.code}). "
                     f"SQL Editor에서 supabase/news_videos_schema.sql을 먼저 실행하세요.\n상세: {detail}")
        sys.exit(f"Supabase upsert 실패 (HTTP {e.code}): {detail}")


def prune_old(before_iso):
    """오래된 영상 삭제 → 첫 화면이 늘 최신 인기 영상으로 갱신되게."""
    url = SUPABASE_URL + "/rest/v1/videos?published_at=lt." + urllib.parse.quote(before_iso)
    req = urllib.request.Request(url, method="DELETE", headers={
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": "Bearer " + SUPABASE_SERVICE_ROLE_KEY,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            res.read()
    except urllib.error.HTTPError as e:
        # 정리는 실패해도 치명적이지 않으므로 경고만
        print(f"경고: 오래된 영상 정리 실패 (HTTP {e.code})", file=sys.stderr)


def main():
    missing = [name for name, val in [
        ("YOUTUBE_API_KEY", YOUTUBE_API_KEY),
        ("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_SERVICE_ROLE_KEY),
    ] if not val]
    if missing:
        sys.exit("환경변수가 필요합니다: " + ", ".join(missing))

    now = datetime.datetime.now(datetime.timezone.utc)
    published_after = (now - datetime.timedelta(days=RECENT_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")

    all_rows = []
    for sec in SECTIONS:
        ids = search_video_ids(sec["query"], published_after)
        rows = fetch_video_rows(ids, sec["section"])
        print(f'  [{sec["section"]}] "{sec["query"]}" → {len(rows)}개 (최근 {RECENT_DAYS}일·조회수순)')
        all_rows.extend(rows)

    if not all_rows:
        sys.exit("수집된 영상이 없습니다. 검색어/쿼터를 확인하세요.")

    upsert_videos(all_rows)
    print(f"Supabase videos upsert 완료: {len(all_rows)}개")

    prune_before = (now - datetime.timedelta(days=PRUNE_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    prune_old(prune_before)
    print(f"{PRUNE_DAYS}일 이전 영상 정리 완료")


if __name__ == "__main__":
    main()
