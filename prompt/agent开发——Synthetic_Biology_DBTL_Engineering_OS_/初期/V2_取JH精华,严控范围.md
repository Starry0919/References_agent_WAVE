# Synthetic Biology Agent V2 Upgrade Specification


# 1. Objective


Upgrade Synthetic Biology Agent V1 into V2.


V2 should behave like a professional metabolic engineering assistant.

The Agent should not only generate engineering suggestions.

It should:

- define the biological problem
- analyze pathways
- identify bottlenecks
- retrieve evidence
- propose engineering actions
- evaluate feasibility
- design validation experiments


Core principle:


No evidence-free engineering recommendation.



# 2. Preserve V1 Architecture


Do NOT remove:


knowledge/


├── papers/

├── ddr_database/

├── engineering_actions/

└── biological_rules/


Keep:


- DDR retrieval
- Action Library
- Evidence Quality
- Validation Module



V2 extends V1.



# 3. Add Strict Phase Workflow


Implement a SynBio Phase Controller.


Workflow:


## Phase 0
Engineering Problem Definition


Extract:


- host chassis
- substrate
- target product
- optimization objective
- constraints



Example:


Input:

Improve L-tryptophan production in E.coli K-12


Output:


```json
{
"host":"E.coli K-12",
"substrate":"glucose",
"product":"L-tryptophan",
"goal":"increase production"
}
````

---

## Phase 1

Pathway Analysis

Analyze:

* native pathway
* precursor molecules
* pathway enzymes
* competing pathways
* regulation

Preferred tools:

KEGG

EcoCyc

---

## Phase 2

Bottleneck Diagnosis

Classify limitation:

* precursor limitation
* enzyme capacity limitation
* regulatory limitation
* cofactor limitation
* transport limitation
* toxicity
* metabolic burden

Output:

Observation

↓

Hypothesis

↓

Evidence

---

## Phase 3

Engineering Design

Generate:

* knockout
* overexpression
* promoter engineering
* heterologous pathway introduction
* transport engineering
* flux redistribution

Every action must connect to:

Engineering Action Library.

---

## Phase 4

Evaluator-Optimizer

Before final output:

All designs must be reviewed.

Evaluator checks:

## Evidence check

Does this modification have:

* paper evidence?
* database evidence?
* general engineering rule?

## Essentiality check

Check:

Is this gene essential?

Tool:

essential gene database / model

## Biological conflict check

Examples:

Deleting a pathway may:

* damage growth
* reduce precursor supply
* create imbalance

## Feasibility score

Output:

```json
{
"action":"",
"evidence_score":"",
"risk_score":"",
"priority":""
}
```

---

## Phase 5

Validation Design

Generate:

### Genotype validation

* PCR
* sequencing

### Mechanistic validation

* metabolite measurement
* flux analysis

### Phenotype validation

* titer
* yield
* productivity

### Trade-off validation

* growth
* substrate consumption
* byproducts

---

## Phase 6

Final Report

Report sections:

1.

Engineering Objective

2.

Pathway Analysis

3.

Bottleneck Diagnosis

4.

Evidence-supported Engineering Strategy

5.

Evaluator Review

6.

Validation Plan

7.

Limitations

# 4. Evidence Rule Upgrade

Replace simple confidence with evidence grading.

Every engineering action requires:

```json
{
"evidence_type":"",

"evidence_grade":"",

"reference":"",

"confidence":""
}
```

Allowed evidence types:

## Hard Evidence

Meaning:

Direct experimental evidence.

Example:

Published gene modification increasing product.

## Soft Evidence

Meaning:

Model prediction or database-supported reasoning.

Example:

FBA predicted knockout.

## Engineering Hypothesis

Meaning:

Reasonable biological inference but not experimentally confirmed.

The Agent MUST clearly distinguish these.

Never fabricate:

* DOI
* papers
* authors
* experimental results

If unknown:

Return:

```json
{
"evidence_grade":"unknown",
"reference":null
}
```

# 5. Biological Tool Ecosystem

Add tool interfaces.

Priority:

## Level 1

Pathway databases

### KEGG

Functions:

* pathway retrieval
* gene retrieval

### UniProt

Functions:

* protein annotation
* enzyme information

---

## Level 2

Genome analysis

Essential gene checking.

Purpose:

Avoid recommending deletion of essential genes.

---

## Level 3

Metabolic Modeling

Prepare interfaces:

COBRApy

FBA

pFBA

Not required to fully implement simulation yet.

Provide modular interface.

# 6. Evaluator-Optimizer Architecture

Add:

```
Designer Agent

↓

Evaluator Agent

↓

Optimization Agent

↓

Final Design
```

Designer:

generates candidate engineering strategies.

Evaluator:

criticizes.

Optimizer:

revises.

Example:

Candidate:

delete gene X

Evaluator:

gene X essential

Optimizer:

replace knockout with down-regulation.

# 7. Global Language Mode

Implement a global hyperparameter.

Configuration:

```
LANGUAGE_MODE=zh
```

or

```
LANGUAGE_MODE=en
```

Rules:

If:

LANGUAGE_MODE=zh

Then:

* system prompt Chinese
* tool descriptions Chinese
* intermediate reports Chinese
* final answer Chinese

If:

LANGUAGE_MODE=en

Then:

* all outputs English

Technical names remain unchanged:

Examples:

E.coli

trpE

KEGG

COBRApy

# 8. Language Controller

Create:

```
language/

├── zh/

│   ├── system_prompt.md

│   └── tool_prompt.md


└── en/

    ├── system_prompt.md

    └── tool_prompt.md

```

Runtime selects based on:

LANGUAGE_MODE.

# 9. Updated Architecture

```
agent-harness/


├── workflows/

│
└── synbio_v2/


    ├── phase_controller.py

    ├── problem_definition.py

    ├── pathway_analysis.py

    ├── bottleneck_analysis.py

    ├── engineering_design.py

    ├── evaluator.py

    ├── optimizer.py

    ├── validation.py

    └── report.py



├── knowledge/

│

├── papers/

├── ddr_database/

├── engineering_actions/

└── biological_rules/



├── tools/

│

├── kegg/

├── uniprot/

├── essentiality/

└── fba/

```

# 10. Testing Requirement

Test case:

"Design E.coli K-12 for improved L-tryptophan production."

Expected:

Phase 0:

identify host/product/substrate

Phase 1:

retrieve shikimate pathway

Phase 2:

identify PEP/E4P limitation

Phase 3:

retrieve:

* xfpk
* ptsG/glf
* pykF

Phase 4:

evaluate:

* evidence
* essentiality
* risk

Phase 5:

generate validation plan

Phase 6:

produce structured report.

# 11. Development Rules

1.

Do not destroy V1.

2.

Add modules incrementally.

3.

Maintain backward compatibility.

4.

Every recommendation must have traceable evidence.

5.

Every tool output must follow language mode.

6.

No biological hallucination.

# 12. Final Deliverables

Provide:

1.

Architecture diagram

2.

Modified files

3.

New modules

4.

Testing results

5.

Example output

6.

Future roadmap

End.

```