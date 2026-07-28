from datetime import datetime, timezone
import hashlib
import json

ARTIFACT_TYPES = {
    "step01_task_contract": "TaskContractArtifact",
    "step02_source_validation": "SourceValidationArtifact",
    "step03_document_parsing": "SourceStructureArtifact",
    "step04_scope_selection": "ExtractionScopeArtifact",
    "step05_basic_knowledge_extraction": "BasicKnowledgeArtifact",
    "step06_principle_distillation": "EngineeringPrincipleArtifact",
    "step07_decision_rule_generation": "DecisionRuleArtifact",
    "step08_pattern_validation_failure": "PatternValidationFailureArtifact",
    "step09_evidence_binding": "EvidenceAuditArtifact",
    "step10_knowledge_fusion": "FusionArtifact",
    "step11_paper_case_linking": "PaperLinkArtifact",
    "step12_quality_governance": "QualityGovernanceArtifact",
    "step13_frontend_adapter": "FrontendArtifact",
}

SCHEMA_VERSION = "0.1.0"


def create(task_id, step, result, index=0):
    content = result.get("output")
    raw = json.dumps(content, ensure_ascii=False, sort_keys=True, default=str)
    input_hash = hashlib.sha256(raw.encode()).hexdigest()
    aid = f"{task_id}:{step}:{index}:{input_hash[:12]}"
    return {
        "artifact_id": aid,
        "artifact_type": ARTIFACT_TYPES[step],
        "step_name": step,
        "version": result.get("provenance", {}).get("step_version", "unknown"),
        "input_hash": input_hash,
        "source_ids": result.get("provenance", {}).get("source_ids", []),
        "created_time": datetime.now(timezone.utc).isoformat(),
        "schema_version": SCHEMA_VERSION,
        "content": content,
        "provenance": result.get("provenance", {}),
        "validation_status": "valid",
    }
