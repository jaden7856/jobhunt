# resume-builder

개발자 이력서를 yaml로 쓰고 A4 PDF로 빌드하는 Claude 스킬.

- 내용: `data/resumes/*.yaml` (형식: `references/yaml_schema.md`)
- 모양·빌드: `scripts/render.py` (디자인 A 에디토리얼 / **B 스위스 그리드(기본)** / C 다크 마스트헤드)
- 검사: `scripts/check.py` (페이지 수, 제목 홀로 남음, 링크, 플레이스홀더, 문체)
- 스킬 동작 순서: `SKILL.md`

## 빠른 시작

```bash
bash scripts/setup.sh                                   # Chromium, Noto Sans CJK KR, poppler
cp data/profile/profile.example.yaml data/profile/profile.yaml   # 이름·연락처 입력
python3 scripts/render.py examples/example.yaml --profile data/profile/profile.example.yaml --offline
```

산출물은 `data/output/이름_직무_버전.pdf` 와 페이지별 PNG.

## 회사별 맞춤본

```bash
cp data/resumes/base_service.yaml data/resumes/회사_service.yaml
# meta.version, 프로젝트 순서, SKILLS, 용어를 공고에 맞춰 수정
python3 scripts/render.py data/resumes/회사_service.yaml
```

## 개인정보

`data/` 하위 폴더의 실제 파일은 `.gitignore`로 빠지고 폴더 구조·README·`*.example.*`만 올라간다. 이름·연락처는 코드에 없고 `data/profile/profile.yaml`에서 읽는다.

## 문체 규칙 고치기

금지어·번역투·기호 한도는 `references/style_rules.yaml`에 있다. 목록을 고치면 다음 빌드 검사부터 반영된다.
