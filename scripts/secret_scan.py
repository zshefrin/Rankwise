#!/usr/bin/env python3
"""
secret_scan.py — block secrets from entering git history (vibecoding guardrail G1).

The audit found `.gitignore` was the ONLY thing standing between the repo and a
leaked credential — and it had already failed twice (an Anthropic key and a
Google OAuth client_secret both reached pushed history). This scanner is the
compensating control the CSA research names as the #1 missing gate: a
pre-commit + CI scan that treats AI-authored code as untrusted input.

Scans the ADDED lines of the staged diff (or, with --all, the whole tree) for
high-signal credential patterns. Exits non-zero on any hit so the commit aborts.

Bypass an individual false positive by appending `  # pragma: allowlist secret`
to the line. Bypass the whole hook only as a last resort: `git commit --no-verify`.

Usage:
    python3 secret_scan.py            # scan staged diff (pre-commit)
    python3 secret_scan.py --all      # scan all tracked files (CI / audit)
"""

import base64
import re
import subprocess
import sys

ALLOW_MARK = "pragma: allowlist secret"

# (name, compiled regex). High-signal only — tuned to avoid blocking os.environ
# reads and env-var names, which are how this codebase correctly handles creds.
PATTERNS = [
    ("Anthropic API key", re.compile(r"sk-ant-[A-Za-z0-9\-]{24,}")),
    ("OpenAI API key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}\b")),
    ("Google OAuth client secret", re.compile(r"GOCSPX-[A-Za-z0-9_\-]{20,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,}")),
    ("Stripe live key", re.compile(r"\b[sr]k_live_[0-9A-Za-z]{16,}")),
    ("Twilio API Key SID", re.compile(r"\bSK[0-9a-fA-F]{32}\b")),
    ("Twilio Account SID", re.compile(r"\bAC[0-9a-f]{32}\b")),
    # The bare 32-hex auth token has no prefix; flag it only when a TWILIO / AUTH_TOKEN
    # keyword sits next to it on the same line (ultrareview #37 -- two tokens already leaked).
    ("Twilio auth token (keyword-adjacent)",
     re.compile(r"(?i)(?:TWILIO|AUTH[_-]?TOKEN)[A-Z0-9_]*\s*[:=]\s*['\"]?[0-9a-fA-F]{32}\b")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP |DSA )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[0-9A-Za-z]{36,}")),
]

# A JWT whose decoded payload contains service_role is a Supabase SECRET key
# (the anon/publishable JWT is public by design and is allowed through).
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\b")


def _b64pad(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _is_service_role_jwt(token: str) -> bool:
    try:
        payload = token.split(".")[1]
        return b"service_role" in _b64pad(payload)
    except Exception:
        return False


def scan_line(text: str):
    """Return a list of finding labels for a single line of content."""
    if ALLOW_MARK in text:
        return []
    hits = []
    for name, rx in PATTERNS:
        if rx.search(text):
            hits.append(name)
    for m in JWT_RE.finditer(text):
        if _is_service_role_jwt(m.group(0)):
            hits.append("Supabase service_role JWT")
    return hits


def staged_added_lines():
    """Yield (path, lineno_in_new_file, line_text) for ADDED lines in the staged diff."""
    diff = subprocess.run(
        ["git", "diff", "--cached", "--unified=0", "--no-color"],
        capture_output=True, text=True,
    ).stdout
    path = None
    newln = 0
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
        elif line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            newln = int(m.group(1)) if m else 0
        elif line.startswith("+") and not line.startswith("+++"):
            yield path, newln, line[1:]
            newln += 1
        elif not line.startswith("-"):
            newln += 1


def all_tracked_lines():
    files = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split()
    for f in files:
        try:
            with open(f, "r", errors="ignore") as fh:
                for i, line in enumerate(fh, 1):
                    yield f, i, line.rstrip("\n")
        except (OSError, UnicodeError):
            continue


def main():
    source = all_tracked_lines() if "--all" in sys.argv else staged_added_lines()
    findings = []
    for path, lineno, text in source:
        for label in scan_line(text):
            findings.append((path, lineno, label))
    if findings:
        print("✗ secret-scan: potential credentials detected — commit blocked.\n")
        for path, lineno, label in findings:
            print(f"    {path}:{lineno}  →  {label}")
        print("\n  If this is a false positive, append  # pragma: allowlist secret  to the line,")
        print("  or move the value into an env var / token store. Last resort: git commit --no-verify")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
