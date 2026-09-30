# -*- coding: utf-8 -*-
"""나인하이어 (*.ninehire.site 또는 회사 도메인에 붙인 나인하이어 채용 사이트, 2026-09-30 실측).

목록: 채용 사이트 첫 화면 __NEXT_DATA__ 의 homepageProps.homepage.companyId →
      https://api.ninehire.com/identity-access/homepage/recruitments?companyId=…
본문: {채용 사이트}/job_posting/{addressKey} 의 __NEXT_DATA__ pageProps.jobPosting.content (HTML)
"""
import json
import re
from typing import List, Optional

from jobkit import Job, ShapeError, html_text, http_get

API = "https://api.ninehire.com/identity-access/homepage/recruitments"
_ND = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)


def _next_data(url: str) -> dict:
    status, body = http_get(url, accept="text/html")
    if status == 404:
        return {}
    m = _ND.search(body)
    if status != 200 or not m:
        raise ShapeError(f"나인하이어 __NEXT_DATA__ 없음: {url}")
    return json.loads(m.group(1))


def _base(url: str) -> str:
    return re.match(r"https?://[^/]+", url).group(0)


def collect(cfg: dict) -> List[Job]:
    base = _base(cfg["careers_url"])
    hp = (((_next_data(base).get("props") or {}).get("pageProps") or {}).get("homepageProps") or {}).get("homepage") or {}
    cid = hp.get("companyId")
    if not cid:
        raise ShapeError(f"나인하이어 companyId 없음: {base}")
    jobs, page = [], 1
    while True:
        status, body = http_get(f"{API}?companyId={cid}&page={page}&countPerPage=50&order=created_at_desc")
        if status != 200:
            raise ShapeError(f"나인하이어 목록 HTTP {status}")
        d = json.loads(body)
        for r in d.get("results") or []:
            if r.get("status") != "in_progress" or r.get("isPrivate"):
                continue
            loc = " ".join(x.get("addressName") or "" for x in r.get("jobLocations") or [])
            car = (r.get("career") or {}).get("range") or {}
            jobs.append(Job(f"ninehire:{base.split('//')[1].split('.')[0]}", r["recruitmentId"], f"{base}/job_posting/{r['addressKey']}",
                            cfg.get("name") or base, r.get("externalTitle") or r["title"], location=loc,
                            closes_at=(r.get("deadlineValue") or "")[:10] or "상시",
                            extra=dict(career=(car.get("over"), car.get("below")), group=(r.get("jobGroup") or {}).get("title"))))
        if page * 50 >= (d.get("count") or 0):
            break
        page += 1
    return jobs


def detail(job: Job) -> str:
    jp = ((_next_data(job.url).get("props") or {}).get("pageProps") or {}).get("jobPosting") or {}
    return html_text(jp.get("content") or "")


def handles(url: str) -> bool:
    return "/job_posting/" in url and ("ninehire" in url or url.count("/") == 4)


def alive(url: str) -> Optional[bool]:
    try:
        pp = (_next_data(url).get("props") or {}).get("pageProps") or {}
    except ShapeError:
        return None
    if not pp:
        return False
    return (pp.get("recruitment") or {}).get("status", "in_progress") == "in_progress" and bool(pp.get("jobPosting"))
