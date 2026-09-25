#!/usr/bin/env python3
"""가이드·카드뉴스 페이지를 스캔해 '관련 글' 추천용 인덱스(JSON)를 생성한다.
- 페이지의 <h1>, 히어로 부제(<p>)를 추출하고, 슬러그로 카테고리(group)를 부여한다.
- 결과: assets/data/related-index.json
새 카드뉴스를 추가한 뒤 이 스크립트를 다시 실행하면 인덱스가 갱신된다.
"""
import re, glob, os, json, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 슬러그 → 카테고리(group)
GROUP_BY_SLUG = {
    # 멘탈·마음
    "confidence": "mental", "consistency": "mental", "effort": "mental",
    "enjoyment": "mental", "failure": "mental", "growth": "mental",
    "mental": "mental", "rolemodel": "mental", "legend-quotes": "mental",
    # 기술·전술
    "agility": "skill", "dribbling": "skill", "first-touch": "skill",
    "goalkeeper": "skill", "heading-safety": "skill", "passing": "skill",
    "positions": "skill", "shooting": "skill", "youth-defending": "skill",
    "youth-midfield": "skill", "youth-movements": "skill",
    # 영양·건강
    "bone-health": "nutrition", "hydration": "nutrition", "iron": "nutrition",
    "match-meals": "nutrition", "meal-plan": "nutrition", "nutrition": "nutrition",
    "recovery-nutrition": "nutrition", "snacks": "nutrition", "supplements": "nutrition",
    # 훈련·컨디션
    "home-training": "training", "injury-prevention": "training", "warmup": "training",
    # 시작·부모
    "age-development": "parenting", "intro": "parenting", "start-youth": "parenting",
    "parents": "parenting", "etiquette": "parenting",
    # 장비
    "soccer-shoes": "gear",
}
GROUP_META = {
    "mental":    ("멘탈·마음",   "#2E7D52"),
    "skill":     ("기술·전술",   "#3A6B8A"),
    "nutrition": ("영양·건강",   "#B5651D"),
    "training":  ("훈련·컨디션", "#1B4332"),
    "parenting": ("시작·부모",   "#8A5A16"),
    "gear":      ("장비",        "#4A6FA5"),
    "guide":     ("가이드",      "#2E7D52"),
}

def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()

def extract(path):
    s = open(path, encoding="utf-8").read()
    m_h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S | re.I)
    h1 = strip_tags(m_h1.group(1)) if m_h1 else ""
    # 히어로 부제: <h1> 바로 뒤의 <p>
    sub = ""
    m_sub = re.search(r"<h1[^>]*>.*?</h1>\s*<p[^>]*>(.*?)</p>", s, re.S | re.I)
    if m_sub:
        sub = strip_tags(m_sub.group(1))
    if not h1:  # 폴백: <title>에서 사이트명 제거
        m_t = re.search(r"<title[^>]*>(.*?)</title>", s, re.S | re.I)
        if m_t:
            h1 = strip_tags(m_t.group(1)).split("|")[0].strip()
    return h1, sub

def main():
    files = sorted(glob.glob(os.path.join(ROOT, "pages", "guide-*.html")) +
                   glob.glob(os.path.join(ROOT, "pages", "cardnews-*.html")))
    items = []
    for f in files:
        base = os.path.basename(f)
        name = base[:-5]  # .html 제거
        kind = "cardnews" if name.startswith("cardnews-") else "guide"
        slug = name.split("-", 1)[1] if "-" in name else name
        group = GROUP_BY_SLUG.get(slug, "guide")
        label, color = GROUP_META[group]
        title, sub = extract(f)
        if kind == "cardnews":
            title = re.sub(r"\s*·\s*카드뉴스\s*$", "", title)
            sub = sub or "카드뉴스로 한눈에"
            label = label + " · 카드뉴스"
        items.append({
            "url": "/pages/" + base,
            "title": title,
            "subtitle": sub,
            "group": group,
            "catLabel": label,
            "color": color,
            "kind": kind,
        })
    out = os.path.join(ROOT, "assets", "data", "related-index.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(items, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {len(items)} items -> {out}")

if __name__ == "__main__":
    main()
