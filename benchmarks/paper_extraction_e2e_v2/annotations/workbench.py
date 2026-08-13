"""Human review lifecycle; refuses Gold without explicit human adjudication."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import validate

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / "gold_workbench.schema.json").read_text(encoding="utf-8"))


def initialize(silver: Path, output: Path) -> None:
    source = json.loads(silver.read_text(encoding="utf-8"))
    review = {"annotation_tier": "silver", "annotation_source": str(silver), "annotator_status": "AI_ASSISTED",
              "review_status": "PENDING", "adjudication_status": "PENDING", "papers": source.get("papers", [])}
    output.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")


def finalize(review_path: Path, output: Path, reviewer: str) -> None:
    if not reviewer.strip():
        raise ValueError("named human reviewer is required")
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if review.get("review_status") != "HUMAN_REVIEWED" or review.get("adjudication_status") != "ADJUDICATED":
        raise ValueError("human review and adjudication must be complete")
    review.update(annotation_tier="gold", annotator_status="HUMAN_REVIEWER", annotation_source=f"human:{reviewer}")
    validate(review, SCHEMA)
    output.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init"); init.add_argument("silver", type=Path); init.add_argument("output", type=Path)
    final = sub.add_parser("finalize"); final.add_argument("review", type=Path); final.add_argument("output", type=Path); final.add_argument("--reviewer", required=True)
    args = parser.parse_args()
    initialize(args.silver, args.output) if args.command == "init" else finalize(args.review, args.output, args.reviewer)


if __name__ == "__main__": main()
