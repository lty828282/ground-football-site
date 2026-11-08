# 인스타그램 카드뉴스 자동 게시 파이프라인

`@askpapa` 고사성어 카드뉴스를 **Instagram Content Publishing API**로 자동 업로드한다.

## 전체 흐름

```
build_toon.py  →  export_jpg.py  →  make_caption.py  →  (commit & push)  →  ig_publish.py
   패널 PNG         IG용 JPEG          캡션 자동작성        공개 raw URL 확보       캐러셀 게시
```

- 이미지는 **공개 저장소의 GitHub raw URL**로 호스팅된다(별도 서버 불필요).
- 토큰은 `graph.facebook.com` **네트워크 시크릿**으로 주입되며 코드에는 더미값만 들어간다.

## 한 번만 하면 되는 준비 (계정 소유자 = 당신만 가능)

1. **인스타 @askpapa 를 프로페셔널(비즈니스/크리에이터) 계정으로 전환**
   - 설정 → 계정 → 프로페셔널 계정으로 전환
2. **페이스북 페이지 생성 후 인스타 계정과 연결**
   - 인스타는 반드시 페이스북 페이지에 연결돼 있어야 API 게시가 된다.
3. **메타 개발자 앱 생성** — developers.facebook.com
   - 앱 유형: Business → 제품에서 **Instagram** 추가
   - 본인을 앱의 관리자/테스터로 (본인 계정 게시는 개발 모드로 충분, 앱 심사 불필요)
4. **장기 액세스 토큰 발급** (Graph API Explorer 또는 앱 설정)
   - 권한(scope): `instagram_basic`, `instagram_content_publish`,
     `pages_show_list`, `pages_read_engagement`, `business_management`
   - 단기 토큰은 60일 장기 토큰으로 교환해 사용.
5. **토큰을 세션에 전달** — Claude가 안내하는 보안 폼(또는 환경 → 네트워크 시크릿)에서:
   - Host: `graph.facebook.com`
   - 방식: `Authorization: Bearer` (접두사 Bearer)
   - Value: 장기 액세스 토큰
   - 저장하면 이 호스트가 자동 허용되고, 프록시가 토큰을 주입한다.

> IG 사용자 ID는 몰라도 된다 — 스크립트가 `/me/accounts`로 자동 탐색한다.
> 직접 지정하려면 `--ig-user-id` 사용.

## 사용법

```bash
# 1) 카드 생성(이미 있으면 생략)
python3 toon/build_toon.py yubimuhwan

# 2) IG용 JPEG 내보내기
python3 toon/tools/export_jpg.py yubimuhwan

# 3) 캡션 자동 생성·저장
python3 toon/tools/make_caption.py yubimuhwan --save

# 4) JPEG와 캡션을 commit & push (공개 raw URL 활성화)
git add toon/out/yubimuhwan/*.jpg toon/content/captions/yubimuhwan.txt
git commit -m "..." && git push

# 5) 먼저 점검(게시 안 함)
python3 toon/tools/ig_publish.py --slug yubimuhwan \
    --caption-file toon/content/captions/yubimuhwan.txt --dry-run

# 6) 실제 게시
python3 toon/tools/ig_publish.py --slug yubimuhwan \
    --caption-file toon/content/captions/yubimuhwan.txt
```

## 참고 / 제약
- 캐러셀은 **2~10장** (에피소드는 6장이라 OK).
- 이미지 포맷은 안전하게 **JPEG** 사용(PNG는 거부될 수 있음).
- 컨테이너가 `FINISHED` 될 때까지 폴링 후 게시.
- 게시 호출에는 시간당 한도가 있다(계정당 하루 다수 게시 가능하나 과도하면 제한).
- `--branch`는 raw URL의 브랜치. 기본값은 개발 브랜치이며, master 병합 후엔 `--branch master`.

## 자동화(선택)
- 매일 정해진 시각 게시: 스케줄러로 5~6단계를 호출(토큰 유효해야 함).
- 토큰 만료(장기 토큰 ~60일) 시 갱신 필요.
