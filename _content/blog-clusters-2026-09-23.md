---
title: Blog same-intent cluster map (merge-decision input)
date: 2026-09-23
status: analysis only. Nothing in this file has been merged, deleted, redirected or noindexed.
source: rankwise-dashboard vault/_dev/index-coverage-diagnosis-2026-09-23.md (section 2, recommendation 3)
---

# Blog same-intent cluster map, 2026-09-23

This file is the input for the operator's decision on recommendation 3 of the index-coverage diagnosis: merge each same-intent blog cluster into one canonical post. **No post is merged, deleted or noindexed by the PR that adds this file.**

## How to read it

- **Coverage** is the Search Console URL Inspection state per weekly run (08-17, 08-19, 08-24, 08-31, 09-07, 09-14, 09-21) from rankwise-dashboard `vault/_research/data/gsc-index-coverage.jsonl`. I = indexed, C = crawled but not indexed, D = discovered but not crawled, U = unknown to Google. History starts 08-17, so there are seven runs. D and U flip between runs for never-crawled URLs; that is API noise.
- **Peak 28-day impressions** is the highest rolling-28-day impressions figure for the page in `gsc_snapshots` (page dimension, read-only query 2026-09-23). Page-dimension sums are known to be inflated, so use these numbers to rank pages against each other, not as totals. 0 means no row was ever recorded.
- **AI-cited** comes from the "cited ever" column of rankwise-dashboard `vault/_dev/aeo-page-inventory-2026-09-23.md`.
- **Words** is the visible text inside the article element of the live HTML in this repo.
- `/blog/hvac-marketing-cost/` has no coverage history because it only became the canonical sitemap URL today (PR 3). Its history lives under the long-slug mirror, `/blog/how-much-does-hvac-marketing-cost-in-british-columbia/`, which was `CCCCCCC` with a last crawl of 2026-04-30 and 131 peak impressions.

## Survivor rule, applied to every cluster

1. Keep the AI-cited URL if the cluster has one.
2. Otherwise keep the page with the most past impressions, not the newest page.
3. If the survivor is thinner than a sibling, fold the sibling's unique sections into it before the sibling becomes a noindex stub canonical to the survivor. That is the pattern the diagnosis recommends, since GitHub Pages cannot serve real 301 redirects.

## Membership

The diagnosis named about 8 clusters. Re-deriving membership from the H1s gives 9, because its "rank on Maps x3 (incl. how-long-to-rank x2)" group is really two pairs: two pages share the exact H1 "What's the Best Way to Rank My HVAC Business on Google Maps?", and two pages answer how long ranking takes. Two more candidate clusters that the diagnosis did not list are included at the end and marked CANDIDATE. Pages marked adjacent are listed for context and are not counted as merge members.

Result if every core recommendation is taken: 9 survivors, 11 pages folded into them (20 core members), which takes the 47-post sitemap blog to about 36 before the two candidate clusters are ruled on.

The hub, homepage and about links added in the same PR point only at pages that survive under this map.

## Clusters

### Marketing cost and spend

| URL | H1 | Words | Coverage 08-17→09-21 | Last crawl | Peak 28-day impressions | AI-cited |
|---|---|---|---|---|---|---|
| /blog/hvac-marketing-cost/ | How Much Does HVAC Marketing Cost in British Columbia? | 1258 | `not in sitemap runs` | — | 153 | yes |
| /blog/how-much-should-hvac-contractors-spend-on-marketing/ | What Percentage of Revenue Should HVAC Contractors Spend on Marketing? | 1078 | `IIIIIIC` | 2026-07-23 | 33 | no |
| /blog/how-much-should-hvac-contractors-spend-on-marketing-each-mon/ | How Much Should HVAC Contractors Spend on Marketing Each Month? | 1547 | `CCCCCCC` | 2026-06-09 | 0 | no |

**Recommended survivor: /blog/hvac-marketing-cost/.** It is the only AI-cited page in the cluster and has the most impressions (153; its long-slug mirror, which carried the coverage history until today, adds 131 and was crawled-not-indexed since the 04-30 crawl). Fold the two spend posts' percentage-of-revenue and monthly-budget sections into it. Operator call: the two spend posts answer a budget question rather than an agency-price question, so an alternative is to keep one spend post (the percentage-of-revenue page, indexed until 09-21) and merge only the monthly one into it.

### Agency vs in-house marketer

| URL | H1 | Words | Coverage 08-17→09-21 | Last crawl | Peak 28-day impressions | AI-cited |
|---|---|---|---|---|---|---|
| /blog/hvac-marketing-agency-vs-in-house-marketer/ | Should HVAC Contractors Hire a Marketing Agency or an In-House Marketer? | 1365 | `IIIICCC` | 2026-07-21 | 5 | no |
| /blog/hvac-marketing-agency-vs-hiring-an-in-house-marketer-which-m/ | HVAC Marketing Agency vs. Hiring an In-House Marketer: Which Makes More Sense for HVAC Contractors? | 1345 | `UUDDDDD` | never | 0 | no |

