# Mode: scan — finding postings

Collect postings from job sites, screen them once, and queue them in `data/search/pipeline.md`. Read `modes/_shared.md` first.

## Files to read

- `data/search/sources.yaml`: channels, title and location filters, priority companies
- `data/profile/brief.md`: first-pass screening criteria (if missing or still the template, build it via `modes/onboard.md` first)
- `references/scoring.md`: scoring (classification and calculation); `data/profile/calibration.md`: judgment cases the user corrected
- `data/search/scan-history.tsv`, `data/search/pipeline.md`, `data/applications/tracker.md`, `data/search/blacklist.md`: duplicates, cooldown, exclusions
- `references/sources.md`: per-site endpoints, body location, closing check

## Steps

0. **Widen companies (once a month, or when the user says "회사 더 찾아줘").** Run `scripts/discover.py collect → probe → promote --dry-run` per "Company discovery" in `references/sources.md`, show the user the table of companies to add, then `promote`. New companies are collected from the next `scan.py` run (ask about `--seed` the first time).

1. **Collect.** Run `python3 scripts/scan.py` first. It fetches Wanted · Jumpit · LinkedIn · Greenhouse · Toss · NHN · Kakao · greetinghr · ninehire, finishes steps 2–3 and the logging, puts new postings under "새로 수집 (선별 전)" in `pipeline.md`, and puts bodies in `data/search/inbox/`.
   - Collect only the channels the output lists as "스크립트 미지원" (Saramin, JobKorea, Remember, browser-only companies) by hand, using `references/sources.md`. Add the results under "새로 수집 (선별 전)" in the same format and log them in `scan-history.tsv`.
   - A channel marked `✗` means its response shape changed. Report it instead of passing it off as 0 results; once confirmed, fix `scripts/providers/` and `references/sources.md`.
   - If a first run piles up too many postings, ask the user about `--seed` (record current postings as seen only).
   - Priority companies (`priority: true`) are always scanned in full.
2. **First filter** (the script does this; do it by hand, from title and metadata only, just for channels collected by hand):
   - Title: must contain one of `title_filter.positive`; contains a `negative` → exclude.
   - Location: `location_filter.block` → exclude. If unclear, pass it and mark `[근무지 확인 필요]`.
   - Duplicates: skip if the url is in `scan-history.tsv`, `pipeline.md`, or `tracker.md`. The same company + same position title also counts as a duplicate.
   - Excluded companies (`blacklist.md`); reapply cooldown (a company within `reapply_days` of `targets.yaml` after a `지원함` in `tracker.md`).
   - Years: if the posting states a number of years, apply `career_filter` from `sources.yaml`.
3. **Fetch bodies.** Fetch the full detail (qualifications, preferred, main tasks) of the remaining postings. Expand umbrella postings down to their sub-positions (for Toss the script gathers sub-links at the end of the body).
4. **First-pass screening.** For each posting under "새로 수집 (선별 전)", follow `references/scoring.md` in order. Never estimate a score.
   - Scaffold with `python3 scripts/score.py init <inbox body> -o data/search/judgments/<source>_<id>.yaml`, then fill every line's classification (fit · met · gap) plus direction, gates, and signals. The `언어:` hint at the end of a line is only a hint; judge conditions from the qualification sentences.
   - If an exclusion gate hits, write only `fail` and the evidence sentence under `gates` and skip line classification.
   - If a posting resembles a case in `calibration.md`, classify it the same way.
   - Use the score and verdict from `python3 scripts/score.py data/search/judgments/<file>.yaml` as is. 3.5+ `PASS`, 3.0–3.4 `MARGINAL`, below `FAIL`.
   - Priority companies get `priority: true` in the judgment file (bonus only, no automatic PASS).
5. **Record.**
   - Remove screened lines from "새로 수집 (선별 전)". Move PASS and MARGINAL to "대기" (replace `선별 전` with `triage: PASS 3.8/5`, followed by a one-line reason and `판정: data/search/judgments/<file>.yaml`); move FAIL to "제외 (YYYY-MM-DD)" with the reason.
   - For closing checks run `python3 scripts/alive.py --write` (closed queued postings go to "마감 확인 (날짜)", tracker rows in 평가함 become 포기). Open `확인 불가` ones in a browser.
6. **Report.** Show the output of `python3 scripts/tracker.py report --since <last scan date>` (table format below) as is, and add per-channel counts and unscanned channels. Full evaluation only for postings the user picks, via `modes/evaluate.md`.
   - Per-channel counts (including 0), exclusion counts per condition, unscanned channels and why.
   - One table: postings newly found this time + postings already evaluated or screened that are still open. Keep evaluated and recommended postings in the same table.

     | 회사 | 포지션 | 근무지 | 점수 | 판정 | 지원 여부 | 새로 찾음 | 마감 | 한 줄 근거 |
     |---|---|---|---|---|---|---|---|---|

     `지원 여부` comes from `tracker.md` (지원함 / 미지원); `판정` is the evaluation score if there is one, otherwise the first-pass result.

## pipeline.md format

Scripts parse these headings and markers; keep them verbatim.

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

## scan-history.tsv columns

`url  first_seen  portal  title  company  status  location  fingerprint  posted_at  trust_score  trust_flags  normalized_company` (tab-separated). Trailing columns may be empty. Read columns by name.

## Weekly scan

`bash scripts/weekly.sh` runs collect → closing check → combined report in one go and saves `data/search/reports/YYYY-MM-DD.md` (no LLM; fine to run from cron or launchd). Then continue from step 4 (first-pass screening).
If the user asks "주기적으로 찾아줘", register `weekly.sh` with `/loop` or cron/launchd running on this machine (cloud `/schedule` cannot reach this machine's `data/`). Write the registered interval into `data/preferences/standing.md`.
