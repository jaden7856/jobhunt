#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""공고 현황표를 HTML 한 파일로 만든다 (디자인: .impeccable/surfaces/scripts-report-html-py.md, DESIGN.md).

  python3 scripts/report_html.py                      # data/search/reports/postings.html
  python3 scripts/report_html.py --fragment <경로>     # 문서 뼈대(<html>·<head>·<body>) 없는 판 — Claude Artifact 처럼 뼈대를 씌워 주는 곳에 올릴 때
  python3 scripts/report_html.py --demo -o <경로>      # 가상 회사로 채운 견본 (디자인 확인·문서용, 개인 자료 없음)

어느 AI 에이전트·브라우저에서도 열리도록 표준 라이브러리만 쓰고, 외부 자원은 제목 글꼴(Google Fonts) 하나뿐이다
(없으면 설치된 글꼴로 똑같이 보인다). 데이터는 data/search/pipeline.md · data/applications/tracker.md · 판정 파일에서 읽는다.
"""
import argparse
import html
import os
import re
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jobkit as K  # noqa: E402

BANDS = [("권장", "지원 권장", "4.0 이상"), ("고려", "지원 고려", "3.5 – 3.9"), ("보류", "보류", "3.0 – 3.4"), ("확인", "확인 필요", "본문을 못 받음")]
APPLIED = ("지원함", "서류합격", "면접", "합격", "불합격")
PART_NAMES = [("work", "업무"), ("required", "필수"), ("preferred", "우대"), ("direction", "방향")]


# ── 데이터 ────────────────────────────────────────────────────────────────

def _closes(inbox: str) -> str:
    m = re.search(r"마감:\s*([^\s·\n]+)", K.read_text(inbox) or "") if inbox else None
    v = m.group(1) if m else ""
    return v if re.match(r"\d{4}-\d{2}-\d{2}$", v) else ("상시" if v in ("상시", "채용시") else "")


def collect(today: date, since: str) -> dict:
    import score as S
    cfg = S.config()
    first = {h["url"]: h["first_seen"] for h in K.read_history()}
    rows = []
    sec = None
    for line in (K.read_text(K.P["pipeline"]) or "").split("\n"):
        if line.startswith("## "):
            sec = line.strip()
            continue
        if sec != "## 대기" or not line.lstrip().startswith("- [ ]"):
            continue
        c = [x.strip() for x in line.lstrip()[5:].split(" | ")]
        url = c[0]
        jf = re.search(r"판정: (\S+\.yaml)", line)
        j = K.load_yaml(jf.group(1)) if jf and os.path.exists(jf.group(1)) else {}
        r = S.score(j, cfg) if j else None
        total = r["total"] if r else None
        verdict = r["verdict"] if r else "확인 필요"
        if "본문 확인 필요" in line:
            verdict, total = "확인 필요", None
        seen = first.get(url, "")
        rows.append(dict(
            url=url, company=c[1] if len(c) > 1 else "", title=re.sub(r"<[^>]+>", "", c[2] if len(c) > 2 else ""),
            location=_short_loc(c[3] if len(c) > 3 else ""), score=total, verdict=verdict,
            reason=(j.get("note") if j else "") or (c[5] if len(c) > 5 else ""),
            parts={k: round(v, 1) for k, v in (r["parts"] if r else {}).items()},
            bonus=round(r.get("bonus", 0), 1) if r else 0, caps=(r["caps"] if r else []), band=(r.get("band", "") if r else ""),
            closes=_closes(j.get("source", "")) if j else "", seen=seen,
            new=bool(seen) and seen >= since,
            judgment=jf.group(1) if jf else ""))
    apps = [dict(no=a["num"], date=a["date"], company=a["company"], role=a["role"], state=a["state"],
                 memo=re.sub(r"\s+", " ", a["memo"]))
            for a in K.read_tracker() if a["state"] in APPLIED]
    return dict(rows=rows, apps=apps, today=today.isoformat(), since=since)


def _short_loc(s: str) -> str:
    """주소를 '서울 성동구'처럼 시·구까지만."""
    s = re.sub(r"\[[^\]]*\]|\([^)]*\)|대한민국\s*|,?\s*South Korea|,?\s*Korea", "", s or "").strip(" ,")
    s = re.sub(r"(서울|부산|대구|인천|광주|대전|울산)(특별시|광역시)", r"\1", s)
    s = re.sub(r"(경기|강원|충청북|충청남|전라북|전라남|경상북|경상남|제주)(특별자치)?도", r"\1", s)
    s = {"Seoul": "서울", "SEOUL": "서울", "Bundang": "성남 분당", "Seongnam": "성남"}.get(s.split(",")[0].strip(), s)
    m = re.match(r"(\S+)\s+(\S+?(?:구|시|군))(?=\s|$)", s)
    return (m.group(1) + " " + m.group(2)) if m else (s.split(",")[0][:14].strip() or "—")


def demo(today: date) -> dict:
    """가상 회사 견본. 실제 공고·지원 기록이 아니다."""
    d = lambda n: (today + timedelta(days=n)).isoformat()  # noqa: E731
    base = [
        ("가나다페이", "Server Engineer (정산 플랫폼)", "서울 강남", 4.7, "지원 권장", "정산 정합성·멱등 처리가 주 업무, Go 허용 — 결제 도메인은 처음", d(5), True,
         dict(work=4.2, required=5.0, preferred=3.2, direction=5.0), 0.4, []),
        ("라마바클라우드", "Platform Backend Engineer", "성남 분당", 4.4, "지원 권장", "⚠ 다른 직무 불합격 이력 — 재지원 가능 여부 확인 필요 · K8s Operator·컨트롤 플레인 개발", "상시", False,
         dict(work=3.8, required=4.6, preferred=2.8, direction=5.0), 0.3, []),
        ("사아자모빌리티", "Backend Engineer - Realtime", "서울 성동", 4.1, "지원 권장", "실시간 위치 이벤트 파이프라인 — 트래픽 규모 수치는 없음", d(20), True,
         dict(work=3.5, required=4.3, preferred=2.5, direction=5.0), 0.2, []),
        ("차카타커머스", "Backend Engineer (주문)", "서울 송파", 3.8, "지원 고려", "주문 상태 전이·동시성은 맞음, 제품 기능 비중이 큼", d(2), False,
         dict(work=3.6, required=4.2, preferred=2.0, direction=3.0), 0.2, []),
        ("파하헬스", "서버 개발자 (B2B SaaS)", "서울 영등포", 3.6, "지원 고려", "요건은 충족, 병원 연동 납품 성격이 있음", "상시", False,
         dict(work=3.5, required=4.0, preferred=2.4, direction=3.0), -0.1, []),
        ("에이치엠에듀", "백엔드 개발자", "서울 구로", 3.4, "보류", "관리자 기능 위주 — 규모·정합성 과제가 드러나지 않음", d(9), True,
         dict(work=3.5, required=5.0, preferred=2.0, direction=1.5), 0.2, ["주 업무 방향 'product_admin' → 상한 3.4"]),
        ("오피스랩", "DevOps Engineer", "과천", 3.1, "보류", "CI/CD·K8s 는 맞지만 운영 비중이 큼", "상시", False,
         dict(work=2.8, required=3.2, preferred=2.0, direction=2.0), 0.0, []),
        ("테스트소프트", "플랫폼 Backend 개발자", "서울 마포", None, "확인 필요", "본문을 받지 못함", "", False, {}, 0, []),
    ]
    rows = [dict(url=f"https://example.com/jobs/{i}", company=b[0], title=b[1], location=b[2], score=b[3], verdict=b[4], reason=b[5],
                 closes=b[6], new=b[7], seen=today.isoformat() if b[7] else d(-14), parts=b[8], bonus=b[9], caps=b[10],
                 judgment=f"data/search/judgments/example_{i}.yaml") for i, b in enumerate(base)]
    apps = [dict(no=1, date=d(-10), company="가나다증권", role="Server Developer", state="지원함", memo="서류 결과 대기"),
            dict(no=2, date=d(-30), company="마바사랩", role="Backend Engineer", state="불합격", memo="1차 면접 탈락")]
    return dict(rows=rows, apps=apps, today=today.isoformat(), since=today.isoformat(), demo=True)


# ── 그리기 ────────────────────────────────────────────────────────────────

CSS = r"""
/* 배치: 한 통의 증명서 — 위에 표제·발급 번호·결재란, 아래로 판정 구간별 괘선 대장. 구간이 내려갈수록 먹이 옅어진다. */
:root {
  --paper: #ffffff;        /* 서식지 */
  --ink: #17191c;          /* 먹 */
  --ink-2: #4a5059;        /* 보조 글 */
  --ink-3: #6b717a;        /* 옅은 글 (보류 구간) */
  --rule: #1b1d21;         /* 괘선 */
  --rule-2: #c9ced6;       /* 안쪽 가는 괘선 */
  --cell: #e8ecf1;         /* 머리 칸 음영 */
  --cell-2: #f4f6f9;       /* 첨부 칸 */
  --seal: #b3122e;         /* 인주 — 지원 권장에만 */
  --blue: #1f3a8a;         /* 청 결재 — 지원 고려·링크 */
  --blue-soft: #e6ebf6;
  --focus: #1f3a8a;
  --f-title: "Nanum Myeongjo", "AppleMyungjo", "Batang", "바탕", serif;
  --f-body: "Apple SD Gothic Neo", "Pretendard", "Malgun Gothic", "맑은 고딕", "Noto Sans KR", system-ui, sans-serif;
  --f-num: var(--f-body);  /* 공문 숫자: 본문 고딕 + tabular-nums */
  --f-code: ui-monospace, "SF Mono", "Menlo", monospace;
  --s-1: .25rem; --s-2: .5rem; --s-3: .75rem; --s-4: 1rem; --s-5: 1.5rem; --s-6: 2.5rem;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper: #15171a; --ink: #e9eaec; --ink-2: #b4b9c1; --ink-3: #8d939c; --rule: #9aa1ab; --rule-2: #3a3f47;
  --cell: #22262c; --cell-2: #1b1e22; --seal: #ef5a72; --blue: #8fa9ff; --blue-soft: #1e2640; --focus: #8fa9ff;
  color-scheme: dark; } }
