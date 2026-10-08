# -*- coding: utf-8 -*-
"""판정 정답 세트 (examples/golden · scripts/eval_golden.py): 정답 파일 형식과 score.py 결론이 그대로인지, 비교가 차이를 짚는지."""
import glob
import os
import shutil
import tempfile
import unittest

from support import HERE, K

import eval_golden as E
import score as S

GOLDEN = os.path.join(os.path.dirname(HERE), "examples", "golden")


class Golden(unittest.TestCase):
    def setUp(self):
        self.cfg = K.load_yaml(os.path.join(GOLDEN, "scoring.yaml"))
        self.answers = sorted(glob.glob(os.path.join(GOLDEN, "answers", "*.yaml")))

    def test_cases_paired_and_documented(self):
        names = lambda d, ext: sorted(os.path.basename(p)[:-len(ext)] for p in glob.glob(os.path.join(GOLDEN, d, "*" + ext)))  # noqa: E731
        self.assertGreaterEqual(len(self.answers), 8)
        self.assertEqual(names("answers", ".yaml"), names("postings", ".md"))
        for p in self.answers:
            j = K.load_yaml(p)
            with self.subTest(answer=os.path.basename(p)):
                self.assertTrue(j.get("rule"), "rule: 이 무엇을 확인하는지")
                self.assertIn(j.get("expect"), ["지원 권장", "지원 고려", "보류", "제외"])

    def test_expect_matches_score(self):
        for p in self.answers:
            j = K.load_yaml(p)
            with self.subTest(answer=os.path.basename(p)):
                self.assertEqual(S.score(j, self.cfg)["verdict"], j["expect"])

    def test_answer_lines_come_from_postings(self):
        """정답의 줄은 공고 본문에 있는 문장이어야 에이전트 판정과 짝지어진다."""
        for p in self.answers:
            body = open(os.path.join(GOLDEN, "postings", os.path.basename(p)[:-5] + ".md"), encoding="utf-8").read()
            j = K.load_yaml(p)
            for sec in E.FIELDS:
                for x in j.get(sec) or []:
                    with self.subTest(answer=os.path.basename(p), line=x["line"]):
                        self.assertIn(x["line"], body)

    def test_self_compare_is_perfect(self):
        res = E.run(os.path.join(GOLDEN, "answers"), GOLDEN)
        self.assertTrue(all(not r["missing"] and r["same"] and not r["diffs"] for r in res))
        self.assertEqual(E.main([os.path.join(GOLDEN, "answers"), "--min-lines", "1", "--min-verdicts", "1"]), 0)

    def test_reports_changed_lines(self):
        d = tempfile.mkdtemp(prefix="jobhunt-golden-")
        self.addCleanup(shutil.rmtree, d, True)
        for p in self.answers:
            shutil.copy(p, d)
        path = os.path.join(d, "05_core_gap_alt.yaml")
        s = open(path, encoding="utf-8").read()
        open(path, "w", encoding="utf-8").write(s.replace("gap: core, alt: true", "gap: core"))
        os.remove(os.path.join(d, "10_gate_location.yaml"))
        res = {r["name"]: r for r in E.run(d, GOLDEN)}
        r = res["05_core_gap_alt.yaml"]
        self.assertFalse(r["same"])
        self.assertEqual((r["want"]["verdict"], r["got"]["verdict"]), ("지원 고려", "보류"))
        self.assertEqual(len(r["diffs"]), 1)
        self.assertIn("alt True→False", r["diffs"][0])
        self.assertTrue(res["10_gate_location.yaml"]["missing"])
        self.assertEqual(E.main([d, "--min-verdicts", "0.9"]), 1)


if __name__ == "__main__":
    unittest.main()
