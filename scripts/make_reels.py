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

def ctext(draw, cy, text, font, fill, maxw=920, lh=1.18, shadow=True,
          stroke_width=0, stroke_fill=(0, 0, 0)):
    lines = []
    for para in text.split("\n"):
        lines += wrap(draw, para, font, maxw)
    asc, desc = font.getmetrics()
    lineh = int((asc + desc) * lh)
    y = cy - lineh * len(lines) // 2
    for ln in lines:
        w = draw.textlength(ln, font=font)
        x = (W - w) / 2
        if shadow and not stroke_width:
            draw.text((x+3, y+3), ln, font=font, fill=(0, 0, 0, 150))
        draw.text((x, y), ln, font=font, fill=fill,
                  stroke_width=stroke_width, stroke_fill=stroke_fill)
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

def qdim():
    """명언 릴스용 균일 딤 + 하단 강화(어디에 글자를 놔도 잘 읽히게)."""
    alpha = Image.new("L", (1, H)); ap = alpha.load()
    for y in range(H):
        a = 120  # 전체 균일 딤
        if y > H * 0.55:
            a = int(120 + 110 * (y - H*0.55) / (H*0.45))  # 하단 강화
        if y < 200:
            a = max(a, 150)  # 상단 워드마크 영역
        ap[0, y] = min(a, 235)
    img = Image.new("RGBA", (W, H), (9, 20, 14, 255))
    img.putalpha(alpha.resize((W, H)))
    return img

QDIM = qdim()

def brand(draw):
    # 좌상단 워드마크 + 그린 바
    draw.rectangle([70, 96, 132, 106], fill=GREEN)
    draw.text((70, 120), "GROUND YOUTH", font=fb(40), fill=WHITE)
    # 하단 핸들
    h = "@groundyouth"
    draw.text((70, H-96), h, font=fb(38), fill=WHITE)

def beat(fn, base=None):
    img = (base if base is not None else SCRIM).copy()
    d = ImageDraw.Draw(img)
    brand(d)
    fn(d)
    p = TMP / fn.__name__
    img.save(p.with_suffix(".png"))
    return str(p.with_suffix(".png"))

def beat_q(fn):
    return beat(fn, base=QDIM)

def qbase_png():
    """지속 베이스: 딤 + 워드마크만(자막 없음). 전체 구간에 계속 깔아 자막 전환 시 배경/브랜드가 깜빡이지 않게."""
    img = QDIM.copy()
    d = ImageDraw.Draw(img)
    brand(d)
    p = TMP / "qbase.png"
    img.save(p.with_suffix(".png"))
    return str(p.with_suffix(".png"))

