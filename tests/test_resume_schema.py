# -*- coding: utf-8 -*-
"""이력서 yaml 형식 검사 (references/resume.schema.json · check.schema_issues)."""
import json
import os
import re
import unittest

import yaml

from support import HERE

import check

REPO = os.path.dirname(HERE)


def problems(resume):
    return [(i["where"], i["msg"]) for i in check.schema_issues(resume)]


class ResumeSchema(unittest.TestCase):
    def test_example_passes(self):
        with open(os.path.join(REPO, "examples", "example.yaml"), encoding="utf-8") as f:
            self.assertEqual(problems(yaml.safe_load(f)), [])
        self.assertEqual(problems({}), [])

    def test_errors_with_location(self):
        cases = [
            ({"sumary": {"lead": "x"}}, ("(맨 위)", "모르는 키 'sumary' — 'summary' 아닌가요?")),
            ({"projects": [{"title": "t", "rows": [{"label": "결과", "kpi": []}]}]},
             ("projects[0].rows[0]", "모르는 키 'kpi' — 'kpis' 아닌가요?")),
            ({"projects": [{"title": "t", "rows": [{"label": "a", "text": "x", "bullets": ["y"]}]}]},
             ("projects[0].rows[0]", "text · options · bullets · kpis · sub · group 중 하나만 있어야 함")),
            ({"projects": [{"title": "t", "rows": [{"group": {"title": "g", "rows": [{"txt": "x"}]}}]}]},
             ("projects[0].rows[0].group.rows[0]", "모르는 키 'txt' — 'text' 아닌가요?")),
            ({"meta": {"design": "D"}}, ("meta.design", "쓸 수 없는 값 'D' (가능: A, B, C)")),
            ({"meta": {"target_pages": [2]}}, ("meta.target_pages", "2개여야 함 (지금 1개)")),
            ({"meta": {"omit_sections": ["education"]}}, ("meta.omit_sections[0]", "쓸 수 없는 값 'education' (가능: summary, skills, experience, projects, other)")),
            ({"skills": "Go, Java"}, ("skills", "목록이어야 함 (지금 글자)")),
            ({"experience": [{"title": "개발자"}]}, ("experience[0]", "'company' 가 없음")),
            ({"experience": [{"company": "가", "period": None}]}, ("experience[0].period", "글자 또는 숫자이어야 함 (지금 빈 값)")),
            ({"projects": [{"title": str(i)} for i in range(6)]}, ("projects", "5개 이하여야 함 (지금 6개)")),
            ({"projects": [{"title": "t", "options": []}]}, ("projects[0]", "모르는 키 'options' (가능: title, period, role, techs, summary, rows, links)")),
        ]
        for resume, want in cases:
            with self.subTest(want=want):
                self.assertIn(want, problems(resume))

    def test_values_that_render_handles_as_empty(self):
        """render.py 가 `or`·`if` 로 비운 값을 기본값으로 바꾸는 칸은 빈 값을 받는다."""
        r = {"meta": {"job": None, "version": None, "posting": None, "target_pages": 2},
             "header": {"role": None}, "summary": {"lead": None},
             "experience": [{"company": "가", "tenure": None, "intro": None, "period": 2024}]}
        self.assertEqual(problems(r), [])

    def test_check_stops_before_other_checks(self):
        rep = check.run_all({"skills": [{"name": "Backend"}]})
        self.assertEqual([(i["kind"], i["where"]) for i in rep["errors"]], [("형식", "skills[0]")])

    def test_doc_keys_in_schema(self):
        """references/yaml_schema.md 의 '전체 구조'에 나온 키가 모두 스키마에 있다 (둘 중 하나만 고치는 것을 막는다)."""
        with open(os.path.join(REPO, "references", "yaml_schema.md"), encoding="utf-8") as f:
            block = f.read().split("## Full structure", 1)[1].split("```yaml", 1)[1].split("```", 1)[0]
        with open(check.SCHEMA_PATH, encoding="utf-8") as f:
            schema_text = f.read()
        json.loads(schema_text)
        keys = set(re.findall(r"^\s*(?:- )?([a-z_]+):", block, re.M)) | set(re.findall(r"[{,]\s*([a-z_]+):", block))
        missing = sorted(k for k in keys if f'"{k}"' not in schema_text)
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
