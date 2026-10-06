# How technical interviews ask — question styles, follow-ups, answer shapes

What `modes/interview.md` uses to ask questions the way Korean backend interviewers do, and to coach answers. Distilled from a working engineer's interview notes (Go · gRPC · MQ · Kubernetes · etcd · PostgreSQL · testing · CS) and public interview guides. When the user keeps their own study notes (path in `data/preferences/standing.md`, "면접 공부 노트"), read the parts that match the posting and prefer the user's wording; this file is the method, the notes are the content.

## Principle for experienced engineers

Interviewers ask CS and language questions of a 5-year engineer not to check memory but to see whether the candidate can **explain a problem from first principles**. So the answer runs:

1. Definition in one line
2. Why it was designed that way (the mechanism, the trade-off)
3. Where it showed up in my own work

With step 3 it is an experienced engineer's answer; without it, a new graduate's. Prepare from the other direction: start from problems already lived through (an OOMKill, a p99 spike, traffic stuck on one pod) and go down to the principle, then generalize — experience → principle → generalization.

## Question styles

| Style | Shape | Example |
|---|---|---|
| Concept + design reason | "What is X, and why was it designed this way?" | Go interfaces vs Java — and why |
| Internals → consequence | "Explain the internal structure; so what happens when …?" | slice header, then pass-by-value or reference |
| Limit + practice | "Is it safe? What happens if …? What do you do in practice?" | concurrent map writes |
| Compare and choose | "What is the fundamental difference, and how do you choose?" | RabbitMQ vs Kafka, pessimistic vs optimistic locking |
| Symptom → diagnosis | "In production you see …; how do you find the cause?" | memory creeping up, 502s during rolling deploys |
| Resume check | "You built X, right? What did you watch out for?" / "You only worked in a single-team setup?" | an operator's reconcile loop |
| Failure / extreme | "If Y dies completely / splits / gets 10× traffic, what breaks first?" | etcd down, 3:2 partition |
| Number check | "You set it to N — why that value?" | probe period and threshold |
| Pressure | a challenge to the candidate's choice | "Isn't that over-engineered?", "Don't tests slow you down?" |
| Integrated design | a problem spanning several technologies | preventing duplicate execution, choosing a data store |
| Most discriminating | "Tell me about the incident you remember most." | — |

Interviewers lean on the resume: every technology and number on it invites the "resume check" and "number check" styles.

## Follow-up patterns

A follow-up digs into the answer just given. Ask one at a time and build on what the user actually said.

| Pattern | Shape |
|---|---|
| Trap in the answer | "그럼 … 하면 항상 …인가요?" — the edge case of the rule just stated |
| Push to the extreme | "크게 만들면 / 많아지면 어떤 문제가 생기죠?" |
| Why not the alternative | "… 이 있는데 왜 항상 그걸 쓰지 않나요?" |
| Same problem, other tool | "Kafka 에서는 같은 문제를 어떻게 풀죠?" |
| Remove the root | "그 의존을 아예 없앨 수는 없나요?" |
| After the fix | "찾은 다음, 재발을 막는 설계 원칙은요?" |
| Lived experience | "실제로 그런 문제를 겪어 보셨나요? 그때 어떻게 했죠?" |
| Deeper diagnosis | "CPU 는 낮은데 지연만 튄다면요?" |
| Worse situation | "그 상태에서 노드 하나가 더 죽으면요?" |
| Challenge a claim | "원인을 먼저 찾지 않는다고요? 원인을 모르면 어떻게 고치죠?" |
| Exact consequence | "정확히 무슨 일이 벌어지나요?" |
| Designer's intent | "왜 언어(시스템)가 그걸 막아 뒀을까요?" |

Two levels deep is the bar: a resume line the user cannot defend two follow-ups deep should be cut or softened.

## Answer shapes

- **Three lines:** conclusion or definition → reason or mechanism → practical consequence or countermeasure. Then stop and let the interviewer pick the follow-up.
- **Split by version or condition:** "지금은 X, 버전 N 이전에는 Y" or "일회성이면 단순안, 반복 제품이면 구조적 해결" — giving the opposite condition is what makes it a trade-off answer.
- **Layers:** walk the layers from cheapest to most expensive (app idempotency → DB constraint/CAS → coordination → infrastructure lock), or by path (client → network → server → DB).
- **Evidence ladder for incidents:** symptom with a number → first hypothesis and why it was dropped → decisive evidence → mitigation first (rollback, scale) → root cause → action items with an owner and a date.
- **Pressure questions:** acknowledge the valid part first, turn it into a cost comparison, state the condition under which the other choice would be right. Never "it was absolutely necessary".
- **Don't know:** say where your knowledge stops ("거기까지는 정확히 모르지만, 제가 아는 범위에서는 …"). A follow-up that finds the edge of knowledge is normal, not a rejection signal; bluffing is.
- **Memory hook:** each concept should reduce to one line the user can recall under stress (the definition, the trap, the one-line rule).

## Topic map for a backend engineer

Use the posting's stack and the resume to choose; the user's notes, when present, hold the answers.

| Area | Typical questions |
|---|---|
| Language (Go) | interfaces and nil, slices, maps and concurrency, value vs pointer receivers, defer, errors and wrapping, embedding vs inheritance, context, closures; scheduler (GMP), GOMAXPROCS in containers, GC tuning, channels vs mutexes, goroutine leaks |
| RPC | why gRPC over REST, protobuf field numbers as the contract, presence in proto3, deadline propagation, load balancing of long-lived connections |
| Messaging | queue vs log, delivery guarantees, idempotency, ordering vs parallelism, exactly-once claims |
| Kubernetes | design philosophy, control plane, requests/limits/QoS, OOMKilled vs Evicted, probes, drain and PDB, operators and leader election, rolling-deploy errors, multi-zone, multi-tenancy, monitoring and alerts, incident story |
| Coordination stores | quorum and odd node counts, partitions, leader election, why Kubernetes uses etcd, Redis vs MongoDB vs RDB, cache invalidation |
| RDB (PostgreSQL) | why this DB, MVCC and VACUUM, indexes (composite order, why not used, adding online), pagination, locking strategy |
| Testing | why test, what not to test, Go table tests, DB and concurrency tests, the "tests slow us down" challenge |
| CS | processes vs threads, virtual memory and OOM, I/O multiplexing, TCP handshakes and TIME_WAIT, HTTP/1.1·2·3, HTTP status codes in diagnosis, deadlock conditions, B-tree vs hash, complexity vs cache locality |
| Integrated | duplicate execution, what breaks at 10× traffic, over-engineering challenge, choosing a store |
