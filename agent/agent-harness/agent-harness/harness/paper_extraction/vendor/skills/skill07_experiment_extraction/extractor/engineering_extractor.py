import re

from .common import unique

METHODS = {
    "gene knockout": re.compile(r"\b(?:gene\s+)?(?:knockout|knock-out|deletion)\b|基因敲除", re.I),
    "knockdown": re.compile(r"\bknockdown\b|基因敲低", re.I),
    "overexpression": re.compile(r"\boverexpress(?:ion|ed)?\b|过表达", re.I),
    "CRISPR": re.compile(r"\bCRISPR(?:-Cas9)?\b", re.I),
    "CRISPRi": re.compile(r"\bCRISPRi\b", re.I),
    "promoter engineering": re.compile(r"\bpromoter\s+engineering\b|启动子工程", re.I),
    "pathway engineering": re.compile(r"\bpathway\s+engineering\b|通路工程", re.I)
}
# Δgene deletion notation (e.g. "ΔtrpB") is a strong, unambiguous signal and is
# accepted on its own. A bare "gene X"/"of X" context (the previous approach) is
# too loose: it matches whatever word follows, including "the", "was", "two",
# "strain", etc. Locus-style gene symbols (aroG, trpB, glnA, GapN, SthA, pntAB)
# always contain an internal case change that ordinary sentence-cased English
# words (Strain, Figure, Results, ...) never have, so shape-matching the token
# itself is far more reliable than matching the word that happens to precede it.
DELTA_GENE = re.compile(r"Δ([A-Za-z][A-Za-z0-9_-]{1,20})")
GENE = re.compile(r"\b(?:[a-z]{2,4}[A-Z][A-Za-z0-9]{0,2}|[A-Z][a-z]{1,4}[A-Z][A-Za-z0-9]{0,2})\b")


def extract_engineering(items):
    methods, genes, candidates = [], [], []
    for item in items:
        text = item["text"]
        found = [name for name, pattern in METHODS.items() if pattern.search(text)]
        if found:
            methods.extend(found)
            genes.extend(DELTA_GENE.findall(text))
            genes.extend(GENE.findall(text))
            candidates.append(item)
    return {"methods": unique(methods), "target_genes": unique(genes)}, candidates

