"""One-time (but safe to re-run) cleanup of duplicate DDR records already
sitting in ``knowledge/ddr_database/`` from before per-paper dedup existed
(see ``harness/paper_extraction/ddr_converter.py::_find_existing_ddr``).

Groups existing DDR files by the same identity rule the extraction pipeline
now uses going forward (DOI if both non-empty, else normalized title), keeps
the most-recently-extracted record in each group, and deletes the rest.

Usage
-----
    cd agent/agent-harness/agent-harness
    python scripts/dedupe_ddr_database.py          # dry run, prints the plan
    python scripts/dedupe_ddr_database.py --apply  # actually deletes
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DDR_DIR = PROJECT_ROOT / "knowledge" / "ddr_database"


def _normalize_title(title: str) -> str:
    return re.sub(r"[^\w]+", " ", title.lower()).strip()


def _identity(rec: dict[str, Any]) -> str:
    ref = rec.get("metadata", {}).get("reference", {})
    doi = (ref.get("doi") or "").strip().lower()
    if doi:
        return f"doi:{doi}"
    return f"title:{_normalize_title(ref.get('title') or '')}"


def _sort_key(rec: dict[str, Any]) -> tuple[str, int]:
    meta = rec.get("extraction_meta", {})
    date = meta.get("extraction_date") or ""
    ddr_num_match = re.match(r"DDR-(\d+)", rec.get("ddr_id", ""))
    ddr_num = int(ddr_num_match.group(1)) if ddr_num_match else 0
    return (date, ddr_num)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="actually delete the superseded files (default: dry run)")
    args = parser.parse_args()

    if not DDR_DIR.is_dir():
        print(f"no such directory: {DDR_DIR}")
        return 1

    groups: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for f in sorted(DDR_DIR.glob("DDR-*.json")):
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"skip unreadable {f.name}: {exc}")
            continue
        if not rec.get("metadata", {}).get("reference", {}).get("title") and not rec.get("metadata", {}).get("reference", {}).get("doi"):
            continue
        groups.setdefault(_identity(rec), []).append((f, rec))

    total_removed = 0
    for identity, entries in groups.items():
        if len(entries) < 2:
            continue
        entries.sort(key=lambda e: _sort_key(e[1]))
        keep_path, keep_rec = entries[-1]
        drop = entries[:-1]
        print(f"duplicate group ({identity}): keeping {keep_path.name} ({keep_rec.get('ddr_id')})")
        for drop_path, drop_rec in drop:
            print(f"  -> removing {drop_path.name} ({drop_rec.get('ddr_id')})")
            total_removed += 1
            if args.apply:
                drop_path.unlink()

    if total_removed == 0:
        print("no duplicates found")
    elif not args.apply:
        print(f"\n{total_removed} file(s) would be removed - re-run with --apply to actually delete them")
    else:
        print(f"\n{total_removed} file(s) removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
