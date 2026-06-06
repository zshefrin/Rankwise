#!/usr/bin/env python3
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
NAV = (ROOT / "partials" / "nav.html").read_text(encoding="utf-8").strip()
NAV_CSS = '<link rel="stylesheet" href="/assets/rankwise-nav.css?v=rw-nav-20260605">'
NAV_JS = '<script src="/assets/nav-mobile.js?v=rw-nav-track-20260605" defer></script>'

OLD_NAV_RE = re.compile(r"<nav\b[^>]*>.*?</nav>", re.DOTALL | re.IGNORECASE)
RW_NAV_RE = re.compile(
    r'<header\s+class=["\']rw-nav["\']\s+role=["\']navigation["\']\s+aria-label=["\']Primary["\']>.*?</header>',
    re.DOTALL | re.IGNORECASE,
)
NAV_CSS_RE = re.compile(r'<link\s+rel=["\']stylesheet["\']\s+href=["\']/assets/rankwise-nav\.css[^"\']*["\']\s*>')
NAV_JS_RE = re.compile(r'<script\s+src=["\']/assets/nav-mobile\.js[^"\']*["\']\s+defer></script>')


def sync_nav_assets(html: str) -> str:
    html = NAV_CSS_RE.sub(NAV_CSS, html)
    html = NAV_JS_RE.sub(NAV_JS, html)

    if NAV_JS not in html:
        html = html.replace("</head>", f"{NAV_JS}\n</head>")

    if NAV_CSS not in html:
        html = html.replace(NAV_JS, f"{NAV_CSS}\n{NAV_JS}", 1)

    return html


def sync_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    html = original

    if RW_NAV_RE.search(html):
        html = RW_NAV_RE.sub(NAV, html, count=1)
    elif OLD_NAV_RE.search(html):
        html = OLD_NAV_RE.sub(NAV, html, count=1)
    else:
        return False

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
