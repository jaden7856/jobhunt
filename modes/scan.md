# 모드: scan — 공고 찾기

채용 사이트에서 공고를 모아 1차 선별하고 `data/search/pipeline.md`에 쌓는다. 먼저 `modes/_shared.md`를 읽는다.

## 읽을 파일

- `data/search/sources.yaml`: 채널, 제목·근무지 필터, 우선 기업
- `data/profile/brief.md`: 1차 선별 기준 (없거나 템플릿 그대로면 `modes/onboard.md`로 먼저 만든다)
- `data/search/scan-history.tsv`, `data/search/pipeline.md`, `data/applications/tracker.md`, `data/search/blacklist.md`: 중복·쿨다운·제외 확인
- `references/sources.md`: 사이트별 엔드포인트, 본문 위치, 마감 판정

## 순서

1. **수집.** `python3 scripts/scan.py`를 먼저 실행한다. 원티드·점핏·LinkedIn·Greenhouse·토스·NHN·카카오·greetinghr을 받아 2·3단계와 기록까지 끝내고, 새 공고를 `pipeline.md`의 "새로 수집 (선별 전)"에, 본문을 `data/search/inbox/`에 둔다.
   - 출력의 "스크립트 미지원" 채널(사람인·잡코리아·리멤버, 브라우저 대상 기업)만 `references/sources.md` 방법으로 직접 수집하고, 결과를 같은 형식으로 "새로 수집 (선별 전)"에 넣고 `scan-history.tsv`에 적는다.
   - `✗` 로 표시된 채널은 응답 형식이 바뀐 것이다. 0건으로 넘기지 말고 보고하고, 확인되면 `scripts/providers/`와 `references/sources.md`를 고친다.
   - 처음 실행이라 쌓인 공고가 너무 많으면 사용자에게 `--seed`(지금 공고는 본 것으로만 기록) 여부를 묻는다.
   - 우선 기업(`priority: true`)은 매번 전부 돈다.
2. **1차 거르기** (스크립트가 자동으로 한다. 직접 수집한 채널만 손으로, 제목·메타만으로):
   - 제목: `title_filter.positive` 중 하나 포함, `negative` 포함이면 제외.
   - 근무지: `location_filter.block`이면 제외. 불명확하면 통과시키고 `[근무지 확인 필요]` 표시.
   - 중복: `scan-history.tsv`의 url, `pipeline.md`, `tracker.md`에 있으면 건너뛴다. 같은 회사+같은 포지션명도 중복으로 본다.
   - 제외 회사(`blacklist.md`), 재지원 쿨다운(`tracker.md`에서 `지원함` 이후 `targets.yaml`의 `reapply_days` 안인 회사).
   - 연차: 공고에 연차 숫자가 있으면 `sources.yaml`의 `career_filter`.
3. **본문 받기.** 남은 공고의 상세 본문(자격요건·우대사항·주요업무)을 받는다. 우산 공고는 하위 포지션까지 펼친다(토스는 스크립트가 하위 링크를 본문 끝에 모아 둔다).
4. **1차 선별.** "새로 수집 (선별 전)"의 공고마다 `inbox/` 본문과 `brief.md`만 보고 판정한다(전체 평가는 하지 않는다). 줄 끝의 `언어:` 힌트는 참고일 뿐이고, 판정은 자격요건 문장으로 한다.
   - 제외 조건(근무지·언어·스택·연차·형태)에 걸리면 `FAIL`. 판정 근거가 된 자격요건 문장을 한 줄 남긴다.
   - 나머지는 역할 적합·요구사항 충족·근무지·보상·서사 적합으로 1~5점. 3.5 이상 `PASS`, 3.0~3.4 `MARGINAL`, 미만 `FAIL`.
   - 우선 기업은 제외 조건을 통과하면 점수와 관계없이 `PASS`.
5. **기록.**
   - 선별한 줄을 "새로 수집 (선별 전)"에서 빼고, PASS·MARGINAL은 "대기"로(`선별 전` 자리를 `triage: PASS 3.8/5`로, 뒤에 한 줄 근거), FAIL은 "제외 (YYYY-MM-DD)"로 근거와 함께 옮긴다.
   - 마감 확인은 `python3 scripts/alive.py --write`(마감된 대기 공고를 "마감 확인 (날짜)"로, 평가함 행을 포기로). `확인 불가`는 브라우저로 본다.
6. **보고.** `python3 scripts/tracker.py report --since <지난 스캔 날짜>` 출력(아래 표 형식)을 그대로 보여 주고, 채널별 건수·미스캔 채널을 덧붙인다. 전체 평가는 사용자가 고른 공고만 `modes/evaluate.md`로.
   - 채널별 건수(0건 포함), 조건별 제외 건수, 미스캔 채널과 이유.
   - 표 하나로: 이번에 새로 찾은 공고 + 이미 평가·선별했던 공고(아직 열려 있는 것). 평가 완료와 지원 추천을 따로 나누지 않는다.

     | 회사 | 포지션 | 근무지 | 점수 | 판정 | 지원 여부 | 새로 찾음 | 마감 | 한 줄 근거 |
     |---|---|---|---|---|---|---|---|---|

     `지원 여부`는 `tracker.md` 기준(지원함 / 미지원), `판정`은 평가 점수가 있으면 그것, 없으면 1차 선별 결과.

## pipeline.md 형식

```markdown
## 새로 수집 (선별 전)
- [ ] {url} | {회사} | {포지션} | {근무지} | 선별 전 | {출처} · {수집일} · 마감 {날짜} | 언어: {힌트} | 본문: data/search/inbox/{파일}

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

## 주간 스캔

`bash scripts/weekly.sh`가 수집 → 마감 확인 → 통합 보고표를 한 번에 하고 `data/search/reports/YYYY-MM-DD.md`에 남긴다(LLM 없이, cron·launchd로 돌려도 됨). 그다음 4단계(1차 선별)부터 이어 간다.
사용자가 "주기적으로 찾아줘"라고 하면 이 PC에서 도는 `/loop`나 cron·launchd로 `weekly.sh`를 등록한다(클라우드 `/schedule`은 이 PC의 `data/`에 접근하지 못한다). 등록한 주기는 `data/preferences/standing.md`에 적는다.
