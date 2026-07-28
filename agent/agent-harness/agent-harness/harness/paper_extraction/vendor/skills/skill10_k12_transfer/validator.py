def validate(output, normalized):
    candidates = output.get("candidate_design_space", [])
    analyses = output.get("k12_analysis", [])
    facts_by_id = {x["paper_id"]: x["literature_facts"] for x in normalized}
    checks = [
        {"name": "candidate_count_matches_inputs", "passed": len(candidates) == len(normalized)},
        {"name": "facts_and_analysis_separated", "passed": all("literature_facts" not in x for x in analyses)},
        {"name": "compatibility_has_basis", "passed": all(x.get("basis") and "evidence_grade" in x["basis"] for x in analyses)},
        {"name": "no_ranking_or_best_strategy", "passed": all("rank" not in x and "best" not in x for x in candidates)},
        {"name": "candidate_only_status", "passed": all(x.get("decision_status") == "candidate_only_not_ranked" for x in candidates)},
        {"name": "unknown_strain_stays_unknown", "passed": all(
            facts_by_id[x["paper_id"]]["biological_system"]["organism_strain"] is not None or x["compatibility"] == "unknown"
            for x in analyses)},
    ]
    return checks
