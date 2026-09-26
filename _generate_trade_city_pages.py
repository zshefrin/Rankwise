#!/usr/bin/env python3
"""Generate the trade x city PILOT pages (roofing, landscaping, plumbing x 5 cities).

Every number on these pages comes from ONE committed facts file,
_content/trade-city-pilot/facts-2026-09.json, which is derived from the
September 2026 map-pack sweep in rankwise-dashboard:

    vault/_research/data/local-ownership-{roofing,landscaping,plumbing}-bc-2026-09.json
    (scout_local_packs.py, captured 2026-09-09; lost captures re-queried
    2026-09-10 by backfill_lost_captures.py; per-capture dates kept)

The facts file records the source path, the dashboard commit and a sha256 of each
source file, so every number is traceable. Pages never read the dashboard directly.

    python3 _generate_trade_city_pages.py                          # (re)write the 15 pages
    python3 _generate_trade_city_pages.py --check                  # exit 1 on drift
    python3 _generate_trade_city_pages.py --refresh-facts ../rankwise-dashboard
                                                                   # re-derive the facts file

PILOT STATUS: every page carries <meta name="robots" content="noindex"> and is kept
out of sitemap.xml until the operator reviews it (generate_sitemap.py skips noindex
city pages). To promote: flip ROBOTS below, then run generate_sitemap.py.
Business truth (offer, pricing, guarantee wording) is canonical in
rankwise-dashboard vault/POSITIONING.md -- the copy below follows it verbatim in
substance; change POSITIONING first, then this file.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FACTS = ROOT / "_content" / "trade-city-pilot" / "facts-2026-09.json"
BASE = "https://rankwise.ca"
ROBOTS = "noindex"  # pilot: operator review before indexing

CITIES = ["Vancouver", "Surrey", "Burnaby", "Richmond", "Abbotsford"]
# Lower Mainland + Fraser Valley cities in the same sweep -- used ONLY for the
# clearly-labelled trade-level context line, never presented as city data.
REGION_CITIES = [
    "Vancouver", "Surrey", "Burnaby", "Richmond", "Coquitlam", "Langley", "Abbotsford",
    "Delta", "North Vancouver", "West Vancouver", "Port Coquitlam", "Port Moody",
    "New Westminster", "Maple Ridge", "Pitt Meadows", "White Rock", "Mission", "Chilliwack",
]
THIN_REVIEWS = 50  # "#1 result had fewer than 50 reviews" threshold (trade-level line)

TRADES = {
    "roofing": {
        "source": "vault/_research/data/local-ownership-roofing-bc-2026-09.json",
        "slug": "roofing",
        "label": "Roofing",
        "biz": "roofing company",
        "biz_pl": "roofing companies",
        "hub": ("/roofing-marketing/", "Roofing marketing in Metro Vancouver"),
        "lab": ("/lab/what-does-the-metro-vancouver-roofer-map-pack-actually-look-/",
                "Lab Market Study: the Metro Vancouver roofer map pack (July 2026)"),
    },
    "landscaping": {
        "source": "vault/_research/data/local-ownership-landscaping-bc-2026-09.json",
        "slug": "landscaping",
        "label": "Landscaping",
        "biz": "landscaping company",
        "biz_pl": "landscaping companies",
        "hub": ("/landscaping-marketing/", "Landscaping marketing in Metro Vancouver"),
        "lab": ("/lab/what-does-the-metro-vancouver-landscaper-map-pack-actually-l/",
                "Lab Market Study: the Metro Vancouver landscaper map pack (July 2026)"),
    },
    "plumbing": {
        "source": "vault/_research/data/local-ownership-plumbing-bc-2026-09.json",
        "slug": "plumbing",
        "label": "Plumbing",
        "biz": "plumbing company",
        "biz_pl": "plumbing companies",
        "hub": ("/plumber-marketing/", "Plumbing marketing in Metro Vancouver"),
        "lab": ("/lab/what-does-the-metro-vancouver-plumber-map-pack-actually-look/",
                "Lab Market Study: the Metro Vancouver plumber map pack (July 2026)"),
    },
}

NUM_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
             8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}


def city_slug(city: str) -> str:
    return city.lower().replace(" ", "-")


def page_slug(trade: str, city: str) -> str:
    return f"{city_slug(city)}-{TRADES[trade]['slug']}-marketing"


# --------------------------------------------------------------------------- facts


def _git(dashboard: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(dashboard), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def _captured_on(cap: dict, generated_at: str) -> str:
    return (cap.get("backfilled_at") or generated_at)[:10]


def refresh_facts(dashboard: Path) -> dict:
    """Derive the facts file from the dashboard sweep JSONs (read-only)."""
    head = _git(dashboard, "rev-parse", "HEAD")
    facts: dict = {
        "_about": ("Derived by _generate_trade_city_pages.py --refresh-facts from the rankwise-dashboard "
                   "September 2026 map-pack sweep. Business names are deliberately NOT carried over: "
                   "pages describe the market, not individual competitors. Letters (A, B, ...) are "
                   "per-city labels for distinct Google listings (place_id), in order of first appearance."),
        "dashboard_commit": head,
        "region_cities": REGION_CITIES,
        "thin_reviews_threshold": THIN_REVIEWS,
        "trades": {},
    }
    for trade, cfg in TRADES.items():
        src = dashboard / cfg["source"]
        raw_bytes = src.read_bytes()
        data = json.loads(raw_bytes)
        gen = data["generated_at"]
        t: dict = {
            "source_file": cfg["source"],
            "source_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "source_last_commit": _git(dashboard, "log", "-1", "--format=%H", "--", cfg["source"]),
            "sweep_generated_at": gen,
            "backfill_ran_at": (data.get("backfill") or {}).get("ran_at"),
            "keywords": data["keywords"],
            "cities": {},
        }
        # trade-level context across the region (searches that returned a pack)
        region_caps = region_thin = 0
        region_dates: set[str] = set()
        for city in REGION_CITIES:
            for cap in data["city_maps"][city]["raw"]:
                first = [r for r in cap["results"] if r["position"] == 1]
                if not first:
                    continue
                region_caps += 1
                region_dates.add(_captured_on(cap, gen))
                if first[0]["reviews"] < THIN_REVIEWS:
                    region_thin += 1
        t["region"] = {"searches_with_pack": region_caps, "first_under_threshold": region_thin,
                       "captured_on": sorted(region_dates)}
        for city in CITIES:
            letters: dict[str, str] = {}
            best: dict[str, int] = {}
            caps = []
            for cap in data["city_maps"][city]["raw"]:
                top3 = sorted((r for r in cap["results"] if r["position"] and r["position"] <= 3),
                              key=lambda r: r["position"])
                rows = []
                for r in top3:
                    key = r.get("place_id") or r["name"]
                    if key not in letters:
                        letters[key] = chr(ord("A") + len(letters))
                    best[letters[key]] = max(best.get(letters[key], 0), r["reviews"])
                    rows.append({"position": r["position"], "business": letters[key],
                                 "reviews": r["reviews"]})
                caps.append({"keyword": cap["keyword"], "captured_on": _captured_on(cap, gen),
                             "backfilled": bool(cap.get("backfilled_at")), "top3": rows})
            t["cities"][city] = {"searches": caps,
                                 "businesses": dict(sorted(best.items()))}
        facts["trades"][trade] = t
    return facts


def load_facts() -> dict:
    return json.loads(FACTS.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- copy helpers


def fmt_reviews(n: int) -> str:
    # Google shows large counts rounded (e.g. "1.6K"), which arrives as 1600.
    if n >= 1000 and n % 100 == 0:
        return f"about {n:,}"
    return f"{n:,}"


def fmt_median(m: float) -> str:
    return fmt_reviews(int(m)) if float(m).is_integer() else f"{m:,.1f}"


def count_word(n: int) -> str:
    return NUM_WORDS.get(n, str(n))


def plural(n: int, one: str, many: str) -> str:
    return one if n == 1 else many


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def city_stats(c: dict) -> dict:
    searches = [s for s in c["searches"] if s["top3"]]
    slots = sum(len(s["top3"]) for s in searches)
    biz = c["businesses"]
    firsts = [s["top3"][0] for s in searches]
    first_letters = {f["business"] for f in firsts}
    min_letter = min(biz, key=lambda k: (biz[k], k))
    dates = sorted({s["captured_on"] for s in c["searches"]})
    return {
        "n_searches": len(c["searches"]),
        "n_with_pack": len(searches),
        "slots": slots,
        "n_biz": len(biz),
        "median": statistics.median(biz.values()),
        "min_letter": min_letter,
        "min_reviews": biz[min_letter],
        "max_reviews": max(biz.values()),
        "firsts": firsts,
        "first_letters": first_letters,
        "dates": dates,
        "backfilled": [s for s in c["searches"] if s["backfilled"]],
    }


def date_phrase(dates: list[str]) -> str:
    return dates[0] if len(dates) == 1 else " and ".join(dates)


# --------------------------------------------------------------------------- page


STYLE = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
@font-face{font-family:"Bricolage Grotesque";font-style:normal;font-weight:800;font-display:swap;
  src:url(/assets/fonts/bricolage-grotesque-800-latin.woff2) format("woff2")}
@font-face{font-family:"Instrument Serif";font-style:italic;font-weight:400;font-display:swap;
  src:url(/assets/fonts/instrument-serif-italic-latin.woff2) format("woff2")}
:root{
  --paper-2:#F5EFE3;--surface:#FFFDF7;--ink:#17231F;--ink-soft:#5D6A63;--ink-muted:#67736C;
  --line:#D9D0C3;--accent:#F2B533;--accent-2:#0F766E;--label:#0A675F;--link:#006E67;
  --headline:"Bricolage Grotesque","Avenir Next","Segoe UI",sans-serif;
  --serif:"Instrument Serif","Iowan Old Style",Georgia,serif;
  --text:"Avenir Next","Segoe UI","Helvetica Neue",sans-serif;
}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{font-family:var(--text);color:var(--ink);line-height:1.7;background:var(--paper-2);-webkit-font-smoothing:antialiased;overflow-wrap:break-word}
main{position:relative;z-index:1;padding-top:96px}
:focus-visible{outline:2px solid var(--accent-2);outline-offset:2px;border-radius:3px}
.crumb{max-width:820px;margin:0 auto;padding:20px 24px 0;font-size:13px;letter-spacing:.03em;color:var(--ink-muted)}
.crumb a{color:var(--link);text-decoration:none;display:inline-flex;align-items:center;min-height:44px}
.tc{max-width:820px;margin:0 auto;padding:6px 24px 56px}
.tc-head{padding:10px 0 14px;border-bottom:1px solid var(--line);margin-bottom:10px}
.tc-badge{display:inline-block;padding:4px 12px;border-radius:999px;background:rgba(15,118,110,.09);border:1px solid rgba(15,118,110,.25);
  font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--label);margin-bottom:14px}
h1{font-family:var(--headline);font-weight:800;font-size:clamp(28px,6vw,40px);line-height:1.14;letter-spacing:-.01em;margin-bottom:10px;text-wrap:balance}
.tc-sub{font-family:var(--serif);font-style:italic;font-size:18px;line-height:1.5;color:var(--ink-soft)}
.tc h2{font-family:var(--headline);font-weight:800;font-size:clamp(21px,4.4vw,26px);line-height:1.2;margin:36px 0 12px;text-wrap:balance}
.tc p{margin:0 0 16px;max-width:72ch}
.tc ul{margin:0 0 18px 1.2em}
.tc li{margin:0 0 9px;max-width:70ch}
.facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:18px 0 8px}
.fact{border:1px solid var(--line);border-radius:12px;background:var(--surface);padding:14px 14px 12px}
.fact strong{display:block;font-family:var(--headline);font-size:26px;line-height:1.05;margin-bottom:6px}
.fact span{display:block;font-size:13px;line-height:1.4;color:var(--ink-soft)}
.pack{width:100%;border-collapse:collapse;margin:8px 0 10px;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:14px;table-layout:fixed}
.pack caption{caption-side:bottom;text-align:left;font-size:12.5px;color:var(--ink-muted);padding:8px 2px 0;line-height:1.5}
.pack th,.pack td{padding:10px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.pack thead th{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--label);background:rgba(15,118,110,.06)}
.pack th[scope=row]{font-weight:600;width:38%}
.pack td b{font-family:var(--headline);font-weight:800;margin-right:4px}
.pack tr:last-child th,.pack tr:last-child td{border-bottom:0}
.note{font-size:13.5px;color:var(--ink-soft);border-left:3px solid var(--accent);padding:2px 0 2px 12px;margin:0 0 16px}
.faq-item{border:1px solid var(--line);border-radius:12px;background:var(--surface);padding:16px 18px;margin:0 0 12px}
.faq-q{font-family:var(--headline);font-weight:800;font-size:16px;line-height:1.35;margin:0 0 7px}
.faq-a{margin:0!important;color:var(--ink-soft)}
.tc-cta{margin:38px 0 8px;padding:24px 22px;border-radius:14px;background:#12211C;color:#F3EFE6}
.tc-cta h2{color:#FFF;margin:0 0 8px!important;font-size:22px!important}
.tc-cta p{color:rgba(243,239,230,.86);margin-bottom:16px}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:12px 22px;border-radius:10px;background:var(--accent);color:#171205;font-weight:700;text-decoration:none;font-family:var(--headline);text-align:center}
.links{margin:30px 0 0;padding:16px 0 0;border-top:1px solid var(--line)}
.links-label{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-muted);margin:0 0 10px!important}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px}
.chips a{display:inline-flex;align-items:center;min-height:44px;padding:8px 14px;border:1px solid var(--line);border-radius:999px;background:var(--surface);color:var(--link);text-decoration:none;font-size:14px;line-height:1.3}
.stack{display:grid;gap:8px;margin:0 0 18px}
.stack a{display:flex;align-items:center;min-height:44px;padding:10px 14px;border:1px solid var(--line);border-radius:10px;background:var(--surface);color:var(--link);text-decoration:none;font-size:14.5px;line-height:1.4}
footer{background:#12211C;color:#B9C4BC;margin-top:48px}
.footer-wrap{max-width:1180px;margin:0 auto;padding:30px 24px;display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between}
.flogo{font-family:var(--headline);font-weight:800;font-size:19px;color:#FFF}
.flogo span{color:var(--accent)}
.flinks{display:flex;flex-wrap:wrap;gap:4px 8px}
.flinks a{display:inline-flex;align-items:center;justify-content:center;min-height:44px;min-width:44px;padding:0 8px;color:#B9C4BC;text-decoration:none;font-size:14px}
.fcopy{font-size:12px;color:#95A199;width:100%}
/* pilot-page tap-target floor (>=44px) over the shared nav's small-screen sizes */
.rw-nav__cta{min-height:44px!important}
.rw-nav__hamburger{min-width:44px;min-height:44px}
.rw-nav__logo{display:inline-flex;align-items:center;min-height:44px}
@media (max-width:1000px){.rw-nav__links a{display:inline-flex;align-items:center;justify-content:center;min-height:44px;min-width:44px}}
.skip-link{min-height:44px}
@media (max-width:640px){
  main{padding-top:84px}
  .tc{padding:4px 16px 44px}.crumb{padding:12px 16px 0}
  .facts{grid-template-columns:1fr;gap:8px}
  .fact{display:flex;align-items:baseline;gap:12px}
  .fact strong{font-size:24px;margin:0;min-width:3.2em}
  .pack{font-size:13.5px}
  .pack th,.pack td{padding:9px 6px}
  .pack th[scope=row]{width:34%}
  .footer-wrap{padding:26px 16px}
}
@media (max-width:1000px){main{padding-top:0}}
"""

