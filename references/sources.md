# 채용 사이트별 수집 방법

사이트 공통 사실만 적는다(엔드포인트, 본문 위치, 마감 판정). 개인 검색 조건은 `data/search/sources.yaml`.
실측 날짜를 붙인다. 형식이 바뀌면 여기를 고치고 날짜를 갱신한다.
`scripts/providers/`가 자동으로 다루는 곳: 원티드, 점핏, Greenhouse, 토스, NHN, 카카오, greetinghr(`__NEXT_DATA__` 있는 곳). 나머지는 Claude가 이 문서대로 직접 수집한다.

## 공통 규칙

- **직군 전체를 받고 본문으로 판정한다.** 검색어를 특정 언어(예: Go)로 좁히면 언어를 특정하지 않은 좋은 공고가 빠진다. 서버·백엔드·플랫폼·DevOps·Systems 같은 직군어로 받고, 언어·연차 조건은 평가 단계에서 자격요건 본문으로 판정한다. (2026-09-23 누락 사고 후)
- **요청 간격을 둔다.** 같은 사이트에 1초 이상, LinkedIn은 1.5초 이상. 429가 나면 멈추고 다음 실행으로 넘긴다.
- **마감 판정은 상세 페이지·상세 API로.** "공개 목록에 없다"는 마감이 아니다(우산 공고 기간에는 하위 포지션이 목록에서 숨겨진다).
- **검색엔진 `site:` 검색은 보조 수단.** 결과가 비거나 목록 페이지만 나오는 경우가 많다. 가능하면 아래 JSON 경로를 쓴다.
- 비공식 엔드포인트는 개인 용도로만 쓰고, 응답 형식이 바뀌면 조용히 0건이 되지 않도록 "응답 형식 변경"으로 보고한다.

## 채용 플랫폼

| 사이트 | 목록 | 상세 (자격요건 본문) | 실측 |
|---|---|---|---|
| 원티드 | `https://www.wanted.co.kr/api/chaos/navigation/v1/results?job_group_id=518&job_ids=872\|674&years=5` 또는 `/api/v4/jobs?country=kr&tag_type_ids=872&job_sort=job.latest_order&limit=..&offset=..` | `/api/v4/jobs/{id}` → `job.detail.{requirements, main_tasks, preferred_points, intro, benefits}`, 마감은 `job.status`(active/close), 연봉은 `annual_from/to`. 키워드 검색(`/api/chaos/search/v1/results?query=`)은 결과가 적어 목록 API를 쓴다 | 2026-09-29 |
| 점핏 | `https://jumpit-api.saramin.co.kr/api/positions?keyword=..&page=N` (`jobCategory=1` 서버/백엔드) | `/api/position/{id}` → `qualifications`. 마감일 필드로 지난 공고를 거른다 | 2026-09-29 |
| 사람인 | 검색 페이지 `/zf_user/search/recruit?searchword=..` (HTML) | `relay/view`가 아니라 `/zf_user/jobs/relay/view-detail?rec_idx={id}&rec_seq=0` 을 받아야 본문이 나온다 | 2026-09-23 |
| 잡코리아 | 검색 페이지 `/Search/?stext=..` (HTML, 목록일 뿐 공고 아님) | `/Recruit/GI_Read/{id}`. 페이지에서 마감일을 정규식으로 뽑으면 엉뚱한 문구가 잡힌다(2026-09-01) → 본문의 접수 기간을 직접 읽는다 | 2026-09-23 |
| LinkedIn | `linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=..&location=Seoul, South Korea&f_TPR=r2592000&start=N` | `/jobs-guest/jobs/api/jobPosting/{id}`. 숫자 ID만으로 `jobs/view/{id}` URL을 다시 만들면 전부 마감처럼 보인다(2026-09-01) → 검색 결과의 전체 URL을 그대로 쓴다. 한국어 JD만 채택 | 2026-09-23 |
| 리멤버 | `https://career.rememberapp.co.kr/job/postings?search=..` (브라우저로 열어 읽음, 검색엔진 색인 없음) | 브라우저 | 2026-09-01 |
| 프로그래머스 커리어 | 도메인 없음 | — | 2026-09-29 |

사람인 공식 OpenAPI(`oapi.saramin.co.kr`)는 접근 키가 필요하다.

## 기업 채용 사이트

| 회사 | 방법 | 주의 | 실측 |
|---|---|---|---|
| Greenhouse 쓰는 회사 (당근, 쿠팡, 크래프톤 등) | `https://boards-api.greenhouse.io/v1/boards/{보드}/jobs?content=true` | 공식 공개 API | 2026-09-29 |
| 토스 (전 계열사) | 목록 `https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs` | 본문은 `content`가 아니라 `metadata` 중 이름에 "Job Description"이 들어간 필드(마크다운). "집중 채용" 같은 우산 공고는 본문의 하위 포지션 링크(`grnh.se/…`, `job_id=`)를 모두 펼쳐 각각 판정하고, 보통 하위 중 1개만 지원 가능. 마감 판정: `toss.im/career/job-detail?job_id=` 가 200이고 `<title>`에 포지션명이 있으면 활성, 404면 마감. HTML 본문은 `</head>` 뒤 "합류하게 될 팀 / 이런 분과 함께하고 싶어요" 섹션 | 2026-09-23 |
| NHN | 목록 `GET https://careers.nhn.com/v1/job-postings` (최신 30건만), 상세 `GET /v1/job-postings/{id}` | `finishYn=N`·`postingYn=Y`·`applicationUseYn=Y`면 활성. 추적 중인 공고는 목록이 아니라 상세 API로 확인. `/preview/…` URL은 추천·전환형일 수 있음 | 2026-09-23 |
| 네이버 | `recruit.navercorp.com/rcrt/loadJobList.do?…&firstIndex=0` (JSON, `annoId`) → `/rcrt/view.do?annoId={id}` | 한 공고에 여러 직무가 섹션으로 들어 있으니 해당 섹션만 판정 | 2026-09-23 |
| 두나무 | `careers.dunamu.com` 메인 HTML의 `/detail/{n}` 링크 | 공고 수 적음 | 2026-09-23 |
| SK텔레콤 | `skcareers.com/Recruit?corpCode=10005` | `careers.sktelecom.com`은 이관 안내만 있음 | 2026-09-23 |
| 카카오 | `https://careers.kakao.com/public/api/job-list?part=TECHNOLOGY&company=ALL&page=N` | 공동체(`S-`) 공고는 자격요건이 비어 있음(외부 사이트) | 2026-09-23 |
| greetinghr (`*.career.greetinghr.com`) | `https://{slug}.career.greetinghr.com/ko/home` HTML의 `__NEXT_DATA__`에 공고 목록, 본문은 `/ko/o/{id}` | bucketplace·kakaopay·kakaoenterprise는 `__NEXT_DATA__`가 없어 브라우저로 읽는다 | 2026-09-23 |
| roundhr (`*.recruit.roundhr.com`) | 브라우저 | — | 미확인 |

새 회사를 추가할 때: Greenhouse·Lever·Ashby 공개 API가 있는지 먼저 확인하고, 없으면 채용 사이트 URL이 열리는지 확인한 뒤에만 `data/search/sources.yaml`에 넣는다. 확인하지 않은 URL은 넣지 않는다.
