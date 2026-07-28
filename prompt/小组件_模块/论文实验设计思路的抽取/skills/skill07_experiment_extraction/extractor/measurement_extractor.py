import re

from .common import unique

ASSAYS = re.compile(r"\b(?:growth assay|RNA-?seq|proteomics|metabolomics|HPLC|LC-?MS(?:/MS)?|GC-?MS|flow cytometry|fluorescence assay|qPCR|RT-?qPCR)\b", re.I)
INSTRUMENT = re.compile(r"\b(?:HPLC|LC-?MS(?:/MS)?|GC-?MS|mass spectrometer|flow cytometer|spectrophotometer)(?:\s*\([^)]{2,80}\))?", re.I)
ANALYSIS = re.compile(r"\b(?:ANOVA|t-?test|Mann[- ]Whitney|DESeq2|GraphPad Prism|R version [\d.]+|Python [\d.]+|mean\s*±\s*(?:SD|SEM)|p\s*[<=>]\s*0?\.\d+)\b", re.I)
REPLICATE = re.compile(r"\b(?:(\d+|two|three|four|five)\s+(biological|technical)\s+replicates?|performed\s+in\s+(duplicate|triplicate|quadruplicate)|n\s*=\s*(\d+))\b", re.I)


def extract_measurements(items):
    assays, instruments, analyses, replicates, candidates = [], [], [], [], []
    word_numbers = {"two": 2, "three": 3, "four": 4, "five": 5, "duplicate": 2, "triplicate": 3, "quadruplicate": 4}
    for item in items:
        found = False
        for match in ASSAYS.findall(item["text"]):
            assays.append(match)
            found = True
        for match in INSTRUMENT.findall(item["text"]):
            instruments.append(match)
            found = True
        for match in ANALYSIS.findall(item["text"]):
            analyses.append(match)
            found = True
        for match in REPLICATE.finditer(item["text"]):
            number, kind, named, n_value = match.groups()
            raw_number = number or named or n_value
            value = int(raw_number) if raw_number and raw_number.isdigit() else word_numbers.get((raw_number or "").casefold())
            replicates.append({
                "type": kind.casefold() if kind else ("technical" if named else "unspecified"),
                "n": value, "reported_text": match.group(0)
            })
            found = True
        if found:
            candidates.append(item)
    return {
        "assays": unique(assays), "instruments": unique(instruments),
        "analysis_methods": unique(analyses), "replicates": _unique_replicates(replicates)
    }, candidates


def _unique_replicates(values):
    seen, result = set(), []
    for value in values:
        key = (value["type"], value["n"], value["reported_text"].casefold())
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result

