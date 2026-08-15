#!/usr/bin/env python3
"""웹툰 스타일 쇼츠(9:16, 1080x1920)에 한국어 음성을 입혀 short.mp4 생성.

  toon/stories/<slug>.json 의 대사(내레이터·아빠·딸)를 읽어
  1) 한국어 TTS로 대사별 음성을 만들고(화자별 목소리 구분)
  2) 대사 길이에 맞춰 자막 프레임을 렌더한 뒤(Pillow·나눔고딕)
  3) 음성과 자막을 동기화해 이어붙여(ffmpeg) short.mp4 를 만든다.

음성 엔진
  - 기본: edge-tts(마이크로소프트 온라인 신경망 음성). 화자별로 서로 다른
    한국어 보이스를 사용해 내레이터/아빠/딸을 자연스럽게 구분한다.
  - 대체: edge-tts 접속이 막힌 환경에서는 자동으로 espeak-ng(오프라인)로
    전환하고, ffmpeg 피치 시프트로 화자(낮은 아빠 / 높은 딸 / 중간 내레이터)를
    구분한다. 결과물은 항상 '음성이 들어간' mp4 가 된다.

사용법
  python3 toon/build_short.py ilseokijo
결과물
  toon/out/<slug>/short.mp4
"""
import os, sys, json, math, asyncio, subprocess, shutil, pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOON = ROOT / "toon"
W, H = 1080, 1920
SR = 44100                 # 오디오 표준 샘플레이트
GAP = 0.35                 # 대사 사이 여백(초)
TAIL = 0.9                 # 마지막 대사 뒤 여운(초)
FPS = 30
AV_R = 128                 # 아바타 반지름
R_OFFSET = 150             # 아바타 중심 아래로 이름표 위치

# ── 색 ───────────────────────────────────────────────
GREEN  = (126, 217, 87)    # #7ED957 브랜드 그린
AMBER  = (255, 213, 79)    # #FFD54F
WHITE  = (255, 255, 255)
INK    = (17, 28, 22)      # 말풍선 글자
BUBBLE = (245, 250, 246)   # 말풍선 배경
DAD_C  = (86, 170, 255)    # 아빠(파랑)
GIRL_C = (255, 121, 166)   # 딸(코럴 핑크)

# ── 폰트 ─────────────────────────────────────────────
def _font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

BOLD  = ["/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"]
XBOLD = ["/usr/share/fonts/truetype/nanum/NanumGothicExtraBold.ttf",
         "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"]
REG   = ["/usr/share/fonts/truetype/nanum/NanumGothic.ttf"]

def fb(sz):  return _font(BOLD, sz)
def fx(sz):  return _font(XBOLD, sz)
def fr(sz):  return _font(REG, sz)

# ── 화자 설정 ────────────────────────────────────────
# side: left/right/center · edge_*: edge-tts 파라미터 · espeak_*: 오프라인 파라미터
# shift: 오프라인 피치 시프트(반음). 아빠는 낮게(-), 딸은 높게(+).
SPEAKERS = {
    "narrator": dict(label="내레이션", color=AMBER, side="center",
                     edge_voice="ko-KR-SunHiNeural", edge_rate="-4%",  edge_pitch="+0Hz",
                     espeak_speed=150, espeak_pitch=48, shift=0.0),
    "dad":      dict(label="아빠",     color=DAD_C,  side="left",
                     edge_voice="ko-KR-InJoonNeural", edge_rate="-3%",  edge_pitch="-2Hz",
                     espeak_speed=140, espeak_pitch=32, shift=-2.5),
    "daughter": dict(label="딸",       color=GIRL_C, side="right",
                     edge_voice="ko-KR-YuJinNeural",  edge_rate="+9%",  edge_pitch="+18Hz",
                     espeak_speed=174, espeak_pitch=82, shift=3.5),
}

def run(cmd, **kw):
    return subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL, **kw)

def probe_dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True).stdout.strip()
    return float(out)

# ── 음성 합성 ────────────────────────────────────────
def edge_available():
    """edge-tts 로 짧게 합성해 접속 가능 여부를 판별."""
    try:
        import edge_tts  # noqa
    except Exception:
        return False
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    async def _probe():
        import edge_tts
        c = edge_tts.Communicate("테스트", "ko-KR-SunHiNeural", proxy=proxy)
        got = 0
        async for ch in c.stream():
            if ch["type"] == "audio":
                got += len(ch["data"])
                if got > 0:
                    return True
        return got > 0
    try:
        return asyncio.run(asyncio.wait_for(_probe(), timeout=25))
    except Exception as e:
        print(f"  · edge-tts 사용 불가 → 오프라인(espeak-ng)로 전환: {type(e).__name__}",
              file=sys.stderr)
        return False

