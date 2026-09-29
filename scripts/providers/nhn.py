# -*- coding: utf-8 -*-
"""NHN. 목록 /v1/job-postings?size=100, 상세 /v1/job-postings/{id}. finishYn·postingYn·applicationUseYn 로 활성 판정."""
import re
from typing import List, Optional

from jobkit import Job, ShapeError, get_json, html_text

API = "https://careers.nhn.com/v1/job-postings"


def _is_open(p: dict) -> bool:
    return p.get("finishYn") == "N" and p.get("postingYn") == "Y" and p.get("applicationUseYn") == "Y"


def collect(cfg: dict) -> List[Job]:
    d = get_json(f"{API}?page=0&size=100")
    if not isinstance(d.get("result"), list):
        raise ShapeError("NHN 응답에 result 목록 없음")
    jobs = []
    for p in d["result"]:
        if not _is_open(p):
            continue
        m = re.match(r"\[([^\]]+)\]", p["name"])
        jobs.append(Job("nhn", p["id"], f"https://careers.nhn.com/recruits/{p['id']}", (p.get("corporation") or {}).get("name", "NHN"),
                        p["name"], location=m.group(1) if m else "", closes_at=(p.get("postingEndDatetime") or "")[:10],
                        extra=dict(career=(p.get("careerType") or {}).get("name"))))
    return jobs


def _strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from _strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from _strings(v)


def detail(job: Job) -> str:
    r = get_json(f"{API}/{job.id}").get("result") or {}
    text = html_text("\n".join(_strings([r.get("introduction"), r.get("jobPostingContentsItems")])))
    if len(text) < 200:
        text += "\n\n[본문이 짧음 — 이미지로 된 공고일 수 있으니 페이지를 직접 확인]"
    return text


def handles(url: str) -> bool:
    return "careers.nhn.com/recruits/" in url


def alive(url: str) -> Optional[bool]:
    m = re.search(r"/recruits/(\d+)", url)
    return None if not m else _is_open(get_json(f"{API}/{m.group(1)}").get("result") or {})
