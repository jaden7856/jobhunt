# Per-site collection methods

Only site-wide facts go here (endpoints, body location, closing check). Personal search conditions live in `data/search/sources.yaml`.
Date every measurement. When a format changes, fix it here and update the date.
Handled automatically by `scripts/providers/`: Wanted, Jumpit, LinkedIn, Greenhouse, Toss, NHN, Kakao, the Naver group, Woowa Brothers, LINE, greetinghr (sites with `__NEXT_DATA__`, including ones on a company domain), ninehire, hiworks recruit. The agent collects the rest by hand following this document.
To widen the set of companies collected, see "Company discovery" below.

## Common rules

- **Fetch the whole job family and judge by body.** Narrowing the search to one language (e.g. Go) drops good postings that name no language. Fetch by job-family words (server, backend, platform, DevOps, Systems) and judge language and years conditions from the qualification text at evaluation time. (After the 2026-09-23 miss)
- **Space out requests.** 1s+ per site, 1.5s+ for LinkedIn. On 429, stop and leave it for the next run.
- **Judge closing from the detail page or detail API.** "Not in the public list" does not mean closed (during umbrella postings, sub-positions are hidden from the list).
- **Search-engine `site:` queries are a fallback.** They often come back empty or list-pages only. Prefer the JSON paths below.
- Use unofficial endpoints for personal use only, and when a response shape changes, report it as "응답 형식 변경" so it never silently turns into 0 results.

## Job platforms

| Site | List | Detail (qualification text) | Measured |
|---|---|---|---|
| Wanted | `https://www.wanted.co.kr/api/chaos/navigation/v1/results?job_group_id=518&job_ids=872\|674\|10110&years={연차}` (872 server developer · 674 DevOps · 10110 software engineer — some backend postings are tagged only 10110, 2026-09-30) or `/api/v4/jobs?country=kr&tag_type_ids=872&job_sort=job.latest_order&limit=..&offset=..` | `/api/v4/jobs/{id}` → `job.detail.{requirements, main_tasks, preferred_points, intro, benefits}`; closing is `job.status` (active/close); salary is `annual_from/to`. Keyword search (`/api/chaos/search/v1/results?query=`) returns few results, so use the list API | 2026-09-29 |
| Jumpit | `https://jumpit-api.saramin.co.kr/api/positions?keyword=..&page=N` (`jobCategory=1` server/backend) | `/api/position/{id}` → `qualifications`. Filter past postings by the deadline field | 2026-09-29 |
| Saramin | search page `/zf_user/search/recruit?searchword=..` (HTML) | fetch `/zf_user/jobs/relay/view-detail?rec_idx={id}&rec_seq=0`, not `relay/view`, to get the body | 2026-09-23 |
| JobKorea | search page `/Search/?stext=..` (HTML; a list, not postings) | `/Recruit/GI_Read/{id}`. Regex-extracting the deadline from the page catches the wrong text (2026-09-01) → read the application period in the body directly | 2026-09-23 |
| LinkedIn | `linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=..&location=Seoul, South Korea&f_TPR=r2592000&start=N` | `/jobs-guest/jobs/api/jobPosting/{id}`. Rebuilding a `jobs/view/{id}` URL from the numeric ID makes everything look closed (2026-09-01) → use the full URL from the search result as is. Keep Korean JDs only (judged by the Hangul ratio of the body). 429s are frequent right after collection; wait 10s and retry. Closed if the detail is 404 or says "No longer accepting applications" | 2026-09-29 |
| Remember | `https://career.rememberapp.co.kr/job/postings?search=..` (open and read in a browser; not indexed by search engines) | browser | 2026-09-01 |
| Programmers Career | domain gone | — | 2026-09-29 |

Saramin's official OpenAPI (`oapi.saramin.co.kr`) needs an access key.

## Company career sites

