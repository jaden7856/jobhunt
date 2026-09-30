# General resume rules

Condensed from earlier guide documents (writing guide, rejection-cause diagnosis, rebuilding a career from GitLab evidence, commit-level analysis), keeping only rules that apply to anyone. When it conflicts with SKILL.md, follow SKILL.md.

## Whole document

- A 15-second scan document. Page 1 must show the summary, skills, and the start of the lead project.
- Target 2–3 pages. Single-column PDF with real text (tables and images pasted in break ATS parsing, search, and editing).
- At most 5 projects; pick, don't include everything. Ones far from the posting drop to one OTHER line.
- Keep the career timeline continuous with the EXPERIENCE timeline (3–4 lines per year), leaving no long blank stretch.
- No motivation statement. Write a separate 5–7 lines only when the company asks.
- Tech stack: 8–12 items overlapping with the posting. No proficiency gauges or stars. Only technologies actually used.
- Ship with every placeholder (【 】, N건, TODO) resolved. A leftover alone is grounds for rejection.
- Filename `이름_직무_버전.pdf`. Open it once on a phone.

## Project block

```
[번호] 임팩트가 보이는 제목 (가능하면 숫자: "주문 API p99 820ms → 240ms : …")
기간 · 역할(단독/주도/원인 분석·구현) · 기술 칩
요약 바 1~2줄 (문제, 해결, 결과)
문제       상황 + 왜 중요한지(비즈니스 영향) 2~3줄
원인 규명  어떻게 찾았나 (로그, 재현 테스트, 코드 추적, 프로파일링) 1~2줄
선택지     2~3개. 기각안은 장점을 먼저 인정하고 단점으로 기각. 채택안은 근거와 약점 통제 방법까지
실행       불릿 3~4개. 행동 동사 + 구체 기법
결과       KPI 2~3개 (큰 숫자 + 설명)
↳ 관련 글  1~2개
```

- Interviewers look at "why that choice" more than execution. The options row matters most.
- Keep each paragraph within 3 lines; split a 5–7 line project paragraph.

## Numbers

- Write numbers as before/after (820ms → 240ms, 4시간 → 20분).
- Attach the cause to every number (what changed to get there).
- Look in four directions: scale, rate of change, frequency, savings.
- Only numbers in the material, and only confirmed ones.
- Operational metrics (inquiries, incidents, reprocessing counts) beat self-defined test results ("재현 테스트 0건"). Use them when available.

## Speaking the company's language

Rewrite the same experience for each target.
- Infra/platform orgs: scale (servers, traffic, data volume), systems integrated, that field's domain terms
- Service companies: results users felt (response time, incidents, conversion), data consistency, concurrency
- If the posting has "이력서 작성 추천사항", order the experience to match it.
- A tailored version copies the base, unifies terms to the posting's, moves relevant experience up, and deletes unrelated lines.

## Links

- 1–2 links per project. More is hard to read and looks like a "hastily made blog".
- Open every link before submitting. An inactive GitHub or blog costs points.

## Finding experience in evidence (git · GitLab)

- Group the author's commit log and MRs by period to build project candidates.
- Traces like reverts, "다시 하향", and closed MRs become trial-and-error stories (first attempt abandoned → new approach).
- If commit messages record the problem, design, and trade-offs, use them as evidence directly.
- Keep MR counts, repository counts, and client names out of the resume (unless the user decides otherwise).
- Interpretations inferred from commits and diffs (why it was done) must be marked "확인 필요" and confirmed by the user.

## Pre-submission checklist

- [ ] Summary, skills, lead project on page 1
- [ ] At most 5 projects, 3–4 bullets, each bullet within one and a half lines
- [ ] Before/after number + cause for every result
- [ ] No motivation statement, no placeholders, no "확인 필요"
- [ ] Tech stack overlaps the posting, no proficiency markers
- [ ] 1–2 links each, all open
- [ ] Target page count, no heading orphaned at a page end
- [ ] 15-second scan test with one person who has hired ("뭐가 기억에 남나")
