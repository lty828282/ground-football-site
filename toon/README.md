# toon — 음성 웹툰 쇼츠 생성기

`toon/stories/<slug>.json` 의 대사(내레이터·아빠·딸)를 읽어 한국어 음성을 입힌
9:16 세로 쇼츠(`short.mp4`)를 만든다. 화자별로 목소리를 구분하고, 대사 음성
길이에 맞춰 자막이 동기화된다.

## 준비물

```bash
apt-get install -y --no-install-recommends ffmpeg fonts-nanum fonts-nanum-extra
pip install edge-tts pillow numpy
# (오프라인 대체 음성용) 선택: apt-get install -y --no-install-recommends espeak-ng
```

## 실행

```bash
python3 toon/build_short.py ilseokijo
# 결과물: toon/out/ilseokijo/short.mp4
```

## 음성 엔진

- **기본: edge-tts** — 마이크로소프트 온라인 신경망 TTS. edge-tts 무료
  엔드포인트가 서비스하는 한국어 보이스는 `ko-KR-SunHiNeural`(여)/
  `ko-KR-InJoonNeural`(남) 두 개뿐이라, 이를 화자별로 배분한다.
  - 아빠 `ko-KR-InJoonNeural`(남) · 내레이터 `ko-KR-SunHiNeural`(차분한 여) ·
    딸 `ko-KR-SunHiNeural`(rate/pitch·피치 시프트로 밝고 어리게 구분)
- **대체: espeak-ng** — edge-tts 서버 접속이 막힌 환경(사내 프록시/CI 등)에서는
  자동으로 오프라인 엔진으로 전환하고, ffmpeg 피치 시프트로 아빠(낮게)/딸(높게)/
  내레이터(중간)를 구분한다. 이 경우에도 항상 음성이 들어간 mp4 가 나온다.

> edge-tts 는 `speech.platform.bing.com` 으로 접속한다. 방화벽/프록시가 이 호스트를
> 막으면 자동으로 espeak-ng 로 대체된다. 자연스러운 신경망 음성을 쓰려면 해당
> 호스트가 열린 네트워크에서 실행하면 된다.

## 새 스토리 추가

`toon/stories/<slug>.json`:

```json
{
  "title": "제목",
  "subtitle": "부제",
  "daughter_name": "지안",
  "lines": [
    { "speaker": "narrator", "text": "…" },
    { "speaker": "dad",      "text": "…" },
    { "speaker": "daughter", "text": "…" }
  ]
}
```

`speaker` 는 `narrator` / `dad` / `daughter` 중 하나. 이후
`python3 toon/build_short.py <slug>` 로 생성한다.
