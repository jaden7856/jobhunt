---
name: resume-pdf-builder
description: 사용자 자료(경험 문서, git 로그, 기존 이력서)로 개발자 이력서 내용을 정리하고 스위스 그리드 디자인의 A4 PDF와 페이지별 PNG를 만든다. 새 공고용 이력서, 회사별 맞춤본, 이력서 수정·재빌드 요청에 쓴다.
---

# 이력서 PDF 빌드

내용은 `resume.yaml`, 모양과 빌드는 `scripts/render.py`. 개인정보는 코드에 적지 않고 `data/profile/profile.yaml`에서 읽는다.
사용자가 알려 준 사실·요구사항은 `data/` 아래 알맞은 폴더에 바로 저장해서 다음 공고 때 다시 쓴다.

## 저장소

기본 위치: 사용자 맥 `~/Desktop/develop/resume-builder` (GitHub에 올려 관리).

```
SKILL.md                    이 파일
scripts/render.py           yaml → HTML → PDF + PNG, 디자인 A/B/C, 빌드 후 검사 호출
scripts/check.py            페이지 수 · 제목 홀로 남음 · 링크 · 플레이스홀더 · 문체 검사
scripts/check_links.py      링크 접속 확인 (표준 라이브러리만, 어디서나 실행)
scripts/git_log.sh          로컬 git 저장소에서 작성자 기준 커밋 로그 추출
scripts/setup.sh            Playwright Chromium, Noto Sans CJK KR, poppler 설치
references/yaml_schema.md   yaml 형식 (먼저 읽는다)
references/writing_rules.md 문장 규칙과 점검 방법
references/style_rules.yaml 금지어·번역투·기호 한도 (check.py 가 읽음)
references/resume_guide.md  이력서 일반 규칙 (프로젝트 수, 수치, 링크 …)
examples/example.yaml       가상 인물 예시
data/                       사용자 자료 (git 제외, 구조만 올라감)
  profile/ experience/ preferences/ portfolio/ job_postings/ resumes/ output/
```

시작할 때
1. 저장소에 접근한다. 맥 폴더가 연결되어 있지 않으면 `~/Desktop/develop/resume-builder` 접근을 요청한다. 없으면 GitHub 주소를 물어 클론한다.
2. `data/preferences/standing.md`, `data/profile/profile.yaml`, `data/resumes/`, `data/job_postings/`, `data/experience/project_index.yaml`, `data/portfolio/portfolio.yaml`을 읽는다. 이미 정해진 것은 다시 묻지 않는다.
3. 이 세션이 Claude 프로젝트에 연결되어 있으면 프로젝트의 확정 yaml과 가이드 문서도 확인한다.
4. `references/yaml_schema.md`, `references/writing_rules.md`를 읽는다.

## 작동 순서

각 단계는 AskUserQuestion으로 묻는다. 한 번에 1~4문항. 이미 `data/`에 답이 있으면 그 값을 추천안으로 먼저 보여 준다.

### 0. 지원 방향

- 목표 포지션: 인프라·플랫폼 / 서비스 백엔드 / 직접 입력.
- 채용공고 링크나 본문이 있는지.
  - 있으면 공고에서 핵심 요구사항 3~5개를 뽑아 보여 준다. 이 목록으로 프로젝트 순서, SKILLS(공고와의 교집합), 용어를 맞춘다.
  - 공고는 `data/job_postings/YYYY-MM_회사_포지션.md`에 링크·원문·요구사항·용어 대응표와 함께 저장한다.
- 기존 기본본(`data/resumes/base_*.yaml`)이 있으면 가장 가까운 것을 복사해서 시작한다. `cp base_service.yaml 회사_service.yaml`

### 1. 자료 수집 (여러 개 선택)

- 경험을 정리한 문서 / 로컬 git 저장소(작성자 기준 커밋 로그) / GitLab / 기존 이력서(pdf, py, docx).
  - git: `bash scripts/git_log.sh <저장소> "<이메일|이름>" [시작일] [종료일]` → `data/experience/git_<저장소>.md`. revert·하향·폐기 커밋(⟲ 표시)은 시행착오 서사 후보.
  - GitLab: 연결된 GitLab 도구가 있으면 MR·커밋을 작성자 기준으로 읽는다. 없으면 사용자에게 내보낸 목록을 받는다.
  - 기존 이력서: 문구를 yaml로 옮긴다. py 빌드 스크립트면 함수 인자·상수에서 문구를 뽑는다.
- 아무것도 없으면 직접 입력받는다. 이 순서로 묻는다.
  1. 회사·기간·역할 (회사가 여럿이면 최근부터)
  2. 프로젝트마다: 문제 → 원인(어떻게 찾았나) → 선택지(검토한 대안과 버린 이유) → 실행 → 결과 수치(전후)
- 수집이 끝나면 프로젝트 후보 목록을 만든다. 후보마다 한 줄 근거(문서 위치, 커밋·MR, 수치 출처)를 붙인다. `data/experience/project_index.yaml`에 저장.
- 넣을 프로젝트는 최대 5개. 공고 요구사항과 겹치는 정도로 추천안을 먼저 보여 주고(순서 포함), 사용자가 고르게 한다(multiSelect). 빠진 후보 중 한 줄로 남길 것은 OTHER 후보로 둔다.

