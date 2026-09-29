# 모드: scan — 공고 찾기

채용 사이트에서 공고를 모아 1차 선별하고 `data/search/pipeline.md`에 쌓는다. 먼저 `modes/_shared.md`를 읽는다.

## 읽을 파일

- `data/search/sources.yaml`: 채널, 제목·근무지 필터, 우선 기업
- `data/profile/brief.md`: 1차 선별 기준 (없거나 템플릿 그대로면 `modes/onboard.md`로 먼저 만든다)
- `data/search/scan-history.tsv`, `data/search/pipeline.md`, `data/applications/tracker.md`, `data/search/blacklist.md`: 중복·쿨다운·제외 확인
- `references/sources.md`: 사이트별 엔드포인트, 본문 위치, 마감 판정

## 순서

1. **수집.** `sources.yaml`의 켜진 채널을 모두 돈다. 방법은 `references/sources.md`를 따른다. 채널마다 받은 건수를 센다(0건도 기록).
   - `scripts/scan.py`가 있으면(2단계) 그것부터 실행하고, 스크립트가 못 다루는 채널만 직접 수집한다.
   - 우선 기업(`priority: true`)은 매번 전부 돈다.
2. **1차 거르기** (본문을 받기 전, 제목·메타만으로):
   - 제목: `title_filter.positive` 중 하나 포함, `negative` 포함이면 제외.
   - 근무지: `location_filter.block`이면 제외. 불명확하면 통과시키고 `[근무지 확인 필요]` 표시.
   - 중복: `scan-history.tsv`의 url, `pipeline.md`, `tracker.md`에 있으면 건너뛴다. 같은 회사+같은 포지션명도 중복으로 본다.
   - 제외 회사(`blacklist.md`), 재지원 쿨다운(`tracker.md`에서 `지원함` 이후 `targets.yaml`의 `reapply_days` 안인 회사).
3. **본문 받기.** 남은 공고의 상세 본문(자격요건·우대사항·주요업무)을 받는다. 우산 공고는 하위 포지션까지 펼친다.
4. **1차 선별.** `brief.md`만 보고 판정한다(전체 평가는 하지 않는다).
   - 제외 조건(근무지·언어·스택·연차·형태)에 걸리면 `FAIL`. 판정 근거가 된 자격요건 문장을 한 줄 남긴다.
   - 나머지는 역할 적합·요구사항 충족·근무지·보상·서사 적합으로 1~5점. 3.5 이상 `PASS`, 3.0~3.4 `MARGINAL`, 미만 `FAIL`.
   - 우선 기업은 제외 조건을 통과하면 점수와 관계없이 `PASS`.
5. **기록.**
   - `pipeline.md` "대기"에 PASS·MARGINAL을 추가, "제외 (YYYY-MM-DD)"에 FAIL을 근거와 함께 추가.
   - 받은 모든 공고를 `scan-history.tsv`에 한 줄씩 추가(`status`: `added` / `skipped_title` / `skipped_location` / `skipped_dup` / `skipped_fail`).
   - 추적 중인데 목록에서 사라진 공고는 상세로 마감 여부를 확인한 뒤에만 "마감"으로 옮긴다.
6. **보고.** 전체 평가는 사용자가 고른 공고만 `modes/evaluate.md`로.
   - 채널별 건수(0건 포함), 조건별 제외 건수, 미스캔 채널과 이유.
   - 표 하나로: 이번에 새로 찾은 공고 + 이미 평가·선별했던 공고(아직 열려 있는 것). 평가 완료와 지원 추천을 따로 나누지 않는다.

     | 회사 | 포지션 | 근무지 | 점수 | 판정 | 지원 여부 | 새로 찾음 | 마감 | 한 줄 근거 |
     |---|---|---|---|---|---|---|---|---|

     `지원 여부`는 `tracker.md` 기준(지원함 / 미지원), `판정`은 평가 점수가 있으면 그것, 없으면 1차 선별 결과.

## pipeline.md 형식

```markdown
## 대기
- [ ] {url} | {회사} | {포지션} | {근무지} | triage: {PASS|MARGINAL} {점수}/5 | {한 줄 근거} | {출처} · {게시일}

## 제외 (YYYY-MM-DD)
- [x] {url} | {회사} | {포지션} | FAIL | {판정 근거 문장}

## 지원 완료 — 재지원 쿨다운
## 마감 확인
## 처리 완료
```

## scan-history.tsv 열

`url  first_seen  portal  title  company  status  location  fingerprint  posted_at  trust_score  trust_flags  normalized_company` (탭 구분). 뒤쪽 열은 비워도 된다. 읽을 때는 열 이름으로 찾는다.

## 반복 실행

사용자가 "주기적으로 찾아줘"라고 하면 `/loop` 또는 `/schedule`로 이 모드를 등록한다. 등록한 주기는 `data/preferences/standing.md`에 적는다.
