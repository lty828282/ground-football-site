#!/usr/bin/env python3
"""인스타그램 · 쓰레드 자동 게시.

큐(assets/data/post-queue.json)의 맨 앞 항목을 공식 그래프 API로 게시한다.
미디어는 공개 URL(https://groundyouth.com/...)로 API가 가져간다.

필요한 환경변수(Secrets):
  IG_USER_ID, IG_ACCESS_TOKEN            (인스타그램 비즈니스 계정)
  THREADS_USER_ID, THREADS_ACCESS_TOKEN  (쓰레드 계정)

토큰이 없으면 자동으로 드라이런(무엇을 올릴지 출력만).
사용:  python3 scripts/publish_social.py [--dry-run]
"""
import os, sys, json, time, urllib.parse, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, "assets", "data", "post-queue.json")
BASE = "https://groundyouth.com"

IG_VER = "v21.0"
TH_VER = "v1.0"
# 인스타 API 호스트: 기본은 페이스북 페이지 불필요한 "Instagram 로그인" 방식.
# 페이지 연동(Facebook 로그인) 방식을 쓰면 IG_API_BASE=graph.facebook.com 로 지정.
IG_BASE = (os.environ.get("IG_API_BASE") or "graph.instagram.com").strip()
IG_ID = (os.environ.get("IG_USER_ID") or "").strip()
IG_TOK = (os.environ.get("IG_ACCESS_TOKEN") or "").strip()
TH_ID = (os.environ.get("THREADS_USER_ID") or "").strip()
TH_TOK = (os.environ.get("THREADS_ACCESS_TOKEN") or "").strip()

DRY = "--dry-run" in sys.argv


# ── HTTP ─────────────────────────────────────────────
def _post(url, params):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def _get(url, params):
    q = urllib.parse.urlencode(params)
    with urllib.request.urlopen(url + "?" + q, timeout=60) as r:
        return json.load(r)

def media_url(path):
    if path.startswith("http"):
        return path
    return BASE + (path if path.startswith("/") else "/" + path)


# ── 인스타그램 ───────────────────────────────────────
def ig_graph(node, params, get=False):
    url = f"https://{IG_BASE}/{IG_VER}/{node}"
    params = dict(params, access_token=IG_TOK)
    return _get(url, params) if get else _post(url, params)

def ig_wait(creation_id, tries=30):
    for _ in range(tries):
        st = ig_graph(creation_id, {"fields": "status_code"}, get=True)
        if st.get("status_code") == "FINISHED":
            return True
        if st.get("status_code") == "ERROR":
            raise RuntimeError("IG 미디어 처리 오류: %s" % st)
        time.sleep(5)
    raise RuntimeError("IG 미디어 처리 시간 초과")

def ig_publish(item):
    typ = item["type"]
    caption = item.get("caption", "")
    media = item["media"]
    if typ == "image":
        c = ig_graph(f"{IG_ID}/media",
                     {"image_url": media_url(media[0]), "caption": caption})
        cid = c["id"]
    elif typ == "carousel":
        children = []
        for m in media[:10]:
            ch = ig_graph(f"{IG_ID}/media",
                          {"image_url": media_url(m), "is_carousel_item": "true"})
            children.append(ch["id"])
        c = ig_graph(f"{IG_ID}/media",
                     {"media_type": "CAROUSEL", "caption": caption,
                      "children": ",".join(children)})
        cid = c["id"]
    elif typ == "reel":
        p = {"media_type": "REELS", "video_url": media_url(media[0]), "caption": caption}
        if item.get("cover"):
            p["cover_url"] = media_url(item["cover"])
        c = ig_graph(f"{IG_ID}/media", p)
        cid = c["id"]
        ig_wait(cid)
    else:
        raise ValueError("알 수 없는 타입: %s" % typ)
    res = ig_graph(f"{IG_ID}/media_publish", {"creation_id": cid})
    return res.get("id")