:root[data-theme="dark"] {
  --paper: #15171a; --ink: #e9eaec; --ink-2: #b4b9c1; --ink-3: #8d939c; --rule: #9aa1ab; --rule-2: #3a3f47;
  --cell: #22262c; --cell-2: #1b1e22; --seal: #ef5a72; --blue: #8fa9ff; --blue-soft: #1e2640; --focus: #8fa9ff;
  color-scheme: dark; }

html { -webkit-text-size-adjust: 100%; }
[hidden] { display: none !important; }
body { margin: 0; background: var(--paper); color: var(--ink); font: 15px/1.55 var(--f-body); font-variant-numeric: tabular-nums; }
code { font: .85em var(--f-code); }
::selection { background: var(--blue-soft); color: var(--ink); }
input { caret-color: var(--blue); }
a { color: var(--blue); text-decoration-thickness: 1px; text-underline-offset: 3px; }
a:hover { text-decoration-thickness: 2px; }
:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
* { scrollbar-color: var(--rule-2) transparent; }

.sheet { max-width: 1440px; margin: 0 auto; padding-inline: clamp(16px, 3vw, 40px); padding-block: var(--s-6); }

/* 표제부 */
.head { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: var(--s-5); align-items: end;
  border-bottom: 3px double var(--rule); padding-bottom: var(--s-4); }
