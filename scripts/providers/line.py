# -*- coding: utf-8 -*-
"""라인 (careers.linecorp.com, Gatsby, 2026-09-30 실측).

목록: /page-data/ko/jobs/page-data.json 의 result.data.allStrapiJobs.edges (전 세계 공고) → 한국 도시만
본문: /page-data/ko/jobs/{id}/page-data.json 의 result.data.strapiJobs.content
공고 URL: /ko/jobs/{id}
"""
import json
from typing import List, Optional

from jobkit import Job, ShapeError, html_text, http_get

BASE = "https://careers.linecorp.com"
KOREA = {"Seoul", "Bundang", "Gwacheon"}


def _page(path: str) -> dict:
    status, body = http_get(f"{BASE}/page-data/ko/{path}/page-data.json")
    if status == 404:
        return {}
    if status != 200:
        raise ShapeError(f"라인 page-data HTTP {status}: {path}")
    return (json.loads(body).get("result") or {}).get("data") or {}


def collect(cfg: dict) -> List[Job]:
    edges = ((_page("jobs").get("allStrapiJobs") or {}).get("edges")) or []
    if not edges:
        raise ShapeError("라인 공고 목록(allStrapiJobs) 없음")
    jobs = []
    for e in edges:
        n = e["node"]
        cities = {c["name"] for c in n.get("cities") or []}
        if not (cities & KOREA) or not n.get("publish", True):
            continue
        company = ", ".join(c["name"] for c in n.get("companies") or []) or cfg.get("name") or "LINE"
        jobs.append(Job("line", str(n["strapiId"]), f"{BASE}/ko/jobs/{n['strapiId']}", company, n["title"],
                        location=", ".join(sorted(cities & KOREA)),
                        closes_at="상시" if n.get("until_filled") or not n.get("end_date") else n["end_date"][:10],
                        extra=dict(unit=[u["name"] for u in n.get("job_unit") or []])))
    return jobs


def detail(job: Job) -> str:
    j = _page(f"jobs/{job.id}").get("strapiJobs") or {}
    return html_text(j.get("content") or "")


def handles(url: str) -> bool:
    return "careers.linecorp.com/" in url and "/jobs/" in url


def alive(url: str) -> Optional[bool]:
    jid = url.rstrip("/").split("/jobs/")[-1].split("/")[0]
    try:
        j = _page(f"jobs/{jid}").get("strapiJobs")
    except ShapeError:
        return None
    return bool(j and j.get("publish", True))
