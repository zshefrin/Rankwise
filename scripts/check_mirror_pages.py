#!/usr/bin/env python3
"""Keep mirror pages (same article served at two URLs) byte-identical.

Source of truth: _content/mirror-pages.json. Each mirror must equal its canonical
file byte for byte, so the next edit to one cannot drift from the other.

Usage:
    python3 scripts/check_mirror_pages.py          # exit 1 on any drift
    python3 scripts/check_mirror_pages.py --sync   # copy canonical -> mirror
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "_content" / "mirror-pages.json"


def load_mirrors() -> list[dict]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))["mirrors"]


def main() -> int:
    sync = "--sync" in sys.argv[1:]
    bad = 0
    for pair in load_mirrors():
        canon, mirror = ROOT / pair["canonical"], ROOT / pair["mirror"]
        if sync:
            shutil.copyfile(canon, mirror)
            print(f"synced {pair['mirror']} <- {pair['canonical']}")
            continue
        if canon.read_bytes() != mirror.read_bytes():
            print(f"DRIFT: {pair['mirror']} differs from {pair['canonical']} "
                  f"(run: python3 scripts/check_mirror_pages.py --sync)")
            bad += 1
    if not sync and not bad:
        print("mirror pages identical")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
