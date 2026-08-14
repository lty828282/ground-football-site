#!/usr/bin/env python3
"""캐러셀 패널 → 유튜브 쇼츠(9:16, 1080x1920) mp4 조립 (+음성 나레이션).

- 각 패널을 9:16 프레임으로 재구성(상단 표제 배너 + 패널 + 하단 핸들 + 진행바)
- 음성: toon/audio/<slug>/panelN.(mp3|wav|m4a) 있으면 그걸 사용,
  없으면 espeak-ng(오프라인) 로 생성. (고품질 뉴럴 TTS는 네트워크 필요)
- 화면을 음성 길이에 맞춰 하드컷 동기화, 오디오 믹스, 페이드 인/아웃.
- 음성 엔진이 전혀 없으면 무성 + 크로스페이드로 폴백.

    python3 toon/build_short.py ilseokijo
    → toon/out/ilseokijo/short.mp4
"""
import sys, os, json, subprocess, pathlib, shutil
from PIL import Image, ImageDraw
import build_toon as bt

# 프록시 재종단 TLS 신뢰(에이전트 프록시 환경) — edge-tts(aiohttp)가 인증서 검증 통과하도록
_CA = "/root/.ccr/ca-bundle.crt"
if os.path.exists(_CA):
    os.environ.setdefault("SSL_CERT_FILE", _CA)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", _CA)

ROOT = pathlib.Path(__file__).resolve().parent
SW, SH, FPS = 1080, 1920, 30
LEAD, TAIL = 0.25, 0.75  # 음성 앞뒤 여백(초)
bt.W, bt.H = SW, SH       # 헬퍼가 9:16 캔버스를 쓰도록

DEVNULL, PIPE = subprocess.DEVNULL, subprocess.PIPE


def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True, stdout=DEVNULL, stderr=PIPE)


def ffdur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nokey=1:noprint_wrappers=1", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0.0)


def have(cmd):
    return shutil.which(cmd) is not None


# ── 9:16 프레임 ──────────────────────────────────────
def caption9(base, text, ink):
    """하단 자막 바(반투명) — 음성 구간과 자동으로 맞물림(패널당 1자막)."""
    if not text:
        return
    d = ImageDraw.Draw(base)
    font = bt.f_bold(48)
    txt = bt.wrap(d, text, font, 900)
    bb = d.multiline_textbbox((0, 0), txt, font=font, spacing=10, align="center")
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    padx, pady = 40, 26
    bw, bh = tw + 2 * padx, th + 2 * pady
    cx, cy = SW // 2, 1690
    x0, y0 = cx - bw // 2, cy - bh // 2
    ov = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=26, fill=(28, 22, 18, 200))
    base.alpha_composite(ov)
    bt.mtext(base, (cx, y0 + pady - bb[1]), txt, font, (255, 255, 255), spacing=10, anchor="ma")


