def assess(strain, target_family):
    if not strain:
        return "unknown", ["Literature strain is not reported."], ["Confirm source strain and genetic background."]
    text = str(strain).lower()
    target = str(target_family).lower()
    if target in text or ("k-12" in text and "k-12" in target):
        return "high", ["The reported strain label explicitly matches the target K-12 family."], ["Verify exact derivative and genotype."]
    return "medium", ["The reported strain label does not explicitly match the target K-12 family; background-dependent effects remain unverified."], ["Revalidate phenotype, growth, and intervention effect in the selected K-12 derivative."]
