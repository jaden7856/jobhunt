# -*- coding: utf-8 -*-
"""빌드 후 검사.

  python3 scripts/check.py RESUME.yaml [PDF] [--offline]

검사 항목
  1. 목표 페이지 수 (meta.target_pages, 기본 [2, 3])
  2. 섹션·프로젝트 제목이 페이지 끝에 홀로 남았는지
  3. 링크 동작 (PDF 안의 모든 링크에 실제 접속)
  4. 플레이스홀더 잔존 (【 】, TODO, [확인 필요], N건 …)
  5. 문체 규칙 (금지어, 번역투, 기호 개수, SUMMARY 첫 문단 '~합니다'체)

금지어·번역투 목록은 references/style_rules.yaml 에서 고친다.
"""
import argparse
import os
import re
import sys

import logging

import yaml

logging.getLogger("pdfminer").setLevel(logging.ERROR)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(ROOT, "references", "style_rules.yaml")


def load_rules():
    with open(RULES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ══════════════════════════════ 텍스트 순회 ══════════════════════════════
def iter_texts(resume):
    """(위치, 문장, 종류) 를 돌려준다. 종류: sentence(문장 규칙 적용) / list(나열형, 기호 규칙 제외)"""
    s = resume.get("summary") or {}
    if s.get("lead"):
        yield "summary.lead", s["lead"], "lead"
    for i, b in enumerate(s.get("bullets", [])):
        yield f"summary.bullets[{i}]", b, "sentence"
    for i, sk in enumerate(resume.get("skills", []) or []):
        yield f"skills[{i}]", sk.get("items", ""), "list"
    for i, e in enumerate(resume.get("experience", []) or []):
        if e.get("intro"):
            yield f"experience[{i}].intro", e["intro"], "sentence"
        for j, t in enumerate(e.get("timeline", [])):
            yield f"experience[{i}].timeline[{j}]", t.get("desc", ""), "sentence"
    pf = resume.get("portfolio") or {}
    if pf.get("desc"):
        yield "portfolio.desc", pf["desc"], "sentence"
    for i, p in enumerate(resume.get("projects", []) or []):
        base = f"projects[{i}]"
        yield f"{base}.title", p.get("title", ""), "title"
        yield f"{base}.summary", p.get("summary", ""), "sentence"
        yield from _iter_rows(p.get("rows", []), f"{base}.rows")
    for i, o in enumerate(resume.get("other", []) or []):
        yield f"other[{i}]", o, "sentence"
    for i, x in enumerate(resume.get("extra_sections", []) or []):
        for j, it in enumerate(x.get("items", []) or []):
            yield f"extra_sections[{i}].items[{j}]", it, "sentence"


def _iter_rows(rows, base):
    for k, r in enumerate(rows):
        pth = f"{base}[{k}]"
        if "sub" in r:
            yield pth + ".sub", r["sub"].get("title", ""), "title"
        elif "group" in r:
            yield pth + ".group", r["group"].get("title", ""), "title"
            yield from _iter_rows(r["group"].get("rows", []), pth + ".group.rows")
        elif "text" in r:
            paras = r["text"] if isinstance(r["text"], list) else [r["text"]]
            for n, t in enumerate(paras):
                yield f"{pth}.text[{n}]", t, "sentence"
        elif "bullets" in r:
            for n, t in enumerate(r["bullets"]):
                yield f"{pth}.bullets[{n}]", t, "sentence"
        elif "options" in r:
            for n, o in enumerate(r["options"]):
                yield f"{pth}.options[{n}].title", o.get("title", ""), "title"
                yield f"{pth}.options[{n}].body", o.get("body", ""), "sentence"
        elif "kpis" in r:
            for n, o in enumerate(r["kpis"]):
                yield f"{pth}.kpis[{n}]", f'{o.get("value", "")} / {o.get("label", "")}', "title"


def plain(s):
    """마크업을 걷어낸 본문"""
    s = str(s or "")
    s = re.sub(r"`[^`]*`", "CODE", s)          # 코드 안 기호는 세지 않는다
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return s.replace("**", "")


# ══════════════════════════════ 문체·플레이스홀더 ══════════════════════════════
def lint(resume, rules=None):
    rules = rules or load_rules()
    issues = []

    def add(level, where, kind, msg, text):
        issues.append(dict(level=level, where=where, kind=kind, msg=msg, text=str(text)))

    ph = [re.compile(p) for p in rules["placeholders"]]
    banned = [(re.compile(w["pattern"]), w.get("hint", "")) for w in rules["banned"]]
    trans = [(re.compile(w["pattern"]), w.get("hint", "")) for w in rules["translationese"]]
    limits = rules["symbol_limits"]
    arrow_allow = [re.compile(p) for p in rules.get("arrow_allow", [])]

    for where, raw, kind in iter_texts(resume):
        t = plain(raw)
        for p in ph:
            if p.search(str(raw)):
                add("error", where, "플레이스홀더", f"'{p.pattern}' 가 남아 있음", raw)
        if kind == "list":
            continue
        for p, hint in banned:
            m = p.search(t)
            if m:
                add("error", where, "상투어", f"'{m.group(0)}' {hint}".strip(), raw)
        for p, hint in trans:
            m = p.search(t)
            if m:
                add("warn", where, "번역투·개념어", f"'{m.group(0)}' {hint}".strip(), raw)
        if kind in ("sentence", "lead"):
            # 허용한 '→'(버전·라이브러리 교체)는 개수와 용도 검사에서 뺀다
            ok_arrows = {m.start() + m.group(0).index("→") for p in arrow_allow for m in p.finditer(t)}
            counted = "".join("⇢" if i in ok_arrows else ch for i, ch in enumerate(t))
            for title in re.findall(r"\[([^\]]+)\]\([^)]+\)", str(raw)):
                counted = counted.replace(title, "LINK")                    # 외부 글 제목은 내 문장이 아니다
            if rules.get("symbol_ignore_parens"):
                counted = re.sub(r"\([^)]*\)", "", counted)     # 괄호 안 기술 나열은 세지 않는다
            for sym, lim in limits.items():
                n = counted.count(sym)
                if n > lim:
                    add("error", where, "기호 개수", f"'{sym}' {n}개 (한 불릿 {lim}개까지)", raw)
            for m in re.finditer("→", t):
                if m.start() in ok_arrows:
                    continue
                left, right = t[max(0, m.start() - 12):m.start()], t[m.end():m.end() + 12]
                if not (re.search(r"\d", left) and re.search(r"\d", right)):
                    add("error", where, "화살표 용도", "'→'는 수치 전후 비교에만 사용", raw)
                    break
        if kind == "lead":
            sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+", t.strip()) if x.strip()]
            bad = [x for x in sents if not x.rstrip(" .").endswith("니다")]
            if bad:
                add("error", where, "SUMMARY 말투", "첫 문단은 '~합니다'체로 끝내야 함", raw)
    return issues


# ══════════════════════════════ PDF 검사 ══════════════════════════════
def _norm(s):
    return re.sub(r"\s+", "", s or "")


def pdf_checks(resume, pdf_path):
    import pdfplumber
    issues, links = [], []
    meta = resume.get("meta", {})
    target = meta.get("target_pages", [2, 3])
    if isinstance(target, int):
        target = [target, target]

    headings = [("섹션", t) for t in ("SUMMARY", "SKILLS", "EXPERIENCE", "PROJECTS", "OTHER")]
    for x in resume.get("extra_sections", []) or []:
        headings.append(("섹션", x["title"]))
    for i, p in enumerate(resume.get("projects", []) or []):
        headings.append(("프로젝트", f"{i + 1:02d}{p['title']}"))
        for r in p.get("rows", []):
            for key in ("sub", "group"):
                if key in r:
                    headings.append(("소제목", f'{r[key].get("num", "")}{r[key]["title"]}'))

    with pdfplumber.open(pdf_path) as pdf:
        n = len(pdf.pages)
        if not (target[0] <= n <= target[1]):
            issues.append(dict(level="error", where="pdf", kind="페이지 수",
                               msg=f"{n}쪽 (목표 {target[0]}~{target[1]}쪽)", text=""))
        pages_lines = []
        for page in pdf.pages:
            lines = [l for l in page.extract_text_lines() if l["text"].strip()]
            pages_lines.append(lines)
            for h in page.hyperlinks:
                if h.get("uri"):
                    links.append(h["uri"])

    for kind, text in headings:
        key = _norm(text)[:14]
        for pi, lines in enumerate(pages_lines):
            for li, l in enumerate(lines):
                if _norm(l["text"]).startswith(key):
                    after = len(lines) - li - 1
                    last_page = pi == len(pages_lines) - 1
                    if after < 3 and not last_page:   # 마지막 쪽 끝은 문서 끝이라 괜찮다
                        issues.append(dict(level="error", where=f"p{pi + 1}", kind="제목 홀로 남음",
                                           msg=f"{kind} 제목 뒤에 같은 쪽 본문이 {after}줄뿐", text=text))
                    break
    return issues, sorted(set(links)), n


def check_links(urls):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from check_links import check
    issues = []
    for u in urls:
        st, info = check(u)
        if st == "broken":
            issues.append(dict(level="error", where="link", kind="링크", msg=f"열리지 않음 ({info})", text=u))
        elif st == "unknown":
            issues.append(dict(level="warn", where="link", kind="링크 미확인",
                               msg=f"이 환경에서 접속 불가 ({info}). 내 PC에서 check_links.py 로 다시 확인", text=u))
    return issues


def run_all(resume, pdf_path=None, offline=False):
    issues = lint(resume)
    links, pages = [], None
    if pdf_path:
        pi, links, pages = pdf_checks(resume, pdf_path)
        issues += pi
        if not offline:
            issues += check_links(links)
    return dict(issues=issues, links=links, pages=pages,
                errors=[i for i in issues if i["level"] == "error"],
                warns=[i for i in issues if i["level"] == "warn"])


def print_report(rep):
    print("\n── 검사 결과 ─────────────────────────")
    if rep["pages"] is not None:
        print(f"페이지 {rep['pages']}쪽 · 링크 {len(rep['links'])}개")
    if not rep["issues"]:
        print("문제 없음")
        return
    for i in rep["issues"]:
        mark = "✗" if i["level"] == "error" else "△"
        print(f"{mark} [{i['kind']}] {i['where']}: {i['msg']}")
        if i["text"]:
            t = i["text"] if len(i["text"]) < 90 else i["text"][:87] + "…"
            print(f"    └ {t}")
    print(f"\n오류 {len(rep['errors'])} · 경고 {len(rep['warns'])}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("resume")
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()
    with open(a.resume, encoding="utf-8") as f:
        res = yaml.safe_load(f)
    rep = run_all(res, a.pdf, a.offline)
    print_report(rep)
    sys.exit(1 if rep["errors"] else 0)
