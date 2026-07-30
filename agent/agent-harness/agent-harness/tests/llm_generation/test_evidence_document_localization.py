from harness.api import generation


def test_localize_evidence_document_unwraps_skill07_field_records(monkeypatch):
    monkeypatch.setattr(generation, "get_locale", lambda: "zh-CN")

    seen: list[str] = []

    def fake_translate_batch(texts: list[str], locale: str, *, cache_only: bool = False) -> list[str]:
        assert locale == "zh-CN"
        assert cache_only is True
        assert all(isinstance(text, str) for text in texts)
        seen.extend(texts)
        return [f"translated:{text}" if text else "" for text in texts]

    monkeypatch.setattr(generation, "translate_batch", fake_translate_batch)
    design = {
        "problem_statement": {
            "value": "Engineer E. coli for tryptophan production",
            "status": "reported",
            "confidence": 0.9,
        },
        "mechanistic_explanation": "",
        "hypothesis": {"value": "Reduce acetate overflow", "status": "inferred"},
        "expected_effect": ["higher titer", "better yield"],
        "actions": [
            {
                "rationale": {"value": "Preserve acetyl-CoA", "status": "reported"},
                "expected_effect": "Lower acetate",
            },
        ],
    }

    title, abstract, localized = generation._localize_evidence_document(
        "A paper", "An abstract", design,
    )

    assert title == "translated:A paper"
    assert abstract == "translated:An abstract"
    assert localized is not None
    assert localized["problem_statement"] == "translated:Engineer E. coli for tryptophan production"
    assert localized["hypothesis"] == "translated:Reduce acetate overflow"
    assert localized["expected_effect"] == "translated:higher titer; better yield"
    assert localized["actions"][0]["rationale"] == "translated:Preserve acetyl-CoA"
    assert localized["actions"][0]["expected_effect"] == "translated:Lower acetate"
    assert "Engineer E. coli for tryptophan production" in seen
