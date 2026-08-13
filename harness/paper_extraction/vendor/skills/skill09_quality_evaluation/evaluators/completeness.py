from .common import field_score, result

GROUPS = {
    "biological_system": ["strain", "genotype"],
    "engineering": ["engineering_method"],
    "experimental_setup": ["experimental_groups", "controls", "culture_conditions"],
    "measurement": ["assay", "instruments", "analysis_methods"],
    "outcome": ["outcomes"],
}
def evaluate(fields):
    names = [name for group in GROUPS.values() for name in group]
    score, found, missing = field_score(fields, names)
    groups = {}
    for key, members in GROUPS.items():
        groups[key] = field_score(fields, members)[0]
    return result(score, f"{len(found)} of {len(names)} required design fields are defined.", missing_fields=missing, group_scores=groups)
