#!/usr/bin/env python3
"""시·도 축구협회(전북 jfa / 충남 cnfa / 대전 djfa) 결과 페이지 구조 탐침.
결과가 서버렌더 HTML 표에 있는지 확인 → 스크래핑 설계용. 러너 실행 후 로그 확인.
"""
import urllib.request, urllib.error, re, ssl

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

URLS = [
    "https://www.jfa.or.kr/competition/?page=matches-schedule-and-matches-result&mode=view&idx=7900",
    "https://www.jfa.or.kr/competition/?page=matches-schedule-and-matches-result&mode=view&idx=7899",
    "https://www.jfa.or.kr/competition/",
    "http://www.cnfa.co.kr/main/index.php",
    "http://www.djfa.co.kr/",
]


def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept": "text/html,*/*",
                                             "Accept-Language": "ko,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
        return r.status, r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")


def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def probe(u):
    print("\n===== " + u)
    try:
        st, body = get(u)
    except Exception as e:
        print("ERR", type(e).__name__, e); return
    print("status", st, "len", len(body), "| nexacro:", "nexacro" in body.lower())
    t = re.search(r"<title>(.*?)</title>", body, re.I | re.S)
    print("title:", clean(t.group(1)) if t else "-")
    tables = re.findall(r"<table.*?</table>", body, re.S | re.I)
    print("tables:", len(tables), "| 경기결과:", "경기결과" in body or "경기 결과" in body,
          "| 스코어패턴:", bool(re.search(r"\d+\s*[:：]\s*\d+", body)))
    # 가장 큰 표의 텍스트
    if tables:
        big = max(tables, key=len)
        print("BIG TABLE:", clean(big)[:600])
    # 대회 링크(idx) 추출
    idxs = sorted(set(re.findall(r'competition/\?[^"\']*idx=(\d+)', body)))[:12]
    if idxs: print("competition idx:", idxs)
    links = sorted(set(re.findall(r'href=["\']([^"\']*(?:competition|result|match|schedule|bbs|board)[^"\']*)["\']', body, re.I)))[:12]
    for l in links: print("  link:", l[:140])


if __name__ == "__main__":
    for u in URLS:
        probe(u)
    print("\nDONE")
