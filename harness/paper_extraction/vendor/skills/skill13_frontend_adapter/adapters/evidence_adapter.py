def build(evidence):
    mapping=evidence.get("evidence_map",{})
    items=[]
    for eid,record in mapping.items():
        locator=record.get("locator",{}); extraction=record.get("extraction",{})
        items.append({"evidence_id":eid,"source_type":"literature","paper":record.get("paper_id","unknown"),
                      "section":locator.get("section_path",[]) or ["unknown"],"page":locator.get("page"),
                      "quote":record.get("quote","unknown"),"confidence":record.get("confidence","unknown"),
                      "status":"reported","extraction_method":extraction.get("method","unknown"),
                      "artifact_id":record.get("artifact_id","unknown")})
    return {"items":items,"by_id":{x["evidence_id"]:x for x in items},"status":"available" if items else "unknown"}
