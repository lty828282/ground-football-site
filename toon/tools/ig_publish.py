#!/usr/bin/env python3
"""Instagram 캐러셀(카드뉴스) 자동 게시 — Content Publishing API.

흐름: child 컨테이너(이미지 URL별) → CAROUSEL 부모 컨테이너 →
상태(FINISHED) 확인 → media_publish.

인증: graph.facebook.com 네트워크 시크릿으로 액세스 토큰을 주입
(Authorization: Bearer). 스크립트는 더미값만 보내고 실제 토큰은 못 봄.

IG 사용자 ID: --ig-user-id, 없으면 /me/accounts 에서 자동 탐색.

예)
  # 공개 JPEG URL을 slug로 자동 구성(저장소 public 전제)
  python3 toon/tools/ig_publish.py --slug yubimuhwan \
      --branch claude/youtube-video-link-t00tce \
      --caption-file toon/content/captions/yubimuhwan.txt

  # URL 직접 지정
  python3 toon/tools/ig_publish.py --images URL1 URL2 ... --caption-file cap.txt

  --dry-run 으로 실제 게시 없이 URL·캡션만 점검.
"""
import sys, json, time, subprocess, argparse, pathlib

GRAPH = "https://graph.facebook.com/v21.0"
REPO = "lty828282/ground-football-site"
RAW = "https://raw.githubusercontent.com/{repo}/{branch}/toon/out/{slug}/panel{n}.jpg"


def _curl(method, url, fields=None):
    cmd = ["curl", "-sS", "-X", method, url,
           "-H", "Authorization: Bearer proxy-injected", "--max-time", "90"]
    for k, v in (fields or {}).items():
        cmd += ["--data-urlencode", f"{k}={v}"]
    r = subprocess.run(cmd, capture_output=True)
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"bad response: {r.stdout.decode()[:300]} {r.stderr.decode()[:200]}")
    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError(f"Graph error: {json.dumps(data['error'], ensure_ascii=False)[:500]}")
    return data


def resolve_ig_user(explicit):
    if explicit:
        return explicit
    d = _curl("GET", f"{GRAPH}/me/accounts?fields=name,instagram_business_account")
    for pg in d.get("data", []):
        iba = pg.get("instagram_business_account")
        if iba:
            print(f"페이지 '{pg.get('name')}' → IG {iba['id']}")
            return iba["id"]
    raise SystemExit("IG 비즈니스 계정을 못 찾음. 페이지에 IG 연결 확인, 또는 --ig-user-id 지정.")


def build_urls(slug, branch, count):
    return [RAW.format(repo=REPO, branch=branch, slug=slug, n=i) for i in range(1, count + 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--branch", default="claude/youtube-video-link-t00tce")
    ap.add_argument("--count", type=int, default=6, help="패널 수(slug 모드)")
    ap.add_argument("--images", nargs="+", help="공개 이미지 URL 직접 지정(2~10)")
    ap.add_argument("--caption-file")
    ap.add_argument("--caption", default="")
    ap.add_argument("--ig-user-id")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    images = a.images or (build_urls(a.slug, a.branch, a.count) if a.slug else None)
    if not images:
        raise SystemExit("--slug 또는 --images 중 하나는 필요.")
    if not (2 <= len(images) <= 10):
        raise SystemExit(f"캐러셀은 2~10장. 현재 {len(images)}장.")

    caption = a.caption
    if a.caption_file:
        caption = pathlib.Path(a.caption_file).read_text().strip()

    if a.dry_run:
        print(f"[dry-run] {len(images)}장:")
        for u in images:
            print("  ", u)
        print("\n[dry-run] 캡션:\n" + caption)
        return

    ig = resolve_ig_user(a.ig_user_id)
    kids = []
    for i, u in enumerate(images, 1):
        d = _curl("POST", f"{GRAPH}/{ig}/media",
                  {"is_carousel_item": "true", "image_url": u})
        kids.append(d["id"])
        print(f"child {i}/{len(images)} → {d['id']}")

    car = _curl("POST", f"{GRAPH}/{ig}/media",
                {"media_type": "CAROUSEL", "children": ",".join(kids), "caption": caption})
    cid = car["id"]
    print("carousel container →", cid)

    for _ in range(40):
        st = _curl("GET", f"{GRAPH}/{cid}?fields=status_code,status")
        sc = st.get("status_code")
        print("  status:", sc)
        if sc == "FINISHED":
            break
        if sc == "ERROR":
            raise SystemExit(f"컨테이너 처리 에러: {st}")
        time.sleep(5)
    else:
        raise SystemExit("컨테이너가 FINISHED 안 됨(타임아웃).")

    pub = _curl("POST", f"{GRAPH}/{ig}/media_publish", {"creation_id": cid})
    print("✅ PUBLISHED:", json.dumps(pub, ensure_ascii=False))


if __name__ == "__main__":
    main()
