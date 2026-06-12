#!/usr/bin/env python3
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
NAV = (ROOT / "partials" / "nav.html").read_text(encoding="utf-8").strip()
NAV_CSS = '<link rel="stylesheet" href="/assets/rankwise-nav.css?v=rw-nav-a11y-20260610">'
NAV_JS = '<script src="/assets/nav-mobile.js?v=rw-nav-a11y-20260611" defer></script>'
THEME_META = '<meta name="theme-color" content="#0F1815">'

OLD_NAV_RE = re.compile(r"<nav\b[^>]*>.*?</nav>", re.DOTALL | re.IGNORECASE)
# Optional leading skip link is part of the nav block — matching it keeps re-runs
# from stacking a second copy in front of the header.
RW_NAV_RE = re.compile(
    r'(?:<a\s+class=["\']skip-link["\'][^>]*>[^<]*</a>\s*)?'
    r'<header\s+class=["\']rw-nav["\'][^>]*>.*?</header>',
    re.DOTALL | re.IGNORECASE,
)
# NOTE: flattens every theme-color meta to the single dark one — revisit before
# introducing media-attributed light/dark theme-color pairs.
THEME_META_RE = re.compile(r'<meta\s+name=["\']theme-color["\'][^>]*>')
NAV_CSS_RE = re.compile(r'<link\s+rel=["\']stylesheet["\']\s+href=["\']/assets/rankwise-nav\.css[^"\']*["\']\s*>')
NAV_JS_RE = re.compile(r'<script\s+src=["\']/assets/nav-mobile\.js[^"\']*["\']\s+defer></script>')


def sync_nav_assets(html: str) -> str:
    html = NAV_CSS_RE.sub(NAV_CSS, html)
    html = NAV_JS_RE.sub(NAV_JS, html)

    if NAV_JS not in html:
        html = html.replace("</head>", f"{NAV_JS}\n</head>")

    if NAV_CSS not in html:
        html = html.replace(NAV_JS, f"{NAV_CSS}\n{NAV_JS}", 1)

    html = THEME_META_RE.sub(THEME_META, html)
    if THEME_META not in html:
        html = html.replace(NAV_CSS, f"{THEME_META}\n{NAV_CSS}", 1)

    return html


def sync_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    html = original

    if RW_NAV_RE.search(html):
        html = RW_NAV_RE.sub(NAV, html, count=1)
    else:
        old = OLD_NAV_RE.search(html)
        # The legacy fallback must never eat a non-header <nav>: the homepage
        # chapter rail, or the menu <nav> inside an rw-nav header that drifted
        # out of RW_NAV_RE's shape (replacing that would nest headers).
        if not old or "chapter-rail" in old.group(0) or "rw-nav__menu" in old.group(0):
            return False
        html = OLD_NAV_RE.sub(NAV, html, count=1)

    html = sync_nav_assets(html)

    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in {"_archive", "node_modules"}:
            continue
        if sync_file(path):
            changed.append(str(rel))

    print(f"Synced nav on {len(changed)} pages.")
    for item in changed:
        print(item)


if __name__ == "__main__":
    main()
