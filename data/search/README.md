# search/

공고 수집 설정과 기록. `modes/scan.md`가 읽고 쓴다.
- `sources.yaml`: 켤 채널, 제목·근무지 필터, 우선 기업 목록. `sources.example.yaml`을 복사해 만든다.
- `pipeline.md`: 1차 선별을 통과한 공고 대기함(대기 / 제외 / 지원 완료 / 마감 / 처리 완료).
- `scan-history.tsv`: 한 번이라도 본 공고 기록. 중복 제거에 쓴다.
- `blacklist.md`: 지원하지 않을 회사(사용자가 직접 정한 것만).
