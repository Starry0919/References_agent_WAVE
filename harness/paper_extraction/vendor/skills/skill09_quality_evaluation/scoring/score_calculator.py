try:
    from ..schema import WEIGHTS
except ImportError:
    from schema import WEIGHTS

def calculate(dimensions):
    details, total = [], 0.0
    for name, weight in WEIGHTS.items():
        score = dimensions[name]["score"]
        contribution = score * weight
        total += contribution
        details.append({"dimension": name, "score": score, "weight": weight, "weighted_contribution": round(contribution, 2), "reason": dimensions[name]["reason"]})
    return round(total, 2), details
