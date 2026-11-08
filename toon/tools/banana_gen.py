#!/usr/bin/env python3
"""Nano Banana(Gemini image) 자동 생성기.

Gemini 네이티브 generateContent 엔드포인트를 호출해 이미지를 생성하고
PNG로 저장한다. 인증은 x-goog-api-key 헤더로, 값은 더미를 보내면
세션 프록시가 환경에 저장된 실제 키로 교체한다(네트워크 시크릿).

    python3 toon/tools/banana_gen.py \
        --prompt "귀여운 2D 플랫 카툰 ..." \
        --out scratchpad/gen/sheet.png \
        --model gemini-2.5-flash-image

여러 장: --n 3  (모델이 candidateCount를 제한하므로 호출 반복)
참조 이미지(편집/일관성): --ref path/to/ref.png (여러 번 지정 가능)
"""
import sys, json, base64, subprocess, argparse, pathlib, mimetypes

EP = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _call(model, parts, modalities):
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": modalities},
    }
    r = subprocess.run(
        ["curl", "-sS", "-X", "POST", EP.format(model=model),
         "-H", "x-goog-api-key: dummy",
         "-H", "Content-Type: application/json",
         "--data-binary", "@-", "--max-time", "180"],
        input=json.dumps(body).encode(), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed: {r.stderr.decode()[:300]}")
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"bad response: {r.stdout.decode()[:300]}")
    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError(f"API error {data['error'].get('code')}: "
                           f"{data['error'].get('message')}")
    imgs, texts = [], []
    for cand in data.get("candidates", []):
        for p in cand.get("content", {}).get("parts", []):
            if "inlineData" in p:
                imgs.append(p["inlineData"]["data"])
            elif "text" in p:
                texts.append(p["text"])
    return imgs, texts


def _ref_part(path):
    b = pathlib.Path(path).read_bytes()
    mime = mimetypes.guess_type(path)[0] or "image/png"
    return {"inlineData": {"mimeType": mime, "data": base64.b64encode(b).decode()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True, help="출력 PNG 경로(여러 장이면 _1,_2 접미사)")
    ap.add_argument("--model", default="gemini-2.5-flash-image",
                    help="gemini-2.5-flash-image | gemini-3-pro-image-preview")
    ap.add_argument("--n", type=int, default=1, help="생성 횟수(호출 반복)")
    ap.add_argument("--ref", action="append", default=[], help="참조 이미지(편집/일관성)")
    ap.add_argument("--modalities", default="IMAGE", help="쉼표구분: IMAGE 또는 TEXT,IMAGE")
    args = ap.parse_args()

    parts = [{"text": args.prompt}] + [_ref_part(p) for p in args.ref]
    mods = [m.strip() for m in args.modalities.split(",") if m.strip()]
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    saved = []
    for i in range(args.n):
        imgs, texts = _call(args.model, parts, mods)
        if not imgs:
            raise SystemExit(f"[{i+1}/{args.n}] 이미지 없음. 텍스트응답: {' '.join(texts)[:300]}")
        for j, b64 in enumerate(imgs):
            if args.n == 1 and len(imgs) == 1:
                dst = out
            else:
                dst = out.with_name(f"{out.stem}_{i+1}{'' if len(imgs)==1 else chr(97+j)}{out.suffix}")
            dst.write_bytes(base64.b64decode(b64))
            saved.append(str(dst))
            print(f"saved {dst}")
    print(f"OK: {len(saved)} image(s)")


if __name__ == "__main__":
    main()
