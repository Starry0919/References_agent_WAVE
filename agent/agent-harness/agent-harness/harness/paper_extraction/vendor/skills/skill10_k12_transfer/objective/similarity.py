import re
def tokens(value):
    text = str(value or "").lower()
    return set(re.findall(r"[\w\u4e00-\u9fff]+", text))
def similarity(a, b):
    left, right = tokens(a), tokens(b)
    if not left or not right: return 0.0
    return round(len(left & right) / len(left | right), 4)
def cluster(items, threshold=.35):
    clusters = []
    for item in items:
        placed = False
        for group in clusters:
            score = similarity(item["objective"], group["representative_objective"])
            if score >= threshold or str(item["objective"]).strip().lower() == str(group["representative_objective"]).strip().lower():
                group["paper_ids"].append(item["paper_id"]); group["similarity_scores"][item["paper_id"]] = score
                placed = True; break
        if not placed:
            clusters.append({"objective_cluster": f"objective_cluster_{len(clusters)+1:02d}",
                             "representative_objective": item["objective"] or "unknown",
                             "paper_ids": [item["paper_id"]], "similarity_scores": {item["paper_id"]: 1.0 if item["objective"] else 0.0}})
    return clusters
