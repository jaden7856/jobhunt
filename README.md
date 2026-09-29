<h1 align="center">resume-builder</h1>

<p align="center">
  Write your developer resume in YAML, build a print-ready A4 PDF — with Claude as your interviewer and editor.
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
  <a href="#-preview">Preview</a> · <a href="#-quick-start">Quick Start</a> · <a href="#-how-it-works">How It Works</a> · <a href="#-build-checks">Build Checks</a> · <a href="#-project-structure">Project Structure</a>
</p>

## 📖 Overview

**resume-builder** is a [Claude](https://claude.com) skill plus a small Python toolchain for writing Korean-language developer resumes.

Content lives in a YAML file. Layout and build live in `scripts/render.py`. Claude walks you through the process step by step — target position, source material, project selection, portfolio links — then writes the YAML, builds the PDF, and runs automated checks until there are zero errors.

### Highlights

- 🧾 **Content as data** — the resume is a YAML file (`references/yaml_schema.md`), so tailoring for each company is a `cp` and a few edits
- 🎨 **Three designs** — A Editorial, **B Swiss Grid (default)**, C Dark Masthead, switchable with one flag
- 🧭 **Guided interview** — Claude asks what it needs one step at a time and reuses answers already saved under `data/`
- 🔍 **Evidence-first projects** — every project follows *problem → root cause → options considered → execution → measured result*
- ✅ **Build checks** — page count, orphaned headings, broken links, placeholders, banned phrases, and tone
- 🔒 **Private by default** — your real data under `data/` is git-ignored; only folder structure and examples are committed

## 🖼 Preview

Rendered from the fictional sample [`examples/example.yaml`](examples/example.yaml).

| A · Editorial | B · Swiss Grid (default) | C · Dark Masthead |
|:---:|:---:|:---:|
| <img src="assets/design-a-p1.png" alt="Design A" width="260"/> | <img src="assets/design-b-p1.png" alt="Design B" width="260"/> | <img src="assets/design-c-p1.png" alt="Design C" width="260"/> |

<details>
<summary>Design B, page 2</summary>
<p align="center"><img src="assets/design-b-p2.png" alt="Design B page 2" width="520"/></p>
</details>

📄 Full sample PDF: [`assets/example-design-b.pdf`](assets/example-design-b.pdf)

## 🚀 Quick Start

### Prerequisites

- Python 3
- macOS (Homebrew) or Debian/Ubuntu (apt)

### 1. Install

```bash
git clone https://github.com/jaden7856/resume-builder.git
cd resume-builder
bash scripts/setup.sh   # Python packages, Playwright Chromium, Noto Sans CJK KR, poppler
```

### 2. Build the sample

```bash
python3 scripts/render.py examples/example.yaml \
  --profile data/profile/profile.example.yaml --offline
```

Output goes to `data/output/<name>_<job>_<version>.pdf`, with one PNG per page.

| Option | Description |
|---|---|
| `--design A\|B\|C` | Design (default: `meta.design` in the YAML, otherwise B) |
| `--profile PATH` | Personal info YAML (default: `data/profile/profile.yaml`) |
| `--out DIR` | Output folder (default: `data/output`) |
| `--offline` | Skip link reachability checks |
| `--no-png` / `--no-check` | Skip PNG previews / post-build checks |

### 3. Make your own

```bash
cp -n data/profile/profile.example.yaml data/profile/profile.yaml   # name and contact info
cp -n examples/example.yaml data/resumes/base_service.yaml          # your content
python3 scripts/render.py data/resumes/base_service.yaml
```

Tailoring for a specific company:

```bash
cp data/resumes/base_service.yaml data/resumes/Company_service.yaml
# adjust meta.version, project order, SKILLS and wording to match the job posting
python3 scripts/render.py data/resumes/Company_service.yaml
```

### Use it as a Claude skill

Put this folder where Claude can load skills, e.g. for Claude Code:

```bash
ln -s "$PWD" ~/.claude/skills/resume-pdf-builder
```

Then ask Claude something like *"Build me a resume for this job posting"*. The full workflow is defined in [`SKILL.md`](SKILL.md).

## 🧭 How It Works

| Step | What Claude does |
|---|---|
| 0. Direction | Asks for the target position and job posting, extracts 3–5 key requirements, and picks the closest base resume |
| 1. Material | Collects experience docs, local git logs (`scripts/git_log.sh`), GitLab MRs, or old resumes, then proposes up to 5 projects with evidence |
| 2. Requests | Records strengths to emphasize, things to leave out, page count, and sections — per posting or as standing preferences |
| 3. Portfolio | Adds GitHub/blog links, suggests 1–2 related posts per project, and verifies that every link opens |
| 4. Write & build | Writes the YAML, tags inferred sentences with `[확인 필요]` ("needs confirmation"), and builds PDF + PNG |
| 5. Review | Shows check results and before/after rewrites, confirms every tagged fact, and repeats until final |

Facts are never invented: anything Claude inferred stays tagged until you confirm it.

## ✅ Build Checks

`render.py` calls `scripts/check.py` after every build. You can also run it on its own: `python3 scripts/check.py <yaml> <pdf>`.

| Check | Rule | Level |
|---|---|---|
| Page count | `meta.target_pages` (default 2–3) | Error |
| Orphaned heading | Fewer than 3 body lines after a heading on the same page | Error |
| Links | Every link in the PDF must open | Error (unreachable) / Warning (unknown) |
| Placeholders | `【 】`, `TODO`, `TBD`, `[확인 필요]` … | Error |
| Banned words & symbols | `references/style_rules.yaml` | Error |
| Translationese | `translationese` in the same file | Warning |
| Summary tone | Every sentence in the first summary paragraph ends in `~니다` | Error |

Writing rules are editable: change `references/style_rules.yaml` and the next build picks them up.

## 📁 Project Structure

```
SKILL.md                     Skill definition and workflow (Claude reads this)
scripts/
  render.py                  YAML → HTML → PDF + PNG, designs A/B/C, runs checks
  check.py                   Page count, orphaned headings, links, placeholders, style
  check_links.py             Link reachability (stdlib only)
  git_log.sh                 Extract your own commits from a local git repo
  setup.sh                   Install Chromium, fonts, poppler
references/
  yaml_schema.md             YAML format
  writing_rules.md           Writing rules and how to check them
  style_rules.yaml           Banned words, translationese, symbol limits
  resume_guide.md            General resume rules
examples/example.yaml        Fictional sample resume
assets/                      README preview images and sample PDF
data/                        Your data (git-ignored; only structure is committed)
  profile/ experience/ preferences/ portfolio/ job_postings/ resumes/ output/
```

## 🔒 Privacy

Real files under `data/` are excluded by `.gitignore`; only folder READMEs, `.gitkeep`, and `*.example.*` files are committed. Your name and contact info are never hard-coded. They're read from `data/profile/profile.yaml` at build time, so the repository can stay public.
