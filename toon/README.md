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
