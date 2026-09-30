# -*- coding: utf-8 -*-
"""공고 점수 계산 (LLM 호출 없음). 기준은 references/scoring.md.

LLM(Claude)은 공고를 한 줄씩 분류만 해서 판정 파일(yaml)을 채우고, 점수는 이 스크립트가 계산한다.
같은 판정이면 언제나 같은 점수가 나오고, 어디서 깎였는지 항목별로 남는다.

  python3 scripts/score.py init <본문.md> [-o 판정.yaml]   본문의 주요업무·자격요건·우대사항을 줄 단위 뼈대로
  python3 scripts/score.py <판정.yaml>...                  점수표 출력
  python3 scripts/score.py --json <판정.yaml>...           한 줄에 하나씩 JSON (다른 스크립트용)

가중치·선호 업무·신호는 data/profile/targets.yaml 의 scoring 절에서 읽는다 (없으면 예시 파일 값).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jobkit as K  # noqa: E402

FIT = {"done": 5.0, "adjacent": 3.5, "new": 1.5}            # 주요 업무: 해 본 일 / 비슷한 일 / 처음
REQ = {"yes": 5.0, "partial": 3.5}                          # 필수: 못 채우면 gap 종류로
REQ_NO = {"bridge": 2.5, "core": 1.0}
PREF = {"yes": 1.0, "partial": 0.5, "no": 0.0}
VERDICTS = [(4.0, "지원 권장", "PASS"), (3.5, "지원 고려", "PASS"), (3.0, "보류", "MARGINAL"), (0, "제외", "FAIL")]
SECTIONS = [("work", r"주요\s*업무|담당\s*업무|하는\s*일|이런\s*일|합류하면|What you('|’)ll do|Responsibilit"),
            ("required", r"자격\s*요건|필수|지원\s*자격|이런\s*분|Requirements|Qualifications|Must"),
            ("preferred", r"우대|Preferred|Nice to have|Plus")]


def config() -> dict:
    t = K.load_yaml(K.P["targets"]) or {}
    if "scoring" not in t:
        t = K.load_yaml(os.path.join(os.path.dirname(K.P["targets"]), "targets.example.yaml")) or {}
    return t.get("scoring") or {}


def _met(x) -> str:
    """YAML 1.1 은 yes/no 를 참/거짓으로 읽는다. 문자열로 되돌린다."""
    v = x.get("met")
    return {True: "yes", False: "no"}.get(v, v) if isinstance(v, bool) else str(v)


def _avg(xs, default):
    return sum(xs) / len(xs) if xs else default


def score(j: dict, cfg: dict) -> dict:
    """판정 dict → {total, verdict, triage, parts, caps, gate}"""
    gates = j.get("gates") or {}
    failed = [k for k, v in gates.items() if v == "fail"]
    if failed:
        return dict(total=None, verdict="제외", triage="FAIL", parts={}, caps=[], gate=failed)

    w = {"work": 0.30, "required": 0.30, "preferred": 0.10, "direction": 0.30, **(cfg.get("weights") or {})}
    work = _avg([FIT[x["fit"]] for x in j.get("work") or []], 3.0)
    req_items = j.get("required") or []
    req = _avg([REQ[_met(x)] if _met(x) in REQ else REQ_NO[x.get("gap", "bridge")] for x in req_items], 3.0)
    pref_items = j.get("preferred") or []
    pref = 1 + 4 * _avg([PREF[_met(x)] for x in pref_items], 0.5)

    prefer, avoid = set(cfg.get("prefer_work") or {}), set(cfg.get("avoid_work") or {})
    kind = lambda t: 1 if t in prefer else (-1 if t in avoid else 0)   # noqa: E731
    d = j.get("direction") or {}
    dir_ = {1: 5.0, 0: 3.0, -1: 1.5}[kind(d.get("primary"))] + 0.5 * sum(kind(t) for t in d.get("secondary") or [])
    dir_ = min(5.0, max(1.0, dir_))

    parts = dict(work=work, required=req, preferred=pref, direction=dir_)
    total = sum(w[k] * v for k, v in parts.items())
    sig = cfg.get("signals") or {}
    bonus = sum(float(sig.get(s, 0)) for s in j.get("signals") or [])
    if j.get("priority"):
        bonus += float(cfg.get("priority_bonus", 0))
    total = min(5.0, max(1.0, total + bonus))

    caps, core = [], sum(1 for x in req_items if _met(x) == "no" and x.get("gap") == "core")
    for n, cap in sorted(((int(k), v) for k, v in (cfg.get("core_gap_caps") or {1: 3.4, 2: 2.9}).items()), reverse=True):
        if core >= n:
            if total > cap:
                caps.append(f"필수 핵심 빈틈 {core}개 → 상한 {cap}")
                total = cap
            break
    total = round(total, 1)
    verdict, triage = next((v, t) for lim, v, t in VERDICTS if total >= lim)
    return dict(total=total, verdict=verdict, triage=triage, parts=parts, bonus=bonus, caps=caps, gate=[])


def init(path: str) -> dict:
    """본문에서 주요업무·자격요건·우대사항 줄을 뽑아 판정 뼈대를 만든다. 분류(fit·met·gap·type)는 비워 둔다."""
    text = K.read_text(path) or ""
    head = re.search(r"^# (.+?) — (.+)$", text, re.M)
    url = re.search(r"^- URL: (\S+)", text, re.M)
    out = dict(url=url.group(1) if url else "", company=head.group(1) if head else "", title=head.group(2) if head else "",
               source=path, gates=dict(location="", language="", stack="", years="", employment="", comp=""),
               gate_note="", work=[], required=[], preferred=[], direction=dict(primary="", secondary=[]),
               signals=[], priority=False, note="")
    cur = None
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        heading = line.startswith("#") or re.fullmatch(r"\[[^\]]{1,30}\]", line)   # [이렇게 일합니다] 같은 소제목은 절을 끝낸다
        short = len(line) < 40 and not re.match(r"^[•·\-*▪◦・●○]|^\d+[.)]", line)
        hit = next((k for k, pat in SECTIONS if re.search(pat, line, re.I)), None) if (heading or short) else None
        if hit or heading:
            cur = hit
            continue
        if cur:
            item = re.sub(r"^([•·\-*▪◦・●○]|\d+[.)])\s*", "", line)
            if len(item) > 3:
                out[cur].append({"line": item, **({"fit": ""} if cur == "work" else {"met": ""})})
    return out


def _row(j, r):
    if r["total"] is None:
        return f"| {j.get('company')} | {j.get('title')} | — | 제외 | 조건: {', '.join(r['gate'])} | {j.get('gate_note', '')} |"
    p = r["parts"]
    detail = f"업무 {p['work']:.1f} · 필수 {p['required']:.1f} · 우대 {p['preferred']:.1f} · 방향 {p['direction']:.1f}"
    if r["bonus"]:
        detail += f" · 신호 {r['bonus']:+.1f}"
    if r["caps"]:
        detail += " · " + "; ".join(r["caps"])
    return f"| {j.get('company')} | {j.get('title')} | {r['total']}/5 | {r['verdict']} | {detail} | {j.get('note', '')} |"


def main(argv=None):
    ap = argparse.ArgumentParser(description="공고 점수 계산")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("-o", "--out")
    a = ap.parse_args(argv)
    if a.files[0] == "init":
        import yaml
        for f in a.files[1:]:
            s = yaml.safe_dump(init(f), allow_unicode=True, sort_keys=False, width=200)
            if a.out:
                K.write_text(a.out, s)
            else:
                print(s)
        return 0
    cfg = config()
    if not a.json:
        print("| 회사 | 포지션 | 점수 | 판정 | 항목별 | 근거 |\n|---|---|---|---|---|---|")
    for f in a.files:
        j = K.load_yaml(f)
        r = score(j, cfg)
        print(json.dumps(dict(file=f, url=j.get("url"), **r), ensure_ascii=False) if a.json else _row(j, r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
