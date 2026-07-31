import hashlib
MAPPING={"skill01":"INPUT_ERROR","skill02":"SYSTEM_ERROR","skill03":"EVIDENCE_ERROR","skill04":"SYSTEM_ERROR",
"skill05":"PARSER_ERROR","skill06":"PARSER_ERROR","skill07":"MODEL_ERROR","skill08":"EVIDENCE_ERROR",
"skill09":"SCHEMA_ERROR","skill10":"MODEL_ERROR","skill11":"MODEL_ERROR","skill12":"HUMAN_REVIEW_ERROR","skill13":"SCHEMA_ERROR"}
def normalize(skill,error):
    code=error.get("code","unknown");message=error.get("message",str(error))
    # Preserve every extra diagnostic field a skill attaches (local_code, category,
    # severity, context, suggested_action, ...) instead of collapsing to a bare
    # message - the frontend error panel renders these so a user sees the full
    # root cause, not just a generic one-liner.
    extra={k:v for k,v in error.items() if k not in {"code","message","retryable"}}
    return {"error_id":"err_"+hashlib.sha256(f"{skill}|{code}|{message}".encode()).hexdigest()[:16],
            "skill":skill,"type":next((v for k,v in MAPPING.items() if skill.startswith(k)),"SYSTEM_ERROR"),
            "message":message,"retryable":bool(error.get("retryable",False)),"source_code":code,**extra}
