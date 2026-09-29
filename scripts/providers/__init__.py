# -*- coding: utf-8 -*-
"""공고 공급원. 모듈마다 같은 세 함수를 둔다.

  collect(cfg) -> List[Job]   목록 (가능하면 본문까지)
  detail(job)  -> str         본문(자격요건·우대·주요업무). 목록에 본문이 있으면 job.text 를 그대로
  alive(url)   -> Optional[bool]   True 활성 / False 마감 / None 판정 불가
  handles(url) -> bool        alive 가 이 URL 을 판정할 수 있는지

방법과 실측 날짜는 references/sources.md. 형식이 바뀌면 ShapeError 를 올려 "응답 형식 변경"으로 보고한다.
"""
from . import greenhouse, greetinghr, jumpit, kakao, linkedin, nhn, toss, wanted

BOARDS = {"wanted": wanted, "jumpit": jumpit, "linkedin": linkedin}
ALL = [wanted, jumpit, linkedin, greenhouse, toss, nhn, kakao, greetinghr]


def for_company(c: dict):
    """sources.yaml companies 항목 → 공급원 모듈 (없으면 None: 브라우저·수동 대상)."""
    api, url = c.get("api") or "", c.get("careers_url") or ""
    if c.get("method") == "browser":
        return None
    if "greenhouse.io" in api:
        return greenhouse
    if "toss.im" in url:
        return toss
    if "careers.nhn.com" in url:
        return nhn
    if "careers.kakao.com" in url:
        return kakao
    if ".career.greetinghr.com" in url:
        return greetinghr
    return None


def for_url(url: str):
    for m in ALL:
        if m.handles(url):
            return m
    return None
