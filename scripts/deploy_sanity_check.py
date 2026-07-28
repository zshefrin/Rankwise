#!/usr/bin/env python3
"""
deploy_sanity_check.py — pre-push / CI gate for Rankwise1 (the live rankwise.ca repo).

Rankwise1 had a secret scanner (scripts/secret_scan.py, added 2026-07-24) but
nothing checked the actual markup a push was about to ship. This adds three
more checks, SCOPED TO CHANGED FILES so a pre-existing site-wide issue can't
turn into a surprise blocker on an unrelated push:

  1. dead-path check   — no hardcoded reference to the retired
                          ~/Documents/GitHub location (2026-07-02 repath; see
                          rankwise-dashboard CLAUDE.md "Canonical paths").
                          Runs over ALL changed files, not just HTML.
  2. HTML spot-check    — doctype/html/head/body present, tag-balance on a
                          curated set of structural tags, and any inline
                          JSON-LD block actually parses as JSON. Not a full
                          validator — a cheap, stdlib-only tripwire for
                          malformed markup.
  3. link integrity     — every root-relative or self-referencing absolute
                          (https://rankwise.ca/...) href/src resolves to a
                          real path in the commit being pushed. External
                          domains are not checked (no network calls — this
                          must stay offline and fast).

Reads PUSHED content, not the working tree: every file this script inspects —
both the changed files themselves and every local link TARGET they point at —
is read via `git show <ref>:<path>` against TIP_REF (HEAD), never from disk.
This repo's tree is shared with cron writers (sitemap.xml regen, portal
republish, etc.), so a disk-read gate has two failure modes: it false-blocks
a push over an unrelated dirty file that isn't even part of the commit, and
it false-passes a genuinely broken commit if the working tree happens to be
hand-fixed-but-not-recommitted at push time. A file that's in the diff range
but no longer exists at TIP_REF (deleted or renamed away by this push) is
reported and skipped, not silently dropped.

NOTE: scripts/check_site_integrity.py already encodes real site invariants
(shared-nav hash, sitemap consistency) but is NOT run here — as of 2026-07-28
it fails on ~40 pre-existing pages (audits/*, portal/*, i/, a/,
tiktok-callback/) that intentionally skip the standard nav. Wiring it into a
blocking gate would turn every push red today. That's a separate site-content
cleanup, not a deploy-gate problem; see the caller for the deliberate omission.

Fails CLOSED: any internal error (git command failure) is a hard failure, not
a silent pass — the opposite of the "scanner reports clean when its git
subprocess errors" gap flagged against secret_scan.py in the 2026-07-25
production review.

Usage:
    python3 scripts/deploy_sanity_check.py                # diff vs @{upstream}, falls back to HEAD~1
    python3 scripts/deploy_sanity_check.py --base <ref>    # diff vs an explicit ref
    python3 scripts/deploy_sanity_check.py --all           # scan every file tracked at HEAD (audit / CI baseline)
"""

import html
import json
import posixpath
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
TIP_REF = "HEAD"  # the commit this push/PR is putting forward — what we grade

DEAD_PATH_NEEDLES = ("/Documents/GitHub", "~/Documents/GitHub")

SELF_HOSTS = {"rankwise.ca", "www.rankwise.ca"}
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:", "blob:", "sms:")

# Directories that hold intentionally non-standard markup — mirrors
# check_site_integrity.py's own SKIP_NAV set ({"_archive", "landing-preview",
# "partials"}) for the same reason: these aren't full standalone documents or
# are frozen dead content, so a "full HTML document" check doesn't apply.
SKIP_DIRS_STRUCTURE = {"_archive", "landing-preview", "partials"}
# Two specific files, not a whole directory: verified 2026-07-28 these are
# fetched as raw text and injected client-side (portal/index.html iframes
# system-map.html, which fetch()'s rankwise-atlas-shell.html) — never served
# as a top-level document, so no doctype/html/head/body wrapper is expected.
SKIP_FILES_STRUCTURE = {
    "portal/system/rankwise-atlas-shell.html",
    "portal/system/system-map.html",
}
# _archive/ pages deliberately link to sibling pages that were later removed
# (that's what makes them archived) — link-checking dead content against a
# live sitemap isn't a real signal, so skip it there specifically.
SKIP_DIRS_LINKS = {"_archive"}

