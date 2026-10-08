# -*- coding: utf-8 -*-
"""우아한형제들 (career.woowahan.com, 2026-09-30 실측).

목록: /w1/recruits?page=N&size=50 (JSON, data.list · totalPageNumber). 연차는 careerRestrictionMin/MaxYears
본문: /w1/recruits/{recruitNumber} 의 data.recruitContents (HTML). 없는 공고는 code 9002
공고 URL: /recruitment/{recruitNumber}/detail
"""
import json
from typing import List, Optional

from jobkit import Job, ShapeError, html_text, http_get

BASE = "https://career.woowahan.com"


def _get(path: str) -> dict:
    status, body = http_get(BASE + path)
    if status != 200:
        raise ShapeError(f"우아한형제들 HTTP {status}: {path}")
    try:
        return json.loads(body)
    except ValueError:
        raise ShapeError(f"우아한형제들 JSON 아님: {path}")


def collect(cfg: dict) -> List[Job]:
    jobs, page = [], 0
    while True:
        d = (_get(f"/w1/recruits?page={page}&size=50") or {}).get("data") or {}
        if not isinstance(d.get("list"), list):          # 공고가 없어도 data.list: [] 가 온다 (2026-10-08 실측)
            raise ShapeError("우아한형제들 목록에 data.list 없음")
        for x in d["list"]:
            end = (x.get("recruitEndDate") or "")[:10]
            jobs.append(Job("woowa", x["recruitNumber"], f"{BASE}/recruitment/{x['recruitNumber']}/detail",
                            cfg.get("name") or "우아한형제들", x["recruitName"], location="서울 송파",
                            closes_at="상시" if end.startswith("9999") or not end else end,
                            extra=dict(career=(x.get("careerRestrictionMinYears"), x.get("careerRestrictionMaxYears")))))
        page += 1
        if page >= int(d.get("totalPageNumber") or 0):
            break
    return jobs


def detail(job: Job) -> str:
    d = _get(f"/w1/recruits/{job.id}").get("data") or {}
    return html_text(d.get("recruitContents") or "")


def handles(url: str) -> bool:
    return "career.woowahan.com/recruitment/" in url


def alive(url: str) -> Optional[bool]:
    num = url.rstrip("/").split("/recruitment/")[-1].split("/")[0]
    try:
        d = _get(f"/w1/recruits/{num}")
    except ShapeError:
        return None
    return bool(d.get("data")) and not (d["data"].get("isAfterOrEqualEndDay") and not d["data"].get("isUnlimitedEndDate"))
