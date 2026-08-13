"""Module 4 - Genetic Engineering Design: turn key nodes into concrete, ranked modifications.

Per the revision spec, suggestions are not an unordered list: each one
gets a priority tier and a reason for that tier, so the report can present
a ranked engineering strategy instead of a flat gene list.
"""
from __future__ import annotations

from typing import Any

# DDR design_action -> spec's modification vocabulary (mostly a pass-through,
# since the mock DDRs already use this vocabulary; kept explicit so a future
# literature-extraction backend doesn't silently produce an unsupported term).
MODIFICATION_VOCABULARY = {
    "knockout": "knockout",
    "knockdown": "knockdown",
    "overexpression": "overexpression",
    "gene insertion": "gene insertion",
    "promoter engineering": "promoter engineering",
    "rbs tuning": "RBS tuning",
    "point mutation": "point mutation",
}

# node_type -> (priority tier, reason for that tier). A rate-limiting,
# feedback-inhibited enzyme is the most direct lever on flux (primary);
# a regulatory bottleneck gives complementary, global derepression
# (secondary); a competing/branch-point intervention is valuable but not
# essential to attempt first (optional).
_PRIORITY_BY_NODE_TYPE: dict[str, tuple[str, str]] = {
    "rate-limiting enzyme": (
        "primary intervention",
        "directly removes committed-step regulation - the most direct lever on pathway flux",
    ),
    "regulatory bottleneck": (
        "secondary optimization",
        "provides global derepression that complements the primary intervention",
    ),
    "branch point": (
        "optional exploration",
        "addresses a competing or precursor-limited branch; most valuable once the primary bottleneck is relieved",
    ),
}
_GENERIC_PRIORITY = (
    "optional exploration",
    "no specific priority evidence in the V0.1 mock store; flagged for future analysis",
)

PRIORITY_ORDER = ["primary intervention", "secondary optimization", "optional exploration"]


def design(nodes: list[dict[str, Any]], literature_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Produce one ranked engineering suggestion per key node, grounded in its DDR when available."""
    by_target = {record.get("target", "").lower(): record for record in literature_records}
    designs: list[dict[str, Any]] = []
    for node in nodes:
        target = node["target"]
        record = by_target.get(target.lower())
        if record and record.get("design_action") in MODIFICATION_VOCABULARY:
            modification = MODIFICATION_VOCABULARY[record["design_action"]]
            reason = record.get("hypothesis") or node["reason"]
            expected_effect = record.get("expected_effect") or node["suggested_strategy"]
        else:
            modification = "knockout" if node["node_type"] == "branch point" else "overexpression"
            reason = node["reason"]
            expected_effect = node["suggested_strategy"]

        priority, priority_reason = _PRIORITY_BY_NODE_TYPE.get(node["node_type"], _GENERIC_PRIORITY)

        designs.append({
            "gene": target,
            "modification": modification,
            "reason": reason,
            "expected_effect": expected_effect,
            "priority": priority,
            "priority_reason": priority_reason,
        })

    order_index = {tier: i for i, tier in enumerate(PRIORITY_ORDER)}
    designs.sort(key=lambda d: order_index.get(d["priority"], len(PRIORITY_ORDER)))
    return designs
