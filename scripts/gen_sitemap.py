#!/usr/bin/env python3
# sitemap.xml 생성기 — 루트 index.html 과 pages/*.html 을 훑어 사이트맵을 만든다.
# 단독 실행(python3 scripts/gen_sitemap.py)도 되고, publish_cardnews 가 발행 후 자동 호출한다.

import datetime
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://groundyouth.com/"
# 색인에서 제외할 페이지(검색 결과 등)
EXCLUDE = {"pages/search.html"}


def build():
    today = datetime.date.today().isoformat()
    urls = ["index.html"]
    for f in sorted(glob.glob(os.path.join(ROOT, "pages", "*.html"))):
        rel = os.path.relpath(f, ROOT).replace(os.sep, "/")
        if rel in EXCLUDE:
            continue
        urls.append(rel)

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        loc = BASE + (u if u != "index.html" else "")
        prio = "1.0" if u == "index.html" else ("0.8" if u.startswith("pages/guide") else "0.6")
        lines.append("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (loc, today, prio))
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main():
    out = os.path.join(ROOT, "sitemap.xml")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build())
    print("sitemap.xml 생성 완료 (%s)" % out)


if __name__ == "__main__":
    main()
