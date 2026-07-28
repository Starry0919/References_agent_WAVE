ERRORS={"UI001":("engineering_plan_missing","Engineering plan is missing."),
"UI002":("evidence_missing","Evidence is unavailable; display unknown."),
"UI003":("ai_source_unmarked","AI or literature content has no valid source label."),
"UI004":("i18n_missing","A required translation is missing.")}
def error(code,details=None):
    name,message=ERRORS[code]; result={"code":code,"name":name,"message":message}
    if details is not None: result["details"]=details
    return result
