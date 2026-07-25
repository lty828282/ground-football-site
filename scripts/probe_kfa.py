#!/usr/bin/env python3
"""joinkfa 접근성·구조 탐침(probe). 러너에서 실행해 로그로 결과 확인.
여러 후보 URL을 브라우저 UA로 요청 → 상태코드·타이틀·표/링크 존재 여부·스니펫 출력.
"""
import urllib.request, urllib.error, re, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"

URLS = [
    "https://www.joinkfa.com/",
    "https://www.joinkfa.com/service/match/matchList.jsp",
    "https://www.joinkfa.com/service/match/matchCenter.jsp",
    "https://www.joinkfa.com/service/match/matchSingle.jsp?matchIdx=42230",
    "https://www.joinkfa.com/service/league/leagueMain.jsp",
    "https://www.joinkfa.com/service/match/scheduleList.jsp",
    "https://sports.daum.net/schedule/kfa",
]


def probe(u):
    print("\n===== " + u)
    req = urllib.request.Request(u, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko,en;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
            status = r.status
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.reason)
        try:
            print("  body head:", e.read().decode("utf-8", "replace")[:200])
        except Exception:
            pass
        return
    except Exception as e:
        print("ERR", type(e).__name__, e)
        return
    print("status", status, "len", len(body))
    t = re.search(r"<title>(.*?)</title>", body, re.I | re.S)
    print("title:", (t.group(1).strip()[:120] if t else "-"))
    print("tables:", len(re.findall(r"<table", body, re.I)),
          "| has 경기결과:", "경기결과" in body, "| has 대회:", "대회" in body,
          "| script-heavy:", body.count("<script") )
    # 경기/대회 관련 링크 추출
    links = re.findall(r'href=["\']([^"\']*(?:match|league|schedule|game|result)[^"\']*)["\']', body, re.I)
    for l in sorted(set(links))[:15]:
        print("  link:", l[:120])


if __name__ == "__main__":
    for u in URLS:
        probe(u)
    print("\nDONE")