GA4 = ("<script async src=\"https://www.googletagmanager.com/gtag/js?id=G-LRX309H9CH\"></script>\n"
       "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
       "gtag('js',new Date());var _rwInt=document.cookie.split(';').some(function(c){return c.trim()==="
       "'internal_traffic=true';});gtag('config','G-LRX309H9CH',_rwInt?{traffic_type:'internal'}:{});</script>")

TRACK_JS = """<script>
document.addEventListener("click",function(e){var a=e.target.closest("a");if(!a||typeof gtag!=="function")return;
var h=a.getAttribute("href")||"";if(h.indexOf("/audit/")!==-1){gtag("event","audit_cta_clicked",{page_path:location.pathname,
cta_location:a.dataset.ctaLocation||(a.closest("nav,header")?"nav":"body"),cta_text:(a.textContent||"").trim().slice(0,80),link_url:a.href});}});
</script>"""

FOOTER = """<footer>
  <div class="footer-wrap">
    <div class="flogo">Rank<span>wise</span></div>
    <div class="flinks">
      <a href="/#services">What we do</a>
      <a href="/#how">How it works</a>
      <a href="/blog/">Blog</a>
      <a href="/lab/">Lab</a>
      <a href="/audit/?utm_source=trade-city&amp;utm_medium=cta&amp;utm_content=footer">Free rank check</a>
    </div>
    <div class="fcopy">© 2026 Rankwise · local-search marketing · Lower Mainland, BC</div>
  </div>
</footer>"""

