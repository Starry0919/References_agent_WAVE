from .common import result, values

def evaluate(extensions):
    data = extensions.get("variables", {})
    categories = {}
    aliases = {
        "independent": ("independent", "independent_variables"),
        "dependent": ("dependent", "dependent_variables"),
        "controlled": ("controlled", "controlled_variables"),
    }
    for name, keys in aliases.items():
        item = next((data.get(k) for k in keys if k in data), [])
        categories[name] = bool(values(item) or item)
    score = round(100 * sum(categories.values()) / 3, 2)
    label = "good" if score == 100 else "partial" if score else "poor"
    missing = [k for k, v in categories.items() if not v]
    return result(score, f"{sum(categories.values())} of 3 variable categories are defined.", variable_quality=label, issues=missing)
