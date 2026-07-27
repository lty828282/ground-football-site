#!/usr/bin/env python3
"""리틀리·인스타 프로필 사진 생성. 1080x1080, 원형 크롭 대비 중앙 정렬 · 브랜드 초록+골드."""
import subprocess, pathlib, math

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "img" / "brand"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def pent(cx, cy, r, rot=-90):
    pts = []
    for i in range(5):
        a = math.radians(rot + i * 72)
        pts.append(f"{cx + r*math.cos(a):.1f},{cy + r*math.sin(a):.1f}")
    return " ".join(pts)


def seams(cx, cy, rin, rout, rot=-90):
    d = []
    for i in range(5):
        a = math.radians(rot + i * 72)
        d.append(f"M{cx + rin*math.cos(a):.1f} {cy + rin*math.sin(a):.1f} "
                 f"L{cx + rout*math.cos(a):.1f} {cy + rout*math.sin(a):.1f}")
    return " ".join(d)

CX, CY, R = 50, 50, 30
BALL = f"""
  <circle cx="{CX}" cy="{CY}" r="{R}" fill="#fff" stroke="#0E2A1C" stroke-width="1.6"/>
  <polygon points="{pent(CX,CY,11)}" fill="#1A4531"/>
  <path d="{seams(CX,CY,11,R)}" stroke="#1A4531" stroke-width="1.9"
        fill="none" stroke-linecap="round"/>
"""

TPL = """<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:540px;height:540px;overflow:hidden;background:#10281D;
  font-family:'WenQuanYi Zen Hei','Noto Sans CJK KR',sans-serif}}
.c{{position:fixed;inset:0;
  background:radial-gradient(circle at 50% 42%,#245A3C 0%,#1A4531 52%,#0E2418 100%);
  display:flex;flex-direction:column;align-items:center;justify-content:center}}
.ring{{position:absolute;width:496px;height:496px;border-radius:50%;
  border:3px solid rgba(255,213,79,.55)}}
.ball{{width:230px;height:230px;filter:drop-shadow(0 6px 16px rgba(0,0,0,.4));margin-bottom:18px}}
.ball svg{{width:100%;height:100%}}
.name{{font-size:46px;font-weight:900;color:#fff;letter-spacing:1px;
  text-shadow:0 2px 10px rgba(0,0,0,.45)}}
.tag{{margin-top:8px;font-size:20px;font-weight:700;color:#F5CE7A;letter-spacing:3px}}
</style></head><body>
<div class="c">
  <div class="ring"></div>
  <div class="ball"><svg viewBox="0 0 100 100">{ball}</svg></div>
  <div class="name">그라운드 유소년</div>
  <div class="tag">YOUTH FOOTBALL</div>
</div></body></html>"""

html = TPL.format(ball=BALL)
hp = OUT / "profile.html"; hp.write_text(html, encoding="utf-8")
png = OUT / "profile.png"
subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
    "--hide-scrollbars", "--force-device-scale-factor=2",
    "--window-size=540,540", f"--screenshot={png}", hp.as_uri()],
    check=True, stderr=subprocess.DEVNULL)
print("rendered", png.name)
print("DONE")
