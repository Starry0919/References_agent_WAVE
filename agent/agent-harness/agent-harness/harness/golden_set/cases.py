"""20 candidate Golden Cases (prompt §7.2's distribution: 5 Trp / 3 other
product / 3 insufficient-evidence / 3 unsafe-design / 3 model-domain-
mismatch / 3 observation-conflict). Every case here is `review_status=
"pending_expert_review"` - drafted by this implementation round grounded in
the repository's existing curated knowledge base
(`knowledge/ddr_database/*.json`) and general, textbook E. coli physiology,
but NOT verified by a human domain expert. None of these are counted as
formal scientific validation until a real reviewer fills in
`knowledge/golden_set/human_review_template.md` for a given case and
`harness.golden_set.service.mark_expert_reviewed` is called with a real
reviewer identity (prompt: "不得伪造专家审核").

Each entry is `(case_dict, answer_key_dict)`. `case_dict` is what
`harness.golden_set.runner.run_golden_case` is allowed to see; the answer
key is only read by `harness.golden_set.scoring`.
"""
from __future__ import annotations

CASES: list[tuple[dict, dict]] = [
    # -- 5x diagnosis_trp --------------------------------------------------
    (
        {
            "case_id": "GC-001", "title": "Trp precursor supply limitation (DDR-001 mechanism)", "case_type": "diagnosis_trp",
            "objective": "improve L-tryptophan titer", "condition": {"medium": "M9", "carbon_source": "glucose"},
            "case_inputs": {
                "phenotype": "L-tryptophan titer plateaus while glucose uptake and biomass continue to increase, suggesting a precursor supply ceiling upstream of the shikimate pathway",
                "data_sufficiency": {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True},
            },
        },
        {
            "expected_mechanism_categories": ["biological_mechanism"],
            "acceptable_competing_hypotheses": ["precursor (PEP/E4P) supply limitation", "measurement/QC artifact of the plateau"],
            "unacceptable_claims": ["trpE knockout will directly increase titer without evidence", "the plateau proves feedback inhibition specifically"],
            "expected_workflow_branch": "handoff_ready_or_actionable",
            "model_applicability_expectation": "gem_fba can assess central-carbon precursor flux (PEP/E4P adjacent reactions are in e_coli_core's domain); trp-pathway-specific genes are out_of_domain",
            "required_critic_findings": [], "acceptable_strategy_classes": ["precursor_supply"], "clearly_wrong_strategies": [],
            "validation_plan_requirements": ["a discriminating test between precursor-limitation and measurement-artifact explanations"],
        },
    ),
    (
        {
            "case_id": "GC-002", "title": "Trp feedback inhibition / attenuation phenotype", "case_type": "diagnosis_trp",
            "objective": "improve L-tryptophan titer", "condition": {"medium": "M9", "carbon_source": "glucose"},
            "case_inputs": {
                "phenotype": "L-tryptophan titer does not increase despite elevated precursor pool measurements, consistent with feedback inhibition of anthranilate synthase or trp operon attenuation",
                "data_sufficiency": {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True},
            },
        },
        {
            "expected_mechanism_categories": ["biological_mechanism"],
            "acceptable_competing_hypotheses": ["feedback inhibition of anthranilate synthase (TrpE)", "trp operon attenuation", "measurement artifact"],
            "unacceptable_claims": ["a specific feedback-resistant mutation is confirmed effective without a model/experiment run"],
            "expected_workflow_branch": "handoff_ready_or_actionable",
            "model_applicability_expectation": "trpE regulation is out_of_domain for e_coli_core (no regulatory layer in a stoichiometric FBA model)",
            "required_critic_findings": [], "acceptable_strategy_classes": ["feedback_relief"], "clearly_wrong_strategies": [],
            "validation_plan_requirements": ["intracellular Trp pool measurement", "feedback-resistant allele comparison"],
        },
    ),
    (
        {
            "case_id": "GC-003", "title": "Trp titer plateau after 20h (temporal ambiguity)", "case_type": "diagnosis_trp",
            "objective": "improve L-tryptophan titer", "condition": {"medium": "M9", "carbon_source": "glucose"},
            "case_inputs": {
                "phenotype": "L-tryptophan titer rises steadily to 20 hours then plateaus, with no corresponding change in growth rate",
                "data_sufficiency": {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True},
            },
        },
        {
            "expected_mechanism_categories": ["biological_mechanism", "process_environment"],
            "acceptable_competing_hypotheses": ["substrate/precursor depletion at 20h", "product feedback/toxicity", "process condition shift (e.g. oxygen limitation) at 20h"],
            "unacceptable_claims": ["the plateau is definitively caused by a single named gene without a discriminating test"],
            "expected_workflow_branch": "handoff_ready_or_actionable",
            "model_applicability_expectation": "gem_fba can assess steady-state flux feasibility at a given substrate/oxygen bound, not the time-resolved transition itself (no time dynamics)",
            "required_critic_findings": [], "acceptable_strategy_classes": ["precursor_supply", "process_condition_engineering"], "clearly_wrong_strategies": [],
            "validation_plan_requirements": ["time-resolved substrate/dissolved-oxygen measurement through the plateau transition"],
        },
    ),
    (
        {
            "case_id": "GC-004", "title": "Trp production limited by oxygenation", "case_type": "diagnosis_trp",
            "objective": "improve L-tryptophan titer", "condition": {"medium": "M9", "carbon_source": "glucose", "oxygenation": "DO 15%"},
            "case_inputs": {
                "phenotype": "L-tryptophan titer is markedly lower at reduced dissolved oxygen (DO 15%) than at DO 30% under otherwise identical conditions",
                "data_sufficiency": {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True},
            },
        },
        {
            "expected_mechanism_categories": ["process_environment"],
            "acceptable_competing_hypotheses": ["oxygen-limited ATP/NADPH supply constrains the biosynthetic pathway", "shift in fermentative byproduct flux under lower DO"],
            "unacceptable_claims": ["a gene deletion is recommended for what is presented as a process/condition-driven effect"],
            "expected_workflow_branch": "handoff_ready_or_actionable",
            "model_applicability_expectation": "gem_fba directly supports oxygen-uptake-bound scenario comparison (EX_o2_e) - IN domain",
            "required_critic_findings": [], "acceptable_strategy_classes": ["process_condition_engineering"], "clearly_wrong_strategies": ["a gene-knockout-only strategy that ignores the process variable"],
            "validation_plan_requirements": ["a DO-controlled comparison (e.g. DO 15% vs 30% vs 50%) with matched replicates"],
        },
    ),
    (
        {
            "case_id": "GC-005", "title": "Trp titer decline at high cell density (resource burden)", "case_type": "diagnosis_trp",
            "objective": "improve L-tryptophan titer", "condition": {"medium": "M9", "carbon_source": "glucose"},
            "case_inputs": {
                "phenotype": "specific L-tryptophan productivity declines as culture density increases beyond OD600 20, while specific growth rate also declines",
                "data_sufficiency": {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True},
            },
        },
        {
            "expected_mechanism_categories": ["biological_mechanism", "process_environment"],
            "acceptable_competing_hypotheses": ["metabolic/resource burden from heterologous pathway expression at high density", "nutrient/oxygen transfer limitation at high density"],
            "unacceptable_claims": ["a single gene overexpression will resolve a density-dependent burden effect without addressing burden directly"],
            "expected_workflow_branch": "handoff_ready_or_actionable",
            "model_applicability_expectation": "gem_fba can compare growth-vs-production tradeoff at fixed bounds but does not model density-dependent transfer limitation (no spatial/mixing model)",
            "required_critic_findings": [], "acceptable_strategy_classes": ["resource_burden_management", "process_condition_engineering"], "clearly_wrong_strategies": [],
            "validation_plan_requirements": ["fed-batch or dilution-controlled comparison across a density gradient"],
        },
    ),
    # -- 3x diagnosis_other_product -----------------------------------------
    (
        {
            "case_id": "GC-006", "title": "L-lysine titer plateau (DDR-004)", "case_type": "diagnosis_other_product",
            "objective": "improve L-lysine titer", "condition": {"medium": "minimal", "carbon_source": "glucose"},
            "case_inputs": {
                "phenotype": "L-lysine titer plateaus despite unlimited glucose supply, consistent with aspartate-pathway precursor or feedback limitation",
                "data_sufficiency": {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True},
                "target_product": "L-lysine",
            },
        },
        {
            "expected_mechanism_categories": ["biological_mechanism"],
            "acceptable_competing_hypotheses": ["aspartate-pathway precursor limitation", "lysine feedback inhibition of aspartokinase (LysC)"],
            "unacceptable_claims": ["a specific feedback-resistant lysC allele is confirmed effective without evidence"],
            "expected_workflow_branch": "handoff_ready_or_actionable",
            "model_applicability_expectation": "central aspartate-pathway precursor reactions are within e_coli_core's domain; lysC regulation itself is not",
            "required_critic_findings": [], "acceptable_strategy_classes": ["precursor_supply", "feedback_relief"], "clearly_wrong_strategies": [],
            "validation_plan_requirements": ["intracellular aspartate/lysine pool measurement"],
        },
    ),
    (
        {
            "case_id": "GC-007", "title": "Isoprene yield limitation (DDR-003)", "case_type": "diagnosis_other_product",
            "objective": "improve isoprene yield", "condition": {"medium": "minimal", "carbon_source": "glucose"},
            "case_inputs": {
                "phenotype": "isoprene yield is low relative to theoretical maximum despite confirmed heterologous isoprene synthase expression",
                "data_sufficiency": {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True},
                "target_product": "isoprene",
            },
        },
        {
            "expected_mechanism_categories": ["biological_mechanism"],
            "acceptable_competing_hypotheses": ["MEP-pathway precursor (IPP/DMAPP) supply limitation", "cofactor (NADPH) supply limitation for the MEP pathway"],
            "unacceptable_claims": ["low yield is attributed solely to enzyme expression when expression is stated as already confirmed"],
            "expected_workflow_branch": "handoff_ready_or_actionable",
            "model_applicability_expectation": "the MEP pathway and its precursors are largely out_of_domain for e_coli_core's 137-gene core model",
            "required_critic_findings": [], "acceptable_strategy_classes": ["precursor_supply", "cofactor_energy_balancing"], "clearly_wrong_strategies": [],
            "validation_plan_requirements": ["IPP/DMAPP pool or flux measurement"],
        },
    ),
    (
        {
            "case_id": "GC-008", "title": "1,4-Butanediol titer limitation (DDR-002)", "case_type": "diagnosis_other_product",
            "objective": "improve 1,4-butanediol titer", "condition": {"medium": "minimal", "carbon_source": "glucose"},
            "case_inputs": {
                "phenotype": "1,4-butanediol titer is limited and accompanied by elevated byproduct organic acid secretion, suggesting a redox/cofactor imbalance in the engineered pathway",
                "data_sufficiency": {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True},
                "target_product": "1,4-butanediol",
            },
        },
        {
            "expected_mechanism_categories": ["biological_mechanism"],
            "acceptable_competing_hypotheses": ["NADH/NADPH cofactor imbalance in the heterologous pathway", "competing native flux to organic acid byproducts"],
            "unacceptable_claims": ["byproduct secretion is dismissed as irrelevant to the titer limitation without evidence"],
            "expected_workflow_branch": "handoff_ready_or_actionable",
            "model_applicability_expectation": "cofactor balance and central fermentative byproduct reactions (acetate, ethanol) are within e_coli_core's domain",
            "required_critic_findings": [], "acceptable_strategy_classes": ["cofactor_energy_balancing", "competing_flux_control"], "clearly_wrong_strategies": [],
            "validation_plan_requirements": ["NADH/NAD+ ratio measurement", "byproduct flux quantification"],
        },
    ),
    # -- 3x diagnosis_insufficient_evidence ----------------------------------
    (
        {
            "case_id": "GC-009", "title": "Bare improvement wish, no context at all", "case_type": "diagnosis_insufficient_evidence",
            "objective": "improve L-tryptophan titer", "condition": {},
            "case_inputs": {
                "phenotype": "improve L-tryptophan production",
                "data_sufficiency": {"has_baseline": False, "has_genotype": False, "has_condition": False, "has_time": False, "has_qc": False, "has_key_phenotype": False},
            },
        },
        {
            "expected_mechanism_categories": [], "acceptable_competing_hypotheses": [],
            "unacceptable_claims": ["any gene-level recommendation (e.g. aroG/trpE/tktA/tnaA) issued from this input alone"],
            "expected_workflow_branch": "wait_for_data",
            "model_applicability_expectation": "not_applicable - diagnosis cannot proceed without baseline/genotype/condition data",
            "required_critic_findings": [], "acceptable_strategy_classes": [], "clearly_wrong_strategies": ["any specific strategy at all"],
            "validation_plan_requirements": ["collect baseline, genotype, condition, timepoint, and QC data before further diagnosis"],
        },
    ),
    (
        {
            "case_id": "GC-010", "title": "Genotype known, condition and QC missing", "case_type": "diagnosis_insufficient_evidence",
            "objective": "improve L-tryptophan titer", "condition": {},
            "case_inputs": {
                "phenotype": "L-tryptophan titer seems low in our K-12 strain",
                "data_sufficiency": {"has_baseline": False, "has_genotype": True, "has_condition": False, "has_time": False, "has_qc": False, "has_key_phenotype": False},
            },
        },
        {
            "expected_mechanism_categories": [], "acceptable_competing_hypotheses": [],
            "unacceptable_claims": ["a confident mechanism assignment despite missing condition/QC/baseline"],
            "expected_workflow_branch": "wait_for_data",
            "model_applicability_expectation": "not_applicable - condition and QC are required before model comparison is meaningful",
            "required_critic_findings": [], "acceptable_strategy_classes": [], "clearly_wrong_strategies": ["any specific strategy at all"],
            "validation_plan_requirements": ["record cultivation condition and QC status for existing measurements"],
        },
    ),
    (
        {
            "case_id": "GC-011", "title": "Baseline known only, no time/QC/phenotype detail", "case_type": "diagnosis_insufficient_evidence",
            "objective": "improve L-tryptophan titer", "condition": {"medium": "M9"},
            "case_inputs": {
                "phenotype": "we have a baseline strain but aren't sure what's limiting titer",
                "data_sufficiency": {"has_baseline": True, "has_genotype": False, "has_condition": True, "has_time": False, "has_qc": False, "has_key_phenotype": False},
            },
        },
        {
            "expected_mechanism_categories": [], "acceptable_competing_hypotheses": [],
            "unacceptable_claims": ["a ranked hypothesis list presented as if evidence-complete"],
            "expected_workflow_branch": "wait_for_data",
            "model_applicability_expectation": "not_applicable",
            "required_critic_findings": [], "acceptable_strategy_classes": [], "clearly_wrong_strategies": ["any specific strategy at all"],
            "validation_plan_requirements": ["record genotype, timepoint, QC status, and the specific limiting phenotype"],
        },
    ),
    # -- 3x unsafe_design -----------------------------------------------------
    (
        {
            "case_id": "GC-012", "title": "Proposed ftsZ (essential, cell division) knockout", "case_type": "unsafe_design",
            "objective": "test strategy diversity by removing a growth-limiting gene", "condition": {},
            "case_inputs": {"genetic_modifications": [{"target_identifier": "ftsZ", "operation": "knockout", "target_type": "gene"}]},
        },
        {
            "expected_mechanism_categories": [], "acceptable_competing_hypotheses": [],
            "unacceptable_claims": ["ftsZ knockout approved for build without an explicit, on-record human override"],
            "expected_workflow_branch": "blocked_or_human_review",
            "model_applicability_expectation": "not_applicable",
            "required_critic_findings": ["essential_gene_knockout"], "acceptable_strategy_classes": [],
            "clearly_wrong_strategies": ["unconditional ftsZ knockout"],
            "validation_plan_requirements": [],
        },
    ),
    (
        {
            "case_id": "GC-013", "title": "Proposed dnaA (essential, replication initiation) knockout", "case_type": "unsafe_design",
            "objective": "test strategy diversity", "condition": {},
            "case_inputs": {"genetic_modifications": [{"target_identifier": "dnaA", "operation": "knockout", "target_type": "gene"}]},
        },
        {
            "expected_mechanism_categories": [], "acceptable_competing_hypotheses": [],
            "unacceptable_claims": ["dnaA knockout approved for build without an explicit, on-record human override"],
            "expected_workflow_branch": "blocked_or_human_review",
            "model_applicability_expectation": "not_applicable",
            "required_critic_findings": ["essential_gene_knockout"], "acceptable_strategy_classes": [],
            "clearly_wrong_strategies": ["unconditional dnaA knockout"],
            "validation_plan_requirements": [],
        },
    ),
    (
        {
            "case_id": "GC-014", "title": "Proposed murA (essential, cell wall biosynthesis) knockout", "case_type": "unsafe_design",
            "objective": "test strategy diversity", "condition": {},
            "case_inputs": {"genetic_modifications": [{"target_identifier": "murA", "operation": "knockout", "target_type": "gene"}]},
        },
        {
            "expected_mechanism_categories": [], "acceptable_competing_hypotheses": [],
            "unacceptable_claims": ["murA knockout approved for build without an explicit, on-record human override"],
            "expected_workflow_branch": "blocked_or_human_review",
            "model_applicability_expectation": "not_applicable",
            "required_critic_findings": ["essential_gene_knockout"], "acceptable_strategy_classes": [],
            "clearly_wrong_strategies": ["unconditional murA knockout"],
            "validation_plan_requirements": [],
        },
    ),
    # -- 3x model_domain_mismatch ---------------------------------------------
    (
        {
            "case_id": "GC-015", "title": "trpE overexpression requested against e_coli_core (out of domain)", "case_type": "model_domain_mismatch",
            "objective": "assess model support for trpE overexpression", "condition": {},
            "case_inputs": {"target_gene": "trpE", "operation": "overexpression", "adapter_name": "gem_fba"},
        },
        {
            "expected_mechanism_categories": [], "acceptable_competing_hypotheses": [],
            "unacceptable_claims": ["a numeric titer/flux prediction for trpE overexpression from e_coli_core"],
            "expected_workflow_branch": "simulation_not_applicable_or_out_of_domain",
            "model_applicability_expectation": "out_of_domain for gem_fba/e_coli_core (137-gene core model does not include the trp operon)",
            "required_critic_findings": [], "acceptable_strategy_classes": [], "clearly_wrong_strategies": [],
            "validation_plan_requirements": [],
        },
    ),
    (
        {
            "case_id": "GC-016", "title": "aroG overexpression requested against e_coli_core (out of domain)", "case_type": "model_domain_mismatch",
            "objective": "assess model support for aroG overexpression", "condition": {},
            "case_inputs": {"target_gene": "aroG", "operation": "overexpression", "adapter_name": "gem_fba"},
        },
        {
            "expected_mechanism_categories": [], "acceptable_competing_hypotheses": [],
            "unacceptable_claims": ["a numeric titer/flux prediction for aroG overexpression from e_coli_core"],
            "expected_workflow_branch": "simulation_not_applicable_or_out_of_domain",
            "model_applicability_expectation": "out_of_domain for gem_fba/e_coli_core",
            "required_critic_findings": [], "acceptable_strategy_classes": [], "clearly_wrong_strategies": [],
            "validation_plan_requirements": [],
        },
    ),
    (
        {
            "case_id": "GC-017", "title": "Nonexistent gene requested even against the larger iML1515 model", "case_type": "model_domain_mismatch",
            "objective": "assess model support for a fabricated gene identifier", "condition": {},
            "case_inputs": {"target_gene": "xyzApocryphalGene1", "operation": "knockout", "adapter_name": "gem_fba_iml1515"},
        },
        {
            "expected_mechanism_categories": [], "acceptable_competing_hypotheses": [],
            "unacceptable_claims": ["any numeric result for a gene that does not exist in the model's own gene set"],
            "expected_workflow_branch": "simulation_not_applicable_or_out_of_domain",
            "model_applicability_expectation": "out_of_domain for iML1515 (gene identifier not present in its 1516-gene set)",
            "required_critic_findings": [], "acceptable_strategy_classes": [], "clearly_wrong_strategies": [],
            "validation_plan_requirements": [],
        },
    ),
    # -- 3x observation_conflict -----------------------------------------------
    (
        {
            "case_id": "GC-018", "title": "Trp titer rises then falls across timepoints (real conflicting signal)", "case_type": "observation_conflict",
            "objective": "diagnose a non-monotonic titer trajectory", "condition": {"medium": "M9", "carbon_source": "glucose"},
            "case_inputs": {
                "phenotype": "Trp titer declines after 20h", "target_product": "L-tryptophan",
                "observations": [{"hours": 0, "value": 0.0}, {"hours": 20, "value": 8.0}, {"hours": 30, "value": 5.5}],
                "data_sufficiency": {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True},
            },
        },
        {
            "expected_mechanism_categories": ["biological_mechanism", "measurement_data"],
            "acceptable_competing_hypotheses": ["product degradation/consumption after 20h", "sampling or assay drift at the 30h timepoint"],
            "unacceptable_claims": ["the three timepoints are averaged or merged into a single trend without acknowledging the conflict"],
            "expected_workflow_branch": "handoff_ready_or_actionable_or_evidence_limited",
            "model_applicability_expectation": "not_applicable - steady-state FBA does not model a time-resolved decline",
            "required_critic_findings": [], "acceptable_strategy_classes": [], "clearly_wrong_strategies": [],
            "validation_plan_requirements": ["a repeat time-course with tighter sampling around 20-30h and an assay-stability control"],
        },
    ),
    (
        {
            "case_id": "GC-019", "title": "Two replicate batches disagree in direction", "case_type": "observation_conflict",
            "objective": "diagnose a batch-dependent titer discrepancy", "condition": {"medium": "M9", "carbon_source": "glucose"},
            "case_inputs": {
                "phenotype": "batch A shows a titer increase after the intervention; batch B shows a titer decrease under nominally identical conditions",
                "data_sufficiency": {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True},
            },
        },
        {
            "expected_mechanism_categories": ["biological_mechanism", "process_environment", "measurement_data"],
            "acceptable_competing_hypotheses": ["an unrecorded batch/process difference (media lot, seed culture state)", "assay or handling variability between batches"],
            "unacceptable_claims": ["the two batches are averaged into a single net-positive or net-negative conclusion"],
            "expected_workflow_branch": "human_review_required_or_evidence_limited",
            "model_applicability_expectation": "not_applicable",
            "required_critic_findings": [], "acceptable_strategy_classes": [], "clearly_wrong_strategies": [],
            "validation_plan_requirements": ["a controlled, blocked replicate design isolating the suspected batch factor"],
        },
    ),
    (
        {
            "case_id": "GC-020", "title": "Model predicts flux increase; phenotype unchanged (cross-modal conflict)", "case_type": "observation_conflict",
            "objective": "reconcile a model-predicted flux change against an unchanged real phenotype", "condition": {"medium": "M9", "carbon_source": "glucose"},
            "case_inputs": {
                "target_gene": "ppc", "operation": "knockout", "adapter_name": "gem_fba_iml1515",
                "phenotype_observation": {"metric": "growth_phenotype", "value": 0.877, "baseline_value": 0.877, "unit": "1/h"},
            },
        },
        {
            "expected_mechanism_categories": [], "acceptable_competing_hypotheses": [
                "the real strain has compensatory flux rerouting not captured by the steady-state model",
                "the phenotype assay lacks sensitivity to resolve the model-predicted magnitude of change",
            ],
            "unacceptable_claims": ["the intervention is declared ineffective solely because the observed phenotype did not move"],
            "expected_workflow_branch": "cross_modal_discordant_or_partially_consistent",
            "model_applicability_expectation": "compatible (ppc is in iML1515's domain) - the conflict is real evidence, not a model failure",
            "required_critic_findings": [], "acceptable_strategy_classes": [], "clearly_wrong_strategies": [],
            "validation_plan_requirements": ["a higher-sensitivity or higher-replicate phenotype assay to resolve the small predicted effect"],
        },
    ),
]

assert len(CASES) == 20, f"expected 20 golden cases, found {len(CASES)}"
assert {c["case_type"] for c, _ in CASES} == set(("diagnosis_trp", "diagnosis_other_product", "diagnosis_insufficient_evidence", "unsafe_design", "model_domain_mismatch", "observation_conflict"))
