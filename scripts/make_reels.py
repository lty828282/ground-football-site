#!/usr/bin/env python3
"""인스타 릴스(9:16, 1080x1920) 2종 생성.

  A) 무료 스톡 영상(Pexels) + 자막 훈련팁 릴스
  B) 카드뉴스(소개) 모션 릴스 — 기존 슬라이드에 줌·전환 애니메이션

자막은 Pillow(나눔고딕)로 렌더, 합성은 ffmpeg. 러너에서 실행(make-reels.yml).
결과물: exports/reels/A-training-tip.mp4, exports/reels/B-intro-motion.mp4
"""
import os, sys, json, subprocess, urllib.request, urllib.parse, urllib.error, pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "exports" / "reels"
TMP = pathlib.Path("/tmp/reels"); TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
KEY = (os.environ.get("PEXELS_API_KEY") or "").strip()

# ── 폰트 ─────────────────────────────────────────────
def _font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

BOLD = ["/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicExtraBold.ttf"]
REG  = ["/usr/share/fonts/truetype/nanum/NanumGothic.ttf"]

def fb(sz): return _font(BOLD, sz)
def fr(sz): return _font(REG, sz)

GREEN = (126, 217, 87)      # #7ED957
AMBER = (255, 213, 79)      # #FFD54F
WHITE = (255, 255, 255)
GREY  = (206, 217, 210)

# ── 그리기 헬퍼 ──────────────────────────────────────
def wrap(draw, text, font, maxw):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def ctext(draw, cy, text, font, fill, maxw=920, lh=1.18, shadow=True):
    lines = []
    for para in text.split("\n"):
        lines += wrap(draw, para, font, maxw)
    asc, desc = font.getmetrics()
    lineh = int((asc + desc) * lh)
    y = cy - lineh * len(lines) // 2
    for ln in lines:
        w = draw.textlength(ln, font=font)
        x = (W - w) / 2
        if shadow:
            draw.text((x+3, y+3), ln, font=font, fill=(0, 0, 0, 150))
        draw.text((x, y), ln, font=font, fill=fill)
        y += lineh
    return y

def scrim():
    """하단 가독성 그라데이션 + 상단 살짝. (1px 세로줄→리사이즈로 빠르게)"""
    alpha = Image.new("L", (1, H))
    ap = alpha.load()
    for y in range(H):
        a = 0
        if y > H * 0.42:
            a = int(215 * (y - H*0.42) / (H*0.58))
        if y < 210:
            a = max(a, int(120 * (210 - y) / 210))
        ap[0, y] = min(a, 230)
    img = Image.new("RGBA", (W, H), (9, 20, 14, 255))
    img.putalpha(alpha.resize((W, H)))
    return img

SCRIM = scrim()

def brand(draw):
    # 좌상단 워드마크 + 그린 바
    draw.rectangle([70, 96, 132, 106], fill=GREEN)
    draw.text((70, 120), "GROUND YOUTH", font=fb(40), fill=WHITE)
    # 하단 핸들
    h = "@groundyouth"
    draw.text((70, H-96), h, font=fb(38), fill=WHITE)

def beat(fn):
    img = SCRIM.copy()
    d = ImageDraw.Draw(img)
    brand(d)
    fn(d)
    p = TMP / fn.__name__
    img.save(p.with_suffix(".png"))
    return str(p.with_suffix(".png"))

# ── A) 스톡 영상 + 자막 ──────────────────────────────
def beats_training():
    def b0_hook(d):
        ctext(d, 1330, "우리 아이 드리블\n이것만 지켜도 달라져요", fb(78), WHITE, lh=1.22)
        d.text((70, 1470), "3가지 습관", font=fb(46), fill=AMBER)
    def b1_step1(d):
        d.text((70, 1230), "①", font=fb(150), fill=AMBER)
        d.text((70, 1420), "공을 몸 가까이", font=fb(70), fill=WHITE)
        d.text((72, 1520), "터치는 짧고 자주 · 뺏기지 않게", font=fr(40), fill=GREY)
    def b2_step2(d):
        d.text((70, 1230), "②", font=fb(150), fill=AMBER)
        d.text((70, 1420), "고개 들고 앞을 보기", font=fb(70), fill=WHITE)
        d.text((72, 1520), "공만 보지 말고 시야 넓히기", font=fr(40), fill=GREY)
    def b3_step3(d):
        d.text((70, 1230), "③", font=fb(150), fill=AMBER)
        d.text((70, 1420), "양발 번갈아 터치", font=fb(70), fill=WHITE)
        d.text((72, 1520), "약한 발도 함께 · 좌우 균형", font=fr(40), fill=GREY)
    def b4_cta(d):
        ctext(d, 1360, "저장하고\n오늘 바로 연습!", fb(84), WHITE, lh=1.2)
        ctext(d, 1560, "매일 유소년 축구 팁 · @groundyouth", fb(40), GREEN)
    return [
        (beat(b0_hook), 0.0, 3.2),
        (beat(b1_step1), 3.2, 6.5),
        (beat(b2_step2), 6.5, 9.8),
        (beat(b3_step3), 9.8, 13.0),
        (beat(b4_cta), 13.0, 15.0),
    ]

