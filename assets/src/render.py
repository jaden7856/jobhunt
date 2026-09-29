"""README 이미지 재생성: python3 assets/src/render.py

동일한 Chromium·폰트 환경에서 같은 PNG를 생성한다.
의존성이나 폰트가 없으면 bash scripts/setup.sh로 설치한다.
"""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    source = Path(__file__).resolve().parent
    options = {}
    if os.environ.get("RESUME_CHROMIUM"):
        options["executable_path"] = os.environ["RESUME_CHROMIUM"]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**options)
        page = browser.new_page(
            viewport={"width": 900, "height": 1000},
            device_scale_factor=2,
            color_scheme="light",
            locale="ko-KR",
            timezone_id="Asia/Seoul",
        )
        for name in ("flow.ko", "flow.en", "eval.ko", "eval.en"):
            page.goto((source / f"{name}.html").as_uri())
            page.evaluate("document.fonts.ready")
            output = source.parent / f"{name}.png"
            page.locator(".capture").screenshot(
                path=str(output), animations="disabled", omit_background=False
            )
            print(f"{output.name}: {output.stat().st_size / 1024:.1f} KB")
        browser.close()


if __name__ == "__main__":
    main()
