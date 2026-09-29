# -*- coding: utf-8 -*-
"""점핏. 목록 /api/positions?keyword=, 상세 /api/position/{id} (2026-09-29 실측)."""
import re
import urllib.parse
from datetime import datetime
from typing import List, Optional

from jobkit import Job, ShapeError, get_json

API = "https://jumpit-api.saramin.co.kr/api"


def collect(cfg: dict) -> List[Job]:
    jobs, seen = [], set()
    for kw in cfg.get("keywords", ["백엔드"]):
        for page in range(1, cfg.get("max_pages", 10) + 1):
            d = get_json(f"{API}/positions?keyword={urllib.parse.quote(kw)}&sort=reg_dt&page={page}")
            ps = (d.get("result") or {}).get("positions")
            if ps is None:
                raise ShapeError("점핏 목록에 result.positions 없음")
            for p in ps:
                if p["id"] in seen:
                    continue
                seen.add(p["id"])
                jobs.append(Job("jumpit", str(p["id"]), f"https://jumpit.saramin.co.kr/position/{p['id']}",
                                p["companyName"], p["title"], location=" ".join(p.get("locations") or []),
                                extra=dict(career=(p.get("minCareer"), p.get("maxCareer")), newcomer=p.get("newcomer"))))
            if len(ps) < 16:
                break
    return jobs


def _pos(id_: str) -> dict:
    d = get_json(f"{API}/position/{id_}")
    if "result" not in d:
        raise ShapeError("점핏 상세에 result 없음")
    return d["result"]


def detail(job: Job) -> str:
    r = _pos(job.id)
    job.posted_at = (r.get("publishedAt") or "")[:10]
    job.closes_at = (r.get("closedAt") or "")[:10] or "상시"
    job.location = r.get("location") or job.location
    parts = [("주요업무", r.get("responsibility")), ("자격요건", r.get("qualifications")),
             ("우대사항", r.get("preferredRequirements")),
             ("경력", f"{r.get('minCareer')}~{r.get('maxCareer')}년" + (" (신입 가능)" if r.get("newcomer") else "")),
             ("기술스택", ", ".join(s["stack"] for s in r.get("techStacks") or []))]
    return "\n\n".join(f"## {k}\n{v}" for k, v in parts if v)


def handles(url: str) -> bool:
    return "jumpit.saramin.co.kr/position/" in url


def alive(url: str) -> Optional[bool]:
    m = re.search(r"/position/(\d+)", url)
    if not m:
        return None
    closed = (_pos(m.group(1)).get("closedAt") or "")[:19]
    if not closed:
        return True
    return datetime.strptime(closed, "%Y-%m-%d %H:%M:%S") > datetime.now()
