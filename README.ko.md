<h1 align="center">resume-builder</h1>

<p align="center">
  개발자 이력서를 YAML로 쓰고 인쇄용 A4 PDF로 빌드합니다. Claude가 질문하고, 정리하고, 검사합니다.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude-Skill-D97757?style=flat-square" alt="Claude Skill"/>
  <img src="https://img.shields.io/badge/Python-3-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3"/>
  <img src="https://img.shields.io/badge/Playwright-Chromium-2EAD33?style=flat-square&logo=playwright&logoColor=white" alt="Playwright"/>
  <img src="https://img.shields.io/badge/Output-A4_PDF_%2B_PNG-555?style=flat-square" alt="A4 PDF + PNG"/>
</p>

<p align="center">
  <a href="./README.md">English</a> | <a href="./README.ko.md">한국어</a>
  <br/>
  <a href="#-미리보기">미리보기</a> · <a href="#-빠른-시작">빠른 시작</a> · <a href="#-작동-순서">작동 순서</a> · <a href="#-빌드-후-검사">빌드 후 검사</a> · <a href="#-폴더-구조">폴더 구조</a>
</p>

## 📖 소개

**resume-builder**는 한국어 개발자 이력서를 만드는 [Claude](https://claude.com) 스킬과 Python 빌드 도구입니다.

내용은 YAML 파일에, 모양과 빌드는 `scripts/render.py`에 있습니다. Claude가 목표 포지션, 자료, 프로젝트 선택, 포트폴리오 링크를 차례로 묻고 YAML을 작성합니다. 그다음 PDF를 빌드하고 자동 검사 오류가 0이 될 때까지 고칩니다.

### 특징

- 🧾 **내용은 데이터로** — 이력서는 YAML 파일(`references/yaml_schema.md`). 회사별 맞춤본은 `cp` 후 몇 군데만 고치면 됩니다
- 🎨 **디자인 3종** — A 에디토리얼, **B 스위스 그리드(기본)**, C 다크 마스트헤드. 옵션 하나로 바꿉니다
- 🧭 **단계별 질문** — 필요한 것만 한 단계씩 묻고, `data/`에 저장된 답은 다시 묻지 않습니다
- 🔍 **근거 중심 프로젝트** — 모든 프로젝트를 *문제 → 원인 규명 → 선택지 → 실행 → 결과 수치* 순서로 씁니다
- ✅ **빌드 후 검사** — 페이지 수, 제목 홀로 남음, 깨진 링크, 플레이스홀더, 금지어, 말투
- 🔒 **개인정보 보호** — `data/` 아래 실제 자료는 git에서 빠지고, 폴더 구조와 예시만 올라갑니다

## 🖼 미리보기

가상 인물 예시 [`examples/example.yaml`](examples/example.yaml)로 만든 결과입니다.

| A · 에디토리얼 | B · 스위스 그리드 (기본) | C · 다크 마스트헤드 |
|:---:|:---:|:---:|
| <img src="assets/design-a-p1.png" alt="디자인 A" width="260"/> | <img src="assets/design-b-p1.png" alt="디자인 B" width="260"/> | <img src="assets/design-c-p1.png" alt="디자인 C" width="260"/> |

<details>
<summary>디자인 B, 2쪽</summary>
<p align="center"><img src="assets/design-b-p2.png" alt="디자인 B 2쪽" width="520"/></p>
</details>

📄 전체 예시 PDF: [`assets/example-design-b.pdf`](assets/example-design-b.pdf)

## 🚀 빠른 시작

### 준비물

- Python 3
- macOS(Homebrew) 또는 Debian/Ubuntu(apt)

### 1. 설치

```bash
git clone https://github.com/jaden7856/resume-builder.git
cd resume-builder
bash scripts/setup.sh   # Python 패키지, Playwright Chromium, Noto Sans CJK KR, poppler
```

### 2. 예시 빌드

```bash
python3 scripts/render.py examples/example.yaml \
  --profile data/profile/profile.example.yaml --offline
```

산출물은 `data/output/이름_직무_버전.pdf`와 페이지별 PNG입니다.

| 옵션 | 설명 |
|---|---|
| `--design A\|B\|C` | 디자인 (기본: YAML `meta.design`, 없으면 B) |
| `--profile PATH` | 개인정보 YAML (기본: `data/profile/profile.yaml`) |
| `--out DIR` | 산출물 폴더 (기본: `data/output`) |
| `--offline` | 링크 접속 검사 생략 |
| `--no-png` / `--no-check` | PNG 미리보기 / 빌드 후 검사 생략 |

### 3. 내 이력서 만들기

```bash
cp -n data/profile/profile.example.yaml data/profile/profile.yaml   # 이름·연락처
cp -n examples/example.yaml data/resumes/base_service.yaml          # 내 내용
python3 scripts/render.py data/resumes/base_service.yaml
```

회사별 맞춤본:

```bash
cp data/resumes/base_service.yaml data/resumes/회사_service.yaml
# meta.version, 프로젝트 순서, SKILLS, 용어를 공고에 맞춰 수정
python3 scripts/render.py data/resumes/회사_service.yaml
```

### Claude 스킬로 쓰기

Claude가 스킬을 읽는 위치에 이 폴더를 연결합니다. Claude Code라면:

```bash
ln -s "$PWD" ~/.claude/skills/resume-pdf-builder
```

그다음 *"이 공고에 맞춰 이력서 만들어줘"* 처럼 요청하면 됩니다. 전체 흐름은 [`SKILL.md`](SKILL.md)에 있습니다.

## 🧭 작동 순서

| 단계 | Claude가 하는 일 |
|---|---|
| 0. 지원 방향 | 목표 포지션과 채용공고를 묻고, 핵심 요구사항 3~5개를 뽑아 가장 가까운 기본본을 고릅니다 |
| 1. 자료 수집 | 경험 문서, 로컬 git 로그(`scripts/git_log.sh`), GitLab MR, 기존 이력서를 모아 근거와 함께 프로젝트 후보를 최대 5개 제안합니다 |
| 2. 추가 요구사항 | 강조할 점, 뺄 내용, 페이지 수, 섹션을 이번 공고용 또는 계속 쓸 설정으로 저장합니다 |
| 3. 포트폴리오 | GitHub·블로그 링크를 넣고, 프로젝트마다 관련 글 1~2개를 제안하고, 링크가 열리는지 확인합니다 |
| 4. 작성과 빌드 | YAML을 쓰고, 추론으로 채운 문장에 `[확인 필요]`를 붙이고, PDF와 PNG를 빌드합니다 |
| 5. 검수와 수정 | 검사 결과와 수정 전·후 문장을 보여 주고, 태그 붙은 사실을 하나씩 확인받아 확정할 때까지 반복합니다 |

자료에 없는 수치나 사실은 만들지 않습니다. 추론한 문장은 확인받기 전까지 태그가 남습니다.

## ✅ 빌드 후 검사

`render.py`가 빌드 끝에 `scripts/check.py`를 부릅니다. 따로 돌릴 때: `python3 scripts/check.py <yaml> <pdf>`

| 항목 | 기준 | 수준 |
|---|---|---|
| 페이지 수 | `meta.target_pages` (기본 2~3) | 오류 |
| 제목 홀로 남음 | 제목 뒤 같은 쪽 본문 3줄 미만 | 오류 |
| 링크 | PDF 안 모든 링크 접속 | 열리지 않음=오류, 확인 불가=경고 |
| 플레이스홀더 | `【 】`, `TODO`, `TBD`, `[확인 필요]` … | 오류 |
| 금지어 · 기호 | `references/style_rules.yaml` | 오류 |
| 번역투 · 개념어 | 같은 파일 `translationese` | 경고 |
| SUMMARY 말투 | 첫 문단 문장마다 `~니다`로 끝남 | 오류 |

문체 규칙은 `references/style_rules.yaml`을 고치면 다음 빌드부터 반영됩니다.

## 📁 폴더 구조

```
SKILL.md                     스킬 정의와 작동 순서 (Claude가 읽음)
scripts/
  render.py                  YAML → HTML → PDF + PNG, 디자인 A/B/C, 검사 호출
  check.py                   페이지 수 · 제목 홀로 남음 · 링크 · 플레이스홀더 · 문체
  check_links.py             링크 접속 확인 (표준 라이브러리만)
  git_log.sh                 로컬 git 저장소에서 내 커밋 로그 추출
  setup.sh                   Chromium, 폰트, poppler 설치
references/
  yaml_schema.md             YAML 형식
  writing_rules.md           문장 규칙과 점검 방법
  style_rules.yaml           금지어 · 번역투 · 기호 한도
  resume_guide.md            이력서 일반 규칙
examples/example.yaml        가상 인물 예시
assets/                      README 미리보기 이미지와 예시 PDF
data/                        내 자료 (git 제외, 구조만 올라감)
  profile/ experience/ preferences/ portfolio/ job_postings/ resumes/ output/
```

## 🔒 개인정보

`data/` 아래 실제 파일은 `.gitignore`로 빠지고 폴더 README, `.gitkeep`, `*.example.*`만 올라갑니다. 이름·연락처는 코드에 없고 빌드할 때 `data/profile/profile.yaml`에서 읽습니다. 그래서 저장소를 공개해도 됩니다.
