"""Module 1 - Literature Reverse Engineering: expert decision logic, not summaries.

For V0.1 this is a mock Design Decision Record (DDR) store keyed by
product, standing in for a future literature knowledge base built from
parsed papers. The interface - `get_records(product) -> list[DDR]` - is
what a future retrieval backend (or PDF-extraction pipeline) must honor;
downstream modules only ever see DDR dicts, never raw literature.

Every record encodes the full reasoning chain the revision spec requires
(observation -> hypothesis -> evidence -> engineering action -> expected
effect -> validation), not just a target gene and an action.

IMPORTANT: none of these records are backed by a verified literature
lookup - V0.1 has no citation-verification pipeline. `evidence_type` is
therefore always "mock evidence" and every `evidence` string is explicitly
labelled "mock knowledge base, not verified", per the revision spec's
"never fabricate real literature" rule. The underlying biology described
(trp operon regulation, TrpE feedback inhibition, tryptophanase activity)
reflects textbook-level knowledge, but no specific paper is cited or
claimed to have been checked.
"""
from __future__ import annotations

from typing import Any

_MOCK_DISCLAIMER = "mock knowledge base, not verified"

_DDR_MOCK_DB: dict[str, list[dict[str, Any]]] = {
    "tryptophan": [
        {
            "design_action": "point mutation",
            "target": "trpE",
            "observation": "Anthranilate synthase (TrpE) activity drops sharply as intracellular tryptophan accumulates, capping flux at the pathway's first committed step.",
            "hypothesis": "The committed step (chorismate -> anthranilate) is allosterically inhibited by the pathway's own end product, so flux stays clamped even when precursor supply is sufficient.",
            "evidence": f"{_MOCK_DISCLAIMER}: classical description of TrpE end-product feedback inhibition in the E. coli trp operon.",
            "evidence_type": "mock evidence",
            "reason_type": "mechanistic reasoning",
            "implementation": "introduce a feedback-resistant trpE allele (e.g. trpE_fbr) via point mutation at the tryptophan-binding regulatory site",
            "expected_effect": "anthranilate synthase remains active despite high intracellular tryptophan, sustaining flux into the pathway",
            "validation": "measure anthranilate synthase activity in vitro under high-tryptophan conditions; compare strain titer/flux to a wild-type control",
            "general_rule": "when end-product feedback inhibits the first committed enzyme, a desensitizing mutation is the most direct lever on pathway flux",
        },
        {
            "design_action": "knockout",
            "target": "trpR",
            "observation": "trp operon transcription drops once intracellular tryptophan rises, independent of TrpE's own enzymatic activity.",
            "hypothesis": "TrpR (aporepressor) binds tryptophan and represses trp operon transcription - a second, transcriptional layer of feedback on top of TrpE's allosteric inhibition.",
            "evidence": f"{_MOCK_DISCLAIMER}: classical description of TrpR-mediated repression of the trp operon.",
            "evidence_type": "mock evidence",
            "reason_type": "mechanistic reasoning",
            "implementation": "delete the trpR ORF",
            "expected_effect": "derepression of trp operon transcription, raising expression of all downstream biosynthetic enzymes",
            "validation": "qRT-PCR or a reporter-fusion assay of trp operon transcript levels before/after deletion",
            "general_rule": "removing a pathway's transcriptional repressor complements relieving allosteric feedback; apply it once the committed-step bottleneck is addressed",
        },
        {
            "design_action": "knockout",
            "target": "tnaA",
            "observation": "Accumulated tryptophan is degraded intracellularly, reducing net titer even when biosynthesis is upregulated.",
            "hypothesis": "Tryptophanase (TnaA) hydrolyzes tryptophan into indole, pyruvate, and ammonia, competing directly with product accumulation.",
            "evidence": f"{_MOCK_DISCLAIMER}: classical description of tryptophanase catabolic activity in E. coli.",
            "evidence_type": "mock evidence",
            "reason_type": "literature analogy",
            "implementation": "delete the tnaA ORF",
            "expected_effect": "reduced catabolic loss of the accumulated product",
            "validation": "compare tryptophan titer and indole byproduct levels between wild-type and tnaA-deletion strains",
            "general_rule": "remove non-essential competing catabolic enzymes of the target product once biosynthetic flux has been increased",
        },
        {
            "design_action": "overexpression",
            "target": "serA/tktA",
            "observation": "Relieving feedback and derepressing the operon alone may not raise titer if precursor supply is limiting.",
            "hypothesis": "Erythrose-4-phosphate and PEP, the shikimate-pathway precursors, are shared with central metabolism and can become limiting once downstream flux increases.",
            "evidence": f"{_MOCK_DISCLAIMER}: general precursor-engineering rationale for aromatic amino acid overproduction.",
            "evidence_type": "mock evidence",
            "reason_type": "screening-derived",
            "implementation": "plasmid-borne overexpression of serA/tktA under a strong constitutive promoter",
            "expected_effect": "increased precursor pool available for the shikimate/aromatic amino acid pathway",
            "validation": "measure intracellular E4P/PEP pools and pathway flux (e.g. 13C-MFA or titer) with and without overexpression",
            "general_rule": "precursor-supply interventions are a secondary optimization; they complement but don't substitute for relieving end-product feedback",
        },
    ],
}

_GENERIC_RECORD: dict[str, Any] = {
    "design_action": "unknown",
    "target": "unknown",
    "observation": "no literature precedent available in the V0.1 mock store",
    "hypothesis": "",
    "evidence": f"none available ({_MOCK_DISCLAIMER})",
    "evidence_type": "mock evidence",
    "reason_type": "uncertain",
    "implementation": "",
    "expected_effect": "",
    "validation": "",
    "general_rule": "",
}


def get_records(product: str) -> list[dict[str, Any]]:
    """Return the mock DDRs for a product.

    Unknown products get a single placeholder record flagged
    `reason_type: uncertain` rather than an empty list, so every downstream
    module still has something to reason over.
    """
    records = _DDR_MOCK_DB.get(product.lower())
    if records:
        return [dict(record) for record in records]
    return [dict(_GENERIC_RECORD, target=product)]