def frame9(panel_png, ep, panel=None):
    th = ep["theme"]
    ink, acc, acc2 = bt.hx(th["ink"]), bt.hx(th["accent"]), bt.hx(th["accent2"])
    base = Image.new("RGBA", (SW, SH), bt.hx(th["bg"]) + (255,))
    bt.bg_dots(base, ink)
    bt.sparkle(base, 120, 470, 22, acc2)
    bt.sparkle(base, 965, 500, 26, acc)
    # 상단: 채널 브랜딩(로고 + 채널명). 표제어는 커버 패널에 이미 있어 중복 제거.
    brand = ep.get("brand", {})
    bname = brand.get("name", "데일리 툰")
    bx, by = SW // 2, 118
    logo = brand.get("logo")
    lp = (ROOT / "assets" / logo) if logo else None
    if lp and lp.exists():
        lg = Image.open(lp).convert("RGBA")
        s = 132
        lg.thumbnail((s, s))
        d = ImageDraw.Draw(base)
        tw = d.textlength(bname, font=bt.f_title(66))
        total = lg.width + 20 + tw
        lx = int(bx - total / 2)
        base.alpha_composite(lg, (lx, by - lg.height // 2))
        bt.mtext(base, (lx + lg.width + 20, by), bname, bt.f_title(66), ink, anchor="lm")
    else:
        bt.mtext(base, (bx, by), bname, bt.f_title(70), ink, anchor="mm")
    ImageDraw.Draw(base).rounded_rectangle([bx - 92, by + 54, bx + 92, by + 62], radius=4, fill=acc)
    p = Image.open(panel_png).convert("RGBA")
    pw = 1004
    ph = int(p.height * pw / p.width)
    p = p.resize((pw, ph), Image.LANCZOS)
    base.alpha_composite(p, ((SW - pw) // 2, 300))
    # 자동 자막: panel.caption 우선(빈 문자열이면 숨김), 없으면 vo 사용
    if panel is not None:
        caption9(base, panel.get("caption", panel.get("vo")), ink)
    bt.mtext(base, (SW // 2, SH - 96), ep.get("handle", "@toon.daily"), bt.f_bold(42), ink, anchor="ma")
    return base.convert("RGB")


def frame_with_bar(panel_png, ep, panel, i, n):
    fr = frame9(panel_png, ep, panel)
    d = ImageDraw.Draw(fr)
    bw = SW - 120
    x0, y0 = 60, SH - 40
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + 12], radius=6, fill=(0, 0, 0, 40))
    d.rounded_rectangle([x0, y0, x0 + int(bw * (i + 1) / n), y0 + 12], radius=6, fill=bt.hx(ep["theme"]["accent"]))
    return fr


# ── 나레이션 ────────────────────────────────────────
def derive_vo(p, ep):
    k = p["kind"]
    if k == "cover":
        return f"{ep.get('tag','')}. {ep['term']}."
    if k == "outro":
        parts = [f"영어로는, {ep.get('en','')}."]
        if p.get("also"):
            parts.append("비슷한 우리 속담은, " + ", ".join(p["also"]) + ".")
        return " ".join(parts)
    return " ".join(b["text"].replace("\n", " ") for b in p.get("bubbles", []))


def edge_synth(text, voice, pitch, out):
    """edge-tts(마이크로소프트 뉴럴)로 mp3 생성. 실패 시 예외."""
    import asyncio, edge_tts
    async def go():
        await edge_tts.Communicate(text, voice, pitch=pitch).save(str(out))
    asyncio.run(go())

def edge_ok(tmp):
    try:
        edge_synth("테스트", "ko-KR-SunHiNeural", "+0Hz", tmp / "_et.mp3")
        return True
    except Exception as e:
        print("edge-tts 사용 불가:", repr(e)[:120])
        return False

def pick_voice(panel):
    """패널 화자에 맞는 목소리. 내레이터=SunHi, 아빠=InJoon, 딸=SunHi(피치↑)."""
    if panel["kind"] in ("cover", "outro"):
        return ("ko-KR-SunHiNeural", "+0Hz")
    frm = (panel.get("bubbles") or [{}])[0].get("from")
    spk = None
    for c in panel.get("chars", []):
        side = c.get("from", "left" if c["x"] < 0.5 else "right")
        if side == frm:
            spk = c["name"]; break
    if not spk and panel.get("chars"):
        spk = panel["chars"][0]["name"]
    if spk and spk.startswith("appa"):
        return ("ko-KR-InJoonNeural", "+0Hz")
    return ("ko-KR-SunHiNeural", "+12Hz")

def make_voice(ep, slug, tmp):
    """패널별 음성 wav(44100/stereo). 우선순위: 사용자 오디오 > edge-tts > espeak-ng."""
    adir = ROOT / "audio" / slug
    engine = None
    if edge_ok(tmp):
        engine = "edge"
    elif have("espeak-ng"):
        engine = "espeak"
    print(f"음성 엔진: {engine or '없음(무성)'}")
    wavs = []
    for i, p in enumerate(ep["panels"], 1):
        user = None
        for ext in ("mp3", "wav", "m4a"):
            c = adir / f"panel{i}.{ext}"
            if c.exists():
                user = c; break
        w = tmp / f"vo{i-1}.wav"
        text = p.get("vo") or derive_vo(p, ep)
        if user:
            run(["ffmpeg", "-y", "-i", user, "-ar", "44100", "-ac", "2", w])
        elif engine == "edge":
            mp3 = tmp / f"raw{i-1}.mp3"
            voice, pitch = pick_voice(p)
            edge_synth(text, voice, pitch, mp3)
            run(["ffmpeg", "-y", "-i", mp3, "-ar", "44100", "-ac", "2", w])
        elif engine == "espeak":
            raw = tmp / f"raw{i-1}.wav"
            run(["espeak-ng", "-v", "ko", "-s", "155", "-p", "40", text, "-w", raw])
            run(["ffmpeg", "-y", "-i", raw, "-ar", "44100", "-ac", "2", w])
        else:
            return None
        wavs.append(w)
    return wavs


# ── 조립 ─────────────────────────────────────────────
def build_voiced(ep, frames, wavs, tmp, out_mp4):
    n = len(frames)
    durs, asegs = [], []
    for i, w in enumerate(wavs):
        dur = round(LEAD + ffdur(w) + TAIL, 3)
        durs.append(dur)
        seg = tmp / f"a{i}.wav"
        run(["ffmpeg", "-y", "-i", w, "-af",
             f"adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad", "-t", f"{dur}",
             "-ar", "44100", "-ac", "2", seg])
        asegs.append(seg)
    total = round(sum(durs), 3)

    # 비디오: 이미지 concat(하드컷, 줌 없음 → 떨림 없음)
    vlist = tmp / "vlist.txt"
    lines = []
    for i in range(n):
        lines += [f"file '{frames[i]}'", f"duration {durs[i]}"]
    lines.append(f"file '{frames[-1]}'")
    vlist.write_text("\n".join(lines))
    video = tmp / "v.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", vlist,
         "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-crf", "20", "-preset", "medium", video])

    # 오디오 concat
    alist = tmp / "alist.txt"
    alist.write_text("\n".join(f"file '{s}'" for s in asegs))
    aud = tmp / "a.wav"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", alist, "-c", "copy", aud])

    # 믹스 + 페이드
    run(["ffmpeg", "-y", "-i", video, "-i", aud,
         "-vf", f"fade=t=in:st=0:d=0.4,fade=t=out:st={total-0.5:.3f}:d=0.5",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", "-b:a", "160k", "-shortest", out_mp4])
    return total


def build_silent(ep, frames, tmp, out_mp4):
    """폴백: 무성 + 크로스페이드."""
    T = 0.5
    durs = []
    for p in ep["panels"]:
        k = p["kind"]
        durs.append(3.0 if k == "cover" else 4.6 if k == "outro"
                    else max(3.0, min(5.2, 2.2 + 0.10 * len(" ".join(b["text"] for b in p.get("bubbles", []))))))
    n = len(frames)
    parts, inputs = [], []
    for i, fp in enumerate(frames):
        inputs += ["-loop", "1", "-t", f"{durs[i]}", "-i", str(fp)]
        parts.append(f"[{i}:v]fps={FPS},format=yuv420p,setsar=1[c{i}]")
    prev, acc = "c0", durs[0]
    for i in range(1, n):
        parts.append(f"[{prev}][c{i}]xfade=transition=fade:duration={T}:offset={acc-T:.3f}[x{i}]")
        prev, acc = f"x{i}", acc + durs[i] - T
    total = acc
    parts.append(f"[{prev}]fade=t=in:st=0:d=0.4,fade=t=out:st={total-0.5:.3f}:d=0.5[vout]")
    cmd = ["ffmpeg", "-y"] + inputs + \
        ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=44100:cl=stereo",
         "-filter_complex", ";".join(parts), "-map", "[vout]", "-map", f"{n}:a",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", "-shortest", out_mp4]
    run([str(c) for c in cmd])
    return total


def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "ilseokijo"
    ep = json.loads((ROOT / "content" / f"{slug}.json").read_text(encoding="utf-8"))
    outdir = ROOT / "out" / slug
    tmp = outdir / "short_tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    n = len(ep["panels"])

    frames = []
    for i in range(n):
        fr = frame_with_bar(outdir / f"panel{i+1}.png", ep, ep["panels"][i], i, n)
        fp = tmp / f"f{i}.png"
        fr.save(fp)
        frames.append(fp)

    out_mp4 = outdir / "short.mp4"
    novoice = os.environ.get("TOON_NOVOICE") == "1" or "--novoice" in sys.argv
    wavs = None if novoice else make_voice(ep, slug, tmp)
    if wavs:
        total = build_voiced(ep, frames, wavs, tmp, out_mp4)
        mode = "음성(espeak-ng/사용자)"
    else:
        total = build_silent(ep, frames, tmp, out_mp4)
        mode = "무성"

    shutil.rmtree(tmp)
    print(f"OK {out_mp4.relative_to(ROOT)}  ({total:.1f}s, {n} panels, {mode})")


if __name__ == "__main__":
    main()