PRICE_A = ("Three set rates, month to month: Starter at $450/month (your profile fully optimized, a review "
           "system and a rank snapshot), Foundation at $750/month (the complete Maps program for one city) "
           "and Growth at $1,250/month (adds analytics, content and city expansion). No long contracts, no "
           "negotiation.")
CONTRACT_A = "No. It's month to month. If you want to stop, give 30 days' notice."
GUARANTEE_A = ("On Foundation and Growth, before month one we agree in writing on your starting Map Pack "
               "position and a 90-day milestone. Miss it, and billing pauses until we hit it. Starter "
               "carries a narrower written guarantee: your profile optimization is done within 30 days.")


def build(trade: str, city: str, facts: dict) -> str:
    cfg = TRADES[trade]
    t = facts["trades"][trade]
    c = t["cities"][city]
    s = city_stats(c)
    slug = page_slug(trade, city)
    url = f"{BASE}/{slug}/"
    label, biz, biz_pl = cfg["label"], cfg["biz"], cfg["biz_pl"]
    dates = date_phrase(s["dates"])
    kw_list = ", ".join(f"“{x['keyword']}”" for x in c["searches"][:-1]) + \
        f" and “{c['searches'][-1]['keyword']}”"

    title = f"{label} Marketing in {city}, BC: Map Pack Data | Rankwise"
    desc = (f"What Google's map pack showed for {s['n_searches']} {label.lower()} searches in {city} on "
            f"{dates}: {s['n_biz']} businesses, review counts from {fmt_reviews(s['min_reviews'])} up. "
            f"Market data, not client results.")
    h1 = f"{label} marketing in {city}, BC"
    sub = (f"Who Google put in the {city} map pack for {s['n_searches']} {label.lower()} searches on {dates}, "
           f"and what that tells a {biz} about getting in.")

    # ---- lead paragraph (all numbers from facts)
    if len(s["first_letters"]) == 1:
        f0 = s["firsts"][0]
        first_line = (f"The same listing (Business {f0['business']}, {fmt_reviews(f0['reviews'])} reviews) "
                      f"was first on every one of them.")
    else:
        parts = [f"{fmt_reviews(f['reviews'])}" for f in s["firsts"]]
        first_line = (f"The #1 result had {', '.join(parts[:-1])} and {parts[-1]} reviews across those "
                      f"searches ({len(s['first_letters'])} different listings took the top spot).")
    lead = (f"On {dates}, Rankwise ran {count_word(s['n_searches'])} Google searches set to {city}, BC "
            f"({kw_list}) and recorded the three businesses in each map pack. "
            f"{s['n_biz']} different businesses filled those {s['slots']} spots. "
            f"{first_line}")

    # ---- table
    rows = []
    for srch in c["searches"]:
        cells = []
        for pos in (1, 2, 3):
            hit = [r for r in srch["top3"] if r["position"] == pos]
            cells.append(f"<td><b>{hit[0]['business']}</b>{fmt_reviews(hit[0]['reviews'])}</td>"
                         if hit else "<td>none shown</td>")
        mark = " *" if srch["backfilled"] else ""
        rows.append(f"<tr><th scope=\"row\">{esc(srch['keyword'])}{mark}</th>{''.join(cells)}</tr>")
    cap_bits = [f"Letters are the same listing across searches in {city}; numbers are Google review counts "
                f"at capture. Business names are left out on purpose: this page describes the market, not "
                f"individual competitors. Captured {dates}."]
    if s["backfilled"]:
        cap_bits.append("* Re-queried on " + s["backfilled"][0]["captured_on"] +
                        " after the original request returned nothing; the value shown is from the re-query.")
    if any(r["reviews"] >= 1000 and r["reviews"] % 100 == 0 for x in c["searches"] for r in x["top3"]):
        cap_bits.append("Counts shown as “about” are rounded by Google (for example “1.6K”).")
    table = (f"<table class=\"pack\"><caption>{' '.join(cap_bits)}</caption>"
             "<thead><tr><th scope=\"col\">Search</th><th scope=\"col\">#1</th><th scope=\"col\">#2</th>"
             f"<th scope=\"col\">#3</th></tr></thead><tbody>{''.join(rows)}</tbody></table>")

    # ---- fact cards
    reg = t["region"]
    reg_dates = date_phrase(reg["captured_on"])
    facts_html = (
        '<div class="facts">'
        f'<div class="fact"><strong>{s["n_biz"]}</strong><span>different businesses held the {s["slots"]} '
        f'top-3 spots across {count_word(s["n_searches"])} searches</span></div>'
        f'<div class="fact"><strong>{fmt_reviews(s["min_reviews"])}</strong><span>fewest reviews on any '
        f'business in a top-3 spot here</span></div>'
        f'<div class="fact"><strong>{fmt_median(s["median"])}</strong><span>median reviews across those '
        f'{s["n_biz"]} businesses</span></div>'
        '</div>'
    )
    min_pos = sorted({r["position"] for x in c["searches"] for r in x["top3"]
                      if r["business"] == s["min_letter"]})
    min_where = " and ".join(f"#{p}" for p in min_pos)
    # does review count alone explain the order? (a listing with fewer reviews above one with more)
    inverted = any(hi["reviews"] < lo["reviews"]
                   for x in c["searches"] for i, hi in enumerate(x["top3"]) for lo in x["top3"][i + 1:])
    slot_count: dict[str, int] = {}
    for x in c["searches"]:
        for r in x["top3"]:
            slot_count[r["business"]] = slot_count.get(r["business"], 0) + 1
    top_letter = max(slot_count, key=lambda k: (slot_count[k], -ord(k)))
    all_full = all(len(x["top3"]) == 3 for x in c["searches"])
    order_line = ("In at least one search a listing with fewer reviews sat above one with more, so review "
                  "count alone did not set the order."
                  if inverted else
                  "In every search the order followed review count: more reviews, higher spot.")
    stands_out = [
        (f"<strong>Review counts in the pack ran from {fmt_reviews(s['min_reviews'])} to "
         f"{fmt_reviews(s['max_reviews'])}.</strong> The fewest belonged to Business {s['min_letter']}, at "
         f"{min_where}. {order_line}"),
        (f"<strong>{s['n_biz']} businesses for {s['slots']} spots.</strong> The most frequent listing, "
         f"Business {top_letter}, held {slot_count[top_letter]} of them."
         + (" Every search returned a full three-business pack, so getting in means displacing a listing "
            "that is already there, not filling an empty seat." if all_full else "")),
        (f"<strong>Across the region, for context (trade-level, not {city}-specific):</strong> in "
         f"{reg['first_under_threshold']} of {reg['searches_with_pack']} {label.lower()} searches across "
         f"{len(facts['region_cities'])} Lower Mainland and Fraser Valley cities in the same sweep "
         f"({reg_dates}), the #1 map result had fewer than {facts['thin_reviews_threshold']} reviews."),
    ]

    # ---- links
    others_trade = [x for x in CITIES if x != city]
    others_city = [x for x in TRADES if x != trade]
    chips_city = "".join(f'<a href="/{page_slug(trade, x)}/">{label} in {x}</a>' for x in others_trade)
    chips_trade = "".join(f'<a href="/{page_slug(x, city)}/">{TRADES[x]["label"]} in {city}</a>'
                          for x in others_city)

    faq = [
        ("How much does Rankwise cost?", PRICE_A),
        ("Am I locked into a contract?", CONTRACT_A),
        ("What if it doesn't work?", GUARANTEE_A),
        (f"Do you work with other {biz_pl} in {city}?",
         f"No. Rankwise takes one business per city, per service category, so we won't work with a "
         f"competing {biz} in {city} while you're a client."),
        ("Are these numbers client results?",
         f"No. Everything on this page is public Google map-pack data that Rankwise recorded on {dates}. "
         f"Nothing here is a client result."),
    ]
    faq_html = "".join(f'<div class="faq-item"><h3 class="faq-q">{esc(q)}</h3><p class="faq-a">{esc(a)}</p></div>'
                       for q, a in faq)
    ld_breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Rankwise", "item": BASE + "/"},
        {"@type": "ListItem", "position": 2, "name": f"{label} marketing", "item": BASE + cfg["hub"][0]},
        {"@type": "ListItem", "position": 3, "name": f"{label} marketing in {city}", "item": url}]}
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    ld = "\n".join(f'<script type="application/ld+json">\n{json.dumps(b, ensure_ascii=False)}\n</script>'
                   for b in (ld_breadcrumb, ld_faq))

    src_file = t["source_file"]
    nav = (ROOT / "partials" / "nav.html").read_text(encoding="utf-8").strip()
    cta_href = f"/audit/?utm_source=trade-city&amp;utm_medium=cta&amp;utm_campaign={slug}"

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#0F1815">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{ROBOTS}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
{GA4}
{ld}
<style>{STYLE}</style>
<link rel="stylesheet" href="/assets/rankwise-nav.css?v=rw-nav-a11y-20260610">
<script src="/assets/nav-mobile.js?v=rw-nav-a11y-20260611" defer></script>
</head>
<body>
{nav}
<main id="main-content">
<div class="crumb"><a href="/">Rankwise</a> · <a href="{cfg['hub'][0]}">{label} marketing</a> · {esc(city)}</div>
<article class="tc">
<div class="tc-head">
<span class="tc-badge">Map pack data · {esc(city)} · {dates}</span>
<h1>{esc(h1)}</h1>
<p class="tc-sub">{esc(sub)}</p>
</div>

