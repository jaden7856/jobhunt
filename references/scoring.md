# Posting scoring

First-pass screening (`modes/scan.md` step 4) and full evaluation (`modes/evaluate.md`) use the same criteria.
**Claude classifies the posting line by line; `scripts/score.py` computes the score; Claude then reviews the result against the whole posting (`references/judgment.md`).** The same classification always yields the same score, and the record shows which item cost points.

The score has two layers, kept apart on purpose:

| Layer | Where | What it decides |
|---|---|---|
| **Common rules** | constants in `scripts/score.py`, this file | the band (how much of the required and preferred lines the user meets), caps for core gaps and unknown domains. Same for every user; never moved by personal settings |
| **Personal preferences** | `scoring` in `data/profile/targets.yaml` | which work the user wants or avoids (`prefer_work`, `avoid_work`, `avoid_cap`), bonuses (`signals`, `priority_bonus`). Orders postings *inside* a band |

## Why it changed (2026-09-30)

Problems with the old method (estimating role 30 · requirements 30 · narrative 15 · location 15 · compensation 10 in one pass):

| Problem | Effect |
|---|---|
| location and compensation were 25%, near-full marks whenever the conditions matched | every posting started around 3.5 |
| an unmet required item ended as one "gap" line | postings missing required items passed |
| only keyword overlap with requirements counted | high scores even when the daily work pointed away from the desired direction |
| priority companies passed regardless of score | poorly fitting postings rose to the top |

## Steps

1. Get the body (`data/search/inbox/*.md`).
2. Scaffold: `python3 scripts/score.py init <body.md> -o data/search/judgments/<source>_<id>.yaml`
   - A draft with main tasks, qualifications, and preferred items split into lines. Delete lines from the wrong section (culture fit, stack listings, benefits) and add missing ones.
3. Fill in the blanks by the criteria below. For lines that need evidence, write the user's experience in one line under `why:` (evidence only from primary material such as `data/experience/`).
4. Check whether the posting resembles a calibration case in `data/profile/calibration.md`.
5. Score with `python3 scripts/score.py data/search/judgments/<file>.yaml`.

## Judgment file

```yaml
url: https://...
company: 가나다
title: Backend Engineer
gates: { location: pass, language: pass, stack: pass, years: pass, employment: pass, comp: pass }
gate_note: "판정 근거가 된 공고 문장"
work:        # one line per main task
  - { line: "정산 데이터 파이프라인 개발", fit: adjacent, why: "정산 배치 재작성" }
required:    # one line per qualification
  - { line: "Kotlin 또는 Java 서버 개발 3년 이상", met: "yes" }
  - { line: "RabbitMQ 운영 경험", met: "no", gap: bridge, why: "Kafka 주문 이벤트 도입으로 설명" }
preferred:   # one line per preferred item
  - { line: "Kafka 운영", met: partial }
  - { line: "대규모 결제 시스템 설계", met: "no", key: true }   # key: a core skill for this position
review: { delta: -0.3, why: "시니어 범위(전사 적용 주도)는 해 본 적 없음" }   # optional agent adjustment, see judgment.md
direction: { primary: payment_settlement, secondary: [large_scale_product] }
domain_new: ""           # core domain of the team's product the user has never worked in (caps at 3.9)
signals: [self_service]
priority: false          # priority company (sources.yaml priority: true)
note: "한 줄 근거"
```

`yes`/`no` may be quoted or not (the script normalizes them).

## Classification

**gates** (`location` · `gates` · `compensation` in `targets.yaml`): `pass` / `fail` / `unclear`. Any `fail` → excluded with no score. Location and compensation are judged here only.

**work.fit** — has the user done this work?

| Value | Meaning | Score |
|---|---|---|
| `done` | has done the same work | 5.0 |
| `adjacent` | has done similar work and can connect it in an interview | 3.5 |
| `new` | never done it | 1.5 |

**required.met** — `yes` 5.0 · `partial` 3.5 · `no` by gap type

| gap | Meaning | Score | Cap |
|---|---|---|---|
| `bridge` | a technical gap similar experience explains (e.g. Kafka ↔ RabbitMQ, AWS ↔ GCP) | 2.5 | none |
| `core` | the career or core domain itself is missing (e.g. N years in payments required, expert in a field never touched) | 1.0 | 3.4 with one, 2.9 with two |
| `core` + `alt: true` | a core gap, but the posting accepts substitute experience ("또는 이에 준하는 경험") | 1.75 | above cap +0.2 (when every core gap is alt) |

- Personality and attitude lines ("서비스에 애착", "기술 도전을 즐김", "소통을 잘함") stay out of required. Classify only verifiable experience and skills.
- Which requirements are core, as decided by the user, is in the `scoring` comments of `targets.yaml` and in `data/profile/calibration.md`. Follow them.

