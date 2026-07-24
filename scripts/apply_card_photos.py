#!/usr/bin/env python3
"""고른 후보 사진을 카드 배경 이미지로 적용한다.

사용:  python3 scripts/apply_card_photos.py home-training "2:3,3:0,4:5,5:1,6:2"
       (카드번호:후보번호 쌍, 콤마 구분)

exports/photo-candidates/<slug>/card<K>/<idx>.jpg → assets/img/cardnews/<slug>-<K>.jpg
적용 후 export-cards 워크플로로 카드 이미지를 다시 뽑으면 된다.
"""
import sys, shutil, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) < 3:
        print("usage: apply_card_photos.py <slug> \"K:idx,K:idx,...\""); sys.exit(1)
    slug = sys.argv[1].strip()
    picks = sys.argv[2].strip()
    cand = ROOT / "exports" / "photo-candidates" / slug
    dest_dir = ROOT / "assets" / "img" / "cardnews"

    applied = 0
    for pair in picks.split(","):
        pair = pair.strip()
        if not pair:
            continue
        k, idx = pair.split(":")
        src = cand / f"card{int(k)}" / f"{int(idx)}.jpg"
        if not src.exists():
            print(f"  ✗ 없음: {src}", file=sys.stderr); continue
        dst = dest_dir / f"{slug}-{int(k)}.jpg"
        shutil.copyfile(src, dst)
        print(f"  ✓ card{k} ← 후보{idx}  → {dst.relative_to(ROOT)}")
        applied += 1
    print(f"RESULT: {applied}개 적용 완료 (이제 export-cards 재실행)")


if __name__ == "__main__":
    main()