.head h1 { font: 800 clamp(2rem, 3.4vw, 2.75rem)/1.1 var(--f-title); letter-spacing: .02em; margin: 0; text-wrap: balance; }
.head .sub { margin: var(--s-2) 0 0; color: var(--ink-2); }
.issue { display: grid; grid-template-columns: auto auto; gap: 0 var(--s-4); font-size: .85rem; color: var(--ink-2); text-align: right; }
.issue dt { letter-spacing: .08em; }
.issue dd { margin: 0; font: 500 .9rem var(--f-num); font-variant-numeric: tabular-nums; color: var(--ink); }

/* 결재란: 왼쪽 세로 표제 칸 + 칸마다 머리 칸과 건수 */
.ledger { display: grid; grid-template-columns: 2.4rem minmax(0, 1fr); margin-top: var(--s-5); border: 1px solid var(--rule); }
.lg-title { display: grid; place-items: center; background: var(--cell); border-right: 1px solid var(--rule);
  font: 800 .95rem/1.25 var(--f-title); letter-spacing: .2em; writing-mode: vertical-rl; }
.lg-cells { display: grid; grid-template-columns: repeat(auto-fit, minmax(128px, 1fr)); }
.lg-cells a, .lg-cells button { display: grid; grid-template-rows: auto 1fr; text-decoration: none; color: inherit;
  border: 0; border-right: 1px solid var(--rule-2); background: none; font: inherit; text-align: center; cursor: pointer; padding: 0; }
.lg-cells > :last-child { border-right: 0; }
.lg-cells .k { background: var(--cell); border-bottom: 1px solid var(--rule); padding: var(--s-1) var(--s-2); font-size: .8rem;
  letter-spacing: .06em; color: var(--ink-2); }
.lg-cells .k small { display: block; font-size: .75rem; letter-spacing: 0; color: var(--ink-3); }
.lg-cells .v { padding: var(--s-3) var(--s-2); font: 700 1.3rem/1.2 var(--f-body); }
.lg-cells .v small { font: 400 .8rem var(--f-body); color: var(--ink-2); margin-left: .15em; }
.lg-cells .is-seal .v { color: var(--seal); }
.lg-cells .is-blue .v { color: var(--blue); }
.lg-cells a:hover .k, .lg-cells button:hover .k { background: var(--blue-soft); }
.lg-cells button[aria-pressed="true"] .k { background: var(--ink); color: var(--paper); }
.lg-cells button[aria-pressed="true"] .k small { color: var(--paper); }

