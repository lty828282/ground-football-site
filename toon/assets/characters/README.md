# 캐릭터 마스코트 에셋 (아빠 + 딸)

속담·고사성어·영어표현 인스타툰/쇼츠 채널용 마스코트. 모든 PNG는 **배경 투명**(scene_bg 제외).
`characters.json` 매니페스트로 자동화 스크립트에서 참조한다.

## 전체 구성 (총 96종)

- **딸** 표정 20 · 포즈 18
- **아빠** 표정 18 · 포즈 17
- **투샷(duo)** 10 · **소품(prop)** 12 · scene_autumn
- 전체 목록·라벨은 `characters.json` 참조 (아래 v1 목록은 초기 26종 기준).

> v2 확장팩(69종)에서 딸/아빠 표정·포즈 대량 추가 + 투샷 9종 + 교육용 소품 12종(책·지구본·돋보기·전구·트로피·칠판·연필·물음표·느낌표·별·두루마리) 추가.

## 딸 (ddal)

- `ddal_happy.png` — expression · 활짝 웃음/신남
- `ddal_playful.png` — expression · 장난(윙크+혀)
- `ddal_thinking.png` — expression · 고민중
- `ddal_smile.png` — expression · 잔잔한 미소
- `ddal_surprised.png` — expression · 놀람
- `ddal_crying.png` — expression · 울음
- `ddal_talking.png` — expression · 말하기
- `ddal_smug.png` — expression · 뿌듯(팔짱)
- `ddal_stand.png` — pose · 서기(기본)
- `ddal_point.png` — pose · 가리키기(설명)
- `ddal_read.png` — pose · 책 읽기
- `ddal_thumbsup.png` — pose · 엄지척
- `ddal_holdhand.png` — pose · 손잡기
- `ddal_apple.png` — pose · 사과 먹기

## 아빠 (appa)

- `appa_smile.png` — expression · 온화한 미소
- `appa_smug.png` — expression · 뿌듯
- `appa_surprised.png` — expression · 당황(식은땀)
- `appa_laugh.png` — expression · 크게 웃음
- `appa_talking.png` — expression · 말하기
- `appa_troubled.png` — expression · 곤란
- `appa_stand.png` — pose · 서기(기본)
- `appa_explain.png` — pose · 설명(손 내밈)
- `appa_point.png` — pose · 가리키기
- `appa_cook.png` — pose · 요리(앞치마)
- `appa_thumbsup.png` — pose · 엄지척

## 공용

- `duo_hold.png` — 손잡은 투샷 (배경 투명)
- `scene_autumn.png` — 가을 배경 씬 (배경 포함, 상단 여백에 자막 얹기)

## 사용 예

```python
import json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
chars = json.loads((root/'assets/img/characters/characters.json').read_text())
byname = {a['file'][:-4]: a for a in chars['assets']}
# byname['ddal_happy'] -> {'file','char','type','label','w','h'}
```