| Company | Method | Notes | Measured |
|---|---|---|---|
| Companies on Greenhouse (Daangn, Coupang, Krafton, etc.) | `https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true` | official public API | 2026-09-29 |
| Toss (all affiliates) | list `https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs` | the body is not `content` but the `metadata` field whose name contains "Job Description" (markdown). Umbrella postings like "집중 채용": expand every sub-position link in the body (`grnh.se/…`, `job_id=`) and judge each; usually only one sub-position can be applied to. Closing: `toss.im/career/job-detail?job_id=` returning 200 with the position name in `<title>` means active, 404 means closed. HTML body is the "합류하게 될 팀 / 이런 분과 함께하고 싶어요" section after `</head>` | 2026-09-23 |
| NHN | list `GET https://careers.nhn.com/v1/job-postings` (latest 30 only), detail `GET /v1/job-postings/{id}` | active when `finishYn=N` · `postingYn=Y` · `applicationUseYn=Y`. Check tracked postings with the detail API, not the list. `/preview/…` URLs may be referral or conversion postings | 2026-09-23 |
| Naver group (Naver · Naver Cloud · Naver Financial · Naver Webtoon) | `https://{recruit.navercorp.com · recruit.navercloudcorp.com · recruit.naverfincorp.com · recruit.webtoonscorp.com}/rcrt/loadJobList.do?annoId=&sw=&…&firstIndex=N` (JSON, 10 per page, `totalSize`) → body in `detail_wrap` of `/rcrt/view.do?annoId={id}` | one posting holds several roles as sections; judge only the matching section. For Naver Cloud the hiring system is `recruit.navercloudcorp.com`, not the intro site `career.navercloudcorp.com` | 2026-09-30 |
| Woowa Brothers | list `https://career.woowahan.com/w1/recruits?page=N&size=50` (JSON), body in `recruitContents` of `/w1/recruits/{recruitNumber}`, posting URL `/recruitment/{recruitNumber}/detail` | a missing posting returns `code: 9002` | 2026-09-30 |
| LINE | `allStrapiJobs` in `https://careers.linecorp.com/page-data/ko/jobs/page-data.json` (worldwide) → keep only city Seoul · Bundang · Gwacheon with `publish: true`; body in `strapiJobs.content` of `/page-data/ko/jobs/{id}/page-data.json` | `publish: false` means the posting ended | 2026-09-30 |
| Dunamu | `/detail/{n}` links in the `careers.dunamu.com` main HTML | few postings | 2026-09-23 |
| SK Telecom | `skcareers.com/Recruit?corpCode=10005` | `careers.sktelecom.com` only shows a migration notice | 2026-09-23 |
| Kakao | `https://careers.kakao.com/public/api/job-list?part=TECHNOLOGY&company=ALL&page=N` | affiliate (`S-`) postings have empty qualifications (external site). Affiliates collected from their own career site go in `skip_companies` (`companyName` values) so they aren't queued twice | 2026-09-30 |
| greetinghr (`*.career.greetinghr.com`, or a company domain like `recruit.회사.com`) | posting list in query `["openings"]` of `__NEXT_DATA__` in `{career site}/ko/home` or the landing HTML; body at `/ko/o/{id}`. On a company domain, set `ats: greetinghr` in `sources.yaml` | bucketplace · kakaoenterprise have no `__NEXT_DATA__`; read them in a browser (kakaopay works again as of 2026-09-30). Closing check recognizes company-domain posting URLs by the `/ko/o/{id}` path. Before adding a company-domain greetinghr site, check it isn't the same workspace as one already collected under `*.career.greetinghr.com` (29CM's musinsacareers.com is MUSINSA's). A "powered by greetinghr" link at the bottom (`www.greetinghr.com/?utm_source=career_page`) means the page is a greetinghr career site | 2026-09-30 |
| ninehire (`*.ninehire.site`, or a company domain) | `homepageProps.homepage.companyId` from the landing page's `__NEXT_DATA__` → `https://api.ninehire.com/identity-access/homepage/recruitments?companyId={id}&page=N&countPerPage=50` (`status: in_progress` only). Body is `pageProps.jobPosting.content` (HTML) in `__NEXT_DATA__` of `{career site}/job_posting/{addressKey}` | years in `career.range.{over, below}` | 2026-09-30 |
| hiworks recruit (`recruit.회사.com/recruit/jobs`, e.g. Gabia) | `recruit-api.gabiaoffice.hiworks.com/v1/career-site`: `tokens/site-information` with header `x-career-site-domain: 회사.com` → `office_no`; list `offices/{office_no}/announces`; body `…/announces/{id}` `description` (HTML, sometimes one image). Set `ats: hiworks` | missing id → 404. Found by reading the page's JS (`.GET("/v1/career-site/…")`) | 2026-09-30 |
| recruiter.co.kr (`*.recruiter.co.kr`) | browser | — | unverified |
| roundhr (`*.recruit.roundhr.com`) | browser | — | unverified |

