def _step(number, phase, title, what, why, how, inputs, outputs, evidence, checkpoint, risks, source="reported_in_literature", level=1):
    return {"step_id": f"{phase.upper()}-{number:02d}", "phase": phase, "title": title,
            "source_type": source, "suggestion_level": level, "what": what, "why": why,
            "how": how, "input": inputs, "output": outputs, "evidence": evidence,
            "validation_checkpoint": checkpoint, "risk": risks}

def reported_steps(candidate, details):
    evidence = candidate["literature_support"]["evidence_ids"]
    risks = [x["detail"] for x in candidate.get("risks", [])]
    return [
        _step(1, "design", "Define evidence-derived intervention", details["modification"],
              "Preserve the literature-supported candidate without adding targets or parameters.",
              {"strategy": details["modification"], "host": details["host"], "genotype": details["genotype"]},
              [details["host"]], ["reviewed design specification"], evidence, "Human confirms target, host, and unknown fields.", risks),
        _step(1, "build", "Construct the candidate strain", details["modification"],
              "Translate the reported intervention into a controlled build task.",
              {"modification": details["modification"], "conditions": details["conditions"]},
              ["approved design specification"], ["candidate construct", "build record"], evidence,
              "Verify construct identity before phenotype testing.", risks),
        _step(1, "test", "Run evidence-aligned validation", details["assay"],
              "Measure the target phenotype using the reported assay where available.",
              {"assay": details["assay"], "instrument": details["instrument"], "groups": details["groups"], "controls": details["controls"]},
              ["verified construct", "controls"], ["measurement dataset"], evidence,
              "Confirm controls, replicate plan, assay suitability, and data quality.", risks),
        _step(1, "learn", "Feed results into the next DBTL iteration", "Compare measured data with acceptance criteria.",
              "Use observed data to update the design record; do not claim a mechanism from the plan.",
              {"analysis": details["analysis"]}, ["measurement dataset"], ["decision record", "next-iteration inputs"], evidence,
              "Human reviews interpretation and approves any next iteration.", risks),
    ]

def combination_steps(candidates):
    evidence = sorted({x for c in candidates for x in c["literature_support"]["evidence_ids"]})
    strategies = [c["candidate_strategy"] for c in candidates]
    uncertainty = "Combined effects are unreported and may be non-additive."
    return [_step(1, phase, f"Combination hypothesis — {phase}", strategies,
                  "Evaluate a combination of separately supported candidates without assuming superiority.",
                  {"hypothesis": "Combination requires staged validation", "strategies": strategies},
                  ["individually reviewed candidates"], [f"{phase} combination checkpoint"], evidence,
                  "Human approval required before execution.", [uncertainty], "ai_generated_proposal", 2)
            for phase in ("design", "build", "test", "learn")]
