#!/usr/bin/env bash
# 빌드 환경 준비: Python 패키지, Playwright Chromium, Noto Sans CJK KR, poppler(PNG 변환)
# 사용: bash scripts/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."

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
  command -v pdftoppm >/dev/null || brew install poppler
else
  if ! fc-list | grep -qi "Noto Sans CJK"; then
    sudo apt-get update -qq && sudo apt-get install -y -qq fonts-noto-cjk
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