<p>{esc(lead)}</p>
{facts_html}

<h2>What Google showed in {esc(city)}</h2>
{table}

<h2>What stands out</h2>
<ul>{''.join(f'<li>{x}</li>' for x in stands_out)}</ul>

<h2>What that means for a {esc(biz)} in {esc(city)}</h2>
<p>Review count is the most visible thing in a map pack, and it is one a business can grow on purpose. It is not the only thing Google weighs: distance from the person searching, the business category on the Google profile, and how closely the profile and website match the search all matter too. That is why a listing with fewer reviews can sit above one with more.</p>
<p>So the useful question is not “how many reviews do I need?” but “which of these gaps is mine?” The free rank check answers that for your business: where you appear for these {city} searches today, which listings sit above you, and what separates you from them.</p>

<h2>What Rankwise does</h2>
<ul>
<li>Google Business Profile optimization: categories, services, service area, photos and posts.</li>
<li>Review velocity: a steady system for asking customers for reviews and replying to them.</li>
<li>Citation and NAP consistency, so your name, address and phone match everywhere Google looks.</li>
<li>City-page and blog content for the searches that matter in {esc(city)}.</li>
<li>Map Pack tracking for your agreed search terms, reported every week.</li>
</ul>
<p>{esc(PRICE_A)}</p>
<p class="note">{esc(GUARANTEE_A)}</p>

