# Deep Work Music 채널 제작 완벽 가이드
### 배경 영상 제작법 + 음악 분석 + Suno 프롬프트 세트 1~10

> 목적: "Deep Work Music / Focus / Study" 계열 앰비언트 채널을 직접 만들기 위한 실전 가이드.
> 레퍼런스로 지정한 5개 영상의 **배경 제작 방식**과 **음악적 특징**을 분석하고,
> Suno로 바로 붙여 쓸 수 있는 **프롬프트 10세트**를 정리했습니다.
> (음악은 Suno, 영상은 AI 툴 + 무료 소스 조합을 전제로 작성)

---

## 목차
1. 레퍼런스 5개 영상 분석 (배경 + 음악 + Suno 프롬프트)
2. 배경 영상 만드는 방법 총정리 (파도·천장 색·별똥별·타이핑 컴퓨터 등)
3. Deep Work Music 장르의 공통 음악 특징
4. **Suno 프롬프트 세트 1~10** (핵심 결과물)
5. Suno 실전 사용법 & 채널 운영 워크플로우

---

## 1. 레퍼런스 5개 영상 분석

식별한 영상 목록:

| # | 영상 | 배경 컨셉 | 성격 |
|---|------|-----------|------|
| A | **Deep work music \| Minimalist ambient beats for deep focus & flow state concentration music** ([TZgFg0Ok7W0](https://www.youtube.com/watch?v=TZgFg0Ok7W0)) | 파도 + 천장 컬러 조명 + 별똥별 | 미니멀 앰비언트 |
| B | **Uninterrupted Deep Work Mix ~ Immersive Productivity Soundscape ~ Neural Focus Study Music** ([UDTmUzu05BE](https://www.youtube.com/watch?v=UDTmUzu05BE)) | 컴퓨터 화면에 코드/글자가 계속 타이핑되며 흐름 | 뉴럴 포커스 사운드스케이프 |
| C | **Deep Work Ocean Vibes ~ Ultimate Focus Music for Concentration & Productivity** ([j6DoeiE5Vmc](https://www.youtube.com/watch?v=j6DoeiE5Vmc)) | 바다/해양 (A와 같은 채널) | 오션 앰비언트 |
| D | **Calm Deep Work Music - Peaceful Focus Sounds for Reading & Creative Work \| Stress-Free Study** ([TI_pZD-FtBU](https://www.youtube.com/watch?v=TI_pZD-FtBU)) | 차분한 독서/창작 공간 | 캄(Calm) 앰비언트 |
| E | **Deep Work / Focus 계열 믹스** ([QYvk_cdkGKk](https://www.youtube.com/watch?v=QYvk_cdkGKk)) | 배경·음악 무드 우수 | 포커스 믹스 |

> 참고: 유튜브 본문 직접 접근이 차단되어(403), 제목·업로드일은 검색 색인 기반으로 확정했고
> 배경·음악 특징은 지정하신 설명 + 장르 표준 특징으로 분석했습니다. E영상은 색인에 노출되지 않아
> 장르 공통 특징으로 다뤘습니다. 실제 채널 방문 후 세부 조정 포인트는 각 항목 하단에 표기.

---

### A. 파도 + 천장 컬러 + 별똥별 (미니멀 앰비언트)

**배경 구성 요소 3층**
1. **하단: 잔잔한 파도** — 밤바다, 달빛/별빛 반사. 수평선 낮게. 물결이 아주 느리게 반복(seamless loop).
2. **중앙~상단: 천장/하늘 컬러 그라데이션** — 오로라처럼 보라·청록·자홍이 아주 느리게 번지며 색이 바뀜(color cycling).
3. **최상단: 별똥별** — 몇 초~수십 초에 한 번씩 사선으로 짧게 지나가는 유성. 랜덤 간격.

**만드는 방법 (난이도순)**
- **가장 쉬운 방법 (합성형):**
  1. AI 이미지로 "밤바다 + 별하늘" 스틸 1장 생성 (Midjourney / SDXL / DALL·E).
     프롬프트 예: `serene night ocean, low horizon, starry sky, aurora gradient, purple teal magenta, cinematic, ultrawide 16:9, calm, minimal`
  2. After Effects / DaVinci Resolve / CapCut에서 레이어로 분리:
     - 물결: **Wave Warp / Turbulent Displace**로 아주 약하게 흔들고 루프
     - 하늘 색: **그라데이션 램프 + Hue 회전**을 느리게 키프레임 → 색이 순환
     - 별똥별: 흰 점을 사선 이동 + 모션 블러 + 페이드. 15~40초 랜덤 간격으로 배치
  3. 8~10분 무손실 루프로 렌더 후, 유튜브 업로드 시 반복해 1~3시간 채움.
- **AI 영상 생성형:** Runway Gen-3 / Kling / Luma / Pika에 위 스틸을 넣고
  `slow gentle ocean waves, drifting aurora light, occasional shooting star, seamless loop, subtle motion` 로 5~10초 클립 여러 개 → 편집에서 크로스디졸브로 이어 붙임.
- **완전 무료형:** Pexels/Pixabay "night sky loop", "ocean night loop", "aurora loop" 무료 4K 클립을
  겹쳐서(Screen/Add 블렌드) 합성 + 별똥별만 직접 그려 얹기.

**핵심 디테일**
- 움직임은 **극도로 느리게**. 딴짓 유발 금지가 목적이라 시선을 끌면 안 됨.
- 색 순환 주기 3~5분, 별똥별은 예측 불가능한 랜덤 간격이어야 "살아있는" 느낌.
- 화면 밝기는 어둡게(다크 모드). 밤 작업/공부에 눈부심 방지.

**음악적 특징 (미니멀 앰비언트 포커스)**
- **BPM:** 60~75, 거의 비트 없음 ~ 아주 옅은 킥. 
- **키/스케일:** 마이너 또는 도리안, 애매하게 떠 있는(모달) 톤. C minor, A minor, D dorian 등.
- **악기:** 워엄 패드(신스 스트링), 낮게 깔린 사인 베이스, 가끔 울리는 전자 피아노/벨, 리버스 리버브.
- **구조:** 뚜렷한 전개 없음. 8~16마디가 미세 변주로 반복. 드롭·후렴 없음.
- **믹스:** 로우패스 필터로 고역 부드럽게, 넓은 리버브/딜레이로 공간감, 사이드체인 없이 잔잔.
- **의도:** 알파파/집중 유도. 멜로디가 기억에 남지 않도록 "배경으로 사라지는" 것이 핵심.

**Suno 프롬프트 (A형)**
```
Style: minimalist ambient, deep focus, drifting warm synth pads, soft sine bass,
sparse felt piano notes, wide reverb, slow evolving drone, no drums or very subtle
sub kick, 65 BPM, C minor, nocturnal, calm, spacious, cinematic, instrumental
Exclude: vocals, lyrics, drums fills, buildup, drop
```

---

### B. 코드가 계속 타이핑되는 컴퓨터 화면 (뉴럴 포커스 사운드스케이프)

**배경 구성**
- 어두운 방/책상 위 모니터(또는 터미널) 클로즈업. 화면에 **코드/텍스트가 스스로 한 글자씩 타이핑**되며 위로 스크롤. 커서 깜빡임. 매트릭스 느낌은 아니고 실제 코딩 화면 톤.
- 주변은 보케(bokeh) 조명, 미묘한 글로우, 김서린 창문/네온 반사 등으로 분위기.

**만드는 방법**
- **타이핑 효과 (가장 실전적):**
  - 웹 방식: HTML 페이지에 코드 텍스트를 넣고 **Typed.js** 또는 CSS `steps()` 타이핑 애니메이션으로 자동 타이핑 → 화면 녹화(OBS).
  - 터미널 방식: 실제 코드 파일을 `pv`/타이핑 시뮬레이터, 또는 asciinema로 재생 → 녹화.
  - 편집 방식: After Effects **Typewriter 프리셋**(Text > Animate > Range Selector)으로 글자 순차 등장 + 커서 레이어.
- **분위기 합성:**
  - 배경 스틸/영상은 AI로: `dark cozy programmer desk at night, glowing monitor, code on screen, bokeh city lights through window, rain, cinematic, moody` 
  - 모니터 화면 영역만 마스크 씌워 타이핑 영상 합성(코너 핀/트래킹).
  - 화면 글로우, 필름 그레인, 미세한 카메라 흔들림(2D wiggle) 추가 → 생동감.
- **루프:** 타이핑은 반복돼도 티가 잘 안 나므로 5~10분 클립 반복이면 충분.

**음악적 특징 (사운드스케이프/코딩 포커스)**
- **BPM:** 70~90, 규칙적이고 최소한의 비트(옅은 킥+하이햇) 또는 순수 드론.
- **악기:** 딥 사인 베이스, 아날로그 패드, 아르페지에이터(느리게 반복되는 신스 시퀀스), 미세한 글리치/텍스처, 화이트노이즈성 앰비언스.
- **성격:** future garage / ambient techno / drone의 경계. "흐름을 유지"시키는 반복적 그루브. 감정 기복 최소.
- **믹스:** 저역 탄탄, 넓은 스테레오, 롱 리버브. 소리들이 안개처럼 서로 스며듦.

**Suno 프롬프트 (B형)**
```
Style: ambient techno, deep work soundscape, hypnotic slow arpeggio, deep sub bass,
analog pads, subtle glitch textures, minimal steady kick, atmospheric drone,
80 BPM, hypnotic, immersive, nocturnal, focused, futuristic, instrumental
Exclude: vocals, melody hooks, breakdown, drop, cymbals crash
```

---

### C. 바다/오션 바이브 (A와 같은 채널)

**배경 구성**
- A와 자매 컨셉. 낮/황혼 바다 또는 심해/발광 바다(bioluminescent). 수면 위 빛 반짝임, 느린 파도, 수평선 위 하늘 그라데이션.

**만드는 방법**
- AI 스틸 → Runway/Kling으로 "느린 파도 + 빛 반짝임" 애니메이션 루프.
- 또는 Pexels/Pixabay 4K 오션 루프 + 상단 하늘 색 합성 + 물비늘 반짝임(Optical Flares) 추가.
- A와 동일한 톤 유지(느린 움직임, 어두운/차분한 색)로 채널 일관성 확보.

**음악적 특징 (오션 앰비언트)**
- **BPM:** 60~75. 파도 소리(SFX)를 아주 낮게 깔면 몰입 상승.
- **악기:** 넓은 패드, 부드러운 벨/마림바, 서브 베이스, 파도/물 앰비언스, 가벼운 필드 레코딩.
- **성격:** A보다 살짝 더 따뜻하고 서정적. 그래도 멜로디는 절제.

**Suno 프롬프트 (C형)**
```
Style: oceanic ambient, deep focus, warm evolving pads, soft mallet bells,
deep sub bass, gentle ocean wave ambience, wide reverb, slow tempo, 68 BPM,
serene, dreamy, spacious, meditative, instrumental
Exclude: vocals, drums, buildup, aggressive synths
```
> 팁: Suno로는 파도 SFX가 약할 수 있어, 영상 편집에서 **실제 파도 소리를 -20dB 정도로 언더레이**하면 원본 채널 느낌에 가까워집니다.

---

### D. 차분한 독서/창작 공간 (Calm 앰비언트)

**배경 구성**
- 아늑한 서재/카페/창가 책상. 따뜻한 조명, 식물, 커피, 비 오는 창문, 은은한 먼지 입자(dust particles).
- 움직임은 거의 정적 + 미세한 요소(비, 촛불 흔들림, 먼지, 커튼).

**만드는 방법**
- AI 스틸: `cozy reading nook by a rainy window, warm lamp light, books, plants, soft morning light, film photography, calm`
- 라이브 요소만 얹기: 비 오버레이(무료 rain overlay, Screen 블렌드), 먼지 파티클, 은은한 김/증기.
- 색은 A/B와 반대로 **따뜻한 톤(앰버/세피아)** → "스트레스 프리" 무드.

**음악적 특징 (Calm / Peaceful)**
- **BPM:** 55~70. 거의 무비트. 
- **악기:** 어쿠스틱 느낌 — 소프트 펠트 피아노, 어쿠스틱 기타 하모닉스, 첼로/스트링 패드, 따뜻한 앰비언스.
- **성격:** neoclassical ambient. 서정적이지만 잔잔. 독서·글쓰기 방해 안 되게 다이나믹 좁게.

**Suno 프롬프트 (D형)**
```
Style: neoclassical ambient, calm focus, soft felt piano, warm cello and string pads,
acoustic guitar harmonics, gentle rain ambience, intimate, tender, minimal, 62 BPM,
peaceful, stress-free, warm, instrumental
Exclude: vocals, drums, electronic synth, buildup
```

---

### E. 포커스 믹스 (배경·음악 무드형)

**배경 구성 (권장)**
- A~D 중 무엇이든 채널 톤에 맞춰 재사용 가능. "무드가 좋다"는 지점은 대개 **색감 + 느린 카메라 무빙 + 은은한 파티클** 3박자.
- 추천: 어두운 배경 + 단일 포인트 광원(달/램프/네온) + 느린 줌인(subtle push-in) 5~10분 루프.

**음악적 특징 (범용 딥워크 믹스)**
- **BPM:** 70~85. 은은한 로우파이/딥하우스성 그루브 또는 드론.
- **악기:** 패드, 로파이 드럼(먼지 낀 킥/스네어), 일렉트릭 피아노, 서브 베이스, 바이닐 크래클.
- **성격:** chillhop ~ downtempo. A보다 그루브 있고 D보다 덜 어쿠스틱한 중간값.

**Suno 프롬프트 (E형)**
```
Style: lofi downtempo, deep focus, dusty lofi drums, warm electric piano, sub bass,
mellow pads, vinyl crackle, subtle groove, laid-back, 78 BPM, cozy, nocturnal,
hypnotic, instrumental
Exclude: vocals, scratching, buildup, drop, bright leads
```

---

## 2. 배경 영상 만드는 방법 총정리

딥워크 배경은 크게 **3가지 파이프라인** 중 선택/조합합니다.

### 파이프라인 1 — 합성형 (추천, 가장 저렴·안정)
1. **AI 이미지**로 고해상 스틸 1~3장 생성 (Midjourney / SDXL / DALL·E / Leonardo).
2. **편집 툴**(After Effects / DaVinci Resolve / CapCut Pro)에서 레이어 분리 후 각 요소에 미세 애니메이션:
   - 물/파도 → Wave Warp, Turbulent Displace
   - 하늘/천장 색 → Gradient + Hue 회전 키프레임(3~5분 주기)
   - 별똥별 → 흰 점 사선 이동 + 모션블러 + 페이드 (랜덤 간격)
   - 비/먼지/보케 → 무료 오버레이 Screen 블렌드
3. 5~10분 **seamless loop**로 렌더 → 업로드 시 반복 재생.

### 파이프라인 2 — AI 영상 생성형 (움직임 자연스러움 ↑)
- Runway Gen-3 / Kling / Luma Dream Machine / Pika에 스틸 + 모션 프롬프트 투입.
- 5~10초 클립 여러 개 → 크로스디졸브로 이어 붙여 몇 분짜리 루프 제작.
- 비용/시간이 들지만 파도·조명의 유기적 움직임이 우수.

### 파이프라인 3 — 무료 스톡 합성형 (제작 시간 최소)
- Pexels / Pixabay / Mixkit의 4K 루프 클립(밤하늘, 오션, 오로라, 비) 무료 사용.
- 여러 클립을 블렌드 모드로 겹치고 색보정 → 별똥별·글로우만 직접 추가.
- **저작권/재사용 조건 확인 필수** (대부분 상업적 사용 허용이나 표기 규정 체크).

### 공통 원칙 (딥워크 배경의 핵심)
- **느림**: 모든 움직임은 시선을 끌지 않을 만큼 느리게.
- **다크 & 로우 콘트라스트**: 장시간 시청 눈 피로 최소화.
- **랜덤 포인트**: 별똥별·반짝임처럼 "가끔 일어나는" 요소로 지루함 방지.
- **루프 이음새 제거**: 시작/끝 프레임을 크로스페이드해 반복 티 제거.
- **일관된 톤**: 채널 전체가 같은 색·분위기여야 브랜드가 됨(썸네일도 통일).

### 장시간(1~3시간) 영상 만들기
- 음악: Suno 곡(2~4분) 8~30곡을 만들어 **크로스페이드로 이어 붙여** 믹스 제작(DAW: Reaper/Audition/Audacity).
- 영상: 5~10분 배경 루프를 반복해 음악 길이에 맞춤(편집 툴에서 클립 반복 또는 `ffmpeg -stream_loop`).
- 챕터 마커, 저작권(자작곡이므로 Content ID 등록), 썸네일 통일.

---

## 3. Deep Work Music 장르 공통 음악 특징

Suno 프롬프트를 잘 뽑기 위한 "장르 문법":

| 요소 | 표준값 |
|------|--------|
| **BPM** | 55~90 (미니멀/오션 60~72, 코딩/테크노 78~90) |
| **비트** | 없음~아주 옅음. 강한 드럼·필·크래시 금지 |
| **키** | 마이너/모달(도리안·에올리안). 애매하게 떠 있는 느낌 |
| **악기** | 워엄 패드, 서브 베이스, 펠트 피아노, 벨/마림바, 아르페지오, 텍스처/노이즈 |
| **구조** | 전개·드롭·후렴 없음. 미세 변주 반복 |
| **다이나믹** | 좁게. 갑작스런 크레셴도 금지 |
| **공간감** | 넓은 리버브/딜레이, 로우패스로 고역 순화 |
| **금지 요소** | 보컬, 가사, 갑작스런 전환, 밝고 날카로운 리드, 브레이크다운 |
| **의도** | 알파파 대역 몰입, 멜로디가 기억에 안 남고 "배경으로 사라짐" |

**Suno에서 반드시 넣을 키워드**: `instrumental`, `deep focus`, `no drums` 또는 `subtle beat`, `ambient`, BPM 수치, 키.
**반드시 뺄 것(Exclude/네거티브)**: `vocals, lyrics, buildup, drop, breakdown, aggressive`.

---

## 4. Suno 프롬프트 세트 1~10 (핵심 결과물)

각 세트는 서로 다른 무드로 채널을 다양하게 채우도록 설계했습니다.
Suno v4.5+ 기준: **Custom Mode → Instrumental 켜기 → Style 칸에 아래 Style 붙여넣기**.
Exclude Styles 칸이 있으면 각 항목의 Exclude를 넣으세요. (없으면 Style 뒤에 `no vocals, no drums fills`처럼 병기)

곡 제목(Title)은 자유. 아래는 스타일 프리셋입니다.

---

### 세트 1 — Minimalist Ambient (파도·천장·별똥별용 / A영상)
```
minimalist ambient, deep focus, drifting warm synth pads, soft sine bass,
sparse felt piano notes, wide reverb, slow evolving drone, very subtle sub kick,
65 BPM, C minor, nocturnal, calm, spacious, cinematic, instrumental
```
**Exclude:** `vocals, lyrics, drums fills, buildup, drop`
**용도:** 밤바다/오로라/별똥별 배경. 채널 시그니처 톤.

---

### 세트 2 — Ambient Techno / Coding Soundscape (타이핑 컴퓨터용 / B영상)
```
ambient techno, deep work soundscape, hypnotic slow arpeggio, deep sub bass,
analog pads, subtle glitch textures, minimal steady kick, atmospheric drone,
82 BPM, hypnotic, immersive, nocturnal, focused, futuristic, instrumental
```
**Exclude:** `vocals, melody hooks, breakdown, drop, crash cymbals`
**용도:** 코드 타이핑 화면, 프로그래밍/집중 세션.

---

### 세트 3 — Oceanic Ambient (바다 바이브 / C영상)
```
oceanic ambient, deep focus, warm evolving pads, soft mallet bells, deep sub bass,
gentle ocean wave ambience, wide reverb, slow tempo, 68 BPM, serene, dreamy,
spacious, meditative, instrumental
```
**Exclude:** `vocals, drums, buildup, aggressive synths`
**용도:** 오션/심해 배경. 영상에서 실제 파도 SFX 언더레이 권장.

---

### 세트 4 — Neoclassical Calm (독서·창작 / D영상)
```
neoclassical ambient, calm focus, soft felt piano, warm cello and string pads,
acoustic guitar harmonics, gentle rain ambience, intimate, tender, minimal,
62 BPM, peaceful, stress-free, warm, instrumental
```
**Exclude:** `vocals, drums, electronic synth, buildup`
**용도:** 비 오는 창가, 서재, 따뜻한 톤의 스트레스 프리 세션.

---

### 세트 5 — Lofi Downtempo (범용 포커스 믹스 / E영상)
```
lofi downtempo, deep focus, dusty lofi drums, warm electric piano, sub bass,
mellow pads, vinyl crackle, subtle groove, laid-back, 78 BPM, cozy, nocturnal,
hypnotic, instrumental
```
**Exclude:** `vocals, scratching, buildup, drop, bright leads`
**용도:** 로파이 감성의 딥워크. 그루브가 살짝 있어 반복 시청에 강함.

---

### 세트 6 — Future Garage (심야 집중, B의 변형)
```
future garage, deep work, deep rolling sub bass, airy pads, distant vocal chops as
texture only, soft syncopated shuffle beat, reverb-drenched, melancholic, 84 BPM,
rainy night, atmospheric, immersive, instrumental
```
**Exclude:** `lead vocals, lyrics, buildup, drop, big drums`
**용도:** 비 오는 밤 도시 무드, 몰입형 코딩/디자인.
> vocal chops는 "가사"가 아니라 텍스처로만. 뚜렷한 보컬이 나오면 재생성.

---

### 세트 7 — Drone / Dark Ambient (제로 디스트랙션, 초집중)
```
dark ambient drone, zero distraction, deep evolving textures, low frequency hum,
subtle granular synths, no beat, glacial pace, 60 BPM, vast, cavernous, meditative,
hypnotic, instrumental
```
**Exclude:** `vocals, drums, melody, buildup, bright tones`
**용도:** 멜로디도 방해되는 극한 집중(수학/코딩/독해). 완전 무비트.

---

### 세트 8 — Binaural Deep Focus (뇌파 집중 컨셉)
```
ambient focus music, binaural style, warm sustained pads, low steady drone,
soft bell tones, gentle theta-alpha mood, spacious reverb, no percussion, 60 BPM,
tranquil, brainwave, meditative, instrumental
```
**Exclude:** `vocals, drums, buildup, sharp transients`
**용도:** "binaural / brainwave / neural" 타이틀 영상.
> 진짜 바이노럴 비트(정확한 Hz 차이)는 Suno가 보장 못 함. Audacity로 40Hz 근처 톤을 아주 낮게 언더레이하면 컨셉 강화(어디까지나 배경음, 의학적 효과 주장 금지).

---

### 세트 9 — Cinematic Ambient (웅장하지만 잔잔, 롱 세션 오프닝용)
```
cinematic ambient, deep focus, wide orchestral pads, soft piano motif, deep sub bass,
subtle swelling strings, airy textures, slow build without drop, 70 BPM, epic yet calm,
spacious, contemplative, instrumental
```
**Exclude:** `vocals, drums fills, loud climax, brass stabs`
**용도:** 1~3시간 믹스의 도입부/전환부. 살짝 서사적인 분위기.

---

### 세트 10 — Deep House Downtempo (은은한 그루브, 낮 작업용)
```
downtempo deep house, focus groove, soft four-on-the-floor muted kick, warm analog
chords, deep bass, gentle plucks, mellow atmosphere, 90 BPM, smooth, hypnotic,
daytime productivity, instrumental
```
**Exclude:** `vocals, vocal chops, buildup, drop, festival synths`
**용도:** 낮 시간 작업, 살짝 에너지 있는 딥워크. 반복 킥이 리듬 유지.

---

### 세트 요약표

| 세트 | 스타일 | BPM | 비트 | 매칭 배경 |
|------|--------|-----|------|-----------|
| 1 | Minimalist Ambient | 65 | 거의 없음 | 밤바다·별똥별 |
| 2 | Ambient Techno | 82 | 옅은 킥 | 코드 타이핑 |
| 3 | Oceanic Ambient | 68 | 없음 | 바다/심해 |
| 4 | Neoclassical Calm | 62 | 없음 | 서재/비창가 |
| 5 | Lofi Downtempo | 78 | 로파이 드럼 | 아늑한 방 |
| 6 | Future Garage | 84 | 셔플 | 비 오는 도시밤 |
| 7 | Dark Ambient Drone | 60 | 없음 | 미니멀/암흑 |
| 8 | Binaural Focus | 60 | 없음 | 뉴럴/뇌파 |
| 9 | Cinematic Ambient | 70 | 없음~미세 | 롱세션 오프닝 |
| 10 | Deep House Downtempo | 90 | 뮤트 킥 | 낮 작업 |

---

## 5. Suno 실전 사용법 & 채널 워크플로우

**Suno 세팅**
1. **Custom Mode** 사용. **Instrumental** 토글 ON (보컬 방지).
2. **Style** 칸에 위 프리셋 붙여넣기. 너무 길면 핵심 키워드 위주로 축약.
3. **Exclude Styles**(v4.5+)에 각 세트의 Exclude 입력.
4. 한 프롬프트로 여러 번 생성 → 마음에 드는 8~30곡 선별.
5. **Extend/Continue**로 곡을 늘리거나, DAW에서 곡들을 **크로스페이드**로 연결해 롱폼 믹스 제작.

**품질 팁**
- 보컬이 새어 나오면: Style에 `strictly instrumental` 추가 + Exclude에 `vocals, vocal chops, spoken word`.
- 너무 밝거나 팝적이면: `dark, muted, low-pass filtered, subdued` 추가.
- 곡 간 톤 튐 방지: 같은 세트 내에서 BPM·키를 고정(예: 모두 65 BPM, C minor).

**롱폼(1~3시간) 제작**
- 음악: 선별 곡 → Reaper/Audition에서 4~8초 크로스페이드로 이어 붙이기.
- 영상: 5~10분 배경 루프 반복(`ffmpeg -stream_loop -1`).
- 배경 SFX(파도/비)는 음악과 별개 트랙으로 -18~-24dB 언더레이.

**채널 운영**
- 썸네일·색·폰트 통일로 브랜드화(A~E가 서로 자매 영상처럼 보이게).
- 제목 공식: `Deep Work Music | [무드] for [용도] ~ [분위기 키워드]`.
- 자작곡(Suno)이므로 유튜브 Content ID/저작권 문제 낮음. (Suno 상업 이용은 유료 플랜 라이선스 조건 확인.)
- 배경 스톡을 쓸 경우 각 소스 라이선스 표기 규정 준수.

---

### 참고(식별된 레퍼런스 링크)
- A: https://www.youtube.com/watch?v=TZgFg0Ok7W0
- B: https://www.youtube.com/watch?v=UDTmUzu05BE
- C: https://www.youtube.com/watch?v=j6DoeiE5Vmc
- D: https://www.youtube.com/watch?v=TI_pZD-FtBU
- E: https://www.youtube.com/watch?v=QYvk_cdkGKk

> 다음 단계 제안: 원하시면 (1) 이 세트별로 **한국어 무드 제목/썸네일 문구**, (2) 1~3시간 믹스용 **트랙 순서/전환 설계**, (3) 특정 영상 하나를 골라 **배경 제작 단계별 실습 스크립트**까지 이어서 만들어 드릴 수 있습니다.
