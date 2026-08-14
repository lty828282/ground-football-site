# 데일리 툰 (속담·고사성어·영어표현 인스타툰 / 쇼츠)

아빠 + 딸 캐릭터로 **속담·고사성어·영어 표현을 쉽게 풀어주는** 인스타툰/쇼츠
자동 조립 프로젝트. **그라운드 유소년(축구) 사이트와는 무관한 별도 채널용**이다.

## 구조

```
toon/
├─ assets/characters/    # 배경 투명 캐릭터 PNG 27종 + characters.json 매니페스트
├─ content/<slug>.json   # 에피소드 대본(패널 단위)
├─ build_toon.py         # 자동 조립기: 대본 → 캐러셀 패널 PNG
└─ out/<slug>/           # 생성 결과 (panel1..N.png, _contact.png)
```

## 사용법

```bash
python3 toon/build_toon.py ilseokijo
# → toon/out/ilseokijo/panel1.png ... panel6.png + _contact.png
```

의존성: Python + Pillow, 한글 폰트(나눔), 한자용 CJK 폰트(WQY).

## 에피소드 대본 포맷 (`content/<slug>.json`)

- `term`/`hanja`/`en` — 표제어·한자·영어 대응
- `theme` — bg/accent/ink/bubble 색
- `panels[]` — 패널 배열. `kind` 별로:
  - `cover` : 표제 표지 (tag 필·타이틀·한자·부제 + 캐릭터)
  - `talk`  : 대화 (chars 배치 + bubbles 말풍선, 꼬리는 말하는 쪽으로)
  - `outro` : 영어 대응 카드 + CTA

각 캐릭터: `{name, x(가로 0~1), scale(세로 비율), flip}` — name 은
`assets/characters/characters.json` 의 파일명(확장자 제외).

## 규격

- 캐러셀 패널 **1080×1350 (4:5)** — 인스타 최적
- 쇼츠(9:16 1080×1920) 출력은 다음 단계에서 추가 예정

## 새 에피소드 만들기

1. `content/<slug>.json` 작성 (표제어·패널 대본·캐릭터/표정 지정)
2. `python3 toon/build_toon.py <slug>` 실행
3. `out/<slug>/_contact.png` 로 전체 확인 후 인스타 캐러셀로 업로드

## 유튜브 쇼츠(9:16) 만들기

```bash
python3 toon/build_short.py ilseokijo
# → toon/out/ilseokijo/short.mp4  (1080x1920)
```

- `build_short.py` 가 캐러셀 패널을 9:16 프레임(상단 표제 배너 + 패널 +
  **하단 자동 자막** + 핸들 + 진행바)으로 재구성하고 ffmpeg 로 조립.
- 자막은 패널의 `caption`(없으면 `vo`)을 하단 바에 굽는다. 패널당 1자막이라
  음성 길이에 맞춰 자동 동기화된다.
- 의존성: `ffmpeg`.
- 무성으로 뽑기: `TOON_NOVOICE=1 python3 toon/build_short.py <slug>`

### 음성(나레이션) 넣기 — 권장 워크플로

이 실행 환경은 외부 TTS 서버(구글/에지/허깅페이스)가 정책상 차단돼 **고품질
음성을 직접 생성할 수 없다**(오프라인 espeak-ng 은 품질 부적합). 대신 외부에서
만든 음성을 넣으면 파이프라인이 자동으로 화면·자막을 음성 길이에 맞춘다.

1. 각 패널 대사(`content/<slug>.json` 의 `vo`)를 고품질 한국어 TTS 로 생성.
   - **edge-tts**(무료, 자연스러움): `pip install edge-tts` 후
     `edge-tts --voice ko-KR-SunHiNeural --text "..." --write-media panel1.mp3`
     (아빠 대사는 `ko-KR-InJoonNeural`, 딸 대사는 `--pitch=+30Hz` 로 톤 조절)
   - 또는 ElevenLabs / Naver CLOVA Voice / Typecast(아동 목소리) 등.
2. 파일을 `toon/audio/<slug>/panel1.mp3 … panelN.mp3` 로 저장(mp3/wav/m4a).
3. `python3 toon/build_short.py <slug>` 실행 → 각 패널이 해당 음성 길이에
   맞춰 재생되고 오디오가 믹스된, **음성+자막 동기화 쇼츠**가 완성된다.

- 영상 산출물(`out/**/*.mp4`, `short_tmp/`)과 `audio/` 는 git 에서 제외됨.
