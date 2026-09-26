#!/usr/bin/env python3
"""Keep folded blog pages (same-intent posts merged into a survivor) consistent.

Source of truth: _content/folded-pages.json. A folded page keeps serving its own
content (GitHub Pages cannot send a real 301) but hands its ranking signal to a
survivor post. For every entry this asserts:

  - the folded page exists;
  - it has exactly one <link rel="canonical">, pointing at its survivor;
  - it carries no robots noindex and no meta refresh;
  - it is absent from sitemap.xml;
  - the survivor exists, is not itself folded or a mirror, is self-canonical
    (exactly one canonical tag) and is present in sitemap.xml;
  - no live page links to the folded URL (links go to the survivor instead).

Unlike check_mirror_pages.py there is no --sync: folded pages keep their own
content, so there is nothing to copy.

Usage:
    python3 scripts/check_folded_pages.py          # exit 1 on any violation
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "_content" / "folded-pages.json"
MIRRORS = ROOT / "_content" / "mirror-pages.json"
BASE = "https://rankwise.ca"
# Same exclusions as check_site_integrity.live_html_files().
SKIP_DIRS = {"_archive", "landing-preview", "partials"}

CANONICAL_RE = re.compile(r'<link\b[^>]*\brel=["\']canonical["\'][^>]*>', re.IGNORECASE)
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
NOINDEX_RE = re.compile(r'<meta\b[^>]*\bname=["\']robots["\'][^>]*noindex', re.IGNORECASE)
REFRESH_RE = re.compile(r'<meta\b[^>]*\bhttp-equiv\s*=\s*["\']refresh["\']', re.IGNORECASE)
LOC_RE = re.compile(r"<loc>https://rankwise\.ca([^<]*)</loc>")


def load_folds() -> list[dict]:
    if not REGISTRY.exists():
        return []
    return json.loads(REGISTRY.read_text(encoding="utf-8"))["folds"]


def url_of(rel: str) -> str:
    """'blog/<slug>/index.html' -> '/blog/<slug>/'."""
    return "/" + rel.removesuffix("index.html")


def canonicals(text: str) -> list[str]:
    out = []
    for tag in CANONICAL_RE.findall(text):
        m = HREF_RE.search(tag)
        out.append(m.group(1) if m else "")
    return out


def live_html_files() -> list[Path]:
    return [p for p in sorted(ROOT.rglob("*.html"))
            if not (p.relative_to(ROOT).parts and p.relative_to(ROOT).parts[0] in SKIP_DIRS)]


def check() -> list[str]:
    errors: list[str] = []
    folds = load_folds()
    if not folds:
        return errors
    sitemap_urls = set(LOC_RE.findall((ROOT / "sitemap.xml").read_text(encoding="utf-8")))
    folded_rels = {f["folded"] for f in folds}
    mirror_rels = set()
    if MIRRORS.exists():
        for m in json.loads(MIRRORS.read_text(encoding="utf-8"))["mirrors"]:
            mirror_rels.add(m["mirror"])

    for entry in folds:
        folded, survivor = entry["folded"], entry["survivor"]
        f_url, s_url = url_of(folded), url_of(survivor)
        f_path, s_path = ROOT / folded, ROOT / survivor

        if not f_path.exists():
            errors.append(f"{folded}: folded page missing (a folded URL must keep serving a page)")
        else:
            text = f_path.read_text(encoding="utf-8")
            canon = canonicals(text)
            if canon != [BASE + s_url]:
                errors.append(f"{folded}: expected exactly one canonical {BASE + s_url}, found {canon}")
            if NOINDEX_RE.search(text):
                errors.append(f"{folded}: carries robots noindex (folds keep the page indexable-by-canonical)")
            if REFRESH_RE.search(text):
                errors.append(f"{folded}: carries a meta refresh (folds do not redirect)")
        if f_url in sitemap_urls:
            errors.append(f"sitemap.xml: folded {f_url} must not be listed (survivor is {s_url})")

        if survivor in folded_rels or survivor in mirror_rels:
            errors.append(f"{folded}: survivor {survivor} is itself folded or a mirror")
        if not s_path.exists():
            errors.append(f"{survivor}: survivor page missing")
        else:
            canon = canonicals(s_path.read_text(encoding="utf-8"))
            if canon != [BASE + s_url]:
                errors.append(f"{survivor}: survivor must be self-canonical ({BASE + s_url}), found {canon}")
        if s_url not in sitemap_urls:
            errors.append(f"sitemap.xml: survivor {s_url} missing")

    # No live page may still link at a folded URL.
    folded_urls = {url_of(r) for r in folded_rels}
    for path in live_html_files():
        rel = path.relative_to(ROOT).as_posix()
        for href in HREF_RE.findall(path.read_text(encoding="utf-8")):
            target = href.split("#", 1)[0].split("?", 1)[0]
            if target.startswith(BASE):
                target = target[len(BASE):]
            if target in folded_urls or target + "/" in folded_urls:
                errors.append(f"{rel}: links to folded {target} (point it at the survivor)")
    return errors


def main() -> int:
    # A folded page's own canonical is a <link href> to its survivor, never to
    # itself, so it cannot trip the no-links-to-folded rule.
    errors = check()
    if errors:
        print("Folded-page check failed:")
        for e in errors:
            print(f"- {e}")
        return 1
    print(f"folded pages consistent ({len(load_folds())} folds)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