# ── 쓰레드 ───────────────────────────────────────────
def th_graph(node, params, get=False):
    url = f"https://graph.threads.net/{TH_VER}/{node}"
    params = dict(params, access_token=TH_TOK)
    return _get(url, params) if get else _post(url, params)

def th_wait(cid, tries=30):
    for _ in range(tries):
        st = th_graph(cid, {"fields": "status"}, get=True)
        s = st.get("status")
        if s == "FINISHED":
            return True
        if s == "ERROR":
            raise RuntimeError("Threads 미디어 처리 오류: %s" % st)
        time.sleep(5)
    raise RuntimeError("Threads 미디어 처리 시간 초과")

def th_publish(item):
    typ = item["type"]
    text = item.get("threads_text") or item.get("caption", "")
    media = item["media"]
    if typ == "reel":
        c = th_graph(f"{TH_ID}/threads",
                     {"media_type": "VIDEO", "video_url": media_url(media[0]), "text": text})
        cid = c["id"]; th_wait(cid)
    elif typ == "carousel":
        children = []
        for m in media[:10]:
            ch = th_graph(f"{TH_ID}/threads",
                          {"media_type": "IMAGE", "image_url": media_url(m),
                           "is_carousel_item": "true"})
            children.append(ch["id"])
        for ci in children:
            th_wait(ci)
        c = th_graph(f"{TH_ID}/threads",
                     {"media_type": "CAROUSEL", "text": text,
                      "children": ",".join(children)})
        cid = c["id"]
    elif typ == "image":
        c = th_graph(f"{TH_ID}/threads",
                     {"media_type": "IMAGE", "image_url": media_url(media[0]), "text": text})
        cid = c["id"]
    else:  # 텍스트 전용도 지원
        c = th_graph(f"{TH_ID}/threads", {"media_type": "TEXT", "text": text})
        cid = c["id"]
    time.sleep(3)
    res = th_graph(f"{TH_ID}/threads_publish", {"creation_id": cid})
    return res.get("id")


# ── 메인 ─────────────────────────────────────────────
PLATFORMS = {
    "instagram": (lambda: bool(IG_ID and IG_TOK), ig_publish),
    "threads":   (lambda: bool(TH_ID and TH_TOK), th_publish),
}

def load():
    with open(QUEUE, encoding="utf-8") as f:
        return json.load(f)

def save(d):
    with open(QUEUE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2); f.write("\n")

def main():
    data = load()
    queue = data.get("queue", [])
    if not queue:
        print("큐가 비어 있음 — 게시할 항목 없음"); return
    item = queue[0]
    want = item.get("platforms", ["instagram", "threads"])
    done = set(item.get("_done", []))
    print(f"▶ 게시: {item['id']} ({item['type']}) → {want}")

    for plat in want:
        if plat in done:
            print(f"  · {plat}: 이미 완료 — 건너뜀"); continue
        has_tok, fn = PLATFORMS[plat]
        if not has_tok():
            print(f"  · {plat}: 토큰 없음 → 드라이런(게시 안 함)")
            for m in item["media"]:
                print(f"      - {media_url(m)}")
            continue
        if DRY:
            print(f"  · {plat}: --dry-run → 게시 생략"); continue
        try:
            pid = fn(item)
            print(f"  ✓ {plat} 게시 완료: {pid}")
            done.add(plat)
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError, KeyError) as e:
            body = ""
            if isinstance(e, urllib.error.HTTPError):
                try: body = e.read().decode()[:400]
                except Exception: pass
            print(f"  ✗ {plat} 실패: {e} {body}", file=sys.stderr)

    item["_done"] = sorted(done)
    # 요청한 플랫폼 중 토큰 있는 것들이 모두 완료되면 published 로 이동
    active = [p for p in want if PLATFORMS[p][0]()]
    if active and all(p in done for p in active):
        item.pop("_done", None)
        data.setdefault("published", []).insert(0, item)
        data["queue"] = queue[1:]
        print("✔ 완료 → published 이동")
    else:
        print("↺ 일부 미완료 — 큐에 유지(다음 실행에서 재시도)")
    save(data)


if __name__ == "__main__":
    main()
