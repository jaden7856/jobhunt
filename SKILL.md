---
name: resume-pdf-builder
description: 한국 개발자 채용 공고를 찾고(원티드·점핏·LinkedIn·사람인·잡코리아·기업 채용 사이트), 사용자 경력·조건으로 평가하고, 공고마다 맞춘 이력서 A4 PDF를 만든다. 공고 찾기, 공고 평가, 회사별 맞춤 이력서, 이력서 수정·재빌드, 지원 현황 기록 요청에 쓴다.
---

# 공고 찾기 → 평가 → 맞춤 이력서

이력서 내용은 yaml, 모양과 빌드는 `scripts/render.py`. 개인 자료는 전부 `data/`에 있고 git에 올라가지 않는다.
사용자가 알려 준 사실·요구사항·판단 교정은 `data/` 아래 알맞은 파일에 바로 저장해서 다음에 다시 쓴다. 쓸수록 선별과 맞춤이 정확해지는 구조다.
작동 방식과 개인화 저장 구조는 career-ops(MIT)를 참고했다. 전체 설계는 `docs/ROADMAP.md`.

## 저장소

기본 위치: 사용자 맥 `~/Desktop/develop/resume-builder` (GitHub에 올려 관리).

```
SKILL.md                    이 파일 (모드 연결)
modes/_shared.md            공통 규칙, 사실 원천, data/ 파일 지도, 한국 채용 용어 (항상 먼저 읽음)
modes/onboard.md            처음 설정, 개인화 파일 점검
modes/scan.md               공고 찾기와 1차 선별
modes/evaluate.md           공고 평가 (조건 판정, 요구사항 대응표, 맞춤 계획)
modes/tailor.md             공고 맞춤 이력서 작성·빌드·검수
modes/track.md              지원 현황표
scripts/render.py           yaml → HTML → PDF + PNG, 디자인 A/B/C, 빌드 후 검사 호출
scripts/check.py            페이지 수 · 제목 홀로 남음 · 링크 · 플레이스홀더 · 문체 검사
scripts/check_links.py      링크 접속 확인 (표준 라이브러리만, 어디서나 실행)
scripts/git_log.sh          로컬 git 저장소에서 작성자 기준 커밋 로그 추출
scripts/setup.sh            스킬 연결(~/.claude/skills 링크) + Playwright Chromium, 폰트(Pretendard, Noto Sans/Serif CJK KR), poppler 설치
scripts/scan.py             공고 수집 (원티드·점핏·LinkedIn·Greenhouse·토스·NHN·카카오·greetinghr) → 거르기 → pipeline.md
scripts/alive.py            추적 공고 마감 확인
scripts/tracker.py          지원 현황 기록(add/set)과 통합 보고표(report)
scripts/score.py            공고 점수 계산 (줄 단위 판정 파일 → 항목별 점수)
scripts/weekly.sh           주간 스캔의 LLM 없는 부분 (scan → alive → report)
scripts/providers/          사이트별 수집 모듈
references/sources.md       채용 사이트별 수집 방법 (엔드포인트, 본문 위치, 마감 판정)
references/scoring.md       공고 점수 기준 (분류 방법, 계산, 교정)
references/yaml_schema.md   yaml 형식
references/writing_rules.md 문장 규칙과 점검 방법
references/style_rules.yaml 금지어·번역투·기호 한도 (check.py 가 읽음)
references/resume_guide.md  이력서 일반 규칙 (프로젝트 수, 수치, 링크 …)
examples/example.yaml       가상 인물 예시
docs/ROADMAP.md             설계와 단계
data/                       사용자 자료 (git 제외, 구조만 올라감)
  profile/ experience/ preferences/ portfolio/ search/ job_postings/ applications/ resumes/ output/
```

## 시작할 때

1. 저장소에 접근한다. 맥 폴더가 연결되어 있지 않으면 `~/Desktop/develop/resume-builder` 접근을 요청한다. 없으면 GitHub 주소를 물어 클론한다.
2. `modes/_shared.md`를 읽는다.
3. `modes/onboard.md`의 세션 시작 점검을 한다. 빠진 개인화 파일이 있으면 알린다.
4. `data/preferences/standing.md`를 읽는다. 이미 정해진 것은 다시 묻지 않는다.
5. 이 세션이 Claude 프로젝트에 연결되어 있으면 프로젝트의 확정 yaml과 가이드 문서도 확인한다.

## 모드

요청에 맞는 모드 파일을 읽고 그대로 따른다.

| 요청 예 | 모드 |
|---|---|
| "처음 설정", "내 조건 바꿀래", "목표 역할 추가" | `modes/onboard.md` |
| "공고 찾아줘", "새 공고 있어?", "주간 스캔" | `modes/scan.md` (`bash scripts/weekly.sh` 먼저) |
| "새로 수집한 공고 선별해줘" | `modes/scan.md` 4단계부터 |
| "공고 현황 보여줘", "표로 보여줘" | `python3 scripts/tracker.py report --alive` 출력 |
| 공고 URL·본문을 줌, "이 공고 어때?", "평가해줘" | `modes/evaluate.md` |
| "이 공고용 이력서 만들어줘", "이력서 고쳐줘", "다시 빌드" | `modes/tailor.md` (평가 없이 공고만 받았으면 evaluate를 먼저 제안) |
| "지원했어", "서류 붙었어", "떨어졌어", "지원 현황" | `modes/track.md` (`scripts/tracker.py`) |
| "prep {회사}", "면접 준비" | 그 공고의 `.eval.md` F블록 + `standing.md` "자주 쓰는 흐름" |

공고 URL을 받으면 evaluate → (사용자가 지원하기로 하면) tailor → track 순서로 이어 간다. 각 단계 사이에 사용자 확인을 받는다.
