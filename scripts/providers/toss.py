# -*- coding: utf-8 -*-
"""토스 전 계열사. 본문은 content 가 아니라 metadata 의 "Job Description" 필드 (2026-09-23 누락 사고 후).

우산 공고("집중 채용" 등)는 본문의 하위 포지션 링크를 extra.children 으로 모은다. 하위 포지션은 공개 목록에서
숨겨질 수 있으므로 마감 판정은 job-detail 페이지로 한다.
"""
import re
from typing import List, Optional

from jobkit import Job, ShapeError, get_json, html_text, http_get

API = "https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs"


def _meta(j: dict, needle: str) -> str:
    for m in j.get("metadata") or []:
        if needle in (m.get("name") or ""):
            v = m.get("value")
            return ", ".join(map(str, v)) if isinstance(v, list) else str(v or "")
    return ""


def collect(cfg: dict) -> List[Job]:
    d = get_json(API)
    if not isinstance(d.get("success"), list):
        raise ShapeError("토스 응답에 success 목록 없음")
    jobs = []
    for j in d["success"]:
        body = html_text(_meta(j, "Job Description"))
        children = sorted(set(re.findall(r"(?:grnh\.se/[\w]+|job_id=\d+)", body)))
        sub = _meta(j, "소속 자회사") or "토스"
        jobs.append(Job("toss", str(j["id"]), f"https://toss.im/career/job-detail?job_id={j['id']}", sub, j["title"],
                        location=(j.get("location") or {}).get("name", ""), posted_at=(j.get("first_published") or "")[:10],
                        text=body, extra=dict(children=children)))
    return jobs


def detail(job: Job) -> str:
    if job.extra.get("children"):
        return job.text + "\n\n## 하위 포지션 링크 (우산 공고 — 각각 판정, 보통 1개만 지원 가능)\n" + "\n".join(job.extra["children"])
    return job.text


def handles(url: str) -> bool:
    return "toss.im/career" in url


def alive(url: str) -> Optional[bool]:
    m = re.search(r"(?:job_id|gh_jid)=(\d+)", url)
    if not m:
        return None
    status, body = http_get(f"https://toss.im/career/job-detail?job_id={m.group(1)}", accept="text/html")
    if status == 404:
        return False
    if status != 200:
        return None
    t = re.search(r"<title>(.*?)</title>", body, re.S)
    return bool(t and t.group(1).strip() and "토스 채용" != t.group(1).strip())
