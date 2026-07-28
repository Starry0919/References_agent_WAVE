from datetime import datetime,timezone
import hashlib,json
ARTIFACT_TYPES={
"skill01_requirement_parser":"RequirementArtifact","skill02_literature_retrieval":"LiteratureSearchArtifact",
"skill03_citation_validation":"PaperValidationArtifact","skill04_pdf_acquisition":"PDFArtifact",
"skill05_pdf_parser":"ParsedDocumentArtifact","skill06_markdown_cleaner":"CleanDocumentArtifact",
"skill07_experiment_extraction":"ExperimentalDesignArtifact","skill08_evidence_binding":"EvidenceArtifact",
"skill09_quality_evaluation":"EvaluationArtifact","skill10_k12_transfer":"K12AdaptationArtifact",
"skill11_engineering_proposal":"EngineeringPlanArtifact","skill12_qc_human_review":"QCArtifact",
"skill13_frontend_adapter":"FrontendArtifact"}
def create(task_id,skill,result,index=0):
    content=result.get("output")
    raw=json.dumps(content,ensure_ascii=False,sort_keys=True,default=str)
    aid=f"{task_id}:{skill}:{index}:{hashlib.sha256(raw.encode()).hexdigest()[:12]}"
    return {"artifact_id":aid,"artifact_type":ARTIFACT_TYPES[skill],"skill_name":skill,
            "version":result.get("provenance",{}).get("skill_version","unknown"),
            "created_time":datetime.now(timezone.utc).isoformat(),"content":content,
            "provenance":result.get("provenance",{})}
