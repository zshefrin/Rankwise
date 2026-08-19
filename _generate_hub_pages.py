#!/usr/bin/env python3
"""Generate the 11 category-hub pages from _content/hubs/*.md.

Source of truth: the markdown files in _content/hubs/ (finalized + persona-reviewed
2026-08-19 from rankwise-dashboard vault/_dev/hub-drafts-2026-08-17, doorway gate
<= 0.075 pairwise). Re-run after editing a hub md:  python3 _generate_hub_pages.py

Output: <slug>/index.html per file, self-contained (inline style, self-hosted
fonts, GA4 with the internal-traffic cookie guard, FAQPage + BreadcrumbList
JSON-LD, cross-hub strip so no hub is an orphan of its siblings).
Then run generate_sitemap.py and commit both.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "_content" / "hubs"
BASE = "https://rankwise.ca"

# display order for the cross-hub strip (winnability tranches, then regulated)
ORDER = ["roofing", "plumber", "landscaping", "electrician", "auto-repair", "hvac",
         "law-firm", "dental", "chiropractor", "med-spa", "veterinary"]
STRIP_LABEL = {
    "roofing": "Roofing", "plumber": "Plumbing", "landscaping": "Landscaping",
    "electrician": "Electricians", "auto-repair": "Auto repair", "hvac": "HVAC",
    "law-firm": "Law firms", "dental": "Dental", "chiropractor": "Chiropractic",
    "med-spa": "Med spas", "veterinary": "Veterinary",
}


def parse_front(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    fm_raw, body = m.group(1), m.group(2)
    fm: dict = {}
    for line in fm_raw.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") :
            try:
                fm[k.strip()] = json.loads(v)
                continue
            except json.JSONDecodeError:
                pass
        fm[k.strip()] = v.strip('"')
    return fm, body


def inline_md(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def md_to_html(body: str) -> tuple[str, list[tuple[str, str]]]:
    """Markdown body -> (article html, faq [(q, a)]). Handles the drafts' actual
    constructs only: #/## headings, paragraphs, - bullets, **bold**, [links]().
    FAQ Q&A pairs are detected inside the FAQ section (one-line or two-line form)."""
    out: list[str] = []
    faq: list[tuple[str, str]] = []
    in_faq = False
    in_list = False
    blocks = [b.strip() for b in body.split("\n\n") if b.strip()]
    for b in blocks:
        if b.startswith("# "):
            continue  # h1 comes from frontmatter
        if b.startswith("## "):
            if in_list:
                out.append("</ul>"); in_list = False
            title = b[3:].strip()
            in_faq = bool(re.match(r"(?i)^(faq|frequently asked questions)$", title))
            hid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
            out.append(f'<h2 id="{hid}">{inline_md(title)}</h2>')
            continue
        if b.startswith("- ") or b.startswith("* "):
            items = [re.sub(r"^[-*] ", "", ln.strip()) for ln in b.splitlines() if ln.strip()]
            out.append("<ul>" + "".join(f"<li>{inline_md(i)}</li>" for i in items) + "</ul>")
            continue
        # FAQ pair? "**Q?** answer" one-line, or "**Q?**\nanswer" two-line
        m = re.match(r"^\*\*(.+?)\*\*\s*\n?(.+)$", b, re.S)
        if in_faq and m and "?" in m.group(1):
            q = m.group(1).strip()
            a = " ".join(m.group(2).split())
            faq.append((q, a))
            out.append(f'<div class="faq-item"><h3 class="faq-q">{inline_md(q)}</h3>'
                       f'<p class="faq-a">{inline_md(a)}</p></div>')
            continue
        out.append(f"<p>{inline_md(' '.join(b.split()))}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out), faq


def cross_hub_strip(current_slug: str) -> str:
    links = []
    for key in ORDER:
        slug = f"/{key}-marketing/"
        if slug == current_slug:
            continue
        links.append(f'<a href="{slug}">{STRIP_LABEL[key]}</a>')
    return ('<nav class="hub-strip" aria-label="Local-search marketing by category">'
            '<span class="hub-strip-label">Marketing guides by category</span>'
            + "".join(links) + "</nav>")


STYLE = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
@font-face{font-family:"Bricolage Grotesque";font-style:normal;font-weight:800;font-display:swap;
  src:url(/assets/fonts/bricolage-grotesque-800-latin.woff2) format("woff2");
  unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
@font-face{font-family:"Instrument Serif";font-style:italic;font-weight:400;font-display:swap;
  src:url(/assets/fonts/instrument-serif-italic-latin.woff2) format("woff2");
  unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
:root{
  --paper-2:#F5EFE3;--surface:#FFFDF7;--ink:#17231F;--ink-soft:#5D6A63;--ink-muted:#67736C;
  --line:#D9D0C3;--accent:#F2B533;--accent-2:#0F766E;--label:#0A675F;--link:#006E67;
  --headline:"Bricolage Grotesque","Avenir Next","Segoe UI",sans-serif;
  --serif:"Instrument Serif","Iowan Old Style",Georgia,serif;
  --text:"Avenir Next","Segoe UI","Helvetica Neue",sans-serif;
}
html{scroll-behavior:smooth}
main{position:relative;z-index:1;padding-top:96px}
body{font-family:var(--text);color:var(--ink);line-height:1.75;background:var(--paper-2);-webkit-font-smoothing:antialiased}
::selection{background:rgba(242,181,51,.32);color:var(--ink)}
:focus-visible{outline:2px solid var(--accent-2);outline-offset:2px;border-radius:3px}
.crumb{max-width:820px;margin:0 auto;padding:20px 24px 0;font-size:12.5px;letter-spacing:.04em;color:var(--ink-muted)}
.crumb a{color:var(--link);text-decoration:none}
.hub{max-width:820px;margin:0 auto;padding:14px 24px 56px}
.hub-head{padding:18px 0 8px;border-bottom:1px solid var(--line);margin-bottom:10px}
.hub-badge{display:inline-block;padding:4px 12px;border-radius:999px;background:rgba(15,118,110,.09);border:1px solid rgba(15,118,110,.25);
  font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--label);margin-bottom:14px}
h1{font-family:var(--headline);font-weight:800;font-size:clamp(28px,5vw,40px);line-height:1.14;letter-spacing:-.01em;margin-bottom:10px;text-wrap:balance}
.hub-sub{font-family:var(--serif);font-style:italic;font-size:17px;color:var(--ink-soft);margin-bottom:6px}
.hub h2{font-family:var(--headline);font-weight:800;font-size:clamp(20px,3.4vw,26px);line-height:1.2;margin:34px 0 12px;letter-spacing:-.005em;text-wrap:balance}
.hub p{margin:0 0 16px;color:var(--ink);max-width:72ch}
.hub a{color:var(--link)}
.hub ul{margin:0 0 18px 1.2em}
.hub li{margin:0 0 9px;max-width:70ch}
.faq-item{border:1px solid var(--line);border-radius:12px;background:var(--surface);padding:16px 18px;margin:0 0 12px}
.faq-q{font-family:var(--headline);font-weight:800;font-size:16px;line-height:1.35;margin:0 0 7px}
.faq-a{margin:0!important;color:var(--ink-soft)}
.hub-cta{margin:38px 0 8px;padding:24px 22px;border-radius:14px;background:#12211C;color:#F3EFE6}
.hub-cta h2{color:#FFF;margin:0 0 8px!important;font-size:22px!important}
.hub-cta p{color:rgba(243,239,230,.85);margin-bottom:14px}
.hub-cta .btn{display:inline-block;padding:12px 22px;border-radius:10px;background:var(--accent);color:#171205;font-weight:700;text-decoration:none;font-family:var(--headline)}
.hub-strip{margin:30px 0 0;padding:16px 0 0;border-top:1px solid var(--line);display:flex;flex-wrap:wrap;gap:8px 14px;align-items:baseline}
.hub-strip-label{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-muted);margin-right:4px}
.hub-strip a{font-size:13.5px;color:var(--link);text-decoration:none;border-bottom:1px dotted var(--line)}
footer{background:#12211C;color:#B9C4BC;margin-top:48px}
.footer-wrap{max-width:1180px;margin:0 auto;padding:34px 28px;display:flex;flex-wrap:wrap;gap:18px;align-items:center;justify-content:space-between}
.flogo{font-family:var(--headline);font-weight:800;font-size:19px;color:#FFF}
.flogo span{color:var(--accent)}
.flinks{display:flex;flex-wrap:wrap;gap:16px}
.flinks a{color:#B9C4BC;text-decoration:none;font-size:13.5px}
.fcopy{font-size:12px;color:#7E8B83;width:100%}
@media (max-width:640px){.hub{padding:10px 18px 44px}.crumb{padding:16px 18px 0}}
"""

