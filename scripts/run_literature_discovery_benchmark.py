from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from harness.literature_discovery.acquisition import AcquisitionManager, handoff_manifest
from harness.literature_discovery.models import RelevanceTier, ScientificLiteratureRequest
from harness.literature_discovery.service import LiteratureDiscoveryService


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/data/literature/literature_discovery_benchmark_k12_tryptophan.json")
    parser.add_argument("--cache-dir", default="artifacts/literature_discovery/cache")
    parser.add_argument("--pdf-dir", default="artifacts/literature_discovery/pdfs")
    parser.add_argument("--acquire", type=int, default=3, help="Acquire up to N top Tier 1/2 candidates")
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()

    request = ScientificLiteratureRequest.k12_tryptophan()
    result = LiteratureDiscoveryService(cache_dir=Path(args.cache_dir)).discover(request, use_cache=not args.fresh)
    manager = AcquisitionManager(Path(args.pdf_dir))
    selected = [c for c in result.candidates if c.relevance and c.relevance.decision in {RelevanceTier.TIER_1, RelevanceTier.TIER_2}][: max(args.acquire, 0)]
    for candidate in selected:
        candidate.acquisition = manager.acquire(candidate)
    tiers = Counter(c.relevance.decision.value for c in result.candidates if c.relevance)
    acquisition = Counter(c.acquisition.state.value for c in selected)
    artifact = {
        "benchmark_version": "1.0",
        "configuration": request.model_dump(mode="json"),
        "statistics": {
            "query_count": len(result.queries), "source_count": len(result.source_runs),
            "raw_hits": sum(s.raw_hits for s in result.source_runs), "source_runs": [s.model_dump(mode="json") for s in result.source_runs],
            "normalized_candidates": sum(s.raw_hits for s in result.source_runs), "deduplicated_candidates": len(result.candidates),
            "relevance_tiers": dict(tiers), "acquisition_selected": len(selected), "acquisition_states": dict(acquisition),
        },
        "queries": [q.model_dump(mode="json") for q in result.queries],
        "candidates": [c.model_dump(mode="json") for c in result.candidates],
        "handoff": handoff_manifest(selected),
    }
    Path(args.output).write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(artifact["statistics"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
