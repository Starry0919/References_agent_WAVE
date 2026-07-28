import re

from .common import unique

ORGANISMS = [
    (re.compile(r"\b(?:E\.?\s*coli|Escherichia\s+coli)\b|大肠杆菌", re.I), "Escherichia coli"),
    (re.compile(r"\bSaccharomyces\s+cerevisiae\b|酿酒酵母", re.I), "Saccharomyces cerevisiae"),
    (re.compile(r"\bBacillus\s+subtilis\b|枯草芽孢杆菌", re.I), "Bacillus subtilis")
]
STRAIN = re.compile(r"\b(K[-\s]?12|MG1655|BW25113|W3110|BL21(?:\(DE3\))?|DH5α|BY4741)\b", re.I)
GENOTYPE = re.compile(r"(?:Δ[A-Za-z0-9_-]+|[A-Za-z0-9_-]+::[A-Za-z0-9_-]+|\b(?:deletion|knockout)\s+(?:of\s+)?[A-Za-z0-9_-]+)", re.I)


def extract_biological_system(items):
    organisms, strains, genotypes, candidates = [], [], [], []
    for item in items:
        found = False
        for pattern, canonical in ORGANISMS:
            if pattern.search(item["text"]):
                organisms.append(canonical)
                found = True
        strains.extend("K-12" if re.fullmatch(r"K[\s-]?12", v, re.I) else v for v in STRAIN.findall(item["text"]))
        genotypes.extend(GENOTYPE.findall(item["text"]))
        if found or STRAIN.search(item["text"]) or GENOTYPE.search(item["text"]):
            candidates.append(item)
    return {
        "organism": unique(organisms), "strain": unique(strains),
        "genotype": unique(genotypes)
    }, candidates

