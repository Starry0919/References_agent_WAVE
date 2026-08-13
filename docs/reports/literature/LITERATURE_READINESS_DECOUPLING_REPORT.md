# Literature Readiness Decoupling Report

The v2 readiness contract separates operational literature functions from formal scientific calibration:

- Literature discovery: `PRODUCTION_READY`
- Literature classification: `PRODUCTION_READY_WITH_CONFIDENCE`
- Literature acquisition: `PRODUCTION_READY_WITH_PROVENANCE`
- Formal validation: `GOLD_PENDING`
- Downstream automatic knowledge admission: `CONSERVATIVE`
- DDR writes: disabled

Human Gold no longer blocks search, retrieval, metadata classification, ranking, routing, or lawful acquisition. The existing annotation package, agreement runner, calibration tools, and conservative downstream validation gate remain intact.

This does not claim calibrated scientific performance. It explicitly distinguishes `functionality_ready=true` from `formal_performance_validated=false`.

