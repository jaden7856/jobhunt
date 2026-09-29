# data/

사용자별 자료가 쌓이는 곳. 하위 폴더 구조와 README, `*.example.*` 파일만 git에 올라가고 실제 내용은 `.gitignore`로 빠진다.
스킬이 공고를 찾고 평가하고 이력서를 만들 때 이 폴더부터 읽는다. 어떤 정보를 어디에 적는지는 `modes/_shared.md` 3절.

| 폴더 | 무엇을 저장하나 | 파일 예 |
|---|---|---|
| `profile/` | 이름·연락처·학력(헤더에 쓰임), 목표 역할·조건, 1차 선별 요약 | `profile.yaml`, `targets.yaml`, `brief.md` |
| `experience/` | 경험 정리 문서, git 로그 추출본, 프로젝트 후보와 근거, 확인받은 사실 | `project_index.yaml`, `git_<저장소>.md`, `facts.md` |
| `preferences/` | 강조할 강점, 뺄 내용, 페이지 수, 연차 표기, 섹션 추가·삭제 같은 요구사항 | `standing.md`, `<공고>_requests.md` |
| `portfolio/` | GitHub·블로그 주소, 글 목록, 링크 확인 결과, 프로젝트별로 고른 글 | `portfolio.yaml` |
| `search/` | 검색 조건·우선 기업, 공고 대기함, 본 공고 기록, 제외 회사 | `sources.yaml`, `pipeline.md`, `scan-history.tsv`, `blacklist.md` |
| `job_postings/` | 공고 원문과 평가(요구사항 대응표, 맞춤 계획) | `2026-10-01_회사_포지션.md`, `….eval.md` |
| `applications/` | 지원 현황표 | `tracker.md` |
| `resumes/` | 확정된 이력서 yaml. 기본본 + 회사별 맞춤본 | `base_service.yaml`, `토스_service.yaml` |
| `output/` | 빌드한 PDF·PNG·HTML | `이름_직무_버전.pdf` |

저장 규칙
- 사용자가 새로 알려준 사실·결정은 그 성격에 맞는 폴더에 바로 적는다. 같은 파일이 있으면 덧붙이고, 날짜를 남긴다.
- 한 번만 적용할 요청(이번 공고만)은 `preferences/<공고>_requests.md`, 계속 적용할 결정은 `preferences/standing.md`.
- 추론으로 채운 내용은 `[확인 필요]` 를 붙여 두고, 확인되면 지운다.