/* 조회란 */
.query { display: flex; flex-wrap: wrap; gap: var(--s-3) var(--s-5); align-items: center; margin-top: var(--s-5); }
.query label { font-size: .85rem; letter-spacing: .08em; color: var(--ink-2); }
.query input { font: inherit; color: var(--ink); background: transparent; border: 0; border-bottom: 1px solid var(--rule);
  padding: var(--s-1) 0; width: min(28rem, 100%); }
.query input::placeholder { color: var(--ink-3); }
.query .count { font: .85rem var(--f-num); color: var(--ink-2); font-variant-numeric: tabular-nums; }

/* 대장 */
.band { margin-top: var(--s-6); }
.band h2 { display: flex; flex-wrap: wrap; gap: var(--s-2) var(--s-4); align-items: baseline; margin: 0 0 var(--s-2);
  font: 800 1.25rem/1.3 var(--f-title); letter-spacing: .04em; }
.band h2 .range { font: 400 .85rem var(--f-body); color: var(--ink-2); letter-spacing: 0; }
.band h2 .n { font: 500 .9rem var(--f-num); color: var(--ink-2); }
.wrap { border: 1px solid var(--rule); }
table { border-collapse: collapse; width: 100%; }
th, td { border-bottom: 1px solid var(--rule-2); border-right: 1px solid var(--rule-2); padding: var(--s-2) var(--s-3);
  text-align: left; vertical-align: top; }
th:last-child, td:last-child { border-right: 0; }
thead th { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 1; background: var(--cell); border-bottom: 1px solid var(--rule);
  font-weight: 600; font-size: .8rem; letter-spacing: .12em; color: var(--ink-2); white-space: nowrap; }
.c-no { width: 3.6rem; text-align: center; font-family: var(--f-num); color: var(--ink-3); }
.c-co { width: 11rem; }
.c-loc { width: 7rem; color: var(--ink-2); }
.c-score { width: 6.2rem; text-align: right; }
.c-seal { width: 4.6rem; text-align: center; }
.c-due { width: 7.4rem; font-size: .88rem; white-space: nowrap; }
.co { font-weight: 600; }
.title { display: block; }
.title a { color: var(--ink); text-decoration-color: var(--rule-2); }
.title a:hover { color: var(--blue); text-decoration-color: currentColor; }
.new { display: inline-block; margin-top: 2px; padding: 0 .3em; border: 1px solid var(--ink); color: var(--ink);
  font: 600 .75rem/1.45 var(--f-body); letter-spacing: .08em; }
.score { font: 600 1.05rem var(--f-num); }
.score small { color: var(--ink-3); font-weight: 400; font-size: .75rem; }
.open { margin-top: 2px; font: .72rem var(--f-body); color: var(--blue); background: none; border: 0; padding: 0; cursor: pointer;
  text-decoration: underline; text-underline-offset: 3px; text-decoration-color: var(--rule-2); }
.open:hover { text-decoration-color: currentColor; }
.due-soon { display: inline-block; padding: 0 .3em; border: 1px solid var(--ink); color: var(--ink); font-weight: 700; }
.caution { display: inline-block; margin-right: .35em; padding: 0 .3em; border: 1px solid var(--ink); color: var(--ink);
  font-size: .78rem; font-weight: 600; letter-spacing: .06em; }
.due-past { color: var(--ink-3); text-decoration: line-through; }
.reason { color: var(--ink-2); max-width: 60ch; }

/* 도장 */
.seal { display: inline-grid; place-items: center; width: 2.9rem; height: 2.9rem; border: 2px solid var(--seal); border-radius: 50%;
  color: var(--seal); font: 800 .9rem/1 var(--f-title); letter-spacing: .02em; transform: rotate(var(--r, -9deg));
  box-shadow: inset 0 0 0 2px var(--paper), inset 0 0 0 3px var(--seal); opacity: .9; }
.stamp-blue { display: inline-grid; place-items: center; width: 2.6rem; height: 2.6rem; border: 1.5px solid var(--blue);
  color: var(--blue); font: 700 .78rem/1.05 var(--f-title); letter-spacing: .05em; }
.stamp-grey { color: var(--ink-3); font-size: .82rem; letter-spacing: .08em; }
.stamp-check { display: inline-block; padding: 0 .35em; border: 1px dashed var(--ink-3); color: var(--ink-2); font-size: .78rem; }

