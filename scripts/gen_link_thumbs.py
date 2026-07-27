#!/usr/bin/env python3
"""리틀리(link-in-bio) 상품 카드용 썸네일 4종 생성. 1080x1080 정사각, 브랜드 초록 톤."""
import subprocess, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "img" / "link-thumbs"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

ICONS = {
 "carton": """
   <path d="M32 44 L50 28 L68 44"/>
   <path d="M32 44 V82 H68 V44"/>
   <path d="M50 28 V44"/>
   <rect x="40" y="55" width="20" height="15" rx="2"/>
 """,
 "cup": """
   <path d="M36 42 H64 L59 82 H41 Z"/>
   <path d="M50 42 C50 33 56 29 65 29 C65 37 58 42 50 42 Z"/>
   <path d="M50 42 V33"/>
 """,
 "bar": """
   <path d="M34 46 H66 V62 H34 Z"/>
   <path d="M34 50 L27 46 V62 L34 58"/>
   <path d="M66 50 L73 46 V62 L66 58"/>
   <path d="M42 54 H58"/>
 """,
 "nuts": """
   <path d="M35 58 C35 50 39 45 44 45 C48 45 51 50 51 58 C51 65 47 68 43 68 C39 68 35 65 35 58 Z"/>
   <path d="M44 47 V66"/>
   <path d="M52 63 C52 56 55 52 59 52 C62 52 65 56 65 63 C65 68 62 71 58 71 C55 71 52 68 52 63 Z"/>
 """,
}

# (파일명, 아이콘, 상품명, 카테고리)
CARDS = [
 ("protein-milk", "carton", "프로틴 초코우유", "운동 후 회복 단백질"),
 ("soy-milk",     "cup",    "베지밀 초코두유", "고소한 식물성 단백"),
 ("energy-bar",   "bar",    "닥터유 에너지바", "간편 에너지 충전"),
 ("nuts",         "nuts",   "견과류 믹스넛",   "건강한 지방·간식"),
]

TPL = """<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:540px;height:540px;overflow:hidden;background:#10281D;
  font-family:'WenQuanYi Zen Hei','Noto Sans CJK KR',sans-serif}}
.c{{position:fixed;inset:0;
  background:radial-gradient(circle at 50% 38%,#245A3C 0%,#1A4531 52%,#10281D 100%);
  display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff}}
.tag{{font-size:15px;font-weight:700;letter-spacing:1px;color:#F5CE7A;margin-bottom:14px}}
.ring{{width:196px;height:196px;border-radius:50%;border:2px solid rgba(255,213,79,.5);
  display:flex;align-items:center;justify-content:center;margin-bottom:26px;
  background:rgba(255,255,255,.04)}}
.ico{{width:120px;height:120px;color:#fff}}
.ico svg{{width:100%;height:100%;fill:none;stroke:currentColor;stroke-width:4;
  stroke-linecap:round;stroke-linejoin:round}}
.name{{font-size:40px;font-weight:900;line-height:1.2;text-align:center;
  text-shadow:0 2px 10px rgba(0,0,0,.4)}}
.sub{{font-size:19px;font-weight:600;color:#B9D8C5;margin-top:12px}}
.brand{{position:absolute;bottom:34px;font-size:15px;font-weight:800;
  letter-spacing:1.5px;color:rgba(255,255,255,.7)}}
</style></head><body>
<div class="c">
  <div class="tag">GROUND YOUTH · 추천 간식</div>
  <div class="ring"><div class="ico"><svg viewBox="0 0 100 100">{icon}</svg></div></div>
  <div class="name">{name}</div>
  <div class="sub">{sub}</div>
  <div class="brand">GROUNDYOUTH.COM</div>
</div></body></html>"""

for fname, icon, name, sub in CARDS:
    html = TPL.format(icon=ICONS[icon], name=name, sub=sub)
    hp = OUT / f"{fname}.html"; hp.write_text(html, encoding="utf-8")
    png = OUT / f"{fname}.png"
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
        "--hide-scrollbars", "--force-device-scale-factor=2",
        "--window-size=540,540", f"--screenshot={png}", hp.as_uri()],
        check=True, stderr=subprocess.DEVNULL)
    print("rendered", png.name)
print("DONE")
