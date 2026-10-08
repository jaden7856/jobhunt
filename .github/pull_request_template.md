## 요약
<!-- 무엇을 왜 바꿨는지 -->

Closes #

## 확인한 것
<!-- 실제로 돌린 명령과 결과. 확인하지 못한 것은 못 했다고 적기 -->
- [ ] `python3 -m unittest discover -s tests` 통과
- [ ] `ruff check .` 통과
- [ ] 고친 스크립트를 직접 실행 (scan.py 는 `--dry-run`)

## 체크리스트
- [ ] `CHANGELOG.md` "다음 버전"에 한 줄 (사용자가 알아챌 변경일 때)
- [ ] `data/` 형식(제목·표 머리·키)을 바꿨다면 "data/ 이전" 줄에 옮기는 방법
- [ ] 개인 자료·실제 공고 원문 없음 (예시·테스트는 가상 인물·회사)
- [ ] README.md 와 README.en.md 를 함께 고침 (README 를 바꿨을 때)
- [ ] 새 수집기라면 고정 응답(`tests/fixtures/providers/`)과 `references/sources.md` 실측 날짜
