# -*- coding: utf-8 -*-
"""자기소개서·지원서 문항 검사 (LLM 없음).

  python3 scripts/cover_check.py data/applications/covers/<회사>_<포지션>.yaml

파일 형식 (references/cover_letter.md):
  company: 가나다
  role: 백엔드 개발자
  questions:
    - q: "지원 동기와 입사 후 하고 싶은 일을 적어 주세요"
      limit: 1000            # 글자 수 제한 (없으면 길이 검사 생략)
      count: spaces          # spaces(공백 포함, 기본) | nospaces(공백 제외)
      answer: |
        …

검사: 글자 수(공백 포함·제외)와 제한 대비 비율 — 넘으면 오류, 70% 미만이면 경고.
문체는 이력서와 같은 references/style_rules.yaml (금지어·번역투·사내 고유 이름·플레이스홀더).
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check  # noqa: E402
import jobkit as K  # noqa: E402

MIN_RATIO = 0.7


def run(path: str):
    d = K.load_yaml(path) or {}
    rows, texts = [], []
    for i, q in enumerate(d.get("questions") or [], 1):
        ans = str(q.get("answer") or "").strip()
        spaces, nospaces = len(ans.replace("\n", "")), len("".join(ans.split()))
        n = nospaces if q.get("count") == "nospaces" else spaces
        lim = q.get("limit")
        level = ""
        if lim:
            level = "오류" if n > lim else ("경고" if n < lim * MIN_RATIO else "")
        rows.append((i, q.get("q", ""), spaces, nospaces, lim, n, level))
        texts.append((f"문항 {i}", ans, "prose"))
    return d, rows, check.lint({}, texts=texts)


def main(argv=None):
    ap = argparse.ArgumentParser(description="자기소개서·지원서 문항 검사")
    ap.add_argument("file")
    a = ap.parse_args(argv)
    d, rows, issues = run(a.file)
    print(f"# {d.get('company', '')} — {d.get('role', '')}\n")
    print("| 문항 | 공백 포함 | 공백 제외 | 제한 | 비율 | 판정 |\n|---|---|---|---|---|---|")
    for i, q, sp, nsp, lim, n, level in rows:
        ratio = f"{n / lim:.0%}" if lim else "—"
        verdict = {"오류": "제한 초과", "경고": f"{MIN_RATIO:.0%} 미만"}.get(level, "통과")
        print(f"| {i}. {q[:30]} | {sp} | {nsp} | {lim or '—'} | {ratio} | {verdict} |")
    if issues:
        print("\n| 위치 | 수준 | 종류 | 내용 |\n|---|---|---|---|")
        for x in issues:
            print(f"| {x['where']} | {'오류' if x['level'] == 'error' else '경고'} | {x['kind']} | {x['msg']} |")
    bad = any(r[6] == "오류" for r in rows) or any(x["level"] == "error" for x in issues)
    print(f"\n{'고칠 것이 있습니다' if bad else '통과'} (문항 {len(rows)}개, 문체 지적 {len(issues)}개)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
