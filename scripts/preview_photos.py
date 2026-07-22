#!/usr/bin/env python3
# 사진 테마(training/match) 미리보기 생성기 — GitHub 러너에서 실행.
# Pexels 로 실제 사진을 받아 base64 로 임베드한 자체 완결형 HTML(preview/photo-preview.html)을 만든다.
# (로컬 샌드박스는 Pexels 접속이 막혀 있어, 이 스크립트는 러너에서만 의미가 있음)

import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "preview", "photo-preview.html")
KEY = (os.environ.get("PEXELS_API_KEY") or "").strip()


def pexels(query, n):
    """검색해서 최대 n장의 (base64 data URI, 촬영자) 반환."""
    if not KEY:
        return []
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": max(n + 4, 10), "orientation": "portrait", "size": "medium"})
    req = urllib.request.Request(url, headers={"Authorization": KEY})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except Exception as e:  # noqa
        print("검색 실패:", query, e, file=sys.stderr)
        return []
    out = []
    for ph in (data.get("photos") or [])[:n]:
        src = ph.get("src") or {}
        u = src.get("large") or src.get("medium") or src.get("portrait")
        if not u:
            continue
        try:
            with urllib.request.urlopen(u, timeout=60) as r:
                raw = r.read()
        except Exception as e:  # noqa
            print("다운로드 실패:", e, file=sys.stderr)
            continue
        b64 = base64.b64encode(raw).decode("ascii")
        out.append(("data:image/jpeg;base64," + b64, ph.get("photographer") or "Pexels"))
    return out


CSS = """
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Pretendard',sans-serif;background:#0c1016;color:#fff;padding:26px 12px 60px;}
.lead{max-width:820px;margin:0 auto 20px;text-align:center;color:#c9d2dc;font-size:14px;line-height:1.7;}
.lead b{color:#fff;} .lead .tag{display:inline-block;background:#FF7A1A;color:#160b03;font-weight:800;font-size:11px;padding:3px 10px;border-radius:999px;margin-bottom:10px;}
.grid{display:flex;flex-wrap:wrap;gap:16px;justify-content:center;}
.cnx-card{--accent:#FF7A1A;--hl:#FF7A1A;--series:#ffb27a;--mark:#FF7A1A;
  --ov:linear-gradient(180deg,rgba(14,8,3,.5),rgba(14,8,3,.16) 42%,rgba(14,8,3,.9));
  position:relative;width:320px;aspect-ratio:4/5;overflow:hidden;border-radius:18px;color:#fff;
  background:#111 center/cover no-repeat;display:flex;flex-direction:column;box-shadow:0 10px 30px rgba(0,0,0,.45);}
.cnx-match{--accent:#F5A623;--hl:#F5A623;--series:#F5A623;--mark:#0b1f45;
  --ov:linear-gradient(180deg,rgba(6,12,28,.5),rgba(6,12,28,.16) 42%,rgba(6,12,28,.86));}
.cnx-card::after{content:"";position:absolute;inset:0;z-index:0;background:var(--ov);}
.cnx-card>*{position:relative;z-index:1;}
.cnx-top{display:flex;justify-content:space-between;gap:12px;padding:20px 24px 0;font-weight:800;font-size:12px;letter-spacing:.5px;}
.cnx-series{color:var(--series);} .cnx-bar{display:block;width:32px;height:4px;background:var(--accent);border-radius:2px;margin-bottom:8px;}
.cnx-handle{opacity:.9;font-weight:700;}
.cnx-main{flex:1;display:flex;flex-direction:column;justify-content:flex-end;padding:0 24px;}
.cnx-tick{display:block;width:32px;height:4px;background:var(--accent);border-radius:2px;margin-bottom:11px;}
.cnx-kicker{font-size:13px;font-weight:800;margin-bottom:13px;text-shadow:0 2px 10px rgba(0,0,0,.6);}
.cnx-no{font-family:'Black Han Sans',sans-serif;font-size:56px;line-height:.92;color:var(--accent);margin-bottom:6px;text-shadow:0 2px 14px rgba(0,0,0,.5);}
.cnx-hl{color:var(--hl);}
.cnx-title{font-family:'Black Han Sans',sans-serif;font-size:32px;line-height:1.22;margin:2px 0 12px;text-shadow:0 2px 14px rgba(0,0,0,.6);}
.cnx-underline{display:block;width:110px;height:4px;background:var(--accent);border-radius:2px;margin:2px 0 15px;}
.cnx-sub{font-size:17px;font-weight:800;margin-bottom:9px;text-shadow:0 2px 12px rgba(0,0,0,.6);}
.cnx-body{font-size:14px;line-height:1.7;opacity:.97;max-width:90%;text-shadow:0 2px 12px rgba(0,0,0,.6);}
.cnx-cta{font-size:13px;opacity:.85;line-height:1.6;text-shadow:0 2px 12px rgba(0,0,0,.6);}
.cnx-bottom{padding:14px 24px 20px;}
.cnx-dots{display:flex;gap:6px;justify-content:center;margin-bottom:11px;}
.cnx-dots i{width:22px;height:3px;border-radius:2px;background:rgba(255,255,255,.4);} .cnx-dots i.on{background:var(--accent);}
.cnx-mark{text-align:center;font-weight:800;letter-spacing:1.5px;font-size:13px;color:var(--mark);text-shadow:0 2px 10px rgba(0,0,0,.6);}
.cap{max-width:760px;margin:20px auto 0;font-size:12px;color:#8a97a6;text-align:center;}
.lbl{width:100%;text-align:center;font-size:12px;color:#93a0a8;margin:6px 0 -4px;}
"""


