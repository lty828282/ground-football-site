#!/usr/bin/env python3
"""속담·고사성어·영어표현 인스타툰 자동 조립기.

content/<slug>.json 을 읽어 캐릭터 에셋을 합성하고 말풍선·자막을 얹어
인스타 캐러셀(1080x1350) 패널 PNG 를 out/<slug>/ 에 생성한다.

    python3 toon/build_toon.py ilseokijo

캐릭터는 assets/characters/ 의 배경 투명 PNG (characters.json 참조).
"""
import sys, json, pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent
CH = ROOT / "assets" / "characters"
W, H = 1080, 1350

# ── 폰트 ────────────────────────────────────────────
NANUM = "/usr/share/fonts/truetype/nanum"
def _f(names, size):
    for n in names:
        p = pathlib.Path(NANUM) / n
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()
def f_title(s): return _f(["NanumSquareRoundEB.ttf", "NanumSquareRoundB.ttf", "NanumGothicBold.ttf"], s)
def f_bold(s):  return _f(["NanumSquareRoundB.ttf", "NanumGothicBold.ttf"], s)
def f_reg(s):   return _f(["NanumSquareRoundR.ttf", "NanumGothic.ttf"], s)
def f_hanja(s):
    """한자(漢字)는 나눔에 글리프가 없어 CJK 폰트(WQY)를 사용."""
    p = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
    if pathlib.Path(p).exists():
        return ImageFont.truetype(p, s, index=0)
    return f_bold(s)

def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

# ── 텍스트 헬퍼 ──────────────────────────────────────
def wrap(draw, text, font, maxw):
    """명시적 \n 은 유지하고, 너무 긴 줄만 어절 단위로 추가 줄바꿈."""
    out = []
    for para in text.split("\n"):
        words, cur = para.split(" "), ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=font) <= maxw or not cur:
                cur = t
            else:
                out.append(cur); cur = w
        out.append(cur)
    return "\n".join(out)

def mtext(base, xy, text, font, fill, spacing=14, align="center", anchor=None):
    ImageDraw.Draw(base).multiline_text(xy, text, font=font, fill=fill,
                                        spacing=spacing, align=align, anchor=anchor)

# ── 캐릭터 배치 ──────────────────────────────────────
def place(base, name, xfrac, scale, baseline=H - 40, flip=False):
    im = Image.open(CH / f"{name}.png").convert("RGBA")
    th = int(scale * H)
    tw = max(1, int(im.width * th / im.height))
    im = im.resize((tw, th), Image.LANCZOS)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    x = int(xfrac * W) - tw // 2
    base.alpha_composite(im, (x, baseline - th))
    return int(xfrac * W)