<div class="tc-cta">
<h2>See where your business sits in {esc(city)}</h2>
<p>A free 15-minute rank check: your current map-pack position for these searches, measured the same way as the data on this page. No pitch deck.</p>
<a class="btn" href="{cta_href}" data-cta-location="pilot-cta">Book my free rank check</a>
</div>

<h2>How this data was collected</h2>
<p>Each search was run through SerpAPI against Google.ca with the search location set to “{esc(city)}, British Columbia, Canada”, and the top three map-pack results were recorded with their review counts. Searches: {esc(kw_list)}. Capture date: {dates}. This is one snapshot from one location per city: someone searching from another neighbourhood, on another day, may see a different pack. Review counts change daily.</p>
<p>Source: Rankwise's September 2026 map-pack sweep (<code>{esc(src_file)}</code>, {len(t['keywords'])} searches in each of 50 BC cities). The July 2026 Lab Market Study (linked below) covers a wider set of {label.lower()} searches across Metro Vancouver.</p>

<h2>FAQ</h2>
{faq_html}

<nav class="links" aria-label="Related pages">
<p class="links-label">{label} in other cities</p>
<div class="chips">{chips_city}</div>
<p class="links-label">Other trades in {esc(city)}</p>
<div class="chips">{chips_trade}</div>
<p class="links-label">Further reading</p>
<div class="stack"><a href="{cfg['hub'][0]}">{esc(cfg['hub'][1])}</a><a href="{cfg['lab'][0]}">{esc(cfg['lab'][1])}</a></div>
</nav>
</article>
</main>
{FOOTER}
{TRACK_JS}
</body></html>
"""


def pages(facts: dict):
    for trade in TRADES:
        for city in CITIES:
            yield page_slug(trade, city), build(trade, city, facts)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if any page differs from the generator")
    ap.add_argument("--refresh-facts", metavar="DASHBOARD_DIR",
                    help="re-derive the facts file from a rankwise-dashboard checkout (read-only)")
    args = ap.parse_args()

    if args.refresh_facts:
        facts = refresh_facts(Path(args.refresh_facts).resolve())
        FACTS.parent.mkdir(parents=True, exist_ok=True)
        FACTS.write_text(json.dumps(facts, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {FACTS.relative_to(ROOT)}")

    facts = load_facts()
    if args.check:
        drift = [slug for slug, body in pages(facts)
                 if not (ROOT / slug / "index.html").exists()
                 or (ROOT / slug / "index.html").read_text(encoding="utf-8") != body]
        if drift:
            print("DRIFT — regenerate these pilot pages:\n  " + "\n  ".join(drift))
            sys.exit(1)
        print("✓ all trade x city pilot pages match the generator")
        return
    for slug, body in pages(facts):
        out = ROOT / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
        print(f"✓ {slug}/index.html")


if __name__ == "__main__":
    main()
