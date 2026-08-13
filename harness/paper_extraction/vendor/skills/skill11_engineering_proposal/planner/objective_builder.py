def build(candidate, clusters, user_target=None, target_system="Escherichia coli K-12"):
    cluster = next((x for x in clusters if x["objective_cluster"] == candidate["objective_cluster"]), {})
    literature_objective = cluster.get("representative_objective")
    if literature_objective and literature_objective != "unknown":
        phenotype, source = literature_objective, "reported_in_literature"
    elif user_target:
        # No paper-reported objective survived extraction/clustering; fall back to
        # the user's own request (Skill01 research_intent) so the UI never shows a
        # bare "unknown" when the user's goal is in fact known. This is explicitly
        # tagged as user-specified, not a literature fact, to preserve the
        # fact/proposal separation the framework requires.
        phenotype, source = user_target, "user_specified_not_literature_verified"
    else:
        phenotype, source = "unknown", "unknown"
    return {"target_phenotype": phenotype, "target_phenotype_source": source,
            "organism": "Escherichia coli", "strain": "K-12",
            "statement": f"{phenotype} in {target_system}"}
