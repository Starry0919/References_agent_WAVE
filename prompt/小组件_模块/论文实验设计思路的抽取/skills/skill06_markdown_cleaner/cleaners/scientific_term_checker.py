import re
from collections import Counter


PROTECTED_PATTERN = re.compile(
    r"(?<!\w)(?:"
    r"\d+(?:\.\d+)?\s*(?:°C|℃|h|min|s|ms|rpm|μL|µL|uL|mL|L|μM|µM|mM|M|mg|g|kg|ng|OD\d{3}|%|v/v|w/v)"
    r"|OD\d{3}\s*[=:]?\s*\d+(?:\.\d+)?"
    r"|(?:Fig(?:ure)?|Table)\.?\s*S?\d+[A-Za-z]?"
    r"|Δ[A-Za-z0-9_-]+"
    r"|CRISPRi"
    r")",
    re.I
)


def protected_tokens(text):
    return Counter(re.sub(r"\s+", "", token).casefold() for token in PROTECTED_PATTERN.findall(text))

