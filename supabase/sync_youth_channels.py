# 유소년 축구 유튜브 채널 동기화 스크립트
#
# 하는 일:
#   1. 유튜브에서 "유소년 축구"로 채널을 검색해 구독자 수/최근 업로드 정보를 수집
#   2. kickofflife 채널(@kickofflife)은 검색 결과와 무관하게 항상 포함(is_pinned=true)
#   3. Supabase youth_channels 테이블에 upsert
#
# 사전 준비:
#   - supabase/youth_channels_schema.sql 을 Supabase SQL Editor에서 실행
#   - 환경변수 설정 후 실행:
#       export YOUTUBE_API_KEY="유튜브 Data API v3 키"
#       export SUPABASE_SERVICE_ROLE_KEY="Supabase service_role 키"
#       python3 supabase/sync_youth_channels.py
#
# 쿼터 참고: search.list는 호출당 100유닛이므로 하루 1~2회 실행이면 충분합니다.

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

SEARCH_QUERY = "유소년 축구"
SEARCH_PAGES = 2          # 페이지당 최대 25개 채널 → 최대 50개 수집
PINNED_HANDLE = "kickofflife"  # 항상 포함할 고정 채널 핸들

YT_BASE = "https://www.googleapis.com/youtube/v3"


def yt_get(endpoint, params):
    params = dict(params, key=YOUTUBE_API_KEY)
    url = YT_BASE + "/" + endpoint + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        if endpoint == "playlistItems":
            raise  # 업로드 없는 채널의 404는 호출부에서 처리
        body = e.read().decode("utf-8", "replace")
        reason = ""
        try:
            reason = json.loads(body)["error"]["errors"][0].get("reason", "")
        except (ValueError, KeyError, IndexError):
            pass
        hints = {
            "badRequest": "유튜브 API 키가 잘못되었습니다. 키 값을 다시 확인하세요.",
            "keyInvalid": "유튜브 API 키가 잘못되었습니다. 키 값을 다시 확인하세요.",
            "accessNotConfigured": "이 키의 Google Cloud 프로젝트에서 'YouTube Data API v3'가 활성화되어 있지 않습니다. "
                "console.cloud.google.com → API 및 서비스 → 라이브러리에서 YouTube Data API v3를 사용 설정하세요.",
            "quotaExceeded": "유튜브 API 일일 쿼터를 초과했습니다. 내일 다시 시도하세요.",
            "forbidden": "유튜브 API 접근이 거부되었습니다. 키 제한(HTTP 리퍼러/IP 제한) 설정을 확인하세요.",
        }
        hint = hints.get(reason, body[:300])
        sys.exit(f"유튜브 API 오류 (HTTP {e.code}, {reason or '원인 미상'}): {hint}")


def search_channel_ids():
    ids = []
    page_token = None
    for _ in range(SEARCH_PAGES):
        params = {
            "part": "snippet",
            "q": SEARCH_QUERY,
            "type": "channel",
            "maxResults": 25,
            "relevanceLanguage": "ko",
            "regionCode": "KR",
        }
        if page_token:
            params["pageToken"] = page_token
        data = yt_get("search", params)
        for item in data.get("items", []):
            cid = item["id"]["channelId"]
            if cid not in ids:
                ids.append(cid)
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return ids


def resolve_handle(handle):
    data = yt_get("channels", {"part": "id", "forHandle": handle})
    items = data.get("items", [])
    return items[0]["id"] if items else None


def fetch_channels(channel_ids):
    channels = []
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i + 50]
        data = yt_get("channels", {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch),
            "maxResults": 50,
        })
        for item in data.get("items", []):
            sn = item["snippet"]
            st = item.get("statistics", {})
            thumbs = sn.get("thumbnails", {})
            thumb = (thumbs.get("medium") or thumbs.get("default") or {}).get("url")
            channels.append({
                "channel_id": item["id"],
                "name": sn["title"],
                "handle": sn.get("customUrl"),
                "thumbnail_url": thumb,
                "subs_count": int(st.get("subscriberCount", 0)),
                "video_count": int(st.get("videoCount", 0)),
                "uploads_playlist": item.get("contentDetails", {})
                    .get("relatedPlaylists", {}).get("uploads"),
            })
    return channels


def attach_latest_upload(ch):
    ch["latest_video_id"] = None
    ch["latest_video_title"] = None
    ch["latest_upload_at"] = None
    playlist = ch.pop("uploads_playlist", None)
    if not playlist:
        return
    try:
        data = yt_get("playlistItems", {
            "part": "snippet",
            "playlistId": playlist,
            "maxResults": 1,
        })
    except urllib.error.HTTPError:
        return  # 업로드 영상이 없는 채널은 404가 반환됨
    items = data.get("items", [])
    if not items:
        return
    sn = items[0]["snippet"]
    ch["latest_video_id"] = sn.get("resourceId", {}).get("videoId")
    ch["latest_video_title"] = sn.get("title")
    ch["latest_upload_at"] = sn.get("publishedAt")


def upsert_channels(rows):
    url = SUPABASE_URL + "/rest/v1/youth_channels?on_conflict=channel_id"
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
        if e.code == 401 or e.code == 403:
            sys.exit(f"Supabase 인증 오류 (HTTP {e.code}): secret(service_role) 키가 잘못되었습니다. "
                     f"대시보드 Settings → API Keys의 Secret key를 다시 복사하세요.\n상세: {detail}")
        if e.code == 404 or "PGRST205" in detail or "does not exist" in detail:
            sys.exit(f"Supabase에 youth_channels 테이블이 없습니다 (HTTP {e.code}). "
                     f"SQL Editor에서 supabase/youth_channels_schema.sql을 먼저 실행하세요.\n상세: {detail}")
        sys.exit(f"Supabase upsert 실패 (HTTP {e.code}): {detail}")


def main():
    missing = [name for name, val in [
        ("YOUTUBE_API_KEY", YOUTUBE_API_KEY),
        ("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_SERVICE_ROLE_KEY),
    ] if not val]
    if missing:
        sys.exit("환경변수가 필요합니다: " + ", ".join(missing))

    print(f'"{SEARCH_QUERY}" 채널 검색 중…')
    channel_ids = search_channel_ids()
    print(f"검색된 채널 {len(channel_ids)}개")

    pinned_id = resolve_handle(PINNED_HANDLE)
    if pinned_id:
        if pinned_id not in channel_ids:
            channel_ids.append(pinned_id)
    else:
        print(f"경고: @{PINNED_HANDLE} 채널을 찾지 못했습니다", file=sys.stderr)

    channels = fetch_channels(channel_ids)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for ch in channels:
        attach_latest_upload(ch)
        ch["is_pinned"] = ch["channel_id"] == pinned_id
        ch["updated_at"] = now
        print(f'  {ch["name"]}: 구독자 {ch["subs_count"]:,}')

    upsert_channels(channels)
    print(f"Supabase upsert 완료: {len(channels)}개 채널")


if __name__ == "__main__":
    main()
