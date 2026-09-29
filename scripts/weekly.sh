#!/usr/bin/env bash
# 주간 스캔의 LLM 없는 부분: 수집 → 마감 확인 → 통합 보고표.
# 1차 선별(brief.md 기준)과 평가는 Claude 가 이어서 한다 (modes/scan.md 4단계부터).
# 사용: bash scripts/weekly.sh [--since YYYY-MM-DD]   (기본: 7일 전)
# cron/launchd 로 돌려도 된다. 결과: data/search/reports/YYYY-MM-DD.md
set -uo pipefail
cd "$(dirname "$0")/.."

since="$(date -v-7d +%F 2>/dev/null || date -d '7 days ago' +%F)"   # macOS / GNU date
[ "${1:-}" = "--since" ] && since="$2"
out="data/search/reports/$(date +%F).md"
mkdir -p data/search/reports

{
  echo "# 주간 스캔 $(date +%F)"
  echo
  echo '```'
  python3 scripts/scan.py 2>&1
  echo
  python3 scripts/alive.py --write 2>&1
  echo '```'
  echo
  python3 scripts/tracker.py report --since "$since" 2>&1
  echo
  echo "다음: Claude 에게 \"새로 수집한 공고 선별해줘\" → modes/scan.md 4단계 (pipeline.md '새로 수집 (선별 전)')"
} > "$out"

echo "보고서: $out"
grep -E "^  |^──" "$out" | head -30
