#!/usr/bin/env python3
import hashlib
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NAV = (ROOT / "partials" / "nav.html").read_text(encoding="utf-8").strip()
SKIP_NAV = {"404.html"}
STALE_NAV_RE = re.compile(r"(?m)^nav\{|\.nav-links|\.nav-cta|\.logo\{")
STALE_STICKY_CTA_RE = re.compile(
    r"\.mobile-sticky-cta\{display:none\}\s*"
    r"@media\(max-width:1000px\)\{\.mobile-sticky-cta\{display:flex;position:fixed;"
)
# Must mirror scripts/sync_nav.py RW_NAV_RE: the shared block is the optional
# skip link plus the header, and the hash compares that whole span to the partial.
RW_NAV_RE = re.compile(
    r'(?:<a\s+class=["\']skip-link["\'][^>]*>[^<]*</a>\s*)?'
    r'<header\s+class=["\']rw-nav["\'][^>]*>.*?</header>',
    re.DOTALL | re.IGNORECASE,
)
JSON_LD_RE = re.compile(r'<script type="application/ld\+json">([\s\S]*?)</script>')
NOINDEX_RE = re.compile(r'<meta\s+name=["\']robots["\'][^>]*noindex', re.IGNORECASE)
NUMBER_WORDS = {
    w: i for i, w in enumerate(
        "zero one two three four five six seven eight nine ten eleven twelve thirteen "
        "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()
    )
}


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

        # Meta-refresh redirect stubs (old slugs) carry no nav or main landmark.
        if 'http-equiv="refresh"' in text:
            continue

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

    mirrors = json.loads((ROOT / "_content" / "mirror-pages.json").read_text(encoding="utf-8"))["mirrors"]
    for pair in mirrors:
        if (ROOT / pair["canonical"]).read_bytes() != (ROOT / pair["mirror"]).read_bytes():
            fail(errors, f"{pair['mirror']}: drifted from mirror source {pair['canonical']} (run scripts/check_mirror_pages.py --sync)")
        mirror_url = "/" + pair["mirror"].removesuffix("index.html")
        if mirror_url in sitemap_urls:
            fail(errors, f"sitemap.xml: mirror {mirror_url} must not be listed (canonical is elsewhere)")

    # Withdrawn/redirect stubs (noindex) must stay out of the sitemap and the
    # blog/lab listing pages; everything else in lab/ counts as a live study.
    live_studies = 0
    listing = {
        "blog": (ROOT / "blog" / "index.html").read_text(encoding="utf-8"),
        "lab": (ROOT / "lab" / "index.html").read_text(encoding="utf-8"),
    }
    for section in ("blog", "lab"):
        for page in sorted((ROOT / section).glob("*/index.html")):
            text = page.read_text(encoding="utf-8")
            url = f"/{section}/{page.parent.name}/"
            if NOINDEX_RE.search(text):
                if url in sitemap_urls:
                    fail(errors, f"sitemap.xml: noindex page {url} must not be listed")
                if f'href="{url}"' in listing[section] or f'href="https://rankwise.ca{url}"' in listing[section]:
                    fail(errors, f"{section}/index.html: links noindex page {url}")
            elif section == "lab":
                live_studies += 1

    # The homepage study count is prose ("Twelve public market studies ...") and
    # publish_lab.py's badge updater no longer finds its target, so pin it here.
    lab_count = re.search(r'data-count="(\d+)">\d+</strong><span>studies published', listing["lab"])
    if not lab_count or int(lab_count.group(1)) != live_studies:
        fail(errors, f"lab/index.html: studies-published count != {live_studies} live lab studies")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    home_count = re.search(r"\b([A-Za-z]+|\d+) public market stud(?:y|ies)\b", home)
    if not home_count:
        fail(errors, "index.html: lab study-count sentence not found (update check_site_integrity.py if reworded)")
    else:
        word = home_count.group(1).lower()
        value = int(word) if word.isdigit() else NUMBER_WORDS.get(word)
        if value != live_studies:
            fail(errors, f"index.html: says '{home_count.group(1)} public market studies' but lab/ has {live_studies} live studies")

    if errors:
        print("Site integrity check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Site integrity check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
