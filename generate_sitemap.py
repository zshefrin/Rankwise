#!/usr/bin/env python3
"""
Regenerate sitemap.xml from the live blog directory.

Uses git log for lastmod dates so they reflect real content changes,
not filesystem timestamps. Falls back to today for uncommitted files.

Usage:
    python3 generate_sitemap.py          # regenerate and print path
    python3 generate_sitemap.py --check  # exit 1 if sitemap would change
"""

import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "https://rankwise.ca"


def git_lastmod(rel_path: str) -> str:
    """Return YYYY-MM-DD of the last commit that touched this path, or today."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%aI", "--", rel_path],
        capture_output=True, text=True, cwd=ROOT,
    )
    raw = result.stdout.strip()
    if raw:
        return raw[:10]  # YYYY-MM-DD from ISO timestamp
    return date.today().isoformat()


def build_sitemap() -> str:
    urls: list[tuple[str, str, str, str]] = []  # (loc, lastmod, changefreq, priority)

    # Homepage
    urls.append((f"{BASE}/", git_lastmod("index.html"), "monthly", "1.0"))

    # Audit page
    audit_html = "audit/index.html"
    if (ROOT / audit_html).exists():
        urls.append((f"{BASE}/audit/", git_lastmod(audit_html), "monthly", "0.9"))

    # Blog index
    blog_index = "blog/index.html"
    if (ROOT / blog_index).exists():
        urls.append((f"{BASE}/blog/", git_lastmod(blog_index), "weekly", "0.8"))

    # City landing pages — any top-level directory ending in -hvac-marketing
    for slug_dir in sorted(ROOT.iterdir()):
        if not slug_dir.is_dir() or not slug_dir.name.endswith("-hvac-marketing"):
            continue
        page_html = slug_dir / "index.html"
        if not page_html.exists():
            continue
        rel = f"{slug_dir.name}/index.html"
        urls.append((f"{BASE}/{slug_dir.name}/", git_lastmod(rel), "monthly", "0.8"))

    # Individual blog posts — any subdirectory of blog/ containing index.html
    blog_dir = ROOT / "blog"
    for slug_dir in sorted(blog_dir.iterdir()):
        if not slug_dir.is_dir():
            continue
        post_html = slug_dir / "index.html"
        if not post_html.exists():
            continue
        rel = f"blog/{slug_dir.name}/index.html"
        urls.append((f"{BASE}/blog/{slug_dir.name}/", git_lastmod(rel), "monthly", "0.7"))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod, changefreq, priority in urls:
        lines += [
            "  <url>",
            f"    <loc>{loc}</loc>",
            f"    <lastmod>{lastmod}</lastmod>",
            f"    <changefreq>{changefreq}</changefreq>",
            f"    <priority>{priority}</priority>",
            "  </url>",
        ]
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main() -> None:
    check_mode = "--check" in sys.argv
    sitemap_path = ROOT / "sitemap.xml"
    new_content = build_sitemap()

    if check_mode:
        current = sitemap_path.read_text(encoding="utf-8") if sitemap_path.exists() else ""
        if current != new_content:
            print("sitemap.xml is out of date — run: python3 generate_sitemap.py")
            sys.exit(1)
        print("sitemap.xml is up to date")
        return

    sitemap_path.write_text(new_content, encoding="utf-8")
    print(f"wrote {sitemap_path.relative_to(ROOT)} ({len([l for l in new_content.splitlines() if '<loc>' in l])} URLs)")


if __name__ == "__main__":
    main()
