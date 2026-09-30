# -*- coding: utf-8 -*-
"""카카오. /public/api/job-list?part=TECHNOLOGY. 공동체(S-) 공고는 자격요건이 비어 있음 — 외부 사이트 (2026-09-23)."""
from typing import List, Optional

from jobkit import Job, ShapeError, get_json, html_text

API = "https://careers.kakao.com/public/api/job-list?part=TECHNOLOGY&company=ALL&page={}"


def collect(cfg: dict) -> List[Job]:
    jobs, page, total = [], 1, 1
    while page <= total and page <= cfg.get("max_pages", 20):
        d = get_json(API.format(page))
        if "jobList" not in d:
            raise ShapeError("카카오 응답에 jobList 없음")
        total = d.get("totalPage") or 1
        for k in d["jobList"]:
            if k.get("closeFlag") or k.get("companyName") in cfg.get("skip_companies", ()):   # 계열사 채용 사이트로 따로 수집하는 곳
                continue
            text = "\n\n".join(f"## {h}\n{html_text(k.get(f))}" for h, f in
                               (("주요업무", "workContentDesc"), ("자격요건", "qualification")) if (k.get(f) or "").strip())
            if str(k["realId"]).startswith("S-") and len(text) < 50:
                text += "\n\n[공동체 공고 — 본문은 해당 계열사 채용 사이트에서 확인]"
            jobs.append(Job("kakao", str(k["realId"]), f"https://careers.kakao.com/jobs/{k['realId']}", k.get("companyName") or "카카오",
                            k["jobOfferTitle"], location=k.get("locationName") or "", closes_at=(k.get("endDate") or "")[:10] or "상시",
                            text=text))
        page += 1
    return jobs


def detail(job: Job) -> str:
    return job.text


def handles(url: str) -> bool:
    return False    # 개별 공고 상태 API 미확인 → scan 목록 대조로 판정


def alive(url: str) -> Optional[bool]:
    return None
