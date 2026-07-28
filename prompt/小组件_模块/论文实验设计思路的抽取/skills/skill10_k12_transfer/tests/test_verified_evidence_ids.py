from comparison.normalizer import normalize
from helpers import design, quality


def test_skill08_verified_ids_replace_skill07_provisional_ids():
    source = design()
    source["fields"]["objective"]["evidence_ids"] = ["candidate:introduction_p001"]
    evidence = {
        "evidence_linked_design": {
            "paper_id": "paper-1",
            "fields": {
                "objective": {
                    "value": "increase production",
                    "status": "reported",
                    "evidence_ids": ["ev_00001"],
                }
            },
        },
        "evidence_map": {"ev_00001": {"evidence_id": "ev_00001"}},
    }
    result = normalize(source, evidence, quality(), 0)
    assert result["evidence_ids"] == ["ev_00001"]