GA4 = ("<script async src=\"https://www.googletagmanager.com/gtag/js?id=G-LRX309H9CH\"></script>\n"
       "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
       "gtag('js',new Date());var _rwInt=document.cookie.split(';').some(function(c){return c.trim()==="
       "'internal_traffic=true';});gtag('config','G-LRX309H9CH',_rwInt?{traffic_type:'internal'}:{});</script>")

NAV = """<header class="rw-nav">
  <a href="/" class="rw-nav__logo">Rank<span>wise</span></a>
  <nav class="rw-nav__menu" aria-label="Primary">
    <ul class="rw-nav__links">
      <li><a href="/#services">What we do</a></li>
      <li><a href="/#how">How it works</a></li>
      <li><a href="/#results">Results</a></li>
      <li><a href="/#faq">FAQ</a></li>
      <li><a href="/blog/">Blog</a></li>
      <li><a href="/lab/">Lab</a></li>
      <li><a href="/about/">About</a></li>
    </ul>
  </nav>
  <a href="/audit/?utm_source=nav&amp;utm_medium=cta&amp;utm_content=global_nav" class="rw-nav__cta">Book free audit</a>
</header>"""

FOOTER = """<footer>
  <div class="footer-wrap">
    <div class="flogo">Rank<span>wise</span></div>
    <div class="flinks">
      <a href="/#services">What we do</a>
      <a href="/#how">How it works</a>
      <a href="/#results">Results</a>
      <a href="/blog/">Blog</a>
      <a href="/lab/">Lab</a>
      <a href="/audit/">Free audit</a>
    </div>
    <div class="fcopy">© 2026 Rankwise · local-search marketing · Metro Vancouver, BC</div>
  </div>
</footer>"""


