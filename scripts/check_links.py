# -*- coding: utf-8 -*-
"""링크 접속 확인. 표준 라이브러리만 쓴다 (설치 없이 어디서나 실행).

  python3 scripts/check_links.py https://a.com https://b.com
  python3 scripts/check_links.py --pdf data/output/xxx.pdf     # PDF 안 링크 전부 (pdfplumber 필요)

결과
  ok       2xx/3xx
  broken   4xx/5xx 또는 주소 없음 → 고쳐야 함
  unknown  이 환경의 네트워크가 막혀 확인하지 못함 → 다른 환경(내 PC 브라우저 등)에서 다시 확인
"""
import socket
import sys
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def check(url, timeout=10):
    if url.startswith(("mailto:", "tel:")):
        return "ok", "skip"
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return "ok", str(r.status)
    except urllib.error.HTTPError as e:
        # 프록시·방화벽이 막은 경우(403/407 + 프록시 응답)는 판단 불가로 본다
        try:
            body = e.read(2000).decode("utf-8", "ignore").lower()
        except Exception:  # noqa: BLE001
            body = ""
        via = str(e.headers.get("Via", "") + e.headers.get("Server", "")).lower()
        if e.code == 407 or "proxy" in via or any(k in body for k in ("agentproxy", "anthropic.com", "canonicalized")):
            return "unknown", f"proxy {e.code}"
        return ("broken" if e.code >= 400 else "ok"), str(e.code)
    except urllib.error.URLError as e:
        reason = str(e.reason)
        if isinstance(e.reason, socket.gaierror) and "Name or service not known" in reason:
            return "broken", "도메인 없음"
        return "unknown", reason[:60]
    except (socket.timeout, TimeoutError):
        return "unknown", "timeout"
    except Exception as e:  # noqa: BLE001
        return "unknown", type(e).__name__


def links_in_pdf(pdf):
    import pdfplumber
    urls = []
    with pdfplumber.open(pdf) as p:
        for page in p.pages:
            urls += [h["uri"] for h in page.hyperlinks if h.get("uri")]
    return sorted(set(urls))


if __name__ == "__main__":
    args = sys.argv[1:]
    urls = links_in_pdf(args[1]) if args[:1] == ["--pdf"] else args
    bad = 0
    for u in urls:
        st, info = check(u)
        bad += st == "broken"
        print(f"{st:8} {info:12} {u}")
    sys.exit(1 if bad else 0)
