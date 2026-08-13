from .evidence_validator import match_score


class EvidenceRetriever:
    MAX_ATTEMPTS = 3

    def __init__(self, index):
        self.index = index

    def retrieve(self, value, provisional_ids):
        audit, found = [], []
        for evidence_id in provisional_ids:
            unit_id = evidence_id.removeprefix("candidate:")
            unit = self.index.get(unit_id)
            audit.append({"attempt": 1, "mode": "provisional_id", "unit_id": unit_id, "found": bool(unit)})
            if unit:
                found.append(unit)
        if found:
            return _unique(found), audit
        ranked = sorted(
            ((match_score(value, unit["text"]), unit) for unit in self.index.text_units()),
            key=lambda pair: pair[0], reverse=True
        )
        text_matches = [unit for score, unit in ranked if score > 0]
        audit.append({"attempt": 2, "mode": "full_text", "matches": len(text_matches)})
        if text_matches:
            return _unique(text_matches[:5]), audit
        ranked_visual = sorted(
            ((match_score(value, unit["text"]), unit) for unit in self.index.visual_units()),
            key=lambda pair: pair[0], reverse=True
        )
        visual_matches = [unit for score, unit in ranked_visual if score > 0]
        audit.append({"attempt": 3, "mode": "figure_table_supplement", "matches": len(visual_matches)})
        return _unique(visual_matches[:5]), audit


def _unique(units):
    seen, result = set(), []
    for unit in units:
        if unit["unit_id"] not in seen:
            seen.add(unit["unit_id"])
            result.append(unit)
    return result