/* 구간이 내려갈수록 먹이 옅어진다 */
.band[data-band="보류"] .co, .band[data-band="보류"] .title a, .band[data-band="보류"] .score { color: var(--ink-2); font-weight: 500; }
.band[data-band="확인"] .co, .band[data-band="확인"] .title a { color: var(--ink-3); font-weight: 500; }

/* 첨부: 붙임 1. 항목별 점수 — 점선 지시선으로 이은 서식 행 */
tr.att td { background: var(--cell-2); padding: var(--s-3) var(--s-4); }
.att-doc { display: grid; grid-template-columns: minmax(0, 22rem) minmax(0, 1fr); gap: var(--s-2) var(--s-6);
  margin-left: calc(3.6rem + var(--s-3)); padding-left: var(--s-4); border-left: 1px solid var(--rule); }
.att-no { grid-column: 1 / -1; margin: 0; font: 700 .85rem var(--f-title); letter-spacing: .06em; }
.leaders { list-style: none; margin: 0; padding: 0; display: grid; gap: 2px; }
.leaders li { display: flex; align-items: baseline; gap: var(--s-2); }
.leaders span { color: var(--ink-2); font-size: .85rem; }
.leaders i { flex: 1; border-bottom: 1px dotted var(--ink-3); transform: translateY(-.3em); }
.leaders b { font-weight: 700; }
.att-meta { margin: 0; align-self: end; font-size: .82rem; color: var(--ink-2); }

/* 지원 기록 */
.apps td.st { white-space: nowrap; font-weight: 600; }
.apps .st-fail { color: var(--ink-3); text-decoration: line-through; font-weight: 500; }
.apps .st-live { color: var(--blue); }

.empty { margin-top: var(--s-5); padding: var(--s-5); border: 1px dashed var(--rule-2); color: var(--ink-2); text-align: center; }
.foot { margin-top: var(--s-6); padding-top: var(--s-4); border-top: 3px double var(--rule); display: flex; flex-wrap: wrap;
  gap: var(--s-3) var(--s-6); font-size: .8rem; color: var(--ink-2); }
.foot .legend { display: flex; flex-wrap: wrap; gap: var(--s-4); align-items: center; }
.foot .legend .seal { transform: scale(.72) rotate(-9deg); }
.foot .legend .stamp-blue { transform: scale(.72); }
.demo-note { margin-top: var(--s-3); padding: var(--s-2) var(--s-3); border: 1px dashed var(--ink); color: var(--ink); font-size: .85rem; }
.closing { margin: var(--s-6) 0 0; text-align: right; font: 700 1rem/1.6 var(--f-title); letter-spacing: .04em; }

