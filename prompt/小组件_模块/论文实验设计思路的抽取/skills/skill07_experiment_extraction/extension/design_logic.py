def build_design_logic(objective, hypothesis, measurements, outcomes):
    return {
        "question": objective[0] if objective else None,
        "hypothesis": hypothesis[0] if hypothesis else None,
        "measurement": measurements.get("assays", []),
        "expected_interpretation": None,
        "status": "reported" if objective or hypothesis else "unknown",
        "notes": "No expected interpretation is generated unless explicitly reported."
    }

