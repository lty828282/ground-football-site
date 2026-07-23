#!/bin/bash
# 맥용 실행 파일 — 더블클릭하면 로컬 서버가 뜨고 브라우저가 열립니다.
cd "$(dirname "$0")"
open http://localhost:8000/index.html
python3 -m http.server 8000