**preferred.met** — average of `yes` 1 · `partial` 0.5 · `no` 0, mapped to 1–5 (3 when there are none). Personality and attitude lines stay out.

**preferred.key** — `true` when the line is a core technical skill or requirement *of this position*, even though the posting files it under 우대: the thing the team builds on every day (vLLM/KV cache for an LLM serving platform, Terraform/AWS for a cloud infra team, RTB for a bidder team). Generic lines (Kafka, DDD, mentoring, agile, English) are not key unless the position is about them. Mark at most 2–3 lines; when unsure, read the main tasks: a preferred line that names what most main tasks need is key.

**direction** — is the daily work in this seat the desired direction? `primary` is what the team mainly builds; `secondary` is side work.
- Values are keys of `scoring.prefer_work` · `scoring.avoid_work` in `targets.yaml`; `other` if neither.
- primary: preferred 5.0 · other 3.0 · avoided 1.5. Each secondary: preferred +0.5 · avoided −0.5 (within 1–5).
- Judge by **main tasks and team description**, not requirement sentences. Generic lines found everywhere ("문서화", "공통 모듈", "테스트·배포") never set the direction.

**domain_new** — a specialised technical domain that the team's product is built around and that the main work lines depend on, when the user has never worked in it (e.g. "LLM 서빙·분산 추론", ML training, game engines, compilers, codecs). Write it in a few Korean words; leave it empty otherwise. Business domains (commerce, payments, securities, …) where general backend skills carry over do not count; a gap there is a required `core` gap or nothing. It caps the score at 3.9 (`domain_new_cap`) even when an "A, B, C 중 하나" requirement is met through a neighbouring skill, because the daily work still sits in the unknown domain. If the user only built what runs next to that domain (a K8s operator that deploys inference servers, not the inference itself), the domain is still new.

**signals** — only keys present in `scoring.signals` of `targets.yaml`, and only what the posting shows (personal layer).

**review** — optional agent adjustment after the script, with a reason: `delta` −1.0 … +0.3, never above the band ceiling. When and how: `references/judgment.md`.

## Calculation

**1. Band (common).** "Required met" means no required line is `no` (`partial` counts as met). "Preferred met" counts `yes` 1 · `partial` 0.5.

| Band | Range | Condition |
|---|---|---|
| S | 4.9 – 5.0 | every required and every preferred line `yes` |
| A | 4.5 – 4.8 | required met, and every `key` preferred line `yes` (with no key line: preferred ≥ 75%) |
| B | 4.0 – 4.4 | required met, no key line missed, preferred ≥ 50% or the posting lists no preferred lines |
| C | ≤ 3.9 | a required line not met, **or a key preferred line not met**, or preferred < 50%, or half or more of the main tasks are `new` |

When half or more of the main tasks are `new`, a posting stays out of S/A/B even when generic requirement sentences all read "met".

**2. Position inside the band.**

```
raw = work×0.30 + required×0.30 + preferred×0.10 + direction×0.30 + signals (+ priority bonus)
S/A/B: raw 3.5 … 5.5 spread evenly over the band range      C: raw below 3.5 as is, 3.5 … 5.5 spread over 3.5 … 3.9
```

Direction and signals come from personal preferences, so they reorder postings inside a band but never lift one into a higher band.

**3. Caps (common, then personal).** core gaps in required: 3.4 with one, 2.9 with two (+0.2 when every core gap is `alt`) · work fit below 2.5 → 3.9 · `domain_new` → 3.9 · personal: `direction.primary` is an `avoid_work` key → `avoid_cap`.

**4. Review.** `review.delta` from the judgment file (−1.0 … +0.3, not above the band ceiling). Round to one decimal.

Change personal preferences in `scoring` of `targets.yaml`. Change common rules only in `scripts/score.py` together with this file.

| Score | Verdict | pipeline label |
|---|---|---|
| 4.0+ | 지원 권장 | PASS |
| 3.5 – 3.9 | 지원 고려 | PASS |
| 3.0 – 3.4 | 보류 | MARGINAL |
| below 3.0 | 제외 | FAIL |

## Calibration

When the user says "이 판정은 틀렸다":
1. Find which classification was wrong in that posting's judgment file and fix it.
2. If the classification is right but the score is off: a personal taste → `scoring` in `targets.yaml` (preferred work, signals); a rule every user should share → `scripts/score.py` and this file.
3. Add one line to `data/profile/calibration.md`: posting, previous verdict, user's judgment, new score, lesson.
4. If a rule changed, recompute everything with `python3 scripts/score.py data/search/judgments/*.yaml` and show postings whose ranking flipped.