### 2. 추가 요구사항

- 강조하고 싶은 강점, 빼고 싶은 내용, 목표 페이지 수(기본 2~3), 추가하거나 뺄 섹션, 연차 표기 방식(예: "5년차", "4년 9개월", 표기 안 함).
- 이번 공고에만 적용할 것은 `data/preferences/<공고>_requests.md`, 앞으로도 적용할 것은 `data/preferences/standing.md`에 날짜와 함께 적는다. 어느 쪽인지 애매하면 묻는다.

### 3. 개인 포트폴리오

- GitHub, 블로그 등이 있는지 묻는다.
- 있으면 `portfolio.items`(헤더 연락처와 PORTFOLIO 박스에 들어감)에 넣는다.
- 글 목록을 읽어 프로젝트마다 관련 글 1~2개를 골라 제안하고, 사용자가 확인한 것만 `links`에 넣는다.
- 링크는 실제로 열리는지 확인한다(아래 "링크 확인").
- 없으면 `portfolio`를 비운다 → PORTFOLIO 박스가 빠진다.
- 결과는 `data/portfolio/portfolio.yaml`에 저장(글 목록, 고른 글, 확인 날짜).

### 4. 작성과 빌드

1. 아래 "구조와 디자인", "문장 규칙"대로 yaml을 쓴다. 파일은 `data/resumes/<회사>_<포지션>.yaml`.
2. 추론으로 채운 문장 앞에는 `[확인 필요]`를 붙인다.
3. 빌드:
   ```
   python3 scripts/render.py data/resumes/<파일>.yaml
   ```
   `--design A|C` 로 다른 시안, `--offline` 으로 링크 접속 검사 생략.
   산출물: `data/output/이름_직무_버전.pdf`, `_p1.png …`, `.html`. 파일명은 profile의 `name`, yaml `meta.job`, `meta.version`.
4. 빌드 환경이 없으면 `bash scripts/setup.sh`부터. 사용자 PC 셸에서 빌드가 안 되면 클라우드 작업공간에 `scripts/`, `references/`, yaml, profile만 올려 빌드하고 PDF·PNG를 `data/output/`으로 돌려보낸다.

### 5. 검수와 수정

1. 빌드 후 검사 결과를 정리해 보여 준다(아래 "빌드 후 검사").
2. 문체 자체 점검 결과를 보여 준다. 걸린 문장은 수정 전·후를 나란히 보여 주고 확인받는다.
3. `[확인 필요]` 문장을 모아 하나씩 확인받는다. 확인되면 태그를 지우고 사실은 `data/experience/facts.md`에 적는다.
4. PNG 미리보기를 페이지별로 보여 주고 수정 요청을 받는다. 확정될 때까지 4~5단계를 반복한다.
5. 확정되면:
   - 완성본 PDF를 연결된 폴더(기본 `data/output/`)에 둔다.
   - 확정 yaml을 `data/resumes/`에 두고, Claude 프로젝트가 연결되어 있으면 프로젝트에도 저장한다.
   - `data/job_postings/` 공고 파일에 사용한 yaml 이름과 제출일을 적는다.

## 구조와 디자인

- 디자인 기본은 B안(스위스 그리드, 코발트). 사용자가 원하면 A안(에디토리얼, 세리프+녹색), C안(다크 마스트헤드, 카퍼). yaml `meta.design`.
- 섹션 순서: 헤더 → PORTFOLIO → SUMMARY → SKILLS → EXPERIENCE → PROJECTS → OTHER. 사용자가 추가한 섹션은 `extra_sections`.
- EDUCATION 섹션은 넣지 않는다. 학력은 profile에 참고로만 보관.
- 헤더: 이름 아래 "Backend Developer"만. 뒤에 붙는 부제 없음. 직무명은 `header.role`(또는 profile `role`)로 바꿀 수 있다.
- 프로젝트 블록: 번호·제목 / 기간·역할·기술 칩 / 요약 바 / 문제 / 원인 규명 / 선택지(채택 표시) / 실행 / 결과 KPI / 관련 글. 형식은 `references/yaml_schema.md`.
- 프로젝트 5개 이하. 첫 페이지에 SUMMARY·SKILLS와 대표 프로젝트 시작이 보이도록 한다.

## 문장 규칙

- SUMMARY 첫 문단은 `~합니다`체.
  - 전: "Go 백엔드 개발자 5년차. … 외부 API 연동 최적화를 담당."
  - 후: "Go 백엔드 개발자 5년차입니다. … 외부 API 연동 최적화를 담당하고 있습니다."