def dots(total, active):
    return '<div class="cnx-dots">' + "".join('<i class="on"></i>' if i == active else "<i></i>" for i in range(total)) + "</div>"


def card(theme, bg, series, kicker, number, title, body, sub, cta, total, active):
    inner = '<div class="cnx-kicker">%s</div>' % kicker if kicker else ""
    if number:
        inner += '<span class="cnx-tick"></span><div class="cnx-no">%s</div>' % number
    inner += '<h2 class="cnx-title">%s</h2>' % title
    if sub or cta:
        inner += '<span class="cnx-underline"></span>'
    if body:
        inner += '<p class="cnx-body">%s</p>' % body
    if sub:
        inner += '<div class="cnx-sub">%s</div>' % sub
    if cta:
        inner += '<div class="cnx-cta">%s</div>' % cta
    style = ' style="background-image:url(%s)"' % bg if bg else ""
    return ('<div class="cnx-card %s"%s>'
            '<div class="cnx-top"><span class="cnx-series"><i class="cnx-bar"></i>%s</span><span class="cnx-handle">groundyouth.com</span></div>'
            '<div class="cnx-main">%s</div>'
            '<div class="cnx-bottom">%s<div class="cnx-mark">GROUND YOUTH</div></div>'
            '</div>' % (theme, style, series, inner, dots(total, active)))


def main():
    tr = pexels("kids soccer warm up training field", 3)
    mt = pexels("soccer player dribbling match stadium", 1)
    note = ""
    if not (tr or mt):
        note = "<p style='color:#ff8a8a'>사진을 받지 못했습니다 — PEXELS_API_KEY 시크릿을 확인하세요.</p>"

    def bg(lst, i):
        return lst[i][0] if i < len(lst) else ""

    cards = []
    cards.append('<div style="width:320px"><div class="lbl">TRAINING · 커버</div>' + card(
        "cnx-training", bg(tr, 0), "TRAINING CLASS", "GROUND YOUTH · 축구 훈련", "",
        "경기 전<br>워밍업 5단계", "", "부상 없이, 처음부터 <span class='cnx-hl'>100%</span>로",
        "저장해두고 다음 편도 확인하세요", 7, 0) + "</div>")
    cards.append('<div style="width:320px"><div class="lbl">TRAINING · 01</div>' + card(
        "cnx-training", bg(tr, 1), "TRAINING CLASS", "", "01",
        "가볍게 뛰기", "먼저 3~5분 조깅으로 체온을 올립니다. 심장이 <span class='cnx-hl'>'이제 운동한다'</span>고 준비하도록.",
        "", "", 7, 1) + "</div>")
    cards.append('<div style="width:320px"><div class="lbl">TRAINING · 02</div>' + card(
        "cnx-training", bg(tr, 2), "TRAINING CLASS", "", "02",
        "동적 스트레칭", "다리 흔들기, 무릎 올리기, 사이드 스텝. <span class='cnx-hl'>'움직이며'</span> 푸는 게 좋아요.",
        "", "", 7, 2) + "</div>")
    cards.append('<div style="width:320px"><div class="lbl">MATCH · 샘플</div>' + card(
        "cnx-match", bg(mt, 0), "MATCH ANALYSIS", "스페인 2-1 벨기에 · 월드컵", "",
        "공격포인트<br>없이 <span class='cnx-hl'>POTM</span>", "", "무엇으로 경기를 지배했나?",
        "골도 도움도 없었다. 그런데 흐름은 그에게서 시작됐다.", 6, 0) + "</div>")

    credits = list(dict.fromkeys([c for _, c in (tr + mt)]))
    cap = ("사진 © %s / Pexels" % ", ".join(credits)) if credits else ""

    html = ("<!DOCTYPE html><html lang='ko'><head><meta charset='UTF-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            "<title>사진 테마 미리보기</title>"
            "<link href='https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap' rel='stylesheet'>"
            "<link rel='stylesheet' as='style' crossorigin href='https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css'>"
            "<style>%s</style></head><body>"
            "<div class='lead'><span class='tag'>사진 테마 실제 미리보기 (Pexels)</span><br>"
            "훈련(주황)·경기분석(남색+앰버) 테마에 <b>실제 사진</b>이 들어간 모습입니다. %s</div>"
            "<div class='grid'>%s</div><div class='cap'>%s</div></body></html>"
            % (CSS, note, "".join(cards), cap))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("생성 완료:", OUT, "| 사진", len(tr) + len(mt), "장")


if __name__ == "__main__":
    main()