**Recommended survivor: /blog/hvac-marketing-agency-vs-in-house-marketer/.** It is the only member Google ever indexed or showed; the other was never crawled.

### Optimize a Google Business Profile

| URL | H1 | Words | Coverage 08-17→09-21 | Last crawl | Peak 28-day impressions | AI-cited |
|---|---|---|---|---|---|---|
| /blog/optimize-gbp-hvac-contractor/ | How Do I Optimize My Google Business Profile as an HVAC Contractor? | 901 | `IIIIIIC` | 2026-07-11 | 138 | no |
| /blog/how-do-i-optimize-my-google-business-profile-as-an-hvac-cont/ | How Do I Optimize My Google Business Profile as an HVAC Contractor? | 1178 | `IIIICCC` | 2026-07-11 | 27 | no |

**Recommended survivor: /blog/optimize-gbp-hvac-contractor/.** Both pages carry the same H1; this one has about 5x the impressions and stayed indexed until 09-21. Fold the other page's extra ~280 words in, since the survivor is the thinner page.

### Best way to rank on Google Maps

| URL | H1 | Words | Coverage 08-17→09-21 | Last crawl | Peak 28-day impressions | AI-cited |
|---|---|---|---|---|---|---|
| /blog/rank-hvac-google-maps/ | What's the Best Way to Rank My HVAC Business on Google Maps? | 829 | `CCCCCCC` | 2026-04-24 | 114 | no |
| /blog/whats-the-best-way-to-rank-my-hvac-business-on-google-maps/ | What's the Best Way to Rank My HVAC Business on Google Maps? | 1061 | `IIIICCC` | 2026-07-11 | 15 | no |
| /blog/how-to-fix-hvac-contractor-map-pack-ranking-issues/ | How Do I Fix My HVAC Contractor Map Pack Ranking? | 1948 | `UUUDDDD` | never | 0 | no |

**Recommended survivor: /blog/rank-hvac-google-maps/.** Same H1 as the second page; by the past-impressions rule it wins 114 to 15, but it is the thinnest page here (829 words) and was last crawled 04-24, so fold the 07-11 page's content into it. The third page (how-to-fix) is adjacent rather than a duplicate: it overlaps the indexed why-isnt-my-hvac-business-showing post more than this cluster. Decide it separately.

### How long ranking takes

| URL | H1 | Words | Coverage 08-17→09-21 | Last crawl | Peak 28-day impressions | AI-cited |
|---|---|---|---|---|---|---|
| /blog/how-long-does-it-take-to-rank-on-google-maps-for-hvac-keywor/ | How Long Does It Take to Rank on Google Maps for HVAC Keywords? | 986 | `IIIICCC` | 2026-04-30 | 130 | no |
| /blog/how-long-does-local-seo-take-for-hvac/ | How Long Does Local SEO Take for HVAC? (Honest Timeline) | 1461 | `UUDDDDU` | never | 0 | no |

**Recommended survivor: /blog/how-long-does-it-take-to-rank-on-google-maps-for-hvac-keywor/.** It holds all of the cluster's impressions (130); the other page was never crawled.

### Primary GBP category

| URL | H1 | Words | Coverage 08-17→09-21 | Last crawl | Peak 28-day impressions | AI-cited |
|---|---|---|---|---|---|---|
| /blog/google-business-profile-category-hvac-contractors/ | What Google Business Profile Category Should HVAC Contractors Use? | 1466 | `IIIIIII` | 2026-07-17 | 10 | no |
| /blog/what-primary-category-should-an-hvac-contractor-pick-on-goog/ | What Primary Category Should an HVAC Contractor Pick on Google Business Profile? | 1890 | `UUUDDDD` | never | 0 | no |

**Recommended survivor: /blog/google-business-profile-category-hvac-contractors/.** It is indexed on every run and linked from the hubs in this PR; the longer 1,890-word sibling was never crawled, so fold its unique sections in.

### Posting on a GBP

| URL | H1 | Words | Coverage 08-17→09-21 | Last crawl | Peak 28-day impressions | AI-cited |
|---|---|---|---|---|---|---|
| /blog/should-hvac-contractors-post-on-google-business-profile/ | Should HVAC Contractors Post on Google Business Profile? | 1251 | `IIICCCC` | 2026-07-11 | 16 | no |
| /blog/how-often-should-hvac-contractors-post-on-google-business-profile/ | How Often Should HVAC Contractors Post on Google Business Profile? | 1162 | `UUDUDDD` | never | 0 | no |

**Recommended survivor: /blog/should-hvac-contractors-post-on-google-business-profile/.** It is the only member ever indexed or shown; add the how-often answer to it as a section.

### Local ranking signals