def build(fm: dict, body: str) -> str:
    slug = fm["slug"].strip("/")
    url = f"{BASE}/{slug}/"
    title = fm["title"]
    desc = fm["metaDescription"]
    h1 = fm["h1"]
    article, faq = md_to_html(body)
    breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Rankwise", "item": BASE + "/"},
        {"@type": "ListItem", "position": 2, "name": title, "item": url}]}
    ld_blocks = [json.dumps(breadcrumb, ensure_ascii=False)]
    if faq:
        ld_blocks.append(json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\*\*|\[|\]\([^)]*\)", "", a)}}
            for q, a in faq]}, ensure_ascii=False))
    ld = "\n".join(f'<script type="application/ld+json">\n{b}\n</script>' for b in ld_blocks)
    esc_t = html.escape(title, quote=True)
    esc_d = html.escape(desc, quote=True)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc_t}</title>
<meta name="description" content="{esc_d}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc_t}">
<meta property="og:description" content="{esc_d}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary">
<meta name="robots" content="index, follow">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
{GA4}
{ld}
<style>{STYLE}</style>
<link rel="stylesheet" href="/assets/rankwise-nav.css?v=rw-nav-a11y-20260610">
<script src="/assets/nav-mobile.js?v=rw-nav-a11y-20260611" defer></script>
</head>
<body>
{NAV}
<main id="main-content">
<div class="crumb"><a href="/">Rankwise</a> · Marketing guides · {html.escape(STRIP_LABEL.get(slug.replace("-marketing", ""), title))}</div>
<article class="hub">
<div class="hub-head">
<span class="hub-badge">Category guide · Metro Vancouver</span>
<h1>{inline_md(h1)}</h1>
<p class="hub-sub">Real Google map-pack data, honest costs, and what actually moves position — no client-results claims, because the numbers here are market data, not testimonials.</p>
</div>
{article}
<div class="hub-cta">
<h2>See where your business actually sits</h2>
<p>The free 15-minute audit shows your current map-pack position against the real numbers on this page — no pitch deck.</p>
<a class="btn" href="/audit/?utm_source=hub&amp;utm_medium=cta&amp;utm_campaign={slug}">Book your free audit</a>
</div>
{cross_hub_strip(fm["slug"])}
</article>
</main>
{FOOTER}
</body></html>
"""


def main() -> None:
    built = []
    for f in sorted(SRC.glob("*.md")):
        fm, body = parse_front(f.read_text(encoding="utf-8"))
        slug = fm["slug"].strip("/")
        out = ROOT / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build(fm, body), encoding="utf-8")
        built.append(slug)
        print(f"built /{slug}/  ({f.name})")
    print(f"{len(built)} hub pages built")


if __name__ == "__main__":
    main()
