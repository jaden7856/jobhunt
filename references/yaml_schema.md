# resume.yaml 형식

내용은 yaml, 모양은 `scripts/render.py`. 개인정보(이름·이메일·전화)는 yaml에 넣지 않고 `data/profile/profile.yaml`에서 읽는다.

## 인라인 표기

| 쓰는 법 | 결과 |
|---|---|
| `**굵게**` | **굵게** |
| `` `코드` `` | 고정폭 코드 |
| `[글자](https://주소)` | 링크 |
| `[확인 필요] 문장` | 노란 표시. 검사에서 오류로 잡힌다. 사용자 확인 후 태그를 지운다 |

HTML 태그는 쓰지 않는다(그대로 글자로 찍힌다).

## 전체 구조

```yaml
meta:
  job: Backend                 # 파일명 두 번째 칸
  version: 토스_v1             # 파일명 세 번째 칸 → 홍길동_Backend_토스_v1.pdf
  position: 서비스 백엔드       # 목표 포지션 (메모용)
  design: B                    # A 에디토리얼 / B 스위스 그리드(기본) / C 다크 마스트헤드
  target_pages: [2, 3]         # 검사 기준. 정수 하나도 가능
  posting: data/job_postings/2026-10_toss_server.md   # 공고 파일 (선택)
  omit_sections: []            # 빼고 싶은 섹션 키: summary, skills, experience, projects, other

header:
  role: Backend Developer      # 이름 아래 한 줄. 부제 없음

portfolio:                     # 없으면 PORTFOLIO 박스와 헤더 링크가 빠진다
  items:
    - { label: github.com/me, url: "https://github.com/me" }
  desc: "기술 블로그. …"

summary:
  lead: "… 5년차입니다. … 담당하고 있습니다."   # '~합니다'체 (검사함)
  bullets: ["…", "…"]                         # 짧게 끊는 말투

skills:
  - { name: Backend, items: "Go · gRPC · PostgreSQL" }

experience:
  - company: 회사명
    title: 백엔드 개발자
    period: "2021.12 ~ 재직 중"
    tenure: 5년차              # 연차 표기. 비우면 괄호 없이 기간만
    intro: "회사·제품 한두 줄"
    timeline:
      - { period: "2025.07 ~", desc: "…" }

projects:                      # 최대 5개. 순서대로 01, 02 … 번호가 붙는다
  - title: "API 호출 99% 감소 : …"
    period: "2025.09 ~ 2026.08"
    role: 설계·개발 단독
    techs: [Go, gRPC]
    summary: "요약 바 1~2줄"
    rows:
      - { label: 문제, text: "…" }
      - { label: 원인 규명, text: ["문단1", "문단2"] }
      - label: 선택지
        options:
          - { title: "① 캐싱", adopted: false, body: "장점. 그러나 단점" }
          - { title: "② 자체 SDK", adopted: true, body: "채택 근거 + 약점 통제" }
      - { label: 실행, bullets: ["…", "…"] }
      - label: 결과
        kpis:
          - { value: "2,000회 → 20회", label: "VM 1대당 API 호출" }
      # 한 프로젝트 안을 A/B로 나눌 때
      - sub: { num: "A.", title: "소제목" }
      - group: { num: "B.", title: "점선 아래 하위 블록", rows: [ …같은 행 형식… ] }
    links:                     # 프로젝트당 1~2개
      - { title: "글 제목", url: "https://…" }

other:
  - "**제목** (기간) — 한 줄"

extra_sections:                # 사용자가 추가한 섹션 (선택)
  - title: CERTIFICATES
    title_ko: 자격증            # C안에서 쓰는 한글 제목
    after: other               # 이 섹션 뒤에 놓는다
    items: ["정보처리기사 (2020)"]
```

섹션 순서는 고정: 헤더 → PORTFOLIO → SUMMARY → SKILLS → EXPERIENCE → PROJECTS → OTHER (→ extra). EDUCATION 섹션은 없다.