def synth_edge(text, spk, raw_path):
    import edge_tts
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    async def _go():
        c = edge_tts.Communicate(text, spk["edge_voice"], rate=spk["edge_rate"],
                                 pitch=spk["edge_pitch"], proxy=proxy)
        with open(raw_path, "wb") as f:
            async for ch in c.stream():
                if ch["type"] == "audio":
                    f.write(ch["data"])
    asyncio.run(_go())

def synth_espeak(text, spk, raw_path):
    run(["espeak-ng", "-v", "ko", "-s", str(spk["espeak_speed"]),
         "-p", str(spk["espeak_pitch"]), "-g", "6", text, "-w", str(raw_path)])

def make_segment(text, spk, engine, raw_path, seg_path, tail=False):
    """대사 → 원음 합성 → (피치 정리 +) 뒤 여백 패딩 → 표준 wav(seg)."""
    if engine == "edge":
        synth_edge(text, spk, raw_path)
        shift = 0.0                       # edge 보이스는 자체로 구분됨
    else:
        synth_espeak(text, spk, raw_path)
        shift = spk["shift"]
    pad = GAP + (TAIL if tail else 0.0)
    chain = [f"aresample={SR}"]
    if abs(shift) > 0.01:
        r = 2 ** (shift / 12.0)
        chain += [f"asetrate={int(SR*r)}", f"aresample={SR}", f"atempo={1.0/r:.5f}"]
    chain += ["dynaudnorm=f=200:g=5", f"apad=pad_dur={pad}"]
    run(["ffmpeg", "-y", "-i", str(raw_path), "-af", ",".join(chain),
         "-ar", str(SR), "-ac", "2", str(seg_path)])

def make_silence(dur, seg_path):
    run(["ffmpeg", "-y", "-f", "lavfi", "-t", f"{dur}",
         "-i", f"anullsrc=r={SR}:cl=stereo", "-ar", str(SR), "-ac", "2", str(seg_path)])

