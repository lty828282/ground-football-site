#!/usr/bin/env python3
"""캐러셀 패널 → 유튜브 쇼츠(9:16, 1080x1920) mp4 조립.

- 각 패널을 9:16 프레임으로 재구성(상단 표제 배너 + 패널 + 하단 핸들)
- ffmpeg zoompan(켄번즈 줌) + 진행바, 하드컷 전환, 페이드 인/아웃
- 무성(현재 환경은 네트워크 TTS 차단). 보이스는 audio/<slug>.* 있으면 믹스.

    python3 toon/build_short.py ilseokijo
    → toon/out/ilseokijo/short.mp4
"""
import sys, json, subprocess, pathlib, shutil
from PIL import Image, ImageDraw
import build_toon as bt

ROOT = pathlib.Path(__file__).resolve().parent
SW, SH, FPS = 1080, 1920, 30
bt.W, bt.H = SW, SH  # 헬퍼(bg_dots/frame 등)가 9:16 캔버스를 쓰도록


def frame9(panel_png, ep):
    th = ep["theme"]
    ink, acc, acc2 = bt.hx(th["ink"]), bt.hx(th["accent"]), bt.hx(th["accent2"])
    base = Image.new("RGBA", (SW, SH), bt.hx(th["bg"]) + (255,))
    bt.bg_dots(base, ink)
    bt.sparkle(base, 120, 470, 22, acc2)
    bt.sparkle(base, 965, 500, 26, acc)
    # 상단 표제 배너(항상 노출 → 중간 유입도 주제 인지)
    bt.pill(base, ep.get("tag", "오늘의 표현"), SW // 2, 130, acc, bt.hx("#1E3A24"), bt.f_bold(44))
    bt.mtext(base, (SW // 2, 190), ep["term"], bt.f_title(108), ink, anchor="ma")
    if ep.get("hanja"):
        bt.mtext(base, (SW // 2, 320), ep["hanja"], bt.f_hanja(50), ink, anchor="ma")
    # 패널 본문
    p = Image.open(panel_png).convert("RGBA")
    pw = 1004
    ph = int(p.height * pw / p.width)
    p = p.resize((pw, ph), Image.LANCZOS)
    base.alpha_composite(p, ((SW - pw) // 2, 400))
    # 하단 핸들
    bt.mtext(base, (SW // 2, SH - 96), ep.get("handle", "@toon.daily"), bt.f_bold(42), ink, anchor="ma")
    return base.convert("RGB")


def durations(ep):
    out = []
    for p in ep["panels"]:
        k = p["kind"]
        if k == "cover":
            d = 3.0
        elif k == "outro":
            d = 4.6
        else:
            txt = " ".join(b["text"].replace("\n", " ") for b in p.get("bubbles", []))
            d = max(3.0, min(5.2, 2.2 + 0.10 * len(txt)))
        out.append(round(d, 2))
    return out


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "ilseokijo"
    ep = json.loads((ROOT / "content" / f"{slug}.json").read_text(encoding="utf-8"))
    outdir = ROOT / "out" / slug
    tmp = outdir / "short_tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)

    durs = durations(ep)
    n = len(ep["panels"])
    prog_col = bt.hx(ep["theme"]["accent"])
    T = 0.5  # 크로스페이드(전환) 길이

    # 1) 9:16 프레임 생성(+진행바)
    frames = []
    for i in range(n):
        fr = frame9(outdir / f"panel{i+1}.png", ep)
        d = ImageDraw.Draw(fr)
        bw = SW - 120
        x0, y0 = 60, SH - 40
        d.rounded_rectangle([x0, y0, x0 + bw, y0 + 12], radius=6, fill=(0, 0, 0, 40))
        d.rounded_rectangle([x0, y0, x0 + int(bw * (i + 1) / n), y0 + 12], radius=6, fill=prog_col)
        fp = tmp / f"f{i}.png"
        fr.save(fp)
        frames.append(fp)

    # 2) 정지 프레임 + 크로스페이드(xfade). 줌 없음 → 떨림 원천 제거.
    parts, inputs = [], []
    for i, fp in enumerate(frames):
        inputs += ["-loop", "1", "-t", f"{durs[i]}", "-i", str(fp)]
        parts.append(f"[{i}:v]fps={FPS},format=yuv420p,setsar=1[c{i}]")
    prev, acc = "c0", durs[0]
    for i in range(1, n):
        off = acc - T
        parts.append(f"[{prev}][c{i}]xfade=transition=fade:duration={T}:offset={off:.3f}[x{i}]")
        prev = f"x{i}"
        acc = acc + durs[i] - T
    total = acc
    parts.append(f"[{prev}]fade=t=in:st=0:d=0.4,fade=t=out:st={total-0.5:.3f}:d=0.5[vout]")

    # 3) 무성 오디오 트랙 + 인코딩
    out_mp4 = outdir / "short.mp4"
    cmd = ["ffmpeg", "-y"] + inputs + \
        ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=44100:cl=stereo",
         "-filter_complex", ";".join(parts),
         "-map", "[vout]", "-map", f"{n}:a",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", "-shortest", str(out_mp4)]
    run(cmd)

    shutil.rmtree(tmp)
    print(f"OK {out_mp4.relative_to(ROOT)}  ({total:.1f}s, {n} panels)")


if __name__ == "__main__":
    main()
