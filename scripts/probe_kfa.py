#!/usr/bin/env python3
"""joinkfa 구조 심화 탐침 — 경기 목록(schedule) 엔드포인트를 찾기 위해
메인 페이지 스크립트/링크에서 API·jsp URL 후보를 추출하고, 개별 경기 페이지의
링크·ID 파라미터·표 내용을 덤프한다. 러너에서 실행 후 로그 확인.
"""
import urllib.request, urllib.error, re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"


def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": UA,
        "Accept": "text/html,*/*", "Accept-Language": "ko,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.status, r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")


def dump_urls(body, label):
    pats = set(re.findall(r'["\'](/[A-Za-z0-9_./?=&%\-]*?(?:match|league|schedule|game|list|api|result|calendar|day)[A-Za-z0-9_./?=&%\-]*)["\']', body, re.I))
    pats |= set(re.findall(r'["\']((?:https?:)?//[^"\']*?joinkfa[^"\']*)["\']', body, re.I))
    jsp = set(re.findall(r'[A-Za-z0-9_./]+\.jsp[A-Za-z0-9_./?=&%\-]*', body))
    print(f"  [{label}] URL 후보 {len(pats)}개, jsp {len(jsp)}개")
    for p in sorted(pats)[:30]:
        print("    u:", p[:140])
    for p in sorted(jsp)[:20]:
        print("    jsp:", p[:140])


def main():
    # 1) 메인 페이지: SPA가 부르는 API/스크립트 URL 후보
    print("===== MAIN https://www.joinkfa.com/")
    try:
        st, body = get("https://www.joinkfa.com/")
        print("status", st, "len", len(body))
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', body, re.I)
        for s in scripts[:25]:
            print("  script:", s[:140])
        dump_urls(body, "main")
    except Exception as e:
        print("ERR", e)

    # 2) 개별 경기 페이지: 부모 대회/일정으로 가는 링크·ID·표
    for idx in ("42230",):
        u = f"https://www.joinkfa.com/service/match/matchSingle.jsp?matchIdx={idx}"
        print("\n===== MATCH", u)
        try:
            st, body = get(u)
            print("status", st, "len", len(body))
            hrefs = set(re.findall(r'href=["\']([^"\']+)["\']', body))
            for h in sorted(hrefs)[:30]:
                print("  href:", h[:140])
            ids = set(re.findall(r'[?&]([A-Za-z]*[Ii]dx)=([0-9]+)', body))
            print("  ID params:", sorted(ids)[:20])
            # 대회/리그 식별자 후보
            for key in ("leagueIdx", "lgIdx", "gmeGubun", "mgctype", "matchTitle", "yy", "leagueId"):
                for m in re.findall(key + r'["\']?\s*[:=]\s*["\']?([A-Za-z0-9가-힣 %+_-]{1,40})', body)[:3]:
                    print(f"    {key} =", m)
            # 표 내용(태그 제거) 앞부분
            tbl = re.search(r"<table.*?</table>", body, re.S | re.I)
            if tbl:
                txt = re.sub(r"<[^>]+>", " ", tbl.group(0))
                txt = re.sub(r"\s+", " ", txt).strip()
                print("  TABLE snippet:", txt[:400])
        except Exception as e:
            print("ERR", e)
    print("\nDONE")


if __name__ == "__main__":
    main()