/* 도장 찍히는 순간: 이미 보이는 상태에서 살짝 눌리며 자리를 잡는다 */
@media (prefers-reduced-motion: no-preference) {
  .seal { animation: press .5s cubic-bezier(.16, 1, .3, 1) both; animation-delay: calc(var(--i, 0) * 45ms); }
  @keyframes press { from { transform: rotate(var(--r, -9deg)) scale(1.28); opacity: .55; } to { transform: rotate(var(--r, -9deg)) scale(1); opacity: .9; } }
}
@media (max-width: 720px) {
  .head { grid-template-columns: 1fr; }
  .issue { text-align: left; }
  .band[data-band] thead { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
  .band[data-band] table, .band[data-band] tbody { display: block; }
  .band[data-band] tr[data-row] { display: grid; grid-template-columns: 2rem minmax(0, 1fr) auto auto;
    grid-template-areas: "no co score seal" "no title title seal" "no due loc loc" "no reason reason reason";
    gap: var(--s-1) var(--s-3); padding: var(--s-3); border-bottom: 1px solid var(--rule-2); }
  .band[data-band] tr[data-row] > td { border: 0; padding: 0; width: auto; }
  .band[data-band] .c-no { grid-area: no; } .band[data-band] .c-co { grid-area: co; } .band[data-band] .c-title { grid-area: title; }
  .band[data-band] .c-loc { grid-area: loc; font-size: .85rem; } .band[data-band] .c-score { grid-area: score; }
  .band[data-band] .c-seal { grid-area: seal; } .band[data-band] .c-due { grid-area: due; }
  .band[data-band] .reason { grid-area: reason; font-size: .88rem; }
  .band[data-band] tr.att { display: block; } .band[data-band] tr.att > td { display: block; }
  .att-doc { grid-template-columns: 1fr; margin-left: 0; }
  .apps thead { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
  .apps table, .apps tbody { display: block; }
  .apps tr { display: grid; grid-template-columns: 2rem minmax(0, 1fr) auto;
    grid-template-areas: "no co st" "no role date" "no memo memo"; gap: var(--s-1) var(--s-3); padding: var(--s-3);
    border-bottom: 1px solid var(--rule-2); }
  .apps tr > td { border: 0; padding: 0; width: auto; }
  .apps .a-no { grid-area: no; } .apps .a-co { grid-area: co; } .apps .st { grid-area: st; }
  .apps .a-role { grid-area: role; } .apps .a-date { grid-area: date; font-size: .85rem; } .apps .a-memo { grid-area: memo; font-size: .88rem; }
}
"""

JS = r"""
(function () {
  var q = document.getElementById('q'), soon = document.getElementById('soon'), count = document.getElementById('count'),
      empty = document.getElementById('empty'), rows = Array.prototype.slice.call(document.querySelectorAll('tr[data-row]'));
  function apply() {
    var t = (q.value || '').trim().toLowerCase(), onlySoon = soon.getAttribute('aria-pressed') === 'true', shown = 0;
    rows.forEach(function (r) {
      var ok = (!t || r.getAttribute('data-text').indexOf(t) >= 0) && (!onlySoon || r.getAttribute('data-soon') === '1');
      r.hidden = !ok;
      var att = document.getElementById(r.getAttribute('data-att'));
      if (att && !ok) att.hidden = true;
      if (ok) shown++;
    });
    document.querySelectorAll('section.band[data-band]').forEach(function (s) {
      var n = s.querySelectorAll('tr[data-row]:not([hidden])').length;
      s.hidden = n === 0;
      var el = s.querySelector('.n'); if (el) el.textContent = n + '건';
    });
    count.textContent = (t || onlySoon) ? ('조건에 맞는 공고 ' + shown + '건') : ('전체 ' + rows.length + '건');
    empty.hidden = shown !== 0;
  }
  q.addEventListener('input', apply);
  soon.addEventListener('click', function () {
    soon.setAttribute('aria-pressed', soon.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); apply();
  });
  document.addEventListener('click', function (e) {
    var b = e.target.closest('button.open'); if (!b) return;
    var att = document.getElementById(b.getAttribute('aria-controls')), open = b.getAttribute('aria-expanded') === 'true';
    att.hidden = open; b.setAttribute('aria-expanded', open ? 'false' : 'true'); b.textContent = open ? '항목별 점수' : '접기';
  });
  apply();
})();
"""


def _e(s) -> str:
    return html.escape(str(s or ""), quote=True)


def _due(v: str, today: date):
    if not v:
        return "—", "", False
    if v == "상시":
        return "상시", "", False
    d = date.fromisoformat(v)
    left = (d - today).days
    if left < 0:
        return f"{v[5:].replace('-', '.')}", "due-past", False
    return (f"{v[5:].replace('-', '.')} · D-{left}" if left <= 7 else v[5:].replace("-", "."),
            "due-soon" if left <= 7 else "", left <= 7)


def _reason(text: str) -> str:
    """판정 메모의 ⚠ 같은 기호는 먹 테두리 '주의' 표식으로."""
    t = _e(text)
    return re.sub(r"^\s*⚠\ufe0f?\s*", '<span class="caution">주의</span>', t)


def _stamp(verdict: str) -> str:
    if verdict == "지원 권장":
        return '<span class="seal" aria-label="지원 권장">지원<br>권장</span>'
    if verdict == "지원 고려":
        return '<span class="stamp-blue" aria-label="지원 고려">지원<br>고려</span>'
    if verdict == "보류":
        return '<span class="stamp-grey">보류</span>'
    return '<span class="stamp-check">확인 필요</span>'


def body(data: dict) -> str:
    today = date.fromisoformat(data["today"])
    rows, apps = data["rows"], data["apps"]
    by = {k: [r for r in rows if r["verdict"] == v] for k, v, _ in BANDS}
    for k in by:
        by[k].sort(key=lambda r: -(r["score"] or 0))
    soon_n = sum(1 for r in rows if _due(r["closes"], today)[2])
    new_n = sum(1 for r in rows if r["new"])
    live = [a for a in apps if a["state"] != "불합격"]
    out = []
    out.append('<main class="sheet">')
    out.append('<header class="head"><div><h1>공고 현황</h1>'
               f'<p class="sub">대기 중인 공고 {len(rows)}건 · {_e(data["since"])} 이후 새로 찾은 공고 {new_n}건</p></div>'
               f'<dl class="issue"><dt>발급일</dt><dd>{_e(data["today"])}</dd>'
               f'<dt>발급 번호</dt><dd>제 {today:%Y}-{today:%m%d} 호</dd></dl></header>')
    if data.get("demo"):
        out.append('<p class="demo-note">견본입니다. 회사와 공고는 모두 가상이며 실제 지원 기록이 아닙니다.</p>')
    cells = []
    for k, v, rng in BANDS:
        cls = "is-seal" if k == "권장" else "is-blue" if k == "고려" else ""
        cells.append(f'<a class="{cls}" href="#band-{k}"><span class="k">{v}<small>{rng}</small></span>'
                     f'<span class="v">{len(by[k])}<small>건</small></span></a>')
    cells.append(f'<button type="button" id="soon" aria-pressed="false"><span class="k">마감 7일 이내<small>눌러서 이것만 보기</small></span>'
                 f'<span class="v">{soon_n}<small>건</small></span></button>')
    cells.append(f'<a href="#apps"><span class="k">지원 기록<small>진행 중 / 전체</small></span>'
                 f'<span class="v">{len(live)}<small>/ {len(apps)}건</small></span></a>')
    out.append('<nav class="ledger" aria-label="판정별 건수"><div class="lg-title" aria-hidden="true">판정</div>'
               '<div class="lg-cells">' + "".join(cells) + "</div></nav>")
    out.append('<div class="query"><label for="q">조회</label>'
               '<input id="q" type="search" placeholder="회사, 포지션, 근거로 찾기" autocomplete="off">'
               '<span class="count" id="count" aria-live="polite"></span></div>')

    i = 0
    for k, v, rng in BANDS:
        if not by[k]:
            continue
        out.append(f'<section class="band" id="band-{k}" data-band="{k}"><h2>{v}<span class="range">{rng}</span>'
                   f'<span class="n">{len(by[k])}건</span></h2><div class="wrap"><table>'
                   '<thead><tr><th class="c-no">번호</th><th class="c-co">회사</th><th>포지션</th><th class="c-loc">근무지</th>'
                   '<th class="c-score">점수</th><th class="c-seal">판정</th><th class="c-due">마감</th><th>비고</th></tr></thead><tbody>')
        for n, r in enumerate(by[k], 1):
            i += 1
            due, due_cls, soon = _due(r["closes"], today)
            att_id = f"att-{i}"
            text = " ".join([r["company"], r["title"], r["reason"], r["location"]]).lower()
            score = f'{r["score"]:.1f}<small>/5</small>' if r["score"] is not None else "—"
            opener = (f'<br><button type="button" class="open" aria-expanded="false" aria-controls="{att_id}">항목별 점수</button>'
                      if r["parts"] else "")
            out.append(f'<tr data-row data-att="{att_id}" data-soon="{1 if soon else 0}" data-text="{_e(text)}">'
                       f'<td class="c-no">{n}{"<br><span class=new>신규</span>" if r["new"] else ""}</td>'
                       f'<td class="c-co"><span class="co">{_e(r["company"])}</span></td>'
                       f'<td class="c-title"><span class="title"><a href="{_e(r["url"])}" target="_blank" rel="noopener">{_e(r["title"])}</a></span></td>'
                       f'<td class="c-loc">{_e(r["location"])}</td>'
                       f'<td class="c-score"><span class="score">{score}</span>{opener}</td>'
                       f'<td class="c-seal" style="--i:{min(n - 1, 12)};--r:{-9 + (n * 37) % 9 - 4}deg">{_stamp(r["verdict"])}</td>'
                       f'<td class="c-due"><span class="{due_cls}">{_e(due)}</span></td>'
                       f'<td class="reason">{_reason(r["reason"])}</td></tr>')
            if r["parts"]:
                items = "".join(f'<li><span>{name}</span><i></i><b>{r["parts"].get(key, 0):.1f}</b></li>' for key, name in PART_NAMES)
                items += f'<li><span>신호·가점</span><i></i><b>{r["bonus"]:+.1f}</b></li>'
                caps = " · ".join(_e(c) for c in r["caps"])
                meta = (f'등급 {_e(r["band"])}<br>' if r.get("band") else "") + (f'상한·검토: {caps}<br>' if caps else "") + f'판정 파일 <code>{_e(r["judgment"])}</code>' + \
                       (f'<br>처음 찾은 날 {_e(r["seen"])}' if r["seen"] else "")
                out.append(f'<tr class="att" id="{att_id}" hidden><td colspan="8"><div class="att-doc">'
                           f'<p class="att-no">붙임 {n}. 항목별 점수 (1–5)</p><ul class="leaders">{items}</ul>'
                           f'<p class="att-meta">{meta}</p></div></td></tr>')
        out.append("</tbody></table></div></section>")
    out.append('<p class="empty" id="empty" hidden>조건에 맞는 공고가 없습니다. 조회어를 지우거나 "마감 7일 이내"를 다시 눌러 해제하세요.</p>')

    out.append('<section class="band apps" id="apps"><h2>지원 기록<span class="range">지원 현황표 기준</span>'
               f'<span class="n">{len(apps)}건</span></h2><div class="wrap"><table>'
               '<thead><tr><th class="c-no">번호</th><th class="c-due">기록일</th><th class="c-co">회사</th><th>포지션</th>'
               '<th class="c-loc">상태</th><th>메모</th></tr></thead><tbody>')
    for a in sorted(sorted(apps, key=lambda a: a["date"], reverse=True), key=lambda a: a["state"] == "불합격"):   # 진행 중 먼저, 최근 순
        st_cls = "st-fail" if a["state"] == "불합격" else "st-live"
        out.append(f'<tr><td class="c-no a-no">{a["no"]}</td><td class="c-due a-date">{_e(a["date"])}</td><td class="c-co co a-co">{_e(a["company"])}</td>'
                   f'<td class="a-role">{_e(a["role"])}</td><td class="st {st_cls}">{_e(a["state"])}</td><td class="reason a-memo">{_e(a["memo"][:120])}</td></tr>')
    out.append("</tbody></table></div></section>")

    out.append('<p class="closing">위와 같이 대기 중인 공고 현황을 발급합니다. 끝.</p>')
    out.append('<footer class="foot"><div class="legend"><span class="seal" style="animation:none">지원<br>권장</span>4.0 이상'
               '<span class="stamp-blue">지원<br>고려</span>3.5 – 3.9<span class="stamp-grey">보류</span>3.0 – 3.4</div>'
               '<p>점수는 공고 줄마다 매긴 판정을 <code>scripts/score.py</code>가 계산한 값입니다. '
               '마감이 7일 안에 오면 마감 칸에 D-일수를 칸 테두리로 표시합니다. 발급: <code>scripts/report_html.py</code></p></footer>')
    out.append("</main>")
    return "\n".join(out)


FONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@700;800&amp;display=swap">'


def fragment(data: dict) -> str:
    """문서 뼈대 없는 판 (Artifact 가 뼈대를 씌운다)."""
    return f"<title>공고 현황</title>\n{FONT}\n<style>{CSS}</style>\n{body(data)}\n<script>{JS}</script>\n"


def document(data: dict) -> str:
    return ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<meta name="report-since" content="{_e(data["since"])}">\n<meta name="report-issued" content="{_e(data["today"])}">\n'
            f'<title>공고 현황</title>\n{FONT}\n<style>{CSS}</style>\n</head>\n<body>\n{body(data)}\n<script>{JS}</script>\n</body>\n</html>\n')


def _since(out: str, today: date) -> str:
    """지난번 현황표의 발급일. 같은 날 다시 만들면 그 판의 기준일을 그대로 쓴다. 처음이면 7일 전."""
    prev = K.read_text(out) or ""
    issued = re.search(r'name="report-issued" content="([\d-]+)"', prev)
    since = re.search(r'name="report-since" content="([\d-]+)"', prev)
    if issued and issued.group(1) == today.isoformat() and since:
        return since.group(1)
    return issued.group(1) if issued else (today - timedelta(days=7)).isoformat()


def main(argv=None):
    ap = argparse.ArgumentParser(description="공고 현황표 HTML")
    ap.add_argument("-o", "--out", default=os.path.join(K.DATA, "search", "reports", "postings.html"))
    ap.add_argument("--fragment", help="문서 뼈대 없는 판도 이 경로에 쓴다 (Claude Artifact 등)")
    ap.add_argument("--demo", action="store_true", help="가상 회사 견본으로 그린다")
    ap.add_argument("--today", help="기준일 YYYY-MM-DD (기본: 오늘)")
    ap.add_argument("--since", help="이 날 이후 처음 찾은 공고에 신규 표시 (기본: 지난번 현황표 발급일)")
    a = ap.parse_args(argv)
    today = date.fromisoformat(a.today) if a.today else date.today()
    data = demo(today) if a.demo else collect(today, a.since or _since(a.out, today))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    K.write_text(a.out, document(data))
    print(f"공고 현황표: {a.out} ({len(data['rows'])}건)")
    if a.fragment:
        os.makedirs(os.path.dirname(os.path.abspath(a.fragment)), exist_ok=True)
        K.write_text(a.fragment, fragment(data))
        print(f"뼈대 없는 판: {a.fragment}")


if __name__ == "__main__":
    main()
