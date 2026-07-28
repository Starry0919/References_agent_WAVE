def build(normalized, clusters):
    membership = {pid: group["objective_cluster"] for group in clusters for pid in group["paper_ids"]}
    rows = []
    for item in normalized:
        rows.append({"paper_id": item["paper_id"], "objective_cluster": membership[item["paper_id"]],
                     "year": item["year"], **item["literature_facts"], "quality": item["quality"]})
    return rows