# ── 말풍선 ───────────────────────────────────────────
def bubble(base, text, side, cx, theme, top=110, maxw=640):
    d = ImageDraw.Draw(base)
    ink, fill = hx(theme["ink"]), hx(theme["bubble"])
    font = f_bold(46)
    text = wrap(d, text, font, maxw)
    bb = d.multiline_textbbox((0, 0), text, font=font, spacing=14, align="center")
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    padx, pady = 46, 38
    bw, bh = tw + 2 * padx, th + 2 * pady
    bx = 70 if side == "left" else W - 70 - bw
    by = top
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=42, fill=fill, outline=ink, width=5)
    # 꼬리(말하는 캐릭터 쪽으로)
    tailx = min(max(cx, bx + 60), bx + bw - 60)
    apex = (tailx, by + bh + 46)
    d.polygon([(tailx - 30, by + bh - 2), (tailx + 30, by + bh - 2), apex], fill=fill)
    d.line([(tailx - 30, by + bh - 2), apex], fill=ink, width=5)
    d.line([(tailx + 30, by + bh - 2), apex], fill=ink, width=5)
    mtext(base, (bx + bw // 2, by + pady - bb[1]), text, font, ink, anchor="ma")
    return by + bh

def pill(base, text, cx, cy, bg, ink, font, padx=30, pady=14):
    d = ImageDraw.Draw(base)
    tw = d.textlength(text, font=font)
    asc, desc = font.getmetrics(); th = asc + desc
    bw, bh = tw + 2 * padx, th + 2 * pady
    d.rounded_rectangle([cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2],
                        radius=bh // 2, fill=bg)
    mtext(base, (cx, cy), text, font, ink, anchor="mm")

def page_no(base, i, n, theme):
    d = ImageDraw.Draw(base)
    txt = f"{i}/{n}"
    font = f_bold(30)
    pill(base, txt, W - 90, H - 60, hx(theme["ink"]), (255, 255, 255), font, padx=22, pady=8)

# ── 패널 렌더 ────────────────────────────────────────
def render(panel, theme, idx, total):
    bg = hx(theme["bg"])
    base = Image.new("RGBA", (W, H), bg + (255,))
    ink, acc, acc2 = hx(theme["ink"]), hx(theme["accent"]), hx(theme["accent2"])
    kind = panel["kind"]

    if kind == "cover":
        pill(base, panel.get("tag", "오늘의 표현"), W // 2, 210, acc, hx("#1E3A24"), f_bold(40))
        mtext(base, (W // 2, 300), panel["title"], f_title(150), ink, anchor="ma")
        if panel.get("hanja"):
            mtext(base, (W // 2, 490), panel["hanja"], f_hanja(76), ink, anchor="ma")
        if panel.get("sub"):
            mtext(base, (W // 2, 600), panel["sub"], f_reg(48), ink, anchor="ma")
        for c in panel.get("chars", []):
            place(base, c["name"], c["x"], c["scale"], baseline=H - 30, flip=c.get("flip", False))

    elif kind == "outro":
        mtext(base, (W // 2, 150), panel.get("title", "영어로는?"), f_title(84), ink, anchor="ma")
        # 영어 카드
        d = ImageDraw.Draw(base)
        sub = panel.get("sub", "")
        font = f_title(74)
        sub_w = wrap(d, sub, font, 900)
        bb = d.multiline_textbbox((0, 0), sub_w, font=font, spacing=16, align="center")
        cw, ch = bb[2] - bb[0] + 90, bb[3] - bb[1] + 70
        cx0, cy0 = (W - cw) // 2, 280
        d.rounded_rectangle([cx0, cy0, cx0 + cw, cy0 + ch], radius=40, fill=acc, outline=ink, width=5)
        mtext(base, (W // 2, cy0 + 35 - bb[1]), sub_w, font, hx("#12300f"), spacing=16, anchor="ma")
        for c in panel.get("chars", []):
            place(base, c["name"], c["x"], c["scale"], baseline=H - 150, flip=c.get("flip", False))
        if panel.get("cta"):
            mtext(base, (W // 2, H - 120), panel["cta"], f_bold(44), ink, anchor="ma")

    else:  # talk
        # 캐릭터 먼저(뒤), 말풍선 나중(앞)
        cxs = {}
        for c in panel.get("chars", []):
            cxs[c.get("from", "left" if c["x"] < 0.5 else "right")] = \
                place(base, c["name"], c["x"], c["scale"], flip=c.get("flip", False))
        top = 110
        for b in panel.get("bubbles", []):
            side = b["from"]
            cx = cxs.get(side, int((0.25 if side == "left" else 0.75) * W))
            top = bubble(base, b["text"], side, cx, theme, top=top) + 40

    page_no(base, idx, total, theme)
    return base.convert("RGB")

def _dark(c, ink):
    return sum(c) < 380  # 밝은 색이면 ink 대신 그대로

def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "ilseokijo"
    ep = json.loads((ROOT / "content" / f"{slug}.json").read_text(encoding="utf-8"))
    theme = ep["theme"]
    panels = ep["panels"]
    outdir = ROOT / "out" / slug
    outdir.mkdir(parents=True, exist_ok=True)
    imgs = []
    for i, p in enumerate(panels, 1):
        im = render(p, theme, i, len(panels))
        fp = outdir / f"panel{i}.png"
        im.save(fp)
        imgs.append(im)
        print("saved", fp.relative_to(ROOT))
    # 컨택트 시트 미리보기
    cols = len(imgs)
    tw = 300
    th = int(tw * H / W)
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 12, th + 24), (240, 240, 240))
    for i, im in enumerate(imgs):
        t = im.resize((tw, th), Image.LANCZOS)
        sheet.paste(t, (12 + i * (tw + 12), 12))
    sheet.save(outdir / "_contact.png")
    print("preview", (outdir / "_contact.png").relative_to(ROOT))

if __name__ == "__main__":
    main()
