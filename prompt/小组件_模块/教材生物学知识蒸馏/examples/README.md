# Examples

All three files are the *actual* recorded `{"input": ..., "output": ...}`
of `biological_knowledge_distillation.execute()` against the synthetic
fixtures in `biological_knowledge_distillation/tests/fixtures/` (generated,
not hand-written, so they can't silently drift from the real code).
`artifacts` and `step_logs` are stripped for readability; everything else
is the real output.

- `example_1_english_textbook.json` - English textbook chapter (feedback
  inhibition + metabolic burden), Level3 engineering distillation +
  Level5 frontend/knowledge-graph adapter. Produces
  `engineering_principles` gated to `derivation_type=model_inference` /
  `requires_human_review=true`, since the source only describes the
  mechanisms and never itself recommends an engineering action.
- `example_2_chinese_textbook.json` - Chinese textbook chapter (反馈抑制 +
  竞争支路), Level2 basic knowledge only (no engineering goal given) -
  shows concepts/mechanisms extracted without forcing engineering
  distillation.
- `example_3_bilingual_fusion_paper_link.json` - the English and Chinese
  chapters above fused together (Level4) plus linking to a synthetic
  `paper_case_artifacts` entry (Level5). Shows `source_conflicts` for
  definitions that genuinely differ across the two sources (never
  silently averaged/overwritten), and a `paper_case_links` entry pinned at
  low confidence with `requires_human_review`-style language in
  `transferability`.

Every source in these examples is a synthetic fixture invented for
testing (`Fixture Press`, ISBN `000-0-00-000000-0`, etc.) - not a real
book, ISBN, or citation. Do not reuse these bibliographic records as if
they were real.
