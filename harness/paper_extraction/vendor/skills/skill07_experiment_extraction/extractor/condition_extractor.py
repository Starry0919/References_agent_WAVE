import re

from .common import unique

TEMPERATURE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:°C|℃)")
TIME = re.compile(r"\b\d+(?:\.\d+)?\s*(?:h|hr|hours?|min|minutes?|s|seconds?)\b", re.I)
VOLUME = re.compile(r"\b\d+(?:\.\d+)?\s*(?:μL|µL|uL|mL|L)\b")
AGITATION = re.compile(r"\b\d+(?:\.\d+)?\s*rpm\b", re.I)
OD = re.compile(r"\bOD\d{3}\s*(?:[=:]\s*)?\d*(?:\.\d+)?", re.I)
DOSAGE = re.compile(r"\b(?:[A-Za-z][A-Za-z0-9_-]*\s+)?\d+(?:\.\d+)?\s*(?:μM|µM|uM|mM|M|mg/?mL|μg/?mL|µg/?mL|%|g/L)\b", re.I)
MEDIA = re.compile(r"\b(?:LB|Luria[- ]Bertani|M9|minimal medium|defined medium|YPD|SOC|TB)\b", re.I)
CARBON = re.compile(r"\b(?:glucose|glycerol|xylose|sucrose|acetate)\b", re.I)


def extract_conditions(items):
    values = {k: [] for k in ("temperature", "time", "volume", "agitation", "od", "medium", "carbon_source", "dosage")}
    candidates = []
    patterns = {
        "temperature": TEMPERATURE, "time": TIME, "volume": VOLUME,
        "agitation": AGITATION, "od": OD, "medium": MEDIA,
        "carbon_source": CARBON, "dosage": DOSAGE
    }
    for item in items:
        found = False
        for name, pattern in patterns.items():
            matches = pattern.findall(item["text"])
            if matches:
                values[name].extend(matches)
                found = True
        if found:
            candidates.append(item)
    return {k: unique(v) for k, v in values.items()}, candidates

