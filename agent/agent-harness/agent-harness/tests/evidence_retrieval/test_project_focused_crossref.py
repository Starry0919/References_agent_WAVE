from harness.evidence_retrieval.crossref_adapter import CrossrefEvidenceAdapter


def _item(title, year=2025, journal="Metabolic Engineering", article_type="journal-article"):
    return {
        "title": [title],
        "abstract": (
            "Escherichia coli K-12 MG1655 metabolic engineering knockout "
            "experimental validation mechanism pathway reproducible strain design "
            "multi-omics iterative DBTL"
        ),
        "container-title": [journal],
        "published-online": {"date-parts": [[year, 1, 1]]},
        "type": article_type,
    }


def test_project_score_exposes_weighted_components_and_if_provenance():
    policy = CrossrefEvidenceAdapter._policy({
        "organism_required": ["e. coli k-12", "mg1655"],
    })
    score = CrossrefEvidenceAdapter._score(
        _item("Engineering tryptophan production"),
        "improve tryptophan production in E. coli",
        policy,
        {"Metabolic Engineering": 12.9},
    )
    assert score["hard_filter_passed"] is True
    assert score["organism_match"] == "required"
    assert score["impact_factor"] == 12.9
    assert score["impact_factor_status"] == "provided_snapshot"
    assert set(score["components"]) == {
        "relevance", "organism", "journal_impact", "recency", "design_quality",
    }


def test_non_target_or_review_article_is_rejected():
    policy = CrossrefEvidenceAdapter._policy({})
    item = _item("A broad review of biotechnology", article_type="journal-article")
    item["abstract"] = "A review of mammalian cell biotechnology."
    assert CrossrefEvidenceAdapter._score(item, "tryptophan", policy, {})["hard_filter_passed"] is False
