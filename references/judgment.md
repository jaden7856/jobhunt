# Agent judgment beyond the scripts

The scripts give a reproducible baseline: `scan.py` collects, `score.py` computes. They only see what was written into files. This guide is what the agent (Claude, Codex, Grok, any) adds on top: reading the whole posting and the market like a person would, then **writing the judgment down** so another agent or the user can repeat or dispute it. Nothing here needs a specific AI vendor; Firecrawl and browsers are optional helpers.

Order of authority: the user's words → `data/profile/calibration.md` → common rules (`references/scoring.md`) → this guide. A review never undoes a recorded user decision.

## 1. Reviewing a score

Run `score.py` first, then read the full body (team intro, main tasks, required, preferred, stack, process) against the user's proof (`data/profile/brief.md`, `data/experience/`). Ask:

| Question | Typical evidence | Action |
|---|---|---|
| Is the seat above the user's level? | Sr./Staff/Principal/Lead title, "주도", "company-wide", "조직 전체", years well above the user's, ownership of a whole platform | `review.delta` −0.3 … −0.5, or mark the matching required line `gap: core` if it is a stated requirement |
| What does the hiring side weigh most? | a skill named in both required and preferred, or in the team intro and most main tasks | mark that preferred line `key: true` |
| Does the daily work sit in a domain the user never touched? | the product is built around a specialised technology (LLM serving, game engine, blockchain node, codecs) | `domain_new` (scoring.md) |
| Are there conditions the gates missed? | 상주, 납품 조직, 포괄임금+야근, the same posting reposted for months | a signal if one exists, otherwise `review.delta` −0.2 … −0.5 |
| Is there a concrete upside the rules cannot see? | the posting explicitly welcomes other stacks and offers ramp-up; the team is small but the scope matches the user's proof exactly | `review.delta` +0.1 … +0.3 |

Rules:
- Write `review: { delta: <number>, why: "<공고 문장 or fact>" }` in the judgment file. `why` quotes or names the posting sentence or the user fact; "느낌상" is not a reason.
- The script limits the delta to −1.0 … +0.3 and never lets it rise above the band ceiling. Personal preferences (B2C, IaC, Go, …) already live in `signals`; do not count them again in a review.
- Prefer fixing the classification (`met`, `gap`, `key`, `fit`) over a review delta when the problem is a specific line. Use the delta for what no single line captures (level, scope, team situation).
- If a review moves a posting across 4.0 / 3.5 / 3.0, say so in the report so the user can check it.
- When the user corrects a verdict, record it in `data/profile/calibration.md` and decide whether the lesson is personal (`targets.yaml`) or common (`scoring.md` + `score.py`).

## 2. Searching beyond the scripts

`scan.py` covers the configured boards and companies. The agent widens the net where the scripts cannot reach, guided by the user's preferences in `brief.md` (for example: look harder at B2C services and at infra teams that work with IaC).

- **Browser-only companies.** Companies in `sources.yaml` without an automatic provider: read their career page (browser or `firecrawl_scrape` in markdown; JSON extraction invents posting IDs, see `references/sources.md`). If the page turns out to use greetinghr/ninehire/etc., switch the company to that provider instead of scraping again.
- **New companies.** Tech blogs, funding news, conference sponsors, and the user's targets in `brief.md`. Add them with `discover.py set` and `promote`, never by hand-editing `sources.yaml` alone.
- **Titles the filter missed.** Now and then skim `skipped_title` rows in `scan-history.tsv` for unusual titles that are really backend or platform roles; add the wording to `title_filter.positive` instead of rescuing rows one by one.
- **Duplicates and liveness.** Before adding a posting found by hand, check it against `pipeline.md` and `tracker.md` with the company's other spellings (`jobkit.dup_keys`) and confirm it is still open on the company's own page.
- **Write down what was searched.** In the scan report, list the channels checked by hand, what was found, and what could not be read, so the next run does not repeat or skip them.

## 3. Where each judgment is stored

| Judgment | File |
|---|---|
| line classification, `key`, `domain_new`, `review` | `data/search/judgments/<id>.yaml` |
| one-line reason shown in the report | `note` in the same file → `pipeline.md` |
| user corrections and their lesson | `data/profile/calibration.md` |
| personal preferences and weights | `data/profile/targets.yaml` `scoring`, summary in `brief.md` |
| new companies and channels | `data/search/companies.yaml` → `sources.yaml` via `discover.py` |
