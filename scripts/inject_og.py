#!/usr/bin/env python3
"""정적 Open Graph/Twitter/canonical 태그를 콘텐츠 페이지 <head>에 삽입.
- 비-JS 소셜 스크래퍼(카카오톡·스레드·페북)도 링크 미리보기를 만들 수 있게 한다.
- 카드뉴스는 자기 표지 이미지를, 그 외는 기본 OG 배너를 og:image 로 사용.
- 이미 og:title 이 있으면 건너뛴다(멱등).
"""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://groundyouth.com"
DEFAULT_IMG = BASE + "/assets/img/brand/og-default.png"
PAGES = ROOT / "pages"

FALLBACK_DESC = "유소년 축구 선수와 부모를 위한 전문 정보 — 훈련·영양·기본기·전술·용품."


def og_image_for(slug_file):
    """카드뉴스면 표지 이미지, 아니면 기본 배너 URL."""
    name = slug_file[:-5]  # strip .html
    if name.startswith("cardnews-"):
        slug = name[len("cardnews-"):]
        cand = [
            ("assets/img/cardnews/%s-0.jpg" % slug),
            ("exports/%s/slide1.jpg" % slug),
        ]
        for rel in cand:
            if (ROOT / rel).exists():
                return BASE + "/" + rel
    return DEFAULT_IMG


def build_block(url, title, desc, img):
    def esc(s): return s.replace('"', "&quot;")
    t, d = esc(title), esc(desc)
    return (
        '<link rel="canonical" href="%s">\n'
        '<meta property="og:site_name" content="그라운드 유소년">\n'
        '<meta property="og:type" content="article">\n'
        '<meta property="og:title" content="%s">\n'
        '<meta property="og:description" content="%s">\n'
        '<meta property="og:url" content="%s">\n'
        '<meta property="og:image" content="%s">\n'
        '<meta property="og:locale" content="ko_KR">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="%s">\n'
        '<meta name="twitter:description" content="%s">\n'
        '<meta name="twitter:image" content="%s">'
        % (url, t, d, url, img, t, d, img)
    )


def process(path):
    s = path.read_text(encoding="utf-8")
    if 'property="og:title"' in s:
        return "skip(이미 있음)"
    mt = re.search(r"<title>(.*?)</title>", s, re.S)
    if not mt:
        return "skip(title 없음)"
    title = re.sub(r"\s+", " ", mt.group(1)).strip()
    md = re.search(r'<meta\s+name="description"\s+content="(.*?)">', s, re.S)
    desc = re.sub(r"\s+", " ", md.group(1)).strip() if md else FALLBACK_DESC
    url = "%s/pages/%s" % (BASE, path.name)
    img = og_image_for(path.name)
    block = build_block(url, title, desc, img)
    # description 태그 전체 뒤(있으면), 없으면 </title> 뒤에 삽입 (문자열 replace 로 안전하게)
    if md:
        anchor = md.group(0)               # 닫는 '>' 포함
        s2 = s.replace(anchor, anchor + "\n" + block, 1)
    else:
        s2 = s.replace("</title>", "</title>\n" + block, 1)
    if s2 == s:
        return "skip(삽입 실패)"
    path.write_text(s2, encoding="utf-8")
    return "ok · " + ("cover" if img != DEFAULT_IMG else "banner")


def main():
    rows = []
    for p in sorted(PAGES.glob("*.html")):
        rows.append((p.name, process(p)))
    for n, r in rows:
        print(f"  {r:16s} {n}")
    ok = sum(1 for _, r in rows if r.startswith("ok"))
    print("삽입 완료:", ok, "/", len(rows))


if __name__ == "__main__":
    main()