- SUMMARY 불릿과 프로젝트 본문은 짧게 끊는 말투(명사형, `~함`).
- AI가 쓴 것 같은 문체를 피한다.
  - `—`, `·`, `→`는 한 불릿에 각각 1개까지. `→`는 수치 전후 비교에만.
  - 쉬운 우리말이 있으면 영어 개념어·번역투를 쓰지 않는다: fence, durable claim, 성립, 봉인, 격리, 일원 관리 …
  - 정확한 기술 용어는 둔다: CAS, gRPC, context …
  - 상투어 금지: 고도화, 극대화, 체계적, 효율적, 원활한, 다양한, 핵심, 혁신, 견고한, 선제적, 확보, ~을 통해, ~기반으로, 단순히 ~가 아니라
  - 한 문장에 수식어를 여러 개 이어 붙이지 않는다. 늘 셋씩 나열하지 않는다. 모든 불릿을 같은 길이·같은 구조로 맞추지 않는다.
  - 판단 기준: 본인이 면접에서 말로 설명할 때 실제로 쓰는 단어인가.
- 행동 동사 + 방법 + 결과. "참여/담당/노력/기여"로 끝내지 않는다(SUMMARY 첫 문단의 "담당하고 있습니다"는 예외).
- 작성이 끝나면 위 목록으로 스스로 점검한다. 자동 검사(`check.py`)가 잡지 못하는 항목(수식어 나열, 셋씩 나열, 같은 구조 반복)은 직접 읽고 판단한다. 걸린 문장은 수정 전·후를 보여 준다.
- 사실 규칙
  - 자료에 없는 수치나 사실은 만들지 않는다.
  - 추론으로 채운 문장은 `[확인 필요]`로 표시하고 사용자 확인을 받은 뒤 확정한다.

## 이력서 일반 규칙 (요약, 자세히는 references/resume_guide.md)

- 프로젝트 5개 이하. 공고와 먼 것은 OTHER 한 줄로.
- 수치는 전후 비교와 원인을 함께 쓴다. 확정 안 된 수치는 쓰지 않는다.
- 선택지는 기각안의 장점을 먼저 인정하고 단점으로 기각, 채택안은 근거와 약점 통제 방법까지.
- 기술 스택은 공고와의 교집합 8~12개, 숙련도 표시 없음, 안 써본 기술 금지.
- 링크는 프로젝트당 1~2개.
- 지원동기는 넣지 않는다. 따로 요구할 때만 5~7줄 별도 작성.
- 플레이스홀더를 남기고 내지 않는다.
- 이 파일과 references 문서가 부딪히면 이 파일을 따른다.

## 빌드 후 검사

`render.py`가 끝에 `check.py`를 부른다. 따로 돌릴 때: `python3 scripts/check.py <yaml> <pdf>`

| 항목 | 기준 | 수준 |
|---|---|---|
| 페이지 수 | `meta.target_pages` (기본 2~3) | 오류 |
| 제목 홀로 남음 | 섹션·프로젝트·소제목 뒤 같은 쪽 본문 3줄 미만 (마지막 쪽 제외) | 오류 |
| 링크 | PDF 안 모든 링크 접속 | 열리지 않음=오류, 확인 불가=경고 |
| 플레이스홀더 | 【 】, TODO, TBD, N건, `[확인 필요]` … | 오류 |
| 금지어 · 기호 | `references/style_rules.yaml` | 오류 |
| 번역투 · 개념어 | 같은 파일 `translationese` | 경고 |
| SUMMARY 말투 | 첫 문단 문장마다 `~니다`로 끝남 | 오류 |

- 오류가 0이 될 때까지 고친다. 경고는 사용자에게 보여 주고 판단을 맡긴다.
- 제목 홀로 남음이나 페이지 초과는 내용을 줄이거나(불릿 합치기, 프로젝트를 OTHER로 내리기) 순서를 바꿔 해결한다. CSS로 억지로 줄이지 않는다.
- 링크 확인: 클라우드 환경은 외부 접속이 막혀 "확인 불가"가 나올 수 있다. 그때는 사용자 PC에서 `python3 scripts/check_links.py --pdf <pdf>`를 실행하거나 브라우저로 열어 확인한다. 결과는 `data/portfolio/portfolio.yaml`의 `last_link_check`에 적는다.

## 저장 규칙 (data/)

| 알게 된 것 | 저장 위치 |
|---|---|
| 이름, 연락처, 학력 | `profile/profile.yaml` |
| 경험 문서, git 로그, 프로젝트 후보와 근거, 확인받은 사실 | `experience/` |
| 강조점, 뺄 내용, 페이지 수, 섹션, 연차 표기 | `preferences/standing.md` 또는 `preferences/<공고>_requests.md` |
| GitHub·블로그, 글 목록, 고른 글, 링크 확인 결과 | `portfolio/portfolio.yaml` |
| 공고, 요구사항, 지원 결과 | `job_postings/` |
| 확정 yaml | `resumes/` (+ Claude 프로젝트) |
| PDF·PNG | `output/` |

- 사용자가 말한 것만 사실로 적는다. 내 추론은 `[확인 필요]`를 붙인다.
- 기존 파일에 덧붙일 때는 날짜를 남기고, 바뀐 결정은 이전 값을 지우지 말고 "(이전: …)"으로 적는다.
- `data/` 내용은 git에 올라가지 않는다. 저장소를 공개해도 개인정보가 새지 않게 `.gitignore`를 건드리지 않는다.
