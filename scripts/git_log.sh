#!/usr/bin/env bash
# 로컬 git 저장소에서 작성자 기준 커밋 로그를 뽑는다. 프로젝트 후보를 찾을 때 쓴다.
# 사용: bash scripts/git_log.sh <저장소 경로> "<작성자 이메일|이름 정규식>" [시작일] [종료일]
#   예: bash scripts/git_log.sh ~/work/manager "me@company.com|me@gmail.com" 2023-01-01 2023-12-31
# 출력: data/experience/git_<저장소명>.md (월별로 묶음, revert·rollback 커밋 표시)
set -euo pipefail
REPO="${1:?저장소 경로}"; AUTHOR="${2:?작성자}"; SINCE="${3:-}"; UNTIL="${4:-}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="$(basename "$(cd "$REPO" && pwd)")"
OUT="$ROOT/data/experience/git_${NAME}.md"
RANGE=()
[ -n "$SINCE" ] && RANGE+=(--since="$SINCE")
[ -n "$UNTIL" ] && RANGE+=(--until="$UNTIL")

{
  echo "# $NAME 커밋 로그 (작성자: $AUTHOR, ${SINCE:-처음} ~ ${UNTIL:-현재})"
  echo
  git -C "$REPO" log --all --no-merges -i -E --author="$AUTHOR" "${RANGE[@]}" \
      --date=format:'%Y-%m' --pretty=format:'%ad%x09%h%x09%s' --shortstat \
  | awk -F'\t' '
      /^[0-9]{4}-[0-9]{2}\t/ { if ($1 != m) { m=$1; print "\n## " m } ;
                               flag = ($3 ~ /[Rr]evert|롤백|되돌|하향|폐기/) ? " ⟲" : "";
                               printf "- %s %s%s\n", $2, $3, flag; next }
      /files? changed/ { gsub(/^ +/, ""); print "  (" $0 ")"; next }
    '
  echo
  echo "## 자주 바뀐 파일 (상위 30)"
  git -C "$REPO" log --all --no-merges -i -E --author="$AUTHOR" "${RANGE[@]}" \
      --name-only --pretty=format: | grep -v '^$' | sort | uniq -c | sort -rn | head -30 | sed 's/^/    /' || true
} > "$OUT"
echo "저장: $OUT"
