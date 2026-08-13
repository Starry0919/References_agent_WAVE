def assess(analysis):
    if analysis["compatibility"] == "unknown": label = "requires_revalidation"
    elif analysis["compatibility"] == "high" and analysis["confidence"] >= .8: label = "direct_reference"
    elif analysis["compatibility"] == "medium": label = "requires_optimization"
    else: label = "requires_revalidation"
    return {"transferability": label, "validation_needed": analysis["validation_needed"],
            "reason": "Classification reflects compatibility, evidence confidence, and unresolved validation; it is not a recommendation."}
