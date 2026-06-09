#!/usr/bin/env python3
import hashlib
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NAV = (ROOT / "partials" / "nav.html").read_text(encoding="utf-8").strip()
SKIP_NAV = {"404.html", "blog/hvac-marketing-cost/index.html"}
STALE_NAV_RE = re.compile(r"(?m)^nav\{|\.nav-links|\.nav-cta|\.logo\{")
STALE_STICKY_CTA_RE = re.compile(
    r"\.mobile-sticky-cta\{display:none\}\s*"
    r"@media\(max-width:1000px\)\{\.mobile-sticky-cta\{display:flex;position:fixed;"
)
RW_NAV_RE = re.compile(
    r'<header\s+class=["\']rw-nav["\']\s+role=["\']navigation["\']\s+aria-label=["\']Primary["\']>.*?</header>',
    re.DOTALL | re.IGNORECASE,
)
JSON_LD_RE = re.compile(r'<script type="application/ld\+json">([\s\S]*?)</script>')


def live_html_files() -> list[Path]:
    files = []
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in {"_archive", "landing-preview", "partials"}:
            continue
        files.append(path)
    return files


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    expected_hash = hashlib.sha1(EXPECTED_NAV.encode()).hexdigest()

    for path in live_html_files():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")

        if rel not in SKIP_NAV:
            match = RW_NAV_RE.search(text)
            if not match:
                fail(errors, f"{rel}: missing shared rw-nav header")
            elif hashlib.sha1(match.group(0).strip().encode()).hexdigest() != expected_hash:
                fail(errors, f"{rel}: shared nav differs from partials/nav.html")

            if "<main" not in text or "</main>" not in text:
                fail(errors, f"{rel}: missing main landmark")

        if STALE_NAV_RE.search(text):
            fail(errors, f"{rel}: contains stale inline old-nav CSS")
        if STALE_STICKY_CTA_RE.search(text):
            fail(errors, f"{rel}: contains duplicated inline sticky CTA CSS")

        for index, match in enumerate(JSON_LD_RE.finditer(text), 1):
            try:
                json.loads(html.unescape(match.group(1)))
            except Exception as exc:
                fail(errors, f"{rel}: invalid JSON-LD block {index}: {exc}")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_urls = set(re.findall(r"<loc>https://rankwise\.ca([^<]*)</loc>", sitemap))

    if "/landing-preview/" in sitemap_urls:
        fail(errors, "sitemap.xml: landing-preview must not be indexable")

    for city_dir in sorted(ROOT.glob("*-hvac-marketing")):
        if city_dir.is_dir() and (city_dir / "index.html").exists():
            url = f"/{city_dir.name}/"
            if url not in sitemap_urls:
                fail(errors, f"sitemap.xml: missing {url}")

    for url in sorted(sitemap_urls):
        if url == "/":
            continue
        if not (ROOT / url.strip("/") / "index.html").exists():
            fail(errors, f"sitemap.xml: {url} has no local index.html")

    if errors:
        print("Site integrity check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Site integrity check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
