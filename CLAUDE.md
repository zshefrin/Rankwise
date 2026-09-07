# Rankwise1 — rankwise.ca (live site)

Public GitHub Pages site for Rankwise. Static HTML, no build system, no server side. Everything here is OUTWARD-FACING — changes ship to prospects. Business truth (offer/pricing/guarantee wording) is canonical in `../rankwise-dashboard/vault/POSITIONING.md` — link, don't copy.

## Hosting facts (verified 2026-07-03)

- GitHub Pages, custom domain via `CNAME` = `rankwise.ca`; A records 185.199.108–111.153 (Pages).
- Registrar: **Squarespace Domains Canada Inc.**; DNS: **Google Cloud DNS** (`ns-cloud-a*.googledomains.com`) — both confirmed via whois/dig 2026-07-03.
- No server-side redirects exist (static Pages) — any "301" must be a meta-refresh/JS pattern.
- Git pushes use SSH alias `github-rankwise` (key `~/.ssh/rankwise_github`).

## Deploy gate (added 2026-07-24, extended 2026-07-28)

This repo had NO pre-push hook and NO CI at all until 2026-07-24 — a real gap, since the dashboard's daily `auto_fix` cron republishes whatever is on `origin/main` unattended (`PROD_REPUBLISH_ARMED=true`). Two layers now watch every push — only the first can actually stop one:
- **Local pre-push hook** (`.git/hooks/pre-push`, NOT version-controlled — reinstall on a new machine with `cp scripts/git-hooks/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push`): `scripts/secret_scan.py --all` (whole-tree), then `scripts/deploy_sanity_check.py` (dead `~/Documents` path refs, HTML spot-check, broken internal links — scoped to files the push actually changed, read from the commit being pushed via `git show`, not the working tree). Both fail CLOSED if the script is missing. This is the only layer that can block a push before it reaches origin.
- **CI, detect-after only** (`.github/workflows/secret-scan.yml`, `.github/workflows/deploy-sanity.yml`): same checks, runs regardless of whether the local hook is installed — but GitHub Pages serves whatever lands on `origin/main` regardless of CI's pass/fail status. On a machine without the hook installed, CI does not stop a bad push from going live; it only surfaces it after the fact.
- `scripts/deploy_sanity_check.py` is diff-scoped on purpose: `scripts/check_site_integrity.py` (nav/sitemap invariants) currently fails on ~40 pre-existing non-standard pages (`audits/*`, `portal/system/*`, `i/`, `a/`) and is NOT wired into either gate — doing so would block every push today. That cleanup is separate, unstarted work.
- Known pre-existing debt the new link-integrity check surfaced: 10 `audits/*/index.html` pages render `href="unknown"` when a prospect has no known website — a template bug in the audit-page generator (dashboard-side; FIXED 2026-07-29, rankwise-dashboard 160962e6 — no new pages can carry it; the 10 existing ones regenerate clean on their next audit refresh). This does NOT retroactively block the already-published pages, but the hook WILL gate any future push that re-touches one of those 10 files while the placeholder is still present.

## Generated pages — NEVER hand-edit (has broken prod before)

| Surface | Generator (lives in rankwise-dashboard) |
|---|---|
| `blog/<slug>/`, `blog/index.html` | `vault/_export/publish_blog.py` |
| `lab/<slug>/`, `lab/index.html`, homepage lab-count badge | `vault/_export/publish_lab.py` |
| `audits/<slug>/`, `audits/index.html` | `vault/_system/publish_audit.py` (auto-commits AND pushes) |
| `portal/index.html` | `vault/_system/publish_portal_page.py` ⚠ hardcodes the RETIRED `~/Documents/GitHub` output path (line 35) — fix before relying on republish |
| `*-hvac-marketing/` (17 city pages) | `_generate_city_pages.py` (repo root here) |
| `sitemap.xml` | `generate_sitemap.py` (`--check` to verify) |

Edit the templates inside those scripts, not the output. There are no generator markers in the HTML — you cannot tell by looking; check the table.

## Nav sync — one source of truth

- `partials/nav.html` is THE nav. Propagate with `scripts/sync_nav.py`; `scripts/check_site_integrity.py` pins a mirror regex (`RW_NAV_RE`) — change the header shape and you must update it or the check goes red.
- `assets/nav-mobile.js` hard-selects `.rw-nav` / `.rw-nav__links` and silently no-ops if absent — nav class names are a contract.
- `publish_blog.py` hardcodes the nav: after any blog publish, re-run/verify `sync_nav`.

## Other hard rules

1. **City pages embed the homepage `<style>` block at generation time** — after ANY home CSS change: `python3 _generate_city_pages.py` then `--check`, or 17 pages silently drift.
2. **Wording compliance (see POSITIONING.md):** guarantee is ONLY "starting Map Pack position + 90-day milestone agreed in writing; miss it, billing pauses until we hit it". BANNED: "no payment", "you don't pay", "no charge for that month", money-back/free-month. No fabricated client results (0 clients) — Lab proof is labeled Market Study / Visibility Experiment / Lab Note. Brand is "Rankwise", never leads with "AI". ⚠ Known violations still live: About page + 5 blog posts (operator-gated cleanup, in NEEDS-ZACK 2026-07-03).
3. `assets/rankwise-theme.css` has a bare `h1,h2{...!important}` rule — scope overrides when promoting heading tags. Theme overrides go through CSS variables in that file.
4. Cache-bust `assets/home-map.css` (`?v=metro-map-N`, referenced twice in index.html) on map CSS changes.
5. FAQ #1 payback math exists in BOTH visible answer and FAQPage JSON-LD — keep in sync.
6. GA4 `G-LRX309H9CH`; custom funnel events `audit_cta_clicked` / `audit_request_submitted` (Key Event). `form_start`/`click` are expected-zero (cross-origin Cal.com iframe) — NOT a bug.
7. PREVIEW-FIRST for UI work: iterate in `../preview-redesign/`, port onto live mechanics only after operator approval. QA over `http.server`, never `file://`.

## Repo gotchas

- Other tabs + automation push here (`publish_audit.py`, portal republish, sync-queue) — `git fetch` before "not pushed" claims; never `git add -A`.
- Design language: field-journal (see preview-redesign/_design-system/). Site is HVAC-only per beachhead plan; trade generalization waits for published studies.
- ⚠ Stale paths inside this repo's own config (found 2026-07-03, not yet fixed): `.claude/skills/rankwise-site-publisher/SKILL.md` and `.claude/launch.json` still reference `~/Documents/GitHub/...` — canonical is `~/dev/GitHub/Rankwise/...`.
