"""Loads gene-level ground truth out of the DDR corpus (knowledge/
ddr_database, schema v2 - see 老师 §4.2 "靶标" field) for a design project's
linked source paper(s). This is what 合理新颖/复现率 diff a generated
design's genetic modifications against, instead of a hand-authored answer
key: the DDR corpus already carries `decision_chain[].target.gene` for every
curated paper, so reusing it avoids a second authoring effort.
"""
from __future__ import annotations

from functools import lru_cache

from harness.config import PROJECT_ROOT

_DDR_DIR = PROJECT_ROOT / "knowledge" / "ddr_database"


@lru_cache(maxsize=32)
def _load_ddr(ddr_id: str) -> dict | None:
    matches = sorted(_DDR_DIR.glob(f"{ddr_id}_*.json"))
    if not matches:
        exact = _DDR_DIR / f"{ddr_id}.json"
        if exact.is_file():
            matches = [exact]
    if not matches:
        return None
    import json

    return json.loads(matches[0].read_text(encoding="utf-8"))


def load_reference_targets(ddr_ids: list[str]) -> set[str]:
    """Union of every `decision_chain[].target.gene` across the given DDR
    ids, lowercased and deduped. Unknown/unloadable ids are skipped rather
    than raising - a stale or mistyped id should degrade the metric's
    denominator, not crash the whole computation."""
    genes: set[str] = set()
    for ddr_id in ddr_ids:
        ddr = _load_ddr(ddr_id)
        if ddr is None:
            continue
        for step in ddr.get("decision_chain", []):
            gene = (step.get("target") or {}).get("gene")
            if gene and isinstance(gene, str):
                genes.add(gene.strip().lower())
    return genes
