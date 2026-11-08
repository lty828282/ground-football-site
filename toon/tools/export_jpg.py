#!/usr/bin/env python3
"""out/<slug>/panel*.png → panel*.jpg (흰 배경 플랫, IG 호환).

Instagram 콘텐츠 게시 API는 JPEG를 안전하게 받으므로 캐러셀 업로드 전
PNG를 JPEG로 변환해 둔다(투명 영역은 흰색으로).

    python3 toon/tools/export_jpg.py yubimuhwan
"""
import sys, pathlib
from PIL import Image

OUT = pathlib.Path(__file__).resolve().parent.parent / "out"


def export(slug):
    d = OUT / slug
    pngs = sorted(d.glob("panel*.png"), key=lambda p: int("".join(c for c in p.stem if c.isdigit()) or 0))
    if not pngs:
        raise SystemExit(f"패널 없음: {d}")
    saved = []
    for p in pngs:
        im = Image.open(p).convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[3])
        dst = p.with_suffix(".jpg")
        bg.save(dst, "JPEG", quality=92, optimize=True)
        saved.append(dst.name)
        print(f"saved {dst}")
    print(f"OK: {len(saved)} jpg")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: export_jpg.py <slug> [<slug> ...]")
    for s in sys.argv[1:]:
        export(s)
