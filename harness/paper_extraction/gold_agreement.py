"""Structure-aware human annotation agreement. No model predictions are treated as labels."""
from __future__ import annotations

from collections import Counter
from typing import Any


def _tokens(value: Any) -> set[str]:
    import json, re
    return set(re.findall(r"[a-z0-9]+", json.dumps(value, ensure_ascii=False, sort_keys=True).casefold()))


def _similarity(a: dict[str, Any], b: dict[str, Any]) -> float:
    fields = ("critical_provenance", "biological_objects", "intervention_or_design_action", "conditions", "controls", "readouts", "results")
    scores = []
    for field in fields:
        x, y = _tokens(a.get(field)), _tokens(b.get(field))
        scores.append(len(x & y) / len(x | y) if x | y else 1.0)
    return sum(scores) / len(scores)


def _greedy_match(a: list[dict[str, Any]], b: list[dict[str, Any]], threshold: float = .45) -> list[tuple[int, int, float]]:
    candidates = sorted(((_similarity(x, y), i, j) for i, x in enumerate(a) for j, y in enumerate(b)), reverse=True)
    used_a: set[int] = set(); used_b: set[int] = set(); matches = []
    for score, i, j in candidates:
        if score < threshold or i in used_a or j in used_b: continue
        used_a.add(i); used_b.add(j); matches.append((i, j, score))
    return matches


def categorical_agreement(a: list[str], b: list[str]) -> dict[str, Any]:
    if not a or len(a) != len(b): return {"status": "NOT_ESTIMABLE", "reason": "no paired human categorical labels", "n": 0}
    labels = sorted(set(a) | set(b)); matrix = {x: {y: 0 for y in labels} for x in labels}
    for x, y in zip(a, b): matrix[x][y] += 1
    observed = sum(x == y for x, y in zip(a, b)) / len(a)
    ca, cb = Counter(a), Counter(b); expected = sum(ca[x] / len(a) * cb[x] / len(a) for x in labels)
    kappa = (observed - expected) / (1 - expected) if expected < 1 else None
    return {"status": "MEASURED_HUMAN", "n": len(a), "raw_agreement": observed, "cohen_kappa": kappa,
            "prevalence_warning": max(max(ca.values()), max(cb.values())) / len(a) > .8, "confusion_matrix": matrix}


def agreement_report(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    human = all(x.get("annotator_id") not in (None, "", "UNASSIGNED") and x.get("annotation_tier") in {"HUMAN_DRAFT", "HUMAN_REVIEWED"} for x in (a, b))
    if not human:
        return {"status": "NOT_ESTIMABLE", "reason": "no paired independent human annotations", "sample_size": 0,
                "experiment": {"status": "NOT_ESTIMABLE"}, "claim": {"status": "NOT_ESTIMABLE"}, "categorical": {"status": "NOT_ESTIMABLE"}}
    ae, be = a.get("experiments", []), b.get("experiments", []); matches = _greedy_match(ae, be)
    p = len(matches) / len(be) if be else (1.0 if not ae else 0.0); r = len(matches) / len(ae) if ae else (1.0 if not be else 0.0)
    f1 = 2*p*r/(p+r) if p+r else 0.0
    ac, bc = a.get("claims", []), b.get("claims", [])
    # Claims match on experiment binding + structured arguments, not prose alone.
    cm = _greedy_match(ac, bc, .55)
    cp = len(cm)/len(bc) if bc else (1.0 if not ac else 0.0); cr = len(cm)/len(ac) if ac else (1.0 if not bc else 0.0)
    labels_a, labels_b = [], []
    for i, j, _ in cm:
        labels_a.append(str(ac[i].get("support_status"))); labels_b.append(str(bc[j].get("support_status")))
    return {"status": "MEASURED_HUMAN", "sample_size": 2,
            "experiment": {"matched": len(matches), "a_only": len(ae)-len(matches), "b_only": len(be)-len(matches), "precision_like": p, "recall_like": r, "f1": f1, "mean_overlap": sum(x[2] for x in matches)/len(matches) if matches else None},
            "claim": {"matched": len(cm), "a_only": len(ac)-len(cm), "b_only": len(bc)-len(cm), "f1": 2*cp*cr/(cp+cr) if cp+cr else 0.0},
            "categorical": categorical_agreement(labels_a, labels_b)}
