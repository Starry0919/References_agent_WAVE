import hashlib
MAPPING={"skill01":"INPUT_ERROR","skill02":"SYSTEM_ERROR","skill03":"EVIDENCE_ERROR","skill04":"SYSTEM_ERROR",
"skill05":"PARSER_ERROR","skill06":"PARSER_ERROR","skill07":"MODEL_ERROR","skill08":"EVIDENCE_ERROR",
"skill09":"SCHEMA_ERROR","skill10":"MODEL_ERROR","skill11":"MODEL_ERROR","skill12":"HUMAN_REVIEW_ERROR","skill13":"SCHEMA_ERROR"}
def normalize(skill,error):
    code=error.get("code","unknown");message=error.get("message",str(error))
    return {"error_id":"err_"+hashlib.sha256(f"{skill}|{code}|{message}".encode()).hexdigest()[:16],
            "skill":skill,"type":next((v for k,v in MAPPING.items() if skill.startswith(k)),"SYSTEM_ERROR"),
            "message":message,"retryable":bool(error.get("retryable",False)),"source_code":code}
