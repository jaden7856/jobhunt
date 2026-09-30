# 공고 점수 기준

1차 선별(`modes/scan.md` 4단계)과 전체 평가(`modes/evaluate.md`)가 같은 기준을 쓴다.
**Claude는 공고를 한 줄씩 분류만 하고, 점수는 `scripts/score.py`가 계산한다.** 같은 분류면 언제나 같은 점수가 나오고, 어느 항목에서 깎였는지 남는다.

## 왜 이렇게 바꿨나 (2026-09-30)

예전 방식(역할 30 · 요구사항 30 · 서사 15 · 근무지 15 · 보상 10을 한 번에 어림)에서 생긴 문제:

| 문제 | 결과 |
|---|---|
| 근무지·보상이 25%인데 조건만 맞으면 거의 만점 | 모든 공고가 3.5 근처에서 시작 |
| 필수 요건을 못 채워도 "빈틈" 한 줄로 끝남 | 필수 미충족 공고가 PASS |
| 요건 키워드가 겹치는지만 봄 | 실제 매일 하는 일이 원하는 방향과 달라도 높은 점수 |
| 우선 기업이면 점수와 관계없이 PASS | 적합도 낮은 공고가 위로 올라옴 |

## 순서

1. 본문을 받는다 (`data/search/inbox/*.md`).
2. 뼈대를 만든다: `python3 scripts/score.py init <본문.md> -o data/search/judgments/<출처>_<id>.yaml`
   - 주요업무·자격요건·우대사항을 줄 단위로 뽑은 초안이다. 절을 잘못 잡은 줄(인재상, 기술 스택 나열, 복지)은 지우고, 빠진 줄은 넣는다.
3. 아래 기준으로 빈칸을 채운다. 근거가 필요한 줄은 `why:` 에 내 경험을 한 줄로 적는다(근거는 `data/experience/` 등 1차 자료에서만).
4. `data/profile/calibration.md` 의 교정 사례와 닮은 공고인지 확인한다.
5. `python3 scripts/score.py data/search/judgments/<파일>.yaml` 로 점수를 낸다.

## 판정 파일

```yaml
url: https://...
company: 가나다
title: Backend Engineer
gates: { location: pass, language: pass, stack: pass, years: pass, employment: pass, comp: pass }
gate_note: "판정 근거가 된 공고 문장"
work:        # 주요 업무 한 줄씩
  - { line: "실시간 이벤트 수집·배포 시스템 개발", fit: adjacent, why: "MQ 이벤트 파이프라인" }
required:    # 자격요건 한 줄씩
  - { line: "Go 서버 개발 3년 이상", met: "yes" }
  - { line: "AWS 운영 경험", met: "no", gap: bridge, why: "온프렘 K8s 배포로 설명" }
preferred:   # 우대사항 한 줄씩
  - { line: "Kafka 운영", met: partial }
direction: { primary: realtime_pipeline, secondary: [distributed_consistency] }
signals: [self_service]
priority: false          # 우선 기업(sources.yaml priority: true)
note: "한 줄 근거"
```

`yes`/`no` 는 따옴표로 감싸도 되고 안 감싸도 된다(스크립트가 맞춘다).

## 분류 기준

**gates** (`targets.yaml` 의 `location`·`gates`·`compensation`): `pass` / `fail` / `unclear`. 하나라도 `fail` 이면 점수 없이 제외. 근무지와 보상은 여기서만 본다.

**work.fit** — 그 업무를 내가 해 봤나

| 값 | 뜻 | 점수 |
|---|---|---|
| `done` | 같은 일을 해 봤다 | 5.0 |
| `adjacent` | 비슷한 일을 해 봤고 면접에서 연결해 설명할 수 있다 | 3.5 |
| `new` | 처음 하는 일 | 1.5 |

**required.met** — `yes` 5.0 · `partial` 3.5 · `no` 는 빈틈 종류로

| gap | 뜻 | 점수 | 상한 |
|---|---|---|---|
| `bridge` | 비슷한 경험으로 설명되는 기술 빈틈 (예: AWS ↔ 온프렘 K8s, Kafka ↔ RabbitMQ) | 2.5 | 없음 |
| `core` | 경력·핵심 도메인 자체가 없음 (예: 결제 도메인 N년 필수, 해 본 적 없는 분야의 전문가 요구) | 1.0 | 1개면 3.4, 2개면 2.9 |
| `core` + `alt: true` | 핵심 빈틈이지만 공고가 "또는 이에 준하는 경험"처럼 대신할 경험을 인정 | 1.75 | 위 상한 +0.2 (핵심 빈틈이 모두 alt 일 때) |

- 사람됨·태도 문장("서비스에 애착", "기술 도전을 즐김", "소통을 잘함")은 required 에 넣지 않는다. 확인할 수 있는 경험·기술만 분류한다.
- 어떤 요건이 core 인지 사용자가 정한 것은 `targets.yaml` 의 `scoring` 주석과 `data/profile/calibration.md` 에 있다. 그대로 따른다.

**preferred.met** — `yes` 1 · `partial` 0.5 · `no` 0 의 평균을 1~5점으로 바꾼다(0개면 3점). 사람됨·태도 문장은 넣지 않는다.

**direction** — 이 자리에서 매일 하는 일이 원하는 방향인가. `primary` 는 팀이 주로 만드는 것, `secondary` 는 곁들여 하는 일.
- 값은 `targets.yaml` 의 `scoring.prefer_work` · `scoring.avoid_work` 키, 둘 다 아니면 `other`.
- primary: 선호 5.0 · 그 외 3.0 · 비선호 1.5. secondary 하나마다 선호 +0.5 · 비선호 −0.5 (1~5 안).
- 요건 문장이 아니라 **주요 업무와 팀 소개**로 판단한다. "문서화", "공통 모듈", "테스트·배포" 같은 어디에나 있는 줄로 방향을 정하지 않는다.

**signals** — `targets.yaml` 의 `scoring.signals` 에 있는 키만 적는다. 공고에 드러난 것만.

## 계산

```
점수 = 업무×0.30 + 필수×0.30 + 우대×0.10 + 방향×0.30 + 신호 합 (+ 우선 기업 가점)
     → 1~5 로 자르고 → 필수 핵심 빈틈 상한 → 업무 적합이 2.5 미만이면 상한 3.9 → 소수 첫째 자리
```

가중치·가점·상한은 `targets.yaml` 의 `scoring` 에서 바꾼다.

| 점수 | 판정 | pipeline 표기 |
|---|---|---|
| 4.0 이상 | 지원 권장 | PASS |
| 3.5 ~ 3.9 | 지원 고려 | PASS |
| 3.0 ~ 3.4 | 보류 | MARGINAL |
| 3.0 미만 | 제외 | FAIL |

## 교정

사용자가 "이 판정은 틀렸다"고 하면:
1. 그 공고의 판정 파일에서 어느 분류가 틀렸는지 찾아 고친다.
2. 분류는 맞는데 점수가 어긋나면 `targets.yaml` 의 `scoring`(선호 업무, 신호, 가중치)을 고친다.
3. `data/profile/calibration.md` 에 한 줄 남긴다: 공고, 이전 판정, 사용자 판단, 새 점수, 교훈.
4. 가중치를 바꿨으면 `python3 scripts/score.py data/search/judgments/*.yaml` 로 전체를 다시 계산해 순위가 뒤집힌 공고를 보여 준다.