# Anchored so a page that merely MENTIONS the string "http-equiv=refresh" (a
# blog post, a code sample) doesn't get its whole document-structure check
# silently skipped — must be an actual <meta http-equiv="refresh" ...> tag.
META_REFRESH_RE = re.compile(r'<meta\b[^>]*\bhttp-equiv\s*=\s*["\']refresh["\']', re.IGNORECASE)
# Word-boundary so "<head" doesn't also match "<header" (a real bug in the
# first version of this script — every page with a <header> before its <head>
# tag looked fine even when <head> was genuinely missing).
HEAD_OPEN_RE = re.compile(r"<head[ >]", re.IGNORECASE)

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
# HTML5 lets these close implicitly (next sibling / parent close does it).
# Don't hard-fail on them — real bugs show up as mismatches on structural tags.
SOFT_CLOSE_TAGS = {"li", "p", "option", "tr", "td", "th", "dt", "dd", "thead", "tbody", "tfoot"}
STRUCTURAL_TAGS = {
    "html", "head", "body", "header", "footer", "nav", "main",
    "div", "section", "article", "a", "table", "ul", "ol", "script", "style", "form",
}


def _first_dir(rel_path):
    parts = Path(rel_path).parts
    return parts[0] if parts else ""


def run_git(args):
    """Text-mode git invocation for simple, non-path output (rev-parse, merge-base)."""
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def _run_git_paths(args):
    """Run a git command that must be invoked with -z (NUL-delimited output) and
    return the list of paths. Plain .split()/.splitlines() on `git ls-files` or
    `git diff --name-only` output silently mis-parses filenames containing
    spaces, and relies on git's C-style quoting for non-ASCII names — -z
    disables quoting and gives an unambiguous delimiter."""
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.decode('utf-8', 'replace').strip()}")
    raw = result.stdout.decode("utf-8", errors="surrogateescape")
    return [p for p in raw.split("\0") if p]


def _exists_at_ref(rel_path, ref=TIP_REF):
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{ref}:{rel_path}"], cwd=ROOT, capture_output=True,
    )
    return result.returncode == 0