# ── 배경/브랜드 ──────────────────────────────────────
def gradient_bg():
    col = Image.new("RGB", (1, H)); cp = col.load()
    for y in range(H):
        t = y / H
        cp[0, y] = (int(31*(1-t) + 9*t), int(96*(1-t) + 40*t), int(64*(1-t) + 30*t))
    bg = col.resize((W, H)).convert("RGBA")
    # 은은한 피치 모티프(가운데 원 + 하프라인)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    line = (255, 255, 255, 20)
    d.line([(60, H//2), (W-60, H//2)], fill=line, width=3)
    d.ellipse([W//2-150, H//2-150, W//2+150, H//2+150], outline=line, width=3)
    d.ellipse([W//2-10, H//2-10, W//2+10, H//2+10], fill=(255, 255, 255, 22))
    d.rectangle([W//2-190, 60, W//2+190, 300], outline=line, width=3)       # 상단 박스
    d.rectangle([W//2-190, H-300, W//2+190, H-60], outline=line, width=3)   # 하단 박스
    bg.alpha_composite(ov)
    return bg

def scrim():
    alpha = Image.new("L", (1, H)); ap = alpha.load()
    for y in range(H):
        a = 40
        if y > H*0.62:
            a = int(40 + 150*(y - H*0.62)/(H*0.38))
        if y < 220:
            a = max(a, 90)
        ap[0, y] = min(a, 205)
    img = Image.new("RGBA", (W, H), (7, 18, 12, 255))
    img.putalpha(alpha.resize((W, H)))
    return img

def brand(d):
    d.rectangle([70, 96, 132, 106], fill=GREEN)
    d.text((70, 120), "GROUND YOUTH", font=fx(40), fill=WHITE)
    d.text((70, H-92), "@groundyouth · 매일 유소년 축구 이야기", font=fb(34), fill=(226, 236, 230))

# ── 텍스트 배치 헬퍼 ─────────────────────────────────
def wrap(d, text, font, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if d.textlength(t, font=font) <= maxw or not cur:
                cur = t
            else:
                lines.append(cur); cur = word
        lines.append(cur)
    return lines

def rounded(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

# ── 아바타(간단한 캐릭터) ────────────────────────────
def draw_avatar(img, cx, cy, kind):
    d = ImageDraw.Draw(img)
    R = AV_R
    ring = GREEN if kind == "narrator" else (DAD_C if kind == "dad" else GIRL_C)
    face = (255, 227, 196)
    # 딸: 양갈래 머리
    if kind == "daughter":
        for dx in (-R+14, R-14):
            d.ellipse([cx+dx-34, cy-70, cx+dx+34, cy-2], fill=(120, 72, 48))
    # 바깥 링
    d.ellipse([cx-R-10, cy-R-10, cx+R+10, cy+R+10], fill=ring)
    # 얼굴
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=face)
    # 머리(앞머리) — 내레이터는 중립 캡
    hair = (60, 44, 34) if kind != "narrator" else (44, 60, 50)
    d.pieslice([cx-R, cy-R, cx+R, cy+R], 180, 360, fill=hair)
    d.rectangle([cx-R, cy-R, cx+R, cy-R+34], fill=hair)
    # 눈
    ey = cy + (8 if kind == "daughter" else 4)
    ex = 52
    for sx in (-ex, ex):
        d.ellipse([cx+sx-13, ey-16, cx+sx+13, ey+16], fill=(40, 32, 28))
        d.ellipse([cx+sx-4, ey-12, cx+sx+5, ey-3], fill=WHITE)
    # 볼(딸)
    if kind == "daughter":
        for sx in (-86, 86):
            d.ellipse([cx+sx-18, ey+22, cx+sx+18, ey+50], fill=(255, 170, 190))
    # 미소
    d.arc([cx-46, ey+6, cx+46, ey+78], 20, 160, fill=(150, 60, 60), width=9)
    return ring

# ── 말풍선 대사 프레임 ───────────────────────────────
def render_dialog(text, spk, kind, out_png):
    img = gradient_bg()
    img.alpha_composite(scrim())
    ImageDraw.Draw(img)  # ensure mode
    side = spk["side"]

    if side == "center":
        # 내레이션: 아바타 없이 가운데 캡션(따옴표 없는 서술체)
        d = ImageDraw.Draw(img)
        # 상단 태그
        tag = spk["label"]
        tw = d.textlength(tag, font=fb(40))
        rounded(d, [W/2-tw/2-34, 560, W/2+tw/2+34, 636], 38,
                (0, 0, 0, 120), outline=AMBER, width=3)
        d.text((W/2-tw/2, 574), tag, font=fb(40), fill=AMBER)
        font = fx(64)
        lines = wrap(d, text, font, 860)
        asc, desc = font.getmetrics(); lh = int((asc+desc)*1.34)
        y = H/2 - lh*len(lines)/2 + 40
        for ln in lines:
            w = d.textlength(ln, font=font); x = (W-w)/2
            d.text((x+3, y+3), ln, font=font, fill=(0, 0, 0, 160))
            d.text((x, y), ln, font=font, fill=WHITE)
            y += lh
    else:
        # 아바타 위치
        acx = 250 if side == "left" else W-250
        acy = 690
        draw_avatar(img, acx, acy, kind)
        d = ImageDraw.Draw(img)
        # 말풍선 크기 계산
        font = fx(62)
        maxw = 780
        lines = wrap(d, text, font, maxw)
        asc, desc = font.getmetrics(); lh = int((asc+desc)*1.26)
        tw = max(d.textlength(ln, font=font) for ln in lines)
        pad = 52
        bw = min(W-140, tw + pad*2)
        bh = lh*len(lines) + pad*2
        bx = (W - bw)/2
        by = 1030
        # 꼬리(아바타 쪽) — 이름표 아래에서 시작해 말풍선으로
        name = spk["label"]
        nf = fx(46); nw = d.textlength(name, font=nf)
        nbx = acx - nw/2
        ntop = acy + R_OFFSET
        base_y = by + 56
        apex_y = ntop + 78
        if side == "left":
            d.polygon([(acx, apex_y), (bx+64, base_y), (bx+172, base_y)], fill=BUBBLE)
        else:
            d.polygon([(acx, apex_y), (bx+bw-64, base_y), (bx+bw-172, base_y)], fill=BUBBLE)
        # 말풍선
        rounded(d, [bx, by, bx+bw, by+bh], 46, BUBBLE)
        d.rounded_rectangle([bx, by, bx+bw, by+bh], radius=46,
                            outline=spk["color"], width=5)
        ty = by + pad
        for ln in lines:
            d.text((bx+pad, ty), ln, font=font, fill=INK)
            ty += lh
        # 이름표(맨 위에 그려 꼬리를 가림)
        rounded(d, [nbx-30, ntop, nbx+nw+30, ntop+74], 37, spk["color"])
        d.text((nbx, ntop+12), name, font=nf, fill=(12, 20, 16))

    d = ImageDraw.Draw(img)
    brand(d)
    img.convert("RGB").save(out_png)

# ── 타이틀/엔딩 카드 ─────────────────────────────────
def render_title(title, subtitle, out_png):
    img = gradient_bg(); img.alpha_composite(scrim())
    d = ImageDraw.Draw(img)
    # 상단 라벨
    lab = "GROUND YOUTH 웹툰"
    lf = fb(44); lw = d.textlength(lab, font=lf)
    d.text(((W-lw)/2, 690), lab, font=lf, fill=GREEN)
    # 타이틀
    tf = fx(150); tw = d.textlength(title, font=tf)
    d.text(((W-tw)/2+4, 838+4), title, font=tf, fill=(0, 0, 0, 170))
    d.text(((W-tw)/2, 838), title, font=tf, fill=WHITE)
    # 밑줄 포인트
    d.rectangle([W/2-120, 1030, W/2+120, 1044], fill=AMBER)
    # 부제
    sf = fx(64); sw = d.textlength(subtitle, font=sf)
    d.text(((W-sw)/2, 1090), subtitle, font=sf, fill=AMBER)
    brand(d)
    img.convert("RGB").save(out_png)

def render_outro(out_png):
    img = gradient_bg(); img.alpha_composite(scrim())
    d = ImageDraw.Draw(img)
    lines = ["함께 공을 차는 시간이", "제일 좋은 훈련이에요"]
    font = fx(78); lh = int(sum(font.getmetrics())*1.3)
    y = H/2 - lh
    for ln in lines:
        w = d.textlength(ln, font=font)
        d.text(((W-w)/2+3, y+3), ln, font=font, fill=(0, 0, 0, 160))
        d.text(((W-w)/2, y), ln, font=font, fill=WHITE); y += lh
    cta = "@groundyouth · 팔로우하고 매일 받아보기"
    cf = fb(46); cw = d.textlength(cta, font=cf)
    d.text(((W-cw)/2, y+40), cta, font=cf, fill=GREEN)
    brand(d)
    img.convert("RGB").save(out_png)

# ── 씬 → AV 클립 ─────────────────────────────────────
def av_clip(png, seg_wav, out_mp4):
    run(["ffmpeg", "-y", "-loop", "1", "-i", str(png), "-i", str(seg_wav),
         "-vf", f"scale={W}:{H},fps={FPS},format=yuv420p",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", str(SR), "-ac", "2",
         "-shortest", "-movflags", "+faststart", str(out_mp4)])

# ── 메인 ─────────────────────────────────────────────
def build(slug):
    story_path = TOON / "stories" / f"{slug}.json"
    if not story_path.exists():
        sys.exit(f"스토리 파일 없음: {story_path}")
    story = json.loads(story_path.read_text(encoding="utf-8"))
    title = story.get("title", slug)
    subtitle = story.get("subtitle", "")
    dname = story.get("daughter_name", "딸")
    lines = story["lines"]

    outdir = TOON / "out" / slug
    tmp = outdir / "tmp"
    outdir.mkdir(parents=True, exist_ok=True)
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)

    engine = "edge" if edge_available() else "espeak"
    if engine == "espeak" and not shutil.which("espeak-ng"):
        sys.exit("edge-tts 도 espeak-ng 도 사용할 수 없습니다. 패키지를 설치하세요.")
    print(f"▶ 음성 엔진: {engine}")

    clips = []

    # 인트로 타이틀 카드(무음 1.6s)
    tpng = tmp / "title.png"; render_title(title, subtitle, tpng)
    tsil = tmp / "title.wav"; make_silence(1.6, tsil)
    tclip = tmp / "clip_title.mp4"; av_clip(tpng, tsil, tclip); clips.append(tclip)

    # 대사 씬
    for i, ln in enumerate(lines):
        spk_key = ln["speaker"]
        spk = dict(SPEAKERS[spk_key])
        if spk_key == "daughter":
            spk["label"] = dname
        text = ln["text"]
        raw = tmp / f"raw_{i}.wav"
        seg = tmp / f"seg_{i}.wav"
        last = (i == len(lines)-1)
        make_segment(text, spk, engine, raw, seg, tail=last)
        dur = probe_dur(seg)
        png = tmp / f"scene_{i}.png"
        render_dialog(text, spk, spk_key, png)
        clip = tmp / f"clip_{i}.mp4"
        av_clip(png, seg, clip)
        clips.append(clip)
        print(f"  [{i+1}/{len(lines)}] {spk['label']:<4} {dur:5.2f}s  {text[:24]}")

    # 엔딩 카드(무음 2.2s)
    opng = tmp / "outro.png"; render_outro(opng)
    osil = tmp / "outro.wav"; make_silence(2.2, osil)
    oclip = tmp / "clip_outro.mp4"; av_clip(opng, osil, oclip); clips.append(oclip)

    # 이어붙이기
    listf = tmp / "concat.txt"
    listf.write_text("".join(f"file '{c}'\n" for c in clips))
    dst = outdir / "short.mp4"
    try:
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf),
             "-c", "copy", "-movflags", "+faststart", str(dst)])
    except subprocess.CalledProcessError:
        # 코덱 파라미터가 어긋나면 재인코딩으로 안전하게 이어붙임
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf),
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(dst)])

    total = probe_dur(dst)
    print(f"✅ 완성: {dst}  ({total:.1f}s, 엔진={engine})")
    return dst


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "ilseokijo"
    build(slug)
