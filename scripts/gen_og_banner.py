#!/usr/bin/env python3
"""소셜 공유용 기본 OG 배너(1200x630) 생성 → assets/img/brand/og-default.png"""
import subprocess, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "img" / "brand"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1200px;height:630px;overflow:hidden;background:#0b1712;
  font-family:'WenQuanYi Zen Hei','Noto Sans CJK KR',sans-serif}
.c{position:relative;width:1200px;height:630px;display:flex;align-items:center;gap:52px;padding:0 92px;
  background:linear-gradient(135deg,#2E7D52 0%,#1B4332 68%,#153a25 100%);color:#fff}
.ring{flex:none;width:250px;height:250px;border-radius:50%;border:5px solid rgba(255,213,79,.6);
  display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.05)}
.ball svg{width:158px;height:158px}
.tx{display:flex;flex-direction:column;min-width:0}
.kicker{font-size:27px;font-weight:800;letter-spacing:6px;color:#FFD54F;margin-bottom:14px}
.title{font-size:82px;font-weight:900;line-height:1.05;letter-spacing:-3px;white-space:nowrap}
.sub{font-size:39px;font-weight:700;color:#cfe9d8;margin-top:20px}
.tags{font-size:27px;font-weight:600;color:#9db9a8;margin-top:22px;letter-spacing:.5px}
.url{position:absolute;right:92px;bottom:54px;font-size:31px;font-weight:800;color:#FFD54F}
.leaf{position:absolute;left:0;top:0;width:17px;height:100%;background:#43B265}
</style></head><body>
<div class="c">
  <div class="leaf"></div>
  <div class="ring"><div class="ball"><svg viewBox="0 0 100 100" fill="none">
    <circle cx="50" cy="50" r="44" stroke="#fff" stroke-width="4"/>
    <polygon points="50,30 63,40 58,56 42,56 37,40" fill="#fff"/>
    <path d="M50 12 L50 30 M79 33 L63 40 M71 74 L58 56 M29 74 L42 56 M21 33 L37 40"
      stroke="#fff" stroke-width="3.5" stroke-linecap="round"/>
  </svg></div></div>
  <div class="tx">
    <div class="kicker">GROUND YOUTH</div>
    <div class="title">그라운드 유소년</div>
    <div class="sub">유소년 축구 전문 허브</div>
    <div class="tags">훈련 · 영양 · 기본기 · 전술 · 용품</div>
  </div>
  <div class="url">groundyouth.com</div>
</div></body></html>"""

hp = OUT / "_og.html"; hp.write_text(HTML, encoding="utf-8")
png = OUT / "og-default.png"
raw = OUT / "_og_raw.png"
# 더 크게 렌더 후 정확히 1200x630으로 크롭(헤드리스 뷰포트 하단 여백 방지)
subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
    "--hide-scrollbars", "--force-device-scale-factor=1",
    "--window-size=1200,780", f"--screenshot={raw}", hp.as_uri()],
    check=True, stderr=subprocess.DEVNULL)
from PIL import Image
Image.open(raw).convert("RGB").crop((0, 0, 1200, 630)).save(png)
raw.unlink(missing_ok=True); hp.unlink(missing_ok=True)
print("rendered", png)
