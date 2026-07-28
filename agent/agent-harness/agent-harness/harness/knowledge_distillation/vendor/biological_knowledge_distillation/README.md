# biological_knowledge_distillation

Python implementation of the **生物学知识蒸馏 / Biological Knowledge Distillation**
capability described in `../生物学知识蒸馏_SKILL.md`. This package is the sibling
of `论文实验设计思路的抽取/paper_experimental_design_extraction` and follows the
same architecture on purpose (see the SKILL.md "架构审查" section for why):

- `module.execute(request, options)` validates the request against
  `schema/input.schema.json`, runs `workflow.WorkflowEngine`, validates the
  result against `schema/output.schema.json`, and returns it.
- `workflow/` is the generic orchestrator: run-level/step-level state
  machine, artifact versioning, checkpointing, error normalization. It has
  no domain logic - it is the same design as
  `paper_experimental_design_extraction/workflow`, ported rather than
  reinvented.
- `skills/registry.py` loads the 13 internal steps from the sibling
  top-level `skills/stepNN_*` folders (mirrors
  `paper_experimental_design_extraction/skills/registry.py` +
  the outer `skills/skillNN_*` layout). **Step01-13 are internal execution
  steps, not independently callable skills** - see SKILL.md.
- `schema/knowledge_object.schema.json` and `../framework/unified-schema.json`
  define the common `KnowledgeObject` layer every knowledge asset here
  inherits, so a canonical fusion object or a paper-case link can point at
  a `concept`, an `engineering_principle`, or (via Step11) an
  `ExperimentalCase` from the paper-extraction module without a schema
  mismatch.

## Running it

```python
from biological_knowledge_distillation import execute

result = execute(request, {"state_dir": "/tmp/bkd-runtime"})
```

`request` must satisfy `schema/input.schema.json`. See `../examples/` for
three complete, actually-executed request/response pairs (English
textbook, Chinese textbook, bilingual fusion + paper-case link).

## Tests

```bash
cd tests
python -m pytest -q .
```

22 tests currently cover: task-contract defaults (never defaulting to
E. coli K-12), source validation (unresolved edition, course-material not
promoted to textbook authority), concept/mechanism extraction, the
IF/THEN/BECAUSE/ONLY IF principle structure and its
`derivation_type=model_inference` discipline, the Step09 evidence hard
gate (unsupported evidence caps confidence and blocks `reported`/
`validated` status), Step10 fusion (same-source duplicate vs cross-source
conflict), and four end-to-end scenarios (Level1-only, engineering
distillation, bilingual fusion + paper linking, and "no target organism
never blocks Level1-4").

## Phase roadmap / known limitations (read before trusting this in production)

This is a **Phase 1** implementation: a complete, working, evidence-gated
pipeline, but with deliberately narrow extraction logic so every step is
auditable rather than a black box. Concretely, not yet built:

1. **No PDF/OCR/image pipeline.** Step03 only parses Markdown-flavoured
   plain text. PDF/EPUB/DOCX ingestion, figure/table image parsing, and
   OCR-uncertainty flagging are Phase 2.
2. **Definition/mechanism extraction is a small regex library**, not an
   LLM call (matching `paper_experimental_design_extraction`'s
   `python_rule_extraction` style for its early skills). It will miss
   phrasing outside the patterns in `step05_basic_knowledge_extraction/skill.py`.
   This is intentional for now - a wrong regex miss is safer than a
   fabricated concept - but recall is low.
3. **Engineering-principle archetypes are a fixed library of five**
   (feedback resistance, competitive-pathway removal, burden reduction,
   toxicity mitigation, cofactor balancing) in
   `step06_principle_distillation/skill.py`. Real textbook content that
   doesn't match one of these keyword sets produces no principle, not a
   wrong one. Expanding this library is the highest-value Phase 2 work.
4. **Fusion is name-based, not embedding/semantic similarity.** Two
   objects only fuse when their type and normalized name match exactly;
   `related_but_distinct` / `broader_narrower` semantic clustering is not
   implemented.
5. **Edition-aware fusion semantics are not implemented.** Step02 flags
   `unresolved_edition`, but Step10 does not yet specifically detect "same
   title, different edition" and label it `version_update` - a same-source,
   same-name divergence is currently generalized as `related_but_distinct`.
6. **Translation/bilingual normalization is not implemented.**
   `translation_quality` in the Step12 report is a placeholder
   (`not_applicable_in_phase1`); machine translation, translation-conflict
   detection, and `translation_status`/`translation_confidence` scoring
   are Phase 2/3.
7. **Step11 paper-case linking is a token-overlap heuristic** against
   whatever fields an `ExperimentalCase`-shaped dict happens to contain.
   It is deliberately capped at low confidence and always flagged
   `requires_human_review` - it is a candidate-surfacing mechanism, not a
   validation mechanism.
8. **No PDF/API/frontend server.** `paper_experimental_design_extraction`
   has `api/server.py` + a Next.js frontend; this module only produces the
   `frontend_view`/`knowledge_graph` JSON structures a frontend would
   consume. Wiring an actual API/UI is Phase 3.

None of the above blocks correct operation of what *is* implemented - the
evidence hard gate, the human-review governance gates, and the
concept/mechanism/principle/decision-rule/pattern/validation/failure
object model are all real and tested. It means recall (how much of a
given textbook gets distilled) is intentionally conservative until Phase
2 deepens the extraction logic, the same trajectory
`paper_experimental_design_extraction`'s skill07 went through (its
`extractor/` submodule split only happened after the initial
`python_rule_extraction` version proved the architecture).
