# Literature Search Quality Benchmark v3

{
  "contract_version": "literature-search-quality-benchmark/3.0",
  "request": {
    "contract_version": "literature-search-request/3.0",
    "raw_request": "Find experimental papers that increase L-tryptophan production in E. coli K-12, preferably metabolic engineering studies.",
    "species": "Escherichia coli",
    "lineage": "K-12",
    "strain_aliases": [
      "MG1655",
      "W3110",
      "BW25113"
    ],
    "excluded_hosts": [],
    "canonical_product": "L-tryptophan",
    "product_aliases": [
      "tryptophan",
      "Trp"
    ],
    "related_products": [
      "5-hydroxytryptophan",
      "serotonin",
      "indole",
      "shikimate",
      "aromatic amino acids"
    ],
    "excluded_target_products": [
      "5-hydroxytryptophan",
      "serotonin",
      "indole"
    ],
    "objective_type": "production",
    "direction": "increase",
    "metric_preferences": [
      "titer",
      "yield",
      "productivity"
    ],
    "requested_engineering_modes": [
      "METABOLIC_ENGINEERING"
    ],
    "excluded_engineering_modes": [],
    "preferred_publication_forms": [
      "ORIGINAL_RESEARCH"
    ],
    "excluded_publication_forms": [],
    "preferred_research_designs": [
      "WET_LAB_EXPERIMENTAL"
    ],
    "year_from": null,
    "year_until": null,
    "search_mode": "DIRECT_ENGINEERING",
    "desired_count": 20,
    "diversity": true,
    "fulltext_preference": true,
    "citation_modes": [
      "BACKWARD_CITATION_EXPANSION",
      "FORWARD_CITATION_EXPANSION"
    ],
    "budgets": {
      "max_queries": 16,
      "max_raw_candidates": 300,
      "max_dedup_candidates": 150,
      "max_citation_expansion": 30,
      "max_fulltext_acquisition": 10,
      "max_fulltext_parse": 10,
      "timeout_budget": 180
    }
  },
  "retrieval": {
    "queries": 8,
    "sources": 1,
    "raw_hits": 92,
    "dedup_hits": 92,
    "citation_expanded_hits": 0,
    "final_candidates": 20
  },
  "identity": {
    "duplicate_rate": 0.0,
    "merge_conflicts": 0
  },
  "classification": {
    "metadata_classified": 92,
    "fulltext_refined": 2,
    "conflicts": 0
  },
  "top_k_composition": {
    "5": {
      "supporting_engineering": 3,
      "mechanistic_or_background": 2,
      "hard_negative_rate": 0.0
    },
    "10": {
      "supporting_engineering": 4,
      "mechanistic_or_background": 3,
      "review": 2,
      "hard_negative": 1,
      "hard_negative_rate": 0.1
    },
    "20": {
      "supporting_engineering": 5,
      "mechanistic_or_background": 11,
      "review": 2,
      "hard_negative": 2,
      "hard_negative_rate": 0.1
    }
  },
  "diversity": {
    "unique_routes_top20": 5,
    "route_distribution": {
      "PRIMARY_EXPERIMENTAL_ROUTE": 6,
      "METHOD_ROUTE": 1,
      "SOFTWARE_ROUTE": 2,
      "BACKGROUND_ROUTE": 9,
      "REVIEW_SYNTHESIS_ROUTE": 2
    }
  },
  "fulltext": {
    "available_in_gold_recovery": 23,
    "verified_or_refined_top20": 2,
    "parser_success": 2
  },
  "explanation_reason_coverage": 1.0,
  "reference_recall_check": {
    "reference_ids": [
      "paper_6edc47062e4719d3",
      "paper_b9ea21673e7a2cc4",
      "paper_165bc7645631fa6b",
      "paper_15f725b9020158af",
      "paper_2aae905b63be2435",
      "paper_25fccf802fa0782d",
      "paper_db18be686c5c0f5c",
      "paper_e7c21a0773671b4b"
    ],
    "ranks": {
      "paper_6edc47062e4719d3": 8,
      "paper_b9ea21673e7a2cc4": null,
      "paper_165bc7645631fa6b": 1,
      "paper_15f725b9020158af": 7,
      "paper_2aae905b63be2435": 10,
      "paper_25fccf802fa0782d": 2,
      "paper_db18be686c5c0f5c": 14,
      "paper_e7c21a0773671b4b": 12
    },
    "rediscovered": 7
  },
  "failure_analysis": {
    "hard_negative_top20": [
      "paper_f315a5bed9777365",
      "paper_ab98b07a10eabc8c"
    ],
    "review_crowding": 2,
    "duplicate_records": 0,
    "notes": "Reference-set invariant check only; not formal precision or recall."
  }
}
