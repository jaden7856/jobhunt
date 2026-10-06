#!/usr/bin/env bash
# 설치: AI 에이전트 스킬 연결 + 빌드 환경(Python 패키지, Playwright Chromium, 폰트 Pretendard·Noto Sans/Serif CJK KR, poppler)
# 사용: bash scripts/setup.sh              전부
#       bash scripts/setup.sh --skill-only 스킬 연결만
#       bash scripts/setup.sh --no-skill   스킬 연결 없이 빌드 환경만
# 스킬 폴더: 설치된 에이전트를 찾아 연결한다 (~/.claude → ~/.claude/skills, ~/.codex → ~/.codex/skills).
#   다른 에이전트·위치는 SKILLS_DIR=경로[:경로…] 로 지정 (예전 이름 CLAUDE_SKILLS_DIR 도 받음).
#   스킬을 읽지 않는 에이전트는 이 폴더에서 실행하면 AGENTS.md 를 따른다.
set -euo pipefail
cd "$(dirname "$0")/.."

SKILL=1; ENV=1
for a in "$@"; do
  case "$a" in
    --skill-only) ENV=0 ;;
    --no-skill) SKILL=0 ;;
    *) echo "알 수 없는 옵션: $a"; exit 2 ;;
  esac
done

link_skill() {
  # 이 폴더를 그대로 스킬로 연결한다. 복사하지 않으므로 data/ 개인화와 git pull 업데이트가 스킬에 바로 반영된다.
  local repo name dir="$1" dest
  repo="$(pwd -P)"
  name="$(sed -n 's/^name:[[:space:]]*//p' SKILL.md | head -1)"
  dest="$dir/$name"
  mkdir -p "$dir"
  if [ -L "$dest" ]; then
    if [ "$(cd "$dest" 2>/dev/null && pwd -P)" = "$repo" ]; then
      echo "  이미 연결됨: $dest"
    else
      echo "  $dest 가 다른 곳($(readlink "$dest"))을 가리킵니다. 바꾸려면: rm \"$dest\" 후 다시 실행"
    fi
  elif [ -e "$dest" ]; then
    echo "  $dest 에 폴더/파일이 이미 있어 건드리지 않았습니다. 옮긴 뒤 다시 실행하세요."
  else
    ln -s "$repo" "$dest"
    echo "  연결함: $dest → $repo"
  fi
}

skill_dirs() {
  local dirs="${SKILLS_DIR:-${CLAUDE_SKILLS_DIR:-}}"
  if [ -n "$dirs" ]; then
    echo "$dirs" | tr ':' '\n'
    return
  fi
  [ -d "$HOME/.claude" ] && echo "$HOME/.claude/skills"   # Claude Code
  [ -d "$HOME/.codex" ] && echo "$HOME/.codex/skills"     # Codex
  return 0
}

if [ "$SKILL" = 1 ]; then
  echo "▶ AI 에이전트 스킬 연결"
  found=0
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    found=1
    link_skill "$d"
  done < <(skill_dirs)
  if [ "$found" = 0 ]; then
    echo "  스킬 폴더를 찾지 못했습니다. 에이전트를 이 폴더에서 실행하면 AGENTS.md 를 따릅니다 (스킬로 쓰려면 SKILLS_DIR=경로)."
  fi
fi
[ "$ENV" = 1 ] || exit 0

PIP_FLAGS=""
python3 -m pip install --help 2>/dev/null | grep -q -- "--break-system-packages" && PIP_FLAGS="--break-system-packages"

echo "▶ Python 패키지"
python3 -m pip install -q $PIP_FLAGS -r requirements.txt

echo "▶ Chromium"
if [ -n "${PLAYWRIGHT_BROWSERS_PATH:-}" ] && ls "$PLAYWRIGHT_BROWSERS_PATH" 2>/dev/null | grep -q chromium; then
  echo "  이미 설치됨 ($PLAYWRIGHT_BROWSERS_PATH)"
else
  python3 -m playwright install chromium
fi

echo "▶ 폰트 · poppler"
if [[ "$(uname)" == "Darwin" ]]; then
  command -v brew >/dev/null || { echo "  Homebrew 가 필요합니다: https://brew.sh"; exit 1; }
  fc-list 2>/dev/null | grep -qi "Noto Sans CJK KR" || ls ~/Library/Fonts 2>/dev/null | grep -qi "NotoSansCJK" \
    || brew install --cask font-noto-sans-cjk-kr
  fc-list 2>/dev/null | grep -qi "Noto Serif CJK KR" || ls ~/Library/Fonts 2>/dev/null | grep -qi "NotoSerifCJK" \
    || brew install --cask font-noto-serif-cjk-kr
  fc-list 2>/dev/null | grep -qi "Pretendard" || ls ~/Library/Fonts 2>/dev/null | grep -qi "Pretendard" \
    || brew install --cask font-pretendard
  command -v pdftoppm >/dev/null || brew install poppler
else
  if ! fc-list | grep -qi "Noto Sans CJK"; then   # fonts-noto-cjk 에 Serif CJK 도 들어 있다
    sudo apt-get update -qq && sudo apt-get install -y -qq fonts-noto-cjk
  fi
  if ! fc-list | grep -qi "Pretendard"; then
    dir=~/.local/share/fonts/pretendard; mkdir -p "$dir"
    for w in Regular Medium SemiBold Bold ExtraBold; do
      curl -fsSL -o "$dir/Pretendard-$w.otf" "https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/public/static/Pretendard-$w.otf"
    done
    fc-cache -f "$dir" >/dev/null
  fi
  command -v pdftoppm >/dev/null || sudo apt-get install -y -qq poppler-utils
fi

echo "▶ 확인"
python3 - <<'PY'
import yaml, pdfplumber, pdf2image
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    p.chromium.launch().close()
print("  준비 완료")
PY
