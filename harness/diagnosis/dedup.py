"""Hypothesis Deduplicator (doc03 4.6): merges only genuinely identical
claims, keeps parent/child + overlap relationships, and never discards a
mechanistically distinct alternative because its wording resembles
another. Two hypotheses are duplicates ONLY if they share the same
`mechanism_class` AND identical `causal_graph_nodes` (same underlying
mechanism, not just similar phrasing) - deliberately conservative so real
alternatives are never silently collapsed.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from harness.diagnosis.hypothesis_generator import GeneratedHypothesis


@dataclass
class DedupGroup:
    kept: GeneratedHypothesis
    merged: list[GeneratedHypothesis] = field(default_factory=list)
    reason: str = ""


def deduplicate(hypotheses: list[GeneratedHypothesis]) -> tuple[list[GeneratedHypothesis], list[DedupGroup]]:
    kept: list[GeneratedHypothesis] = []
    groups: list[DedupGroup] = []
    seen: dict[tuple, GeneratedHypothesis] = {}

    for h in hypotheses:
        key = (h.mechanism_class, tuple(sorted(h.causal_graph_nodes)))
        if key in seen:
            existing = seen[key]
            group = next((g for g in groups if g.kept is existing), None)
            if group is None:
                group = DedupGroup(kept=existing, reason=f"same mechanism_class={h.mechanism_class!r} and identical causal_graph_nodes")
                groups.append(group)
            group.merged.append(h)
        else:
            seen[key] = h
            kept.append(h)

    return kept, groups
