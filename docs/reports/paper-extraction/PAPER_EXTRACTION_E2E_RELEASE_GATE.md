# Paper Extraction E2E Release Gate

Final status: **PARTIAL**

| Gate | Status | Reason |
|---|---|---|
| A Scientific safety | scoped PASS | safety corpus retains zero known critical false verification; real admission not replayable |
| B Extraction quality | INSUFFICIENT | Silver strict-support yield measured; independent experiment precision/recall unavailable |
| C Verification quality | PARTIAL | E1/E2/E3 measured on 240 Silver field claims; human recall unavailable |
| D DDR quality | INSUFFICIENT | no human decision/trigger/rationale Gold |
| E Provenance | PASS | 100% of measured artifacts trace to cache, document and hash |
| F Generalization | PARTIAL | five-paper disjoint holdout measured, but not human Gold |

Scoped regression: 175 passed. Whole-repository regression: INCONCLUSIVE after
the 120-second bound, with no failure output before timeout.

## Required seven answers

1. Skill07 real-paper experiment precision/recall: **not estimable** without
   independent ExperimentInstance Gold. Silver strict field-support yield is
   0.068 combined; this is not experiment precision.
2. Skill07 most often fails at composite document-level projection and precise
   experiment/object binding, visible as the E3 bottleneck.
3. Skill08 caught many unsupported composite candidates, but the exact number of
   true Skill07 errors caught is not estimable without Gold.
4. Correct knowledge rejected by Skill08: not estimable; candidate false-reject
   labels require human adjudication.
5. DDR decision precision/recall: not estimable; temporal trigger/rationale Gold
   is absent.
6. Wrong admitted critical knowledge: not estimable for these historical caches
   because current admission was not replayable. Scoped admission regression
   tests remain fail-closed.
7. The next largest bottleneck is **human ExperimentInstance/DDR Gold**, followed
   technically by Skill07 experiment-level representation; E3 appears low largely
   because it receives flattened composite claims.

PASS is prohibited until human-reviewed Gold and current-contract end-to-end
artifacts cover extraction, DDR and admission on a sealed holdout.