def fetch_pexels_video():
    if not KEY:
        print("PEXELS_API_KEY 없음", file=sys.stderr); return None
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode({
        "query": "boy soccer training dribbling", "per_page": 15,
        "orientation": "portrait", "size": "medium"})
    req = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            data = json.load(r)
    except Exception as e:
        print("Pexels 실패:", e, file=sys.stderr); return None
    vids = data.get("videos") or []
    for v in vids:
        files = [f for f in v.get("video_files", []) if (f.get("height") or 0) >= 1200
                 and (f.get("width") or 0) <= (f.get("height") or 0)]
        files.sort(key=lambda f: f.get("height", 0))
        if not files:
            continue
        link = files[0]["link"]
        dst = TMP / "stock.mp4"
        try:
            rq = urllib.request.Request(link, headers={"User-Agent": UA})
            with urllib.request.urlopen(rq, timeout=90) as resp, open(dst, "wb") as out:
                out.write(resp.read())
            print("stock video:", v.get("id"), files[0]["width"], "x", files[0]["height"])
            return str(dst)
        except Exception as e:
            print("다운로드 실패:", e, file=sys.stderr); continue
    return None

def build_A():
    src = fetch_pexels_video()
    if not src:
        print("A 릴스 건너뜀(영상 없음)"); return None
    bs = beats_training()
    inp = ["-stream_loop", "9", "-i", src]
    for png, _, _ in bs:
        inp += ["-i", png]
    # 배경: 1080x1920 커버 크롭
    fc = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,trim=0:15,setpts=PTS-STARTPTS[bg];"
    prev = "bg"
    for i, (_, s, e) in enumerate(bs, start=1):
        out = f"v{i}"
        fc += f"[{prev}][{i}:v]overlay=0:0:enable='between(t,{s},{e})'[{out}];"
        prev = out
    fc = fc.rstrip(";")
    dst = OUT / "A-training-tip.mp4"
    cmd = ["ffmpeg", "-y", *inp,
           "-f", "lavfi", "-t", "15", "-i", "anullsrc=r=44100:cl=stereo",
           "-filter_complex", fc, "-map", f"[{prev}]", "-map", f"{len(bs)+1}:a",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-t", "15",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dst)]
    subprocess.run(cmd, check=True)
    print("A 완성:", dst)
    return dst

# ── B) 카드뉴스 모션 릴스 ────────────────────────────
def build_B():
    slides = sorted((ROOT / "exports" / "intro").glob("slide*.png"))
    if not slides:
        print("intro 슬라이드 없음 → B 건너뜀"); return None
    # 각 슬라이드를 1080x1920 브랜드 캔버스에 배치
    frames = []
    for i, sp in enumerate(slides, 1):
        # 은은한 세로 그라데이션 (1px 세로줄→리사이즈)
        col = Image.new("RGB", (1, H)); cp = col.load()
        for y in range(H):
            t = y / H
            cp[0, y] = (int(36*(1-t)+16*t), int(90*(1-t)+40*t), int(60*(1-t)+29*t))
        canvas = col.resize((W, H))
        card = Image.open(sp).convert("RGB")
        cw = 980
        ch = int(card.height * cw / card.width)
        card = card.resize((cw, ch))
        cx = (W - cw)//2; cy = (H - ch)//2
        canvas.paste(card, (cx, cy))
        d = ImageDraw.Draw(canvas)
        d.rectangle([cx, cy+90, cx+64, cy+100], fill=GREEN)  # 살짝 포인트(가림 최소)
        d.text((70, 70), "GROUND YOUTH", font=fb(40), fill=WHITE)
        d.text((70, H-96), "@groundyouth · 프로필에서 더보기", font=fb(38), fill=WHITE)
        fp = TMP / f"bframe{i}.png"; canvas.save(fp); frames.append(str(fp))
    # 각 프레임 → 2.5s 줌 클립
    clips = []
    for i, fp in enumerate(frames):
        cp = TMP / f"bclip{i}.mp4"
        vf = ("zoompan=z='min(zoom+0.0009,1.10)':d=75:x='iw/2-(iw/zoom/2)':"
              "y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,setsar=1")
        subprocess.run(["ffmpeg", "-y", "-loop", "1", "-t", "2.5", "-i", fp,
                        "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", str(cp)],
                       check=True)
        clips.append(str(cp))
    # xfade 체인
    inp = []
    for c in clips: inp += ["-i", c]
    d_tr = 0.4; seg = 2.5
    fc = ""; prev = "0:v"; total = seg
    for k in range(1, len(clips)):
        out = f"x{k}"
        off = total - d_tr
        fc += f"[{prev}][{k}:v]xfade=transition=fade:duration={d_tr}:offset={off}[{out}];"
        prev = out; total += seg - d_tr
    fc = fc.rstrip(";")
    dst = OUT / "B-intro-motion.mp4"
    subprocess.run(["ffmpeg", "-y", *inp,
                    "-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=44100:cl=stereo",
                    "-filter_complex", fc, "-map", f"[{prev}]", "-map", f"{len(clips)}:a",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dst)],
                   check=True)
    print("B 완성:", dst)
    return dst

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("A", "both"): build_A()
    if which in ("B", "both"): build_B()
    print("RESULT: reels done")