When adding a company: first check for a Greenhouse · Lever · Ashby public API; otherwise add it to `data/search/sources.yaml` only after confirming the career site URL opens. Unverified URLs stay out.

## Company discovery

Find companies that rarely post on job boards and post only on their own career site (large or well-known companies), and add them to `companies` in `sources.yaml`. `scripts/discover.py`.

**Sources**

| Source | What it gives | How |
|---|---|---|
| `references/company_seed.yaml` | well-known dev companies (big-tech IT · platform · fintech · games · cloud · AI) and homepages | list kept in the repo. Personal additions go in `data/search/company_seed.yaml` |
| [awesome-korean-techblog](https://github.com/maczniak/awesome-korean-techblog) | companies running a tech blog (dev-culture signal) | README "기업 블로그" section |
| [korea-devculture](https://github.com/channy/korea-devculture) | companies running a GitHub org, with follower counts | `github.json` |
| Wanted company info | for companies that posted dev jobs: salary tier (연봉상위 1% · 6~10% · 11~20%), headcount band, founding year, homepage | `company.id` from the list API → `company_tags`, `detail.link` of `/api/v4/companies/{id}` |

**Not used:** JobPlanet and Kreditjob block all crawlers in `robots.txt` (`Disallow: /`), and Catch blocks company pages (`/Company`). A person browsing them and writing into `company_seed.yaml` is fine.

**Score (recognition · size):** salary top 1% 3.5 · 6–10% 2.0 · 11–20% 1.0; headcount 1,001+ 2.0 · 301–1,000 1.5 · 51–300 0.5; known-company list 2.0; tech blog 1.5; GitHub org 1.0 (+0.5 at 100+ followers). By default probe at 2.5+. `promote` adds auto-collected companies (verified ATS) at 2.5+ and browser-only ones at 4.0+, since each browser site costs manual work every scan. Companies in the known-company list are added regardless of score: firms that post only on their own site have no Wanted salary/headcount data, so their score runs low exactly where they matter most.

**Finding the career site (probe):** (Python 3.9 urllib doesn't follow 308 redirects, so `jobkit.http_get` handles them itself.) Find a "채용 · Careers · Recruit · Jobs" link on the homepage, open it, and identify the ATS from URL and HTML (greetinghr · ninehire · Greenhouse · Lever · recruiter.co.kr · Notion · in-house). For an ATS the scripts handle, actually fetch the posting list (`verified: posting count`) and add only verified ones to automatic collection. The rest get `method: browser`.

```bash
python3 scripts/discover.py collect            # gather candidates (~20 min with Wanted, seconds with --skip-wanted)
python3 scripts/discover.py probe --top 150    # find career sites for top-scoring candidates
python3 scripts/discover.py report             # candidate table
python3 scripts/discover.py promote --dry-run  # preview companies to add → after user confirmation, run without --dry-run
```

**Not found from the homepage:** for sites whose links are drawn by script or that block bots (403), list them with `discover.py missing`, find the career site URL with Firecrawl (`firecrawl_search "{회사} 채용"`, or WebSearch without it; the free plan returns 429 past ~3 requests at once, so send 2–3 at a time), and feed a `회사<TAB>URL<TAB>출처` file to `discover.py set <file>`. The script does ATS detection and list verification. For a company with no career site, put `-` in the URL slot.

**Sweeping browser-only companies with Firecrawl:** `firecrawl_scrape` with `formats: ["json"]` on a careers landing page often **invents postings** (example.com URLs, past deadlines, or real posting ids paired with the wrong title). Prefer markdown (1 credit) or `firecrawl_map` to find the list page, then check every posting URL by fetching its body and comparing the title before judging. If a company turns out to use greetinghr or ninehire, try `providers.greetinghr/ninehire.collect` on it and switch it to `ats:` in `sources.yaml` instead of sweeping it by hand again.

`status` (후보 · 추가 · 제외) and `memo` in `data/search/companies.yaml` may be edited by hand and survive the next run. Skip companies the user won't apply to (`blacklist.md`) and affiliates that use a career site already being collected.
