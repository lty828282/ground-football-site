#!/usr/bin/env python3
"""인스타 하이라이트(스토리) 커버 6종 생성. 1080x1080, 원형 크롭 안전영역 중앙 배치."""
import subprocess, pathlib, os

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "img" / "highlight-covers"
OUT.mkdir(exist_ok=True)
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# 아이콘: 로컬 viewBox 0 0 100 100, stroke=currentColor(흰색), 선 아이콘
ICONS = {
 "01-about": """
   <circle cx="50" cy="50" r="40"/>
   <polygon points="50,35 64.3,45.4 58.8,62.1 41.2,62.1 35.7,45.4"/>
   <line x1="50" y1="35" x2="50" y2="10"/>
   <line x1="64.3" y1="45.4" x2="79" y2="40"/>
   <line x1="58.8" y1="62.1" x2="66" y2="82"/>
   <line x1="41.2" y1="62.1" x2="34" y2="82"/>
   <line x1="35.7" y1="45.4" x2="21" y2="40"/>
 """,
 "02-training": """
   <path d="M35 80 L50 22 L65 80"/>
   <line x1="28" y1="80" x2="72" y2="80"/>
   <line x1="43.5" y1="52" x2="56.5" y2="52"/>
   <line x1="39" y1="66" x2="61" y2="66"/>
 """,
 "03-motivation": """
   <path d="M50 14 C58 30 67 34 67 52 A17 17 0 0 1 33 52 C33 43 38 38 41 34
            C42 39 45 41 47 44 C49 36 43 30 50 14 Z"/>
   <path d="M50 47 C53 51 55 53 55 58 A5 5 0 0 1 45 58 C45 55 47 53 50 47 Z"/>
 """,
 "04-gear": """
   <path d="M31 24 L18 32 L24 44 L32 40 V74 H68 V40 L76 44 L82 32 L69 24
            C64 31 36 31 31 24 Z"/>
   <path d="M40 27 C44 32 56 32 60 27"/>
 """,
 "05-parents": """
   <path d="M50 78 C20 58 14 40 26 30 C34 23 44 26 50 35
            C56 26 66 23 74 30 C86 40 80 58 50 78 Z"/>
 """,
 "06-tips": """
   <path d="M50 14 A21 21 0 0 1 64 49 C60 53 59 56 59 61 H41
            C41 56 40 53 36 49 A21 21 0 0 1 50 14 Z"/>
   <line x1="42" y1="68" x2="58" y2="68"/>
   <line x1="45" y1="74" x2="55" y2="74"/>
   <line x1="46" y1="61" x2="46" y2="52"/>
   <line x1="54" y1="61" x2="54" y2="52"/>
 """,
}

TPL = """<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:540px;height:540px;overflow:hidden;background:#10281D}}
.c{{position:fixed;inset:0;
  background:radial-gradient(circle at 50% 42%,#245A3C 0%,#1A4531 48%,#10281D 100%);
  display:flex;align-items:center;justify-content:center}}
.ring{{position:absolute;width:392px;height:392px;border-radius:50%;
  border:2px solid rgba(255,213,79,.45)}}
.ring2{{position:absolute;width:440px;height:440px;border-radius:50%;
  border:1px solid rgba(255,255,255,.10)}}
.ico{{width:210px;height:210px;color:#fff;
  filter:drop-shadow(0 6px 14px rgba(0,0,0,.35))}}
.ico svg{{width:100%;height:100%;fill:none;stroke:currentColor;
  stroke-width:4.4;stroke-linecap:round;stroke-linejoin:round}}
</style></head><body>
<div class="c"><div class="ring2"></div><div class="ring"></div>
  <div class="ico"><svg viewBox="0 0 100 100">{icon}</svg></div>
</div></body></html>"""

for name, icon in ICONS.items():
    html = TPL.format(icon=icon)
    hp = OUT / f"{name}.html"
    hp.write_text(html, encoding="utf-8")
    png = OUT / f"{name}.png"
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
        "--hide-scrollbars", "--force-device-scale-factor=2",
        "--window-size=540,540", f"--screenshot={png}", hp.as_uri()],
        check=True, stderr=subprocess.DEVNULL)
    print("rendered", png.name)
print("DONE")