def read_at_ref(rel_path, ref=TIP_REF):
    """Content of rel_path as committed at `ref` — NOT the working tree.
    Returns None if the path doesn't exist at that ref (deleted/renamed away
    by this push — nothing to check, not an error). Raises RuntimeError on a
    genuine git failure (fails CLOSED via main()'s handler)."""
    if not _exists_at_ref(rel_path, ref):
        return None
    result = subprocess.run(
        ["git", "show", f"{ref}:{rel_path}"], cwd=ROOT, capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git show {ref}:{rel_path} failed: {result.stderr.decode('utf-8', 'replace').strip()}")
    return result.stdout.decode("utf-8", errors="ignore")


def _tracked_files_at(ref):
    return sorted(_run_git_paths(["ls-tree", "-r", "--name-only", "-z", ref]))


def changed_files(base_ref=None):
    """Return repo-relative paths added/copied/modified/renamed between
    base_ref and TIP_REF. Fails CLOSED: if git can't establish a diff base at
    all, falls back to scanning every file tracked at TIP_REF rather than
    silently checking nothing."""
    if base_ref is None:
        for candidate in ("@{upstream}", "origin/main", "HEAD~1"):
            try:
                run_git(["rev-parse", "--verify", candidate])
                base_ref = candidate
                break
            except RuntimeError:
                continue
    if base_ref is None:
        print(f"deploy-sanity: no diff base found (no upstream, no origin/main, no HEAD~1) "
              f"— falling back to a full tree scan at {TIP_REF}.", file=sys.stderr)
        return _tracked_files_at(TIP_REF)

    return _run_git_paths(["diff", "-z", "--name-only", "--diff-filter=ACMR", base_ref, TIP_REF])


def gather_contents(files, ref=TIP_REF):
    """Read every changed file's content AT ref once. Returns (contents,
    deleted): contents maps rel-path -> text for files present at ref;
    deleted lists rel-paths that were changed but don't exist at ref (deleted
    or renamed away by this push) — reported by the caller, not silently
    dropped."""
    contents = {}
    deleted = []
    for rel in files:
        text = read_at_ref(rel, ref)
        if text is None:
            deleted.append(rel)
        else:
            contents[rel] = text
    return contents, deleted


class _SpotCheckParser(HTMLParser):
    """Lightweight structural spot-check: tag balance + JSON-LD JSON validity."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.saw_doctype = False
        self._in_jsonld = False
        self._jsonld_buf = []
        self._jsonld_count = 0

    def handle_decl(self, decl):
        if decl.strip().lower().startswith("doctype html"):
            self.saw_doctype = True

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            attr_d = dict(attrs)
            if attr_d.get("type", "").strip().lower() == "application/ld+json":
                self._in_jsonld = True
                self._jsonld_buf = []
        if tag in VOID_TAGS:
            return
        self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass  # self-closed <tag/> — nothing pushed, nothing to pop.

    def handle_data(self, data):
        if self._in_jsonld:
            self._jsonld_buf.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            self._jsonld_count += 1
            raw = "".join(self._jsonld_buf).strip()
            if raw:
                try:
                    json.loads(html.unescape(raw))
                except Exception as exc:
                    self.errors.append(f"JSON-LD block {self._jsonld_count}: invalid JSON ({exc})")
        if tag in VOID_TAGS:
            return
        if not self.stack:
            if tag not in SOFT_CLOSE_TAGS:
                self.errors.append(f"stray closing </{tag}> with no matching open tag")
            return
        if self.stack[-1] == tag:
            self.stack.pop()
            return
        if tag in self.stack:
            skipped = []
            while self.stack and self.stack[-1] != tag:
                skipped.append(self.stack.pop())
            if self.stack:
                self.stack.pop()
            hard_skipped = [t for t in skipped if t not in SOFT_CLOSE_TAGS]
            if hard_skipped:
                self.errors.append(
                    f"closing </{tag}> skipped unclosed structural tag(s): {', '.join(hard_skipped)}"
                )
        elif tag not in SOFT_CLOSE_TAGS:
            self.errors.append(f"closing </{tag}> doesn't match open <{self.stack[-1]}>")


class _LinkParser(HTMLParser):
    """Collects href/src values worth checking for local link integrity."""

    LINK_ATTRS = {
        "a": "href", "link": "href",
        "img": "src", "script": "src",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        self._collect(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._collect(tag, attrs)

    def _collect(self, tag, attrs):
        attr_name = self.LINK_ATTRS.get(tag)
        if not attr_name:
            return
        attr_d = dict(attrs)
        val = attr_d.get(attr_name)
        if val:
            self.links.append(val)


# The dead-path check guards SERVED content only — html/css/js/xml that the live
# site actually delivers. Repo tooling legitimately contains the retired-path
# strings (this script's own DEAD_PATH_NEEDLES constants, CLAUDE.md's docs of
# them) — on its first real push this gate flagged its own source (2026-07-29),
# which is a scoping bug, not a detection win.
_DEAD_PATH_SCOPE = (".html", ".css", ".js", ".xml", ".txt")


def check_dead_paths(contents):
    errors = []
    for rel, text in contents.items():
        if not rel.endswith(_DEAD_PATH_SCOPE):
            continue
        for needle in DEAD_PATH_NEEDLES:
            if needle in text:
                errors.append(f"{rel}: references retired path containing '{needle}'")
    return errors


def _resolve_local_path(href, source_file_rel):
    """Return (repo-relative POSIX path with no leading slash, had_trailing_slash)
    worth checking for local link integrity, or None if not a local link.
    Pure path arithmetic (posixpath) — never touches the filesystem, since
    existence is checked against the git tree, not disk."""
    href = html.unescape(href).strip()
    if not href or href.startswith("#"):
        return None
    for scheme in SKIP_SCHEMES:
        if href.startswith(scheme):
            return None

    parts = urlsplit(href)
    if parts.scheme in ("http", "https"):
        if parts.netloc not in SELF_HOSTS:
            return None  # external domain — not our job, no network calls here
        path = parts.path or "/"
    elif parts.scheme:
        return None  # some other scheme (ftp:, etc.) — not our concern
    else:
        path = parts.path

    if not path:
        return None  # e.g. bare "?x=1" or fragment-only, already excluded above

    had_trailing_slash = path.endswith("/")
    if path.startswith("/"):
        combined = path.lstrip("/")
    else:
        combined = posixpath.join(posixpath.dirname(source_file_rel), path)
    combined = posixpath.normpath(combined)
    if combined == ".":
        combined = ""
    return combined, had_trailing_slash


def _link_target_exists(rel_path, had_trailing_slash, ref=TIP_REF):
    if rel_path == "" or had_trailing_slash:
        candidate = posixpath.join(rel_path, "index.html") if rel_path else "index.html"
        return _exists_at_ref(candidate, ref)
    if posixpath.splitext(rel_path)[1]:  # has a file extension — must exist literally
        return _exists_at_ref(rel_path, ref)
    # no trailing slash, no extension — accept either a matching directory's
    # index.html or a flat "<name>.html"
    return _exists_at_ref(posixpath.join(rel_path, "index.html"), ref) or _exists_at_ref(rel_path + ".html", ref)


def check_links(contents):
    errors = []
    for rel, text in contents.items():
        if _first_dir(rel) in SKIP_DIRS_LINKS:
            continue
        parser = _LinkParser()
        try:
            parser.feed(text)
        except Exception as exc:
            errors.append(f"{rel}: link parser choked ({exc})")
            continue
        for href in parser.links:
            resolved = _resolve_local_path(href, rel)
            if resolved is None:
                continue
            rel_path, had_trailing_slash = resolved
            if not _link_target_exists(rel_path, had_trailing_slash):
                errors.append(f"{rel}: broken local link '{href}'")
    return errors


def check_html_validity(contents):
    errors = []
    for rel, text in contents.items():
        if META_REFRESH_RE.search(text):
            continue  # redirect stubs carry no real body

        is_fragment = _first_dir(rel) in SKIP_DIRS_STRUCTURE or rel in SKIP_FILES_STRUCTURE

        if not is_fragment:
            if not text.lstrip().lower().startswith("<!doctype html"):
                errors.append(f"{rel}: missing '<!DOCTYPE html>' at the top of the file")
            if not HEAD_OPEN_RE.search(text):
                errors.append(f"{rel}: missing required element '<head'")
            for required in ("<html", "</html>", "</head>", "<body", "</body>"):
                if required not in text.lower():
                    errors.append(f"{rel}: missing required element '{required}'")

        parser = _SpotCheckParser()
        try:
            parser.feed(text)
        except Exception as exc:
            errors.append(f"{rel}: HTML parser choked ({exc})")
            continue
        for err in parser.errors:
            errors.append(f"{rel}: {err}")
        if not is_fragment:
            unclosed = [t for t in parser.stack if t not in SOFT_CLOSE_TAGS]
            if unclosed:
                errors.append(f"{rel}: unclosed structural tag(s) at end of file: {', '.join(unclosed)}")
    return errors


def main():
    args = sys.argv[1:]
    scan_all = "--all" in args
    base_ref = None
    if "--base" in args:
        base_ref = args[args.index("--base") + 1]

    try:
        files = _tracked_files_at(TIP_REF) if scan_all else changed_files(base_ref)
        contents, deleted = gather_contents(files)
    except RuntimeError as exc:
        # Fail CLOSED — a git failure must not read as "nothing changed".
        print(f"deploy-sanity: git error, failing closed: {exc}", file=sys.stderr)
        return 1

    if deleted:
        print(f"deploy-sanity: {len(deleted)} changed path(s) no longer exist at {TIP_REF} "
              f"(deleted/renamed by this push) — skipped, not an error:", file=sys.stderr)
        for rel in deleted:
            print(f"    {rel}", file=sys.stderr)

    html_contents = {rel: text for rel, text in contents.items() if rel.endswith(".html")}

    errors = []
    errors += check_dead_paths(contents)
    errors += check_html_validity(html_contents)
    errors += check_links(html_contents)

    if errors:
        print(f"deploy-sanity: {len(errors)} issue(s) found across {len(contents)} changed file(s) "
              f"(checked at {TIP_REF}, not the working tree):\n")
        for err in errors:
            print(f"    {err}")
        print("\n  Fix these, or if a hit is a deliberate false positive, ask before bypassing —")
        print("  this is the live site's deploy gate. Bypass (last resort): git push --no-verify")
        return 1

    print(f"deploy-sanity: {len(html_contents)} changed HTML file(s), {len(contents)} changed file(s) "
          f"— clean (checked at {TIP_REF}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
