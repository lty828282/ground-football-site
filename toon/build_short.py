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
import sys, json, subprocess, pathlib, shutil
from PIL import Image, ImageDraw
import build_toon as bt

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
def frame9(panel_png, ep):
    th = ep["theme"]
    ink, acc, acc2 = bt.hx(th["ink"]), bt.hx(th["accent"]), bt.hx(th["accent2"])
    base = Image.new("RGBA", (SW, SH), bt.hx(th["bg"]) + (255,))
    bt.bg_dots(base, ink)
    bt.sparkle(base, 120, 470, 22, acc2)
    bt.sparkle(base, 965, 500, 26, acc)
    bt.pill(base, ep.get("tag", "오늘의 표현"), SW // 2, 130, acc, bt.hx("#1E3A24"), bt.f_bold(44))
    bt.mtext(base, (SW // 2, 190), ep["term"], bt.f_title(108), ink, anchor="ma")
    if ep.get("hanja"):
        bt.mtext(base, (SW // 2, 320), ep["hanja"], bt.f_hanja(50), ink, anchor="ma")
    p = Image.open(panel_png).convert("RGBA")
    pw = 1004
    ph = int(p.height * pw / p.width)
    p = p.resize((pw, ph), Image.LANCZOS)
    base.alpha_composite(p, ((SW - pw) // 2, 400))
    bt.mtext(base, (SW // 2, SH - 96), ep.get("handle", "@toon.daily"), bt.f_bold(42), ink, anchor="ma")
    return base.convert("RGB")


def frame_with_bar(panel_png, ep, i, n):
    fr = frame9(panel_png, ep)
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


def make_voice(ep, slug, tmp):
    """패널별 음성 wav(44100/stereo) 목록. 사용자 오디오 우선, 없으면 espeak-ng."""
    adir = ROOT / "audio" / slug
    espeak = have("espeak-ng")
    wavs = []
    for i, p in enumerate(ep["panels"], 1):
        user = None
        for ext in ("mp3", "wav", "m4a"):
            c = adir / f"panel{i}.{ext}"
            if c.exists():
                user = c
                break
        w = tmp / f"vo{i-1}.wav"
        if user:
            run(["ffmpeg", "-y", "-i", user, "-ar", "44100", "-ac", "2", w])
        elif espeak:
            raw = tmp / f"raw{i-1}.wav"
            run(["espeak-ng", "-v", "ko", "-s", "155", "-p", "40", p.get("vo") or derive_vo(p, ep), "-w", raw])
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
        fr = frame_with_bar(outdir / f"panel{i+1}.png", ep, i, n)
        fp = tmp / f"f{i}.png"
        fr.save(fp)
        frames.append(fp)

    out_mp4 = outdir / "short.mp4"
    wavs = make_voice(ep, slug, tmp)
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
