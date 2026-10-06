# -*- coding: utf-8 -*-
"""공고 수집 (LLM 호출 없음). modes/scan.md 의 1~3단계와 5단계 기록을 자동으로 한다.

  python3 scripts/scan.py                 켜진 채널 전부
  python3 scripts/scan.py --only wanted,linkedin,toss
  python3 scripts/scan.py --dry-run       파일을 쓰지 않고 결과만 출력
  python3 scripts/scan.py --no-detail     본문을 받지 않음 (빠름, 1차 선별 불가)
  python3 scripts/scan.py --seed          지금 열린 공고를 "본 것"으로만 기록 (대기함에 넣지 않음, 다음 실행부터 새 공고만)

결과
  data/search/pipeline.md   "## 새로 수집 (선별 전)" 섹션에 추가 → AI 에이전트가 brief.md 로 1차 선별
  data/search/inbox/*.md    공고별 본문 (자격요건·우대·주요업무) + 언어 요건 힌트
  data/search/scan-history.tsv  본 공고 전부 (중복 제거용)

스택 조건으로는 거르지 않는다(판정 단계에서만, standing.md). 언어 힌트는 참고용이다.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jobkit as K  # noqa: E402
import providers  # noqa: E402

NEW_HEADER = "## 새로 수집 (선별 전)"


def plan(sources: dict, only):
    """(이름, 모듈, cfg) 목록과 스크립트가 못 도는 채널 목록."""
    runs, manual = [], []
    for name, cfg in (sources.get("boards") or {}).items():
        if not cfg.get("enabled"):
            continue
        mod = providers.BOARDS.get(name)
        (runs.append((name, mod, cfg)) if mod else manual.append(name))
    for c in sources.get("companies") or []:
        mod = providers.for_company(c)
        (runs.append((c["name"], mod, c)) if mod else manual.append(c["name"]))
    if only:
        keep = set(only)
        runs = [r for r in runs if r[0] in keep or r[1].__name__.split(".")[-1] in keep]
    return runs, manual


def main(argv=None):
    ap = argparse.ArgumentParser(description="공고 수집")
    ap.add_argument("--only", help="쉼표로 구분한 채널·회사·공급원 이름")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-detail", action="store_true")
    ap.add_argument("--seed", action="store_true")
    a = ap.parse_args(argv)
    if a.seed:
        a.no_detail = True

    sources = K.load_yaml(K.P["sources"])
    if not sources:
        sys.exit("data/search/sources.yaml 이 없습니다. sources.example.yaml 을 복사해 만드세요 (modes/onboard.md).")
    targets = K.load_yaml(K.P["targets"])
    tf, lf = sources.get("title_filter") or {}, sources.get("location_filter") or {}
    cf = sources.get("career_filter") or {}

    seen = {r["url"] for r in K.read_history()} | K.pipeline_urls()
    tracked = {k for r in K.read_tracker() for k in K.dup_keys(r["company"], r["role"])} | K.pipeline_keys()
    cool = K.cooldown_companies(int(targets.get("reapply_days", 183)))
    black = K.blacklist_companies()

    runs, manual = plan(sources, a.only.split(",") if a.only else None)
    stats, errors, fresh, hist = {}, {}, [], []
    reasons = Counter()
    batch_keys = set()
    for name, mod, cfg in runs:
        try:
            jobs = mod.collect(cfg)
        except Exception as e:           # 한 채널이 깨져도 나머지는 돈다
            errors[name] = f"{type(e).__name__}: {e}"
            continue
        n_new = 0
        for j in jobs:
            status = None
            keys = K.dup_keys(j.company, j.title)
            url_seen = j.url in seen
            if url_seen or keys & tracked or keys & batch_keys:
                status = "skipped_dup"      # 다른 사이트에 올라온 같은 공고도 URL은 기록해 둔다 (다음 실행에서 다시 안 나오게)
            elif K.title_ok(j.title, tf):
                status = "skipped_title"
            elif K.career_check(j.extra.get("career"), cf):
                status = "skipped_career"
            elif K.location_check(j.location, lf) == "block":
                status = "skipped_location"
            elif K.company_in(j.company, black):
                status = "skipped_blacklist"
            elif K.company_in(j.company, cool, exact=True):
                status = "skipped_cooldown"
            elif a.seed:
                status = "seeded"
            batch_keys |= keys
            if not url_seen:
                seen.add(j.url)
                hist.append(dict(url=j.url, first_seen=K.TODAY, portal=j.source, title=j.title, company=j.company,
                                 status=status or "added", location=j.location, posted_at=j.posted_at,
                                 normalized_company=K.norm_company(j.company)))
            if status:
                reasons[status] += 1
                continue
            n_new += 1
            fresh.append((mod, j))
        stats[name] = (len(jobs), n_new)

    # 본문
    for i, (mod, j) in enumerate(fresh, 1):
        if a.no_detail:
            continue
        if i % 25 == 0:
            print(f"  … 본문 {i}/{len(fresh)}", file=sys.stderr)
        try:
            j.text = mod.detail(j)
        except Exception as e:
            j.text = f"[본문 받기 실패: {type(e).__name__}: {e}]"
        # 본문을 받은 뒤 근무지가 구체화되면 다시 본다. 공급원이 본문을 보고 뺄 수도 있다 (예: LinkedIn 영어 전용 JD)
        if not j.extra.get("skip") and K.location_check(j.location, lf) == "block":
            j.extra["skip"] = "skipped_location"

    fresh_ok = [(m, j) for m, j in fresh if not j.extra.get("skip")]
    late = {j.url: j.extra["skip"] for _, j in fresh if j.extra.get("skip")}
    for why in late.values():
        reasons[why] += 1
    for h in hist:
        if h["url"] in late:
            h["status"] = late[h["url"]]

    lines = []
    for _, j in fresh_ok:
        loc = j.location or "?"
        tag = " [근무지 확인 필요]" if K.location_check(j.location, lf) == "unknown" else ""
        hint = K.stack_hint(j.text) if j.text else "본문 없음"
        raw = ""
        if not a.dry_run and not a.no_detail:
            os.makedirs(K.P["inbox"], exist_ok=True)
            fn = f"{K.TODAY}_{j.source.replace(':', '-')}_{j.id}.md"
            with open(os.path.join(K.P["inbox"], fn), "w", encoding="utf-8") as f:
                f.write(f"# {j.company} — {j.title}\n\n- URL: {j.url}\n- 출처: {j.source}\n- 근무지: {loc}\n"
                        f"- 게시: {j.posted_at or '?'} · 마감: {j.closes_at or '?'}\n- 수집: {K.TODAY} (scripts/scan.py)\n"
                        f"- 언어 요건 힌트: {hint}\n\n{j.text}\n")
            raw = f" | 본문: data/search/inbox/{fn}"
        lines.append(f"- [ ] {j.url} | {j.company} | {j.title} | {loc}{tag} | 선별 전 | {j.source} · {K.TODAY}"
                     f" · 마감 {j.closes_at or '?'} | 언어: {hint}{raw}")

    if not a.dry_run:
        if lines and not a.seed:
            md = K.read_text(K.P["pipeline"]) or "# 공고 대기함\n"
            K.write_text(K.P["pipeline"], K.insert_under(md, NEW_HEADER, lines, before="## 대기"))
        if hist:
            K.append_history(hist)

    # 보고
    print(f"── 공고 수집 {K.TODAY} {'(dry-run: 파일 안 씀)' if a.dry_run else ''}")
    for name, (n, new) in stats.items():
        print(f"  {name:<22} 받음 {n:>4} · 새 공고 {new}")
    for name, err in errors.items():
        print(f"  {name:<22} ✗ {err}")
    if manual:
        print(f"  스크립트 미지원 (브라우저·Firecrawl로 modes/scan.md 수동 단계): {', '.join(manual)}")
    print("  제외: " + (", ".join(f"{k} {v}" for k, v in sorted(reasons.items())) or "없음"))
    print(f"  새로 추가: {len(lines)}건 → {'pipeline.md ' + NEW_HEADER if not a.dry_run else '(dry-run)'}")
    for l in lines[:40]:
        print("   " + re.sub(r" \| 본문: .*$", "", l)[6:])
    if len(lines) > 40:
        print(f"   … 외 {len(lines) - 40}건")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