| URL | H1 | Words | Coverage 08-17→09-21 | Last crawl | Peak 28-day impressions | AI-cited |
|---|---|---|---|---|---|---|
| /blog/signals-google-uses-rank-local-hvac-businesses/ | What Signals Does Google Use to Rank Local HVAC Businesses? | 1905 | `IIICCCC` | 2026-07-09 | 14 | yes |
| /blog/7-local-ranking-signals-hvac-contractors-google-maps-metro-vancouver/ | What Are the 7 Local Ranking Signals That Determine Where HVAC Contractors Appear on Google Maps in Metro Vancouver? | 1533 | `UUDDDDU` | never | 0 | no |

**Recommended survivor: /blog/signals-google-uses-rank-local-hvac-businesses/.** It is AI-cited, the longest page, and the only member ever indexed.

### More leads, calls and customers

| URL | H1 | Words | Coverage 08-17→09-21 | Last crawl | Peak 28-day impressions | AI-cited |
|---|---|---|---|---|---|---|
| /blog/how-do-i-get-more-hvac-leads-in-vancouver/ | How Do I Get More HVAC Leads in Vancouver? | 1333 | `IIIIIII` | 2026-07-01 | 182 | no |
| /blog/how-to-get-more-hvac-service-calls/ | How Do I Get More HVAC Service Calls Each Month? | 1526 | `UUUDDUD` | never | 0 | no |
| /blog/how-do-hvac-contractors-find-new-customers-in-2026/ | How Do HVAC Contractors Find New Customers in 2026? | 1555 | `UUUUUDD` | never | 0 | no |
| /blog/whats-the-best-hvac-lead-generation-strategy/ | What's the Best HVAC Lead Generation Strategy? | 1350 | `IIICCCC` | 2026-07-10 | 29 | no |

**Recommended survivor: /blog/how-do-i-get-more-hvac-leads-in-vancouver/.** It is indexed on every run, home-linked, and holds 182 of the cluster's impressions. The service-calls and find-customers pages were never crawled. The lead-generation-strategy page is adjacent (strategy comparison rather than how-to); decide it separately.

### CANDIDATE: choosing or vetting an agency

| URL | H1 | Words | Coverage 08-17→09-21 | Last crawl | Peak 28-day impressions | AI-cited |
|---|---|---|---|---|---|---|
| /blog/who-should-i-hire-for-hvac-marketing-in-vancouver/ | Who Should I Hire for HVAC Marketing in Vancouver? | 1526 | `IIIIIII` | 2026-08-24 | 73 | yes |
| /blog/local-seo-agency-hvac-contractors/ | What Does a Local SEO Agency Actually Do for HVAC Contractors? | 1238 | `CCCCCCC` | 2026-04-24 | 183 | no |
| /blog/what-to-ask-hvac-agency/ | What Should You Actually Ask an HVAC Marketing Agency Before Hiring One? | 1416 | `IIICCCC` | 2026-07-11 | 7 | no |
| /blog/how-to-choose-an-hvac-marketing-agency-in-metro-vancouver/ | How to Choose an HVAC Marketing Agency in Metro Vancouver | 1537 | `UUDDDUD` | never | 0 | no |
| /blog/best-hvac-marketing-agency-canada/ | What Is the Best HVAC Marketing Agency in Canada? | 963 | `UUDDDDU` | never | 0 | no |
| /blog/what-should-hvac-marketing-agency-deliver-each-month/ | What Should an HVAC Marketing Agency Deliver Each Month? | 1411 | `UUDDUDD` | never | 0 | no |

**Not in the diagnosis; flagged for review.** Tentative survivor: /blog/who-should-i-hire-for-hvac-marketing-in-vancouver/, which is AI-cited, indexed on every run and home-linked. This conflicts with the past-impressions rule, because the local-seo-agency page peaked higher (183). That page answers what an agency does rather than whom to hire, so it may be a separate intent. The operator should rule on membership before any merge.

### CANDIDATE: marketing ideas and strategy

| URL | H1 | Words | Coverage 08-17→09-21 | Last crawl | Peak 28-day impressions | AI-cited |
|---|---|---|---|---|---|---|
| /blog/what-are-the-best-hvac-marketing-ideas-that-actually-work/ | What Are the Best HVAC Marketing Ideas That Actually Work? | 1853 | `CCCCCCC` | 2026-06-13 | 19 | no |
| /blog/best-hvac-marketing-strategies-2026/ | What Are the Best HVAC Marketing Strategies for Metro Vancouver Contractors? | 1684 | `IIICCCC` | 2026-07-21 | 6 | no |
| /blog/how-to-grow-hvac-business-metro-vancouver/ | How Do I Grow My HVAC Business in Metro Vancouver? | 1565 | `UUUUUDU` | never | 0 | no |

**Not in the diagnosis; flagged for review.** Tentative survivor by impressions: /blog/what-are-the-best-hvac-marketing-ideas-that-actually-work/ (19 against 6). Neither page is indexed now. The grow-my-business page was never crawled.
