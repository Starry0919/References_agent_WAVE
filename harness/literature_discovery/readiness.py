def literature_readiness(formal_gold_complete: bool = False) -> dict:
    """Functional readiness is deliberately separate from formal calibration."""
    return {
        "contract_version": "literature-readiness/2.0",
        "functionality_ready": True,
        "literature_discovery": "PRODUCTION_READY",
        "literature_classification": "PRODUCTION_READY_WITH_CONFIDENCE",
        "literature_acquisition": "PRODUCTION_READY_WITH_PROVENANCE",
        "formal_performance_validated": bool(formal_gold_complete),
        "formal_validation": "VALIDATED" if formal_gold_complete else "GOLD_PENDING",
        "downstream_auto_knowledge_admission": "CONSERVATIVE",
        "ddr_writes_enabled": False,
    }
