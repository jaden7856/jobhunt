# -*- coding: utf-8 -*-
"""개인 자료 커밋 방지 (scripts/privacy_check.py · .githooks/pre-commit): 임시 git 저장소에서 실제 커밋으로 확인한다."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from support import HERE

REPO = os.path.dirname(HERE)
PROFILE = "name: 김가상\nemail: gasang.kim@example.org\nphone: 010-9999-8888\neducation:\n  school: 가상대학교\n  major: 컴퓨터공학과\n"


class PrivacyGuard(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="jobhunt-privacy-")
        self.addCleanup(shutil.rmtree, self.dir, True)
        os.makedirs(os.path.join(self.dir, "scripts"))
        shutil.copy(os.path.join(REPO, "scripts", "privacy_check.py"), os.path.join(self.dir, "scripts"))
        shutil.copytree(os.path.join(REPO, ".githooks"), os.path.join(self.dir, ".githooks"))
        shutil.copy(os.path.join(REPO, ".gitignore"), self.dir)
        self.write("data/profile/profile.yaml", PROFILE)
        self.write("data/profile/profile.example.yaml", "name: 홍길동\n")
        self.write("README.md", "# 가상 저장소\n")
        self.git("init", "-q")
        self.git("config", "core.hooksPath", ".githooks")
        self.git("add", ".")
        self.assertEqual(self.commit("처음").returncode, 0)

    def write(self, path, text):
        p = os.path.join(self.dir, path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)

    def git(self, *args):
        return subprocess.run(["git", "-C", self.dir, "-c", "user.name=t", "-c", "user.email=t@example.org", *args],
                              capture_output=True, text=True)

    def commit(self, msg, *extra):
        return self.git("commit", "-q", "-m", msg, *extra)

    def check(self, *args):
        return subprocess.run([sys.executable, os.path.join(self.dir, "scripts", "privacy_check.py"), *args],
                              capture_output=True, text=True)

    def assertBlocked(self, r, *why):
        self.assertNotEqual(r.returncode, 0, r.stderr)
        for w in why:
            self.assertIn(w, r.stderr)
        self.assertNotIn("김가상", r.stderr + r.stdout)          # 막으면서 값을 화면에 다시 찍지 않는다

    def test_initial_commit_kept_profile_out(self):
        self.assertEqual(self.git("ls-files", "data").stdout.split(), ["data/profile/profile.example.yaml"])

    def test_force_added_profile_blocked(self):
        self.git("add", "-f", "data/profile/profile.yaml")
        self.assertBlocked(self.commit("실수"), "data/profile/profile.yaml", "data/ 의 개인 자료", "profile.yaml 의 이름")
        self.assertEqual(self.git("rev-list", "--count", "HEAD").stdout.strip(), "1")

    def test_personal_values_in_other_files_blocked(self):
        self.write("notes.md", "연락처 01099998888\n")
        self.write("docs/a.md", "GASANG.KIM@example.org 로 보내기\n")
        self.git("add", ".")
        self.assertBlocked(self.commit("메모"), "notes.md  ← profile.yaml 의 전화번호", "docs/a.md  ← profile.yaml 의 이메일")

    def test_allowed_files_pass(self):
        self.write("data/search/sources.example.yaml", "companies: []\n")
        self.write("data/search/README.md", "# 검색\n")
        self.write("scripts/x.py", "# 홍길동 은 예시 이름\n")
        self.git("add", "-f", "data/search/sources.example.yaml", "data/search/README.md", "scripts/x.py")
        r = self.commit("허용")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_value_already_public_is_skipped(self):
        self.write("LICENSE", "Copyright 김가상\n")
        self.git("add", "LICENSE")
        self.commit("공개", "--no-verify")
        self.write("README.md", "# 가상 저장소\n만든 사람: 김가상\n")
        self.git("add", "README.md")
        r = self.commit("이름")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("이름은(는) 이미 저장소에 있어", r.stderr)

    def test_tracked_mode_for_ci(self):
        self.assertEqual(self.check().returncode, 0)
        self.git("add", "-f", "data/profile/profile.yaml")
        self.commit("건너뜀", "--no-verify")
        self.assertBlocked(self.check(), "data/profile/profile.yaml")


if __name__ == "__main__":
    unittest.main()
