---
name: resume-pdf-builder
description: Finds Korean developer job postings (Wanted, Jumpit, LinkedIn, Saramin, JobKorea, company career sites), scores them against the user's experience and conditions, and builds a resume A4 PDF tailored to each posting. Use for finding postings, evaluating a posting, a company-specific resume, editing or rebuilding a resume, and logging application status.
---

# Find postings → evaluate → tailored resume

Resume content lives in yaml; layout and build are `scripts/render.py`. All personal data lives in `data/` and never goes to git.
Save every fact, requirement, or judgment correction the user gives into the matching file under `data/` right away, so the next run reuses it. Screening and tailoring get sharper with use.
The workflow and personalization layout follow career-ops (MIT). Full design: `docs/ROADMAP.md`.

**Language.** These instruction files are English for the agent only. Everything the user sees is Korean: replies, questions, reports, tables and their headings, files written under `data/`, and resume text. Korean strings quoted in these files (state values, section headings, templates, example sentences) are used verbatim.

## Repository

The folder holding this SKILL.md is the repository root (`scripts/setup.sh` links the skill folder to the repository). Every path and command below is relative to the repository root.

```
SKILL.md                    this file (routes to modes)
modes/_shared.md            shared rules, sources of truth, data/ file map, Korean hiring terms (always read first)
modes/onboard.md            first-time setup, personalization file check
modes/scan.md               finding postings and first-pass screening
modes/evaluate.md           evaluating a posting (gates, requirement map, tailoring plan)
modes/tailor.md             writing, building, and reviewing a tailored resume
modes/track.md              application tracker
scripts/render.py           yaml → HTML → PDF + PNG, designs A/B/C, runs post-build checks
scripts/check.py            page count · orphaned headings · links · placeholders · style checks
scripts/check_links.py      link reachability (stdlib only, runs anywhere)
scripts/git_log.sh          author-filtered commit log from a local git repository
scripts/setup.sh            skill link (~/.claude/skills) + Playwright Chromium, fonts (Pretendard, Noto Sans/Serif CJK KR), poppler
scripts/scan.py             posting collection (Wanted · Jumpit · LinkedIn · Greenhouse · Toss · NHN · Kakao · Naver · Baemin · LINE · greetinghr · ninehire) → filters → pipeline.md
scripts/alive.py            closing check for tracked postings
scripts/tracker.py          application log (add/set) and combined report table (report)
scripts/score.py            posting score (line-level judgment file → per-item scores)
scripts/discover.py         company discovery (tech blogs · GitHub · Wanted · known companies → career site and ATS detection → sources.yaml)
scripts/weekly.sh           the LLM-free part of the weekly scan (scan → alive → report)
scripts/providers/          per-site collectors
references/sources.md       per-site collection method (endpoints, body location, closing check)
references/scoring.md       posting scoring (classification, calculation, calibration)
references/company_seed.yaml default candidates for company discovery (well-known Korean dev companies)
references/yaml_schema.md   resume yaml format
references/writing_rules.md sentence rules and how to check them
references/style_rules.yaml banned words · translationese · symbol limits (read by check.py)
references/resume_guide.md  general resume rules (project count, numbers, links …)
examples/example.yaml       fictional example person
docs/ROADMAP.md             design and stages
data/                       user data (git-ignored; only the structure is committed)
  profile/ experience/ preferences/ portfolio/ search/ job_postings/ applications/ resumes/ output/
```

## On start

1. Go to the repository root. If the skill folder is a link, that is the folder it points to. If this environment cannot reach the folder (a cloud workspace, say), ask the user to connect the repository folder; if there is no repository, ask for its GitHub URL and clone it.
2. Read `modes/_shared.md`.
3. Run the session-start check in `modes/onboard.md`. Tell the user about any missing personalization file.
4. Read `data/preferences/standing.md`. Anything already decided there is settled; use it without asking again.
5. If this session is attached to a Claude project, also check the project's finalized yaml and guide documents.

## Modes

Read the mode file that matches the request and follow it.

| Example request | Mode |
|---|---|
| "처음 설정", "내 조건 바꿀래", "목표 역할 추가" | `modes/onboard.md` |
| "공고 찾아줘", "새 공고 있어?", "주간 스캔" | `modes/scan.md` (run `bash scripts/weekly.sh` first) |
| "회사 더 찾아줘", "수집 회사 넓혀줘" | `modes/scan.md` step 0 (`scripts/discover.py`) |
| "새로 수집한 공고 선별해줘" | `modes/scan.md` from step 4 |
| "공고 현황 보여줘", "표로 보여줘" | output of `python3 scripts/tracker.py report --alive` |
| a posting URL or body, "이 공고 어때?", "평가해줘" | `modes/evaluate.md` |
| "이 공고용 이력서 만들어줘", "이력서 고쳐줘", "다시 빌드" | `modes/tailor.md` (given only a posting with no evaluation, offer evaluate first) |
| "지원했어", "서류 붙었어", "떨어졌어", "지원 현황" | `modes/track.md` (`scripts/tracker.py`) |
| "prep {회사}", "면접 준비" | block F of that posting's `.eval.md` + the "자주 쓰는 흐름" section of `standing.md` |

Given a posting URL, continue evaluate → tailor (if the user decides to apply) → track, with user confirmation between steps.
