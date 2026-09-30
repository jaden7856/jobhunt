# -*- coding: utf-8 -*-
"""greetinghr (*.career.greetinghr.com). 목록은 /ko/home 의 __NEXT_DATA__ ["openings"], 본문은 /ko/o/{id} 의
getOpeningById.data.openingsInfo (2026-09-29 실측). __NEXT_DATA__ 가 없는 회사는 브라우저로 읽는다."""
import json
import re
from typing import List, Optional

from jobkit import Job, ShapeError, html_text, http_get

_ND = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)


def _next_data(url: str) -> dict:
    status, body = http_get(url, accept="text/html")
    if status == 404:
        return {}
    m = _ND.search(body)
    if status != 200 or not m:
        raise ShapeError(f"__NEXT_DATA__ 없음 (브라우저로 읽어야 함): {url}")
    return json.loads(m.group(1))


def _query(nd: dict, first_key: str):
    for q in ((nd.get("props") or {}).get("pageProps") or {}).get("dehydratedState", {}).get("queries", []):
        if q.get("queryKey") and first_key in json.dumps(q["queryKey"]):
            return (q.get("state") or {}).get("data")
    return None


def base_of(url: str) -> str:
    return re.match(r"https?://[^/]+", url).group(0)


def collect(cfg: dict) -> List[Job]:
    base = base_of(cfg["careers_url"])
    ops = None
    for url in (f"{base}/ko/home", cfg["careers_url"], base):   # 회사 도메인에 붙인 greetinghr 는 첫 화면에 openings 가 있기도 하다
        try:
            ops = _query(_next_data(url), '"openings"')
        except ShapeError:
            continue
        if isinstance(ops, list):
            break
    if not isinstance(ops, list):
        raise ShapeError(f"greetinghr openings 없음: {base}")
    jobs = []
    for o in ops:
        pos = (o.get("openingJobPosition") or {}).get("openingJobPositions") or [{}]
        place = pos[0].get("workspacePlace") or {}
        occ = (pos[0].get("workspaceOccupation") or {}).get("occupation", "")
        jobs.append(Job(f"greetinghr:{base.split('//')[1].split('.')[0]}", str(o["openingId"]), f"{base}/ko/o/{o['openingId']}",
                        cfg.get("name") or base, o["title"], location=" ".join(x for x in (place.get("place"), place.get("location")) if x),
                        closes_at=(o.get("dueDate") or "")[:10] or "상시", extra=dict(occupation=occ)))
    return jobs


def _longest(o, best=""):
    if isinstance(o, str):
        return o if len(o) > len(best) else best
    for v in (o.values() if isinstance(o, dict) else o if isinstance(o, list) else []):
        best = _longest(v, best)
    return best


def detail(job: Job) -> str:
    d = _query(_next_data(job.url), "getOpeningById") or {}
    return html_text(_longest(((d.get("data") or {}).get("openingsInfo")) or {}))


def handles(url: str) -> bool:
    return ".career.greetinghr.com/ko/o/" in url


def alive(url: str) -> Optional[bool]:
    try:
        d = _query(_next_data(url), "getOpeningById")
    except ShapeError:
        return None
    return bool(d and d.get("success") and (d.get("data") or {}).get("openingsInfo"))
