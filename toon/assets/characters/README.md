# 캐릭터 마스코트 에셋 (아빠 + 딸)

그라운드 유소년 카드뉴스·릴스용 마스코트. 모든 PNG는 **배경 투명**(scene_bg 제외).
`characters.json` 매니페스트로 자동화 스크립트에서 참조한다.

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
