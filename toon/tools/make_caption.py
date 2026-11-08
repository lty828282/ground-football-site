#!/usr/bin/env python3
"""에피소드 JSON에서 인스타그램 캡션을 자동 생성.

표제어·한자·훈음·뜻풀이·영어표현·비슷한 속담·해시태그를 조합한다.

    python3 toon/tools/make_caption.py yubimuhwan            # 출력
    python3 toon/tools/make_caption.py yubimuhwan --save     # content/captions/<slug>.txt 저장
"""
import sys, json, pathlib, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"


def _clean(s):
    return " ".join(s.replace("\n", " ").split())


def build(slug):
    ep = json.loads((CONTENT / f"{slug}.json").read_text())
    term = ep["term"]
    hanja = ep.get("hanja", "")
    gloss = ep.get("hanja_gloss", [])
    sub = ep.get("sub") or ep["panels"][0].get("sub", "")
    en = ep.get("en", "")

    # 뜻풀이: appa_board(칠판) 패널의 말풍선에서 추출
    meaning = ""
    for p in ep["panels"]:
        if p.get("kind") == "talk" and any(c.get("name") == "appa_board" for c in p.get("chars", [])):
            bs = p.get("bubbles", [])
            if bs:
                meaning = _clean(bs[0]["text"])
                break

    # 비슷한 속담: outro
    also = []
    for p in ep["panels"]:
        if p.get("kind") == "outro":
            also = p.get("also", [])
            break

    # 훈음 줄
    gloss_line = ""
    if hanja and gloss:
        pairs = [f"{h} {g}" for h, g in zip(list(hanja), gloss)]
        gloss_line = "  ·  ".join(pairs)

    lines = []
    lines.append(f"📚 오늘의 고사성어 · {term} ({hanja})")
    if sub:
        lines.append(f"“{sub}”")
    lines.append("")
    if gloss_line:
        lines.append(f"✍️ {gloss_line}")
    if meaning:
        lines.append(f"뜻 ▶ {meaning}")
    lines.append("")
    if en:
        lines.append(f"🇺🇸 영어로는: {en}")
    if also:
        lines.append(f"💬 비슷한 말: {' / '.join(also)}")
    lines.append("")
    lines.append("아빠랑 딸이 매일 하나씩 쉽게 풀어주는 고사성어 ✨")
    lines.append("팔로우하고 어휘력 쑥쑥 👉 @askpapa")
    lines.append("")

    tags = ["#고사성어", f"#{term}", "#사자성어", "#어휘력", "#초등어휘", "#한자",
            "#교육", "#공부스타그램", "#아이교육", "#문해력", "#아빠뭐야", "#askpapa"]
    lines.append(" ".join(tags))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--save", action="store_true")
    a = ap.parse_args()
    cap = build(a.slug)
    if a.save:
        d = CONTENT / "captions"
        d.mkdir(exist_ok=True)
        dst = d / f"{a.slug}.txt"
        dst.write_text(cap + "\n")
        print(f"saved {dst}")
    else:
        print(cap)


if __name__ == "__main__":
    main()
