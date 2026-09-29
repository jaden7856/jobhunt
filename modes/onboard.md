# 모드: onboard — 처음 설정과 개인화

처음 쓰는 사용자의 `data/`를 채우고, 이후에도 개인화 파일이 비어 있지 않은지 확인한다. 먼저 `modes/_shared.md`를 읽는다.

## 세션 시작 점검

아래 파일이 있는지, 예시(`*.example.*`) 내용 그대로인지 본다.

| 파일 | 없거나 예시 그대로면 |
|---|---|
| `data/profile/profile.yaml` | 이름·연락처를 묻는다. 빌드에 필수 |
| `data/profile/targets.yaml` | 아래 "목표 정하기" |
| `data/experience/project_index.yaml` | `modes/tailor.md` 1단계(자료 수집)로 |
| `data/profile/brief.md` | targets와 project_index로 만든다 |
| `data/search/sources.yaml` | 예시를 복사하고 목표 역할에 맞게 `title_filter`를 고친다 |
| `data/applications/tracker.md` | 빈 표로 만든다 (`modes/track.md` 형식) |

`targets.yaml`이나 `brief.md`가 예시 그대로인데 scan·evaluate를 하려 하면 먼저 알린다: "선별 기준이 아직 예시라 점수가 내 기준이 아닙니다. 먼저 채울까요?"

## 목표 정하기 (AskUserQuestion, 한 번에 1~4문항)

1. 목표 역할 2~4개와 우선순위, 인접 역할(이직 가능하면 고려할 것)
2. 연차 표기, 원하는 연봉 범위와 하한 (세전)
3. 근무지 조건, 재택·출근 선호
4. 제외 조건: 언어(영어 필수 등), 기술 스택(경험 없는 언어 필수 요구), 고용 형태(SI·파견·계약직), 회사 규모
5. 이직 이유와 원하는 환경 (본인 말 그대로 받아 `narrative.exit_story`에)
6. 가점·감점 신호, 우선 기업 기준

답을 `targets.yaml`에 적고, 대표 성과 3~8개(`project_index.yaml`의 `confirmed`만)와 함께 `brief.md`를 만든다. 만든 brief를 보여 주고 확인받는다.

## 계속 배우기

- 평가·선별 후 사용자의 교정은 `_shared.md` 4절대로 바로 반영한다.
- 한 달에 한 번, 또는 지원 결과가 3건 이상 쌓이면 `targets.yaml`·`brief.md`가 최근 판단과 맞는지 점검을 제안한다.