def beat_qtext(fn):
    """자막만 그린 투명 오버레이(딤/브랜드 없음). 지속 베이스 위에 얹어 전환 시 텍스트만 사라지게."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fn(d)
    p = TMP / ("t_" + fn.__name__)
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

def fetch_pexels_video(query="boy soccer training dribbling", name="stock.mp4"):
    if not KEY:
        print("PEXELS_API_KEY 없음", file=sys.stderr); return None
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode({
        "query": query, "per_page": 15,
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
        dst = TMP / name
        try:
            rq = urllib.request.Request(link, headers={"User-Agent": UA})
            with urllib.request.urlopen(rq, timeout=90) as resp, open(dst, "wb") as out:
                out.write(resp.read())
            print("stock video:", v.get("id"), files[0]["width"], "x", files[0]["height"])
            return str(dst)
        except Exception as e:
            print("다운로드 실패:", e, file=sys.stderr); continue
    return None

def fetch_pexels_clips(queries, n, prefix):
    """여러 검색어에서 '서로 다른' 세로 클립 n개를 모은다(중복 영상 ID 제외)."""
    if not KEY:
        print("PEXELS_API_KEY 없음", file=sys.stderr); return []
    got, seen = [], set()
    for q in queries:
        if len(got) >= n:
            break
        url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode({
            "query": q, "per_page": 15,
            "orientation": "portrait", "size": "medium"})
        req = urllib.request.Request(url, headers={"Authorization": KEY, "User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.load(r)
        except Exception as e:
            print("Pexels 실패:", e, file=sys.stderr); continue
        for v in data.get("videos") or []:
            if len(got) >= n:
                break
            vid = v.get("id")
            if vid in seen:
                continue
            files = [f for f in v.get("video_files", []) if (f.get("height") or 0) >= 1200
                     and (f.get("width") or 0) <= (f.get("height") or 0)]
            files.sort(key=lambda f: f.get("height", 0))
            if not files:
                continue
            dst = TMP / f"{prefix}_{len(got)}.mp4"
            try:
                rq = urllib.request.Request(files[0]["link"], headers={"User-Agent": UA})
                with urllib.request.urlopen(rq, timeout=90) as resp, open(dst, "wb") as out:
                    out.write(resp.read())
            except Exception as e:
                print("다운로드 실패:", e, file=sys.stderr); continue
            seen.add(vid)
            got.append(str(dst))
            print("stock clip:", vid, files[0]["width"], "x", files[0]["height"])
    return got


def build_bg_concat(srcs, dur, seg_max, prefix):
    """여러 클립을 각각 1080x1920/30fps로 정규화(최대 seg_max초)한 뒤 이어붙여
    반복 없는 배경 하나를 만든다. 총 길이가 dur보다 짧아도 렌더 단계에서 loop로 채운다."""
    segs = []
    for i, s in enumerate(srcs):
        seg = TMP / f"{prefix}_seg{i}.mp4"
        cmd = ["ffmpeg", "-y", "-i", s, "-t", str(seg_max),
               "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,"
                      "crop=1080:1920,setsar=1,fps=30",
               "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(seg)]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            segs.append(seg)
        except subprocess.CalledProcessError:
            print(f"세그먼트 정규화 실패({s}) 건너뜀", file=sys.stderr)
    if not segs:
        return None
    listfile = TMP / f"{prefix}_list.txt"
    listfile.write_text("".join(f"file '{p}'\n" for p in segs))
    out = TMP / f"{prefix}_bg.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
                    "-c", "copy", str(out)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return str(out)


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

# ── C) 재능<노력 명언 릴스 (스톡영상 + 자막) ─────────
def beats_quotes():
    def c0_cover(d):
        ctext(d, 760, "재능일까,\n노력일까", fb(100), WHITE, lh=1.16, stroke_width=6)
        ctext(d, 1010, "세계 최고들이 남긴 한마디", fb(50), AMBER, stroke_width=5)
        ctext(d, 1560, "끝까지 넘겨보세요 →", fb(46), GREEN, stroke_width=5)

    def c1_ronaldo(d):
        ctext(d, 860, "“재능이 있어도\n열심히 하지 않으면\n아무것도 아니다”",
              fb(76), WHITE, lh=1.3, stroke_width=6)
        ctext(d, 1240, "— 크리스티아누 호날두", fb(60), AMBER, stroke_width=7)

    def c2_pele(d):
        ctext(d, 860, "“성공은\n우연이 아니다.\n노력, 인내,\n그리고 희생이다”",
              fb(74), WHITE, lh=1.28, stroke_width=6)
        ctext(d, 1320, "— 펠레", fb(60), AMBER, stroke_width=7)

    def c3_beckham(d):
        ctext(d, 860, "“내 비결은 연습이다.\n특별한 걸 이루려면\n일하고, 또 일해야 한다”",
              fb(70), WHITE, lh=1.3, stroke_width=6)
        ctext(d, 1240, "— 데이비드 베컴", fb(60), AMBER, stroke_width=7)

    def c4_park(d):
        ctext(d, 860, "“나는 천재가 아니었다.\n그저 남들보다\n더 뛰었을 뿐이다”",
              fb(74), WHITE, lh=1.3, stroke_width=6)
        ctext(d, 1240, "— 박지성", fb(60), AMBER, stroke_width=7)

    def c5_cta(d):
        ctext(d, 820, "재능은 시작일 뿐,\n끝까지 가는 건\n노력이다", fb(84), WHITE, lh=1.24, stroke_width=6)
        ctext(d, 1190, "우리 아이의 오늘 한 걸음을 응원해요", fb(50), WHITE, stroke_width=6)
        ctext(d, 1560, "매일 유소년 축구 이야기 · @groundyouth", fb(44), GREEN, stroke_width=5)

    return [
        (beat_q(c0_cover),  0.0,  3.2),
        (beat_q(c1_ronaldo), 3.2,  7.2),
        (beat_q(c2_pele),    7.2, 11.2),
        (beat_q(c3_beckham),11.2, 15.2),
        (beat_q(c4_park),   15.2, 19.2),
        (beat_q(c5_cta),    19.2, 22.0),
    ]

def build_C():
    src = fetch_pexels_video("soccer player training sunset", "stock_c.mp4") \
        or fetch_pexels_video("soccer training", "stock_c.mp4")
    if not src:
        print("C 릴스 건너뜀(영상 없음)"); return None
    bs = beats_quotes()
    dur = 22
    inp = ["-stream_loop", "12", "-i", src]
    for png, _, _ in bs:
        inp += ["-i", png]
    fc = (f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
          f"crop=1080:1920,setsar=1,fps=30,trim=0:{dur},setpts=PTS-STARTPTS[bg];")
    prev = "bg"
    for i, (_, s, e) in enumerate(bs, start=1):
        out = f"v{i}"
        fc += f"[{prev}][{i}:v]overlay=0:0:enable='between(t,{s},{e})'[{out}];"
        prev = out
    fc = fc.rstrip(";")
    dst = OUT / "C-effort-quotes.mp4"
    cmd = ["ffmpeg", "-y", *inp,
           "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo",
           "-filter_complex", fc, "-map", f"[{prev}]", "-map", f"{len(bs)+1}:a",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-t", str(dur),
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dst)]
    subprocess.run(cmd, check=True)
    print("C 완성:", dst)
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
                    "-crf", "30", "-maxrate", "3M", "-bufsize", "6M", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dst)],
                   check=True)
    print("B 완성:", dst)
    return dst

# ── 공용: 스톡 훈련영상 + 자막 릴스 렌더 ───────────────
def _render_quote_reel(dst_name, beats, dur, queries, tmp, persist_base=None):
    prefix = tmp.rsplit(".", 1)[0]  # 파일명 충돌 방지용 접두어
    # 서로 다른 클립 여러 개를 모아 이어붙여 배경으로 사용 → 같은 장면 반복을 줄인다.
    clips = fetch_pexels_clips(queries, n=4, prefix=prefix)
    if not clips:
        print(f"{dst_name} 건너뜀(영상 없음)"); return None
    if len(clips) >= 2:
        seg_max = max(6, -(-dur // len(clips)) + 3)  # 클립당 상한(초): 총합이 dur을 넉넉히 넘게
        bg = build_bg_concat(clips, dur, seg_max, prefix)
        # 이어붙인 배경이 혹시 dur보다 짧아도 무한 loop로 안전하게 채운다.
        inp = ["-stream_loop", "-1", "-i", bg] if bg else ["-stream_loop", "16", "-i", clips[0]]
    else:
        inp = ["-stream_loop", "16", "-i", clips[0]]
    # 지속 베이스(딤+브랜드)를 먼저 입력으로 추가 → 전체 구간 상시 표시
    if persist_base:
        inp += ["-i", persist_base]
    for png, _, _ in beats:
        inp += ["-i", png]
    fc = (f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
          f"crop=1080:1920,setsar=1,fps=30,trim=0:{dur},setpts=PTS-STARTPTS[bg];")
    prev = "bg"
    idx = 1
    if persist_base:
        fc += f"[{prev}][{idx}:v]overlay=0:0[b0];"
        prev = "b0"; idx += 1
    for j, (_, s, e) in enumerate(beats, start=1):
        out = f"v{j}"
        fc += f"[{prev}][{idx}:v]overlay=0:0:enable='between(t,{s},{e})'[{out}];"
        prev = out; idx += 1
    fc = fc.rstrip(";")
    dst = OUT / dst_name
    # anullsrc(무음)는 모든 영상 입력 뒤에 붙으므로 그 입력 인덱스는 idx와 같다.
    # persist_base가 입력을 하나 더 밀어내므로 len(beats)+1 하드코딩 대신 idx를 쓴다.
    audio_idx = idx
    cmd = ["ffmpeg", "-y", *inp,
           "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo",
           "-filter_complex", fc, "-map", f"[{prev}]", "-map", f"{audio_idx}:a",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-t", str(dur),
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dst)]
    subprocess.run(cmd, check=True)
    print(f"{dst_name} 완성:", dst)
    return dst


# ── D) 동기부여: 노력의 기준은 옆 사람 ────────────────
def beats_peers():
    def d0(d):
        ctext(d, 830, "네 노력의 기준은", fb(78), WHITE, lh=1.25, stroke_width=6)
        ctext(d, 945, "네 옆 사람이 정한다", fb(86), AMBER, lh=1.2, stroke_width=6)
    def d1(d):
        ctext(d, 850, "사람은 자기도 모르게\n주변의 '평균'을\n내 기준으로 삼는다", fb(72), WHITE, lh=1.36, stroke_width=6)
    def d2(d):
        ctext(d, 840, "새벽 훈련을 당연히 여기는\n친구들 사이에 있으면\n그게 나에게도 '기본'이 된다", fb(62), WHITE, lh=1.38, stroke_width=6)
    def d3(d):
        ctext(d, 850, "훈련을 하나 더 늘리기 전에\n네가 매일 어울리는\n사람부터 살펴봐라", fb(66), WHITE, lh=1.37, stroke_width=6)
    def d4(d):
        ctext(d, 880, "기준이 바뀌면,\n노력의 양은\n저절로 따라온다", fb(76), AMBER, lh=1.32, stroke_width=6)
    def d5(d):
        ctext(d, 840, "더 뛰는 사람 곁에 서라", fb(74), WHITE, lh=1.3, stroke_width=6)
        ctext(d, 1180, "매일 유소년 축구 이야기 · @groundyouth", fb(42), GREEN, stroke_width=5)
    return [
        (beat_q(d0), 0.0, 4.3),
        (beat_q(d1), 4.1, 8.8),
        (beat_q(d2), 8.6, 13.7),
        (beat_q(d3), 13.5, 18.3),
        (beat_q(d4), 18.1, 22.7),
        (beat_q(d5), 22.5, 26.5),
    ]

def build_D():
    return _render_quote_reel("D-peers.mp4", beats_peers(), 26,
        ["youth soccer team training", "kids soccer practice group", "soccer training session"],
        "stock_d.mp4")


# ── E) 동기부여: 재능은 출발선, 습관은 결승선 ─────────
def beats_habit():
    def e0(d):
        ctext(d, 820, "재능은 출발선을 정하고", fb(70), WHITE, lh=1.25, stroke_width=6)
        ctext(d, 945, "습관은 결승선을 정한다", fb(80), AMBER, lh=1.2, stroke_width=6)
    def e1(d):
        ctext(d, 880, "재능 있는 아이는\n남들보다\n앞에서 출발한다", fb(74), WHITE, lh=1.34, stroke_width=6)
    def e2(d):
        ctext(d, 870, "하지만 경기는\n출발선이 아니라\n결승선에서 판가름 난다", fb(68), WHITE, lh=1.36, stroke_width=6)
    def e3(d):
        ctext(d, 850, "열두 살에 최고였던 아이가\n열여덟엔 사라지는 걸\n수도 없이 봤다", fb(62), WHITE, lh=1.38, stroke_width=6)
    def e4(d):
        ctext(d, 840, "그때 평범했던 아이가\n매일 같은 시간에 공을 만진다\n그 습관으로 끝까지 남는다", fb(60), WHITE, lh=1.38, stroke_width=6)
    def e5(d):
        ctext(d, 870, "재능은 못 골라도\n습관은 오늘\n네가 고를 수 있다", fb(72), AMBER, lh=1.34, stroke_width=6)
    def e6(d):
        ctext(d, 850, "나는 재능보다\n습관에 미래를 건다", fb(76), WHITE, lh=1.3, stroke_width=6)
        ctext(d, 1200, "매일 유소년 축구 이야기 · @groundyouth", fb(42), GREEN, stroke_width=5)
    # 딤/브랜드는 지속 베이스가 상시 담당 → 자막은 '텍스트만' 오버레이.
    # 사이에 0.1s 공백을 둬 전환 시 겹침 완전 제거(베이스가 있어 배경 깜빡임 없음).
    return [
        (beat_qtext(e0), 0.0, 4.4),
        (beat_qtext(e1), 4.5, 8.9),
        (beat_qtext(e2), 9.0, 13.5),
        (beat_qtext(e3), 13.6, 18.6),
        (beat_qtext(e4), 18.7, 23.8),
        (beat_qtext(e5), 23.9, 28.1),
        (beat_qtext(e6), 28.2, 31.0),
    ]

def build_E():
    return _render_quote_reel("E-habit.mp4", beats_habit(), 31,
        ["soccer freestyle training outdoor", "teenager soccer player training field", "football skills training pitch"],
        "stock_e.mp4", persist_base=qbase_png())


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("A", "both"): build_A()
    if which in ("B", "both"): build_B()
    if which in ("C", "both"): build_C()
    if which in ("D", "both", "DE"): build_D()
    if which in ("E", "both", "DE"): build_E()
    print("RESULT: reels done")
