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
 "07-nutrition": """
   <path d="M50 32 C43 24 27 25 27 44 C27 62 39 80 50 80 C61 80 73 62 73 44 C73 25 57 24 50 32 Z"/>
   <path d="M50 32 V21"/>
   <path d="M50 25 C50 16 58 9 68 9 C68 18 60 25 50 25 Z"/>
 """,
 "08-meal": """
   <circle cx="50" cy="52" r="22"/>
   <circle cx="50" cy="52" r="14"/>
   <path d="M15 18 V30 M20 18 V30 M25 18 V30"/>
   <path d="M15 30 H25"/>
   <path d="M20 30 V84"/>
   <path d="M85 18 C79 22 79 40 85 44 V84"/>
 """,
 "09-hydration": """
   <path d="M50 12 C50 12 28 37 28 55 A22 22 0 0 0 72 55 C72 37 50 12 50 12 Z"/>
   <path d="M39 55 A11 11 0 0 0 50 66"/>
 """,
 "10-snack": """
   <path d="M24 24 A46 46 0 0 0 72 72 A5 5 0 0 0 69 63 A35 35 0 0 1 33 27 A5 5 0 0 0 24 24 Z"/>
   <path d="M24 24 C20 19 22 15 27 14"/>
 """,
 "11-summer": """
   <circle cx="50" cy="50" r="18"/>
   <path d="M50 14 V24"/><path d="M50 76 V86"/>
   <path d="M14 50 H24"/><path d="M76 50 H86"/>
   <path d="M27 27 L34 34"/><path d="M73 27 L66 34"/>
   <path d="M27 73 L34 66"/><path d="M73 73 L66 66"/>
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
