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
    total = sum(durs)
    n = len(ep["panels"])
    prog_col = bt.hx(ep["theme"]["accent"])

    # 1) 9:16 프레임 생성 + 진행바 굽기 → 클립 렌더
    clips = []
    for i in range(n):
        fr = frame9(outdir / f"panel{i+1}.png", ep)
        # 진행바 (하단)
        d = ImageDraw.Draw(fr)
        bw = SW - 120
        x0, y0 = 60, SH - 40
        d.rounded_rectangle([x0, y0, x0 + bw, y0 + 12], radius=6, fill=(0, 0, 0, 40))
        fillw = int(bw * (i + 1) / n)
        d.rounded_rectangle([x0, y0, x0 + fillw, y0 + 12], radius=6, fill=prog_col)
        fp = tmp / f"f{i}.png"
        fr.save(fp)
        # zoompan 클립 (짝수 줌인 / 홀수 살짝 다른 속도)
        dur = durs[i]
        frames = int(dur * FPS)
        zexpr = f"min(zoom+0.0006,1.10)" if i % 2 == 0 else f"min(zoom+0.0009,1.14)"
        clip = tmp / f"c{i}.mp4"
        run(["ffmpeg", "-y", "-loop", "1", "-i", str(fp), "-t", f"{dur}",
             "-filter_complex",
             f"zoompan=z='{zexpr}':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={SW}x{SH}:fps={FPS},format=yuv420p",
             "-r", str(FPS), "-an", str(clip)])
        clips.append(clip)

    # 2) concat (하드컷)
    listf = tmp / "list.txt"
    listf.write_text("".join(f"file '{c}'\n" for c in clips))
    concat = tmp / "concat.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf), "-c", "copy", str(concat)])

    # 3) 무성 오디오 + 전체 페이드
    out_mp4 = outdir / "short.mp4"
    run(["ffmpeg", "-y", "-i", str(concat),
         "-f", "lavfi", "-t", f"{total}", "-i", "anullsrc=r=44100:cl=stereo",
         "-vf", f"fade=t=in:st=0:d=0.4,fade=t=out:st={total-0.5:.2f}:d=0.5",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", "-shortest", str(out_mp4)])

    shutil.rmtree(tmp)
    print(f"OK {out_mp4.relative_to(ROOT)}  ({total:.1f}s, {n} panels)")


if __name__ == "__main__":
    main()
