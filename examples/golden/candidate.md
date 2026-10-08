# 지원자 (가상 인물, 정답 세트 전용)

정답 판정은 이 파일만 근거로 한다. `data/` 의 실제 사용자 자료는 쓰지 않는다.

## 경력

- 백엔드 개발자 4년차. 가나다커머스(오픈마켓, 월 거래액 300억)에서 주문·정산 도메인 담당, 백엔드 8명 팀의 팀원
- Kotlin · Spring Boot · JPA · MySQL · Redis 로 서버 개발 4년
- Kafka 로 주문 이벤트를 도입하고 운영했다 (토픽 설계, 컨슈머 재처리)
- 결제 대행사(PG) 3곳 연동 모듈을 하나의 인터페이스로 묶었다
- 정산 배치를 재시작 가능한 청크 단위로 다시 짰다 (Spring Batch)
- 주문 API p99 820ms → 240ms (N+1 제거, 캐시 키 재설계)
- 레거시 PHP 주문 API 를 Kotlin 으로 옮겼다
- 인프라: AWS ECS · RDS, Docker, GitHub Actions, Datadog. 서비스 배포·모니터링은 해 봤지만 인프라 전담은 아님

## 해 본 적 없는 것

Python·Django 실무, Go 실무, Terraform 등 IaC, Kubernetes 클러스터 운영, LLM·ML, 증권·주식 매매, 광고 입찰(RTB),
게임 서버, 모바일·프론트엔드, 팀 리딩

## 조건 (gates)

- 근무지: 서울 · 판교 (과천 · 안양은 통근 가능). 원격은 어떤 형태든 괜찮다
- 정규직만. SI · 파견 · 고객사 상주 제외
- 요구 연차가 2~8년 범위를 벗어나면 제외
- 영어 필수 · 영어 면접 공고 제외
- 경험 없는 언어(Go, Python 등)를 필수로 요구하면 제외. 우대에만 있으면 통과
- 연봉 하한 6,000만원 미만을 명시하면 제외

## 선호 (direction · signals 키는 scoring.yaml)

- 하고 싶은 일: `payment_settlement` 결제·정산처럼 돈이 맞아야 하는 시스템, `large_scale_product` 사용자가 많은 B2C 서비스의 API·도메인
- 피하는 일: `admin_only` 어드민·백오피스 화면용 API 위주, `ops_only` 운영·온콜 위주
