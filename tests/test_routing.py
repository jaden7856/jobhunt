# -*- coding: utf-8 -*-
"""공급원 고르기: 공고 주소 → 마감 판정 모듈(for_url), sources.yaml 회사 항목 → 수집 모듈(for_company)."""
import unittest

from support import providers, replay

P = providers


def _name(m):
    return m.__name__.split(".")[-1] if m else None


class Routing(unittest.TestCase):
    def test_for_url(self):
        cases = [
            ("https://www.wanted.co.kr/wd/1001", "wanted"),
            ("https://jumpit.saramin.co.kr/position/501", "jumpit"),
            ("https://kr.linkedin.com/jobs/view/backend-at-ganadalab-3900000001", "linkedin"),
            ("https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=48000001", "saramin"),
            ("https://boards.greenhouse.io/ganadalab/jobs/4001", "greenhouse"),
            ("https://careers.ganadalab.com/?gh_jid=4001", "greenhouse"),
            ("https://jobs.lever.co/ganadalab/0a1b2c3d-0000-4000-8000-000000000001", "lever"),
            ("https://toss.im/career/job-detail?job_id=7001", "toss"),
            ("https://careers.nhn.com/recruits/301", "nhn"),
            ("https://recruit.navercorp.com/rcrt/view.do?annoId=9001", "naver"),
            ("https://career.woowahan.com/recruitment/R2609001/detail", "woowa"),
            ("https://careers.linecorp.com/ko/jobs/3001", "line"),
            ("https://ganadalab.career.greetinghr.com/ko/o/111", "greetinghr"),
            ("https://ganadalab.ninehire.site/job_posting/AbCd1234", "ninehire"),
            ("https://recruit.ganadalab.co.kr/recruit/view/a1b2c3", "hiworks"),
            ("https://careers.ganadalab.com/jobs/detail/11", "htmllinks"),
            ("https://careers.ganadalab.io/jobs/1", "jsonapi"),
            ("https://rabaso.wd3.myworkdayjobs.com/External/job/Seoul/Software-Engineer_R100", "jsonapi"),
            ("https://careers.kakao.com/jobs/P-1001", None),          # 개별 상태 API 없음 → scan 목록 대조
            ("https://careers.unknown-co.com/jobs/1", None),
        ]
        with replay({}):
            for url, want in cases:
                with self.subTest(url=url):
                    self.assertEqual(_name(P.for_url(url)), want)

    def test_for_company(self):
        cases = [
            ({"careers_url": "https://ganadalab.career.greetinghr.com"}, "greetinghr"),
            ({"careers_url": "https://www.rabaso.co.kr/careers", "ats": "greetinghr"}, "greetinghr"),
            ({"careers_url": "https://careers.rabaso.co.kr", "ats": "ninehire"}, "ninehire"),
            ({"careers_url": "https://recruit.ganadalab.co.kr", "ats": "hiworks"}, "hiworks"),
            ({"api": "https://boards-api.greenhouse.io/v1/boards/ganadalab/jobs"}, "greenhouse"),
            ({"ats": "greenhouse", "api": "https://boards-api.greenhouse.io/v1/boards/ganadalab/jobs"}, "greenhouse"),
            ({"ats": "greenhouse", "careers_url": "https://careers.ganadalab.com"}, None),   # 보드 주소(api) 없이는 못 읽음
            ({"api": "https://api.lever.co/v0/postings/ganadalab"}, "lever"),
            ({"careers_url": "https://rabaso.wd3.myworkdayjobs.com/External", "ats": "workday"}, "jsonapi"),
            ({"careers_url": "https://careers.ganadalab.io", "jsonapi": {"list": "x"}}, "jsonapi"),
            ({"careers_url": "https://careers.ganadalab.com/jobs", "links": "/jobs/detail/\\d+"}, "htmllinks"),
            ({"careers_url": "https://toss.im/career/jobs"}, "toss"),
            ({"careers_url": "https://careers.nhn.com/recruits"}, "nhn"),
            ({"careers_url": "https://careers.kakao.com/jobs"}, "kakao"),
            ({"careers_url": "https://recruit.navercorp.com/rcrt/list.do"}, "naver"),
            ({"careers_url": "https://career.navercloudcorp.com/"}, "naver"),
            ({"careers_url": "https://career.woowahan.com/"}, "woowa"),
            ({"careers_url": "https://careers.linecorp.com/ko/jobs"}, "line"),
            ({"careers_url": "https://ganadalab.career.greetinghr.com", "method": "browser"}, None),
            ({"careers_url": "https://careers.unknown-co.com"}, None),
        ]
        for cfg, want in cases:
            with self.subTest(cfg=cfg):
                self.assertEqual(_name(P.for_company(cfg)), want)

    def test_registry(self):
        """BOARDS·BY_ATS 에 든 모듈은 모두 ALL 에도 있어야 alive 가 판정할 수 있다."""
        for m in list(P.BOARDS.values()) + list(P.BY_ATS.values()):
            self.assertIn(m, P.ALL)


if __name__ == "__main__":
    unittest.main()
