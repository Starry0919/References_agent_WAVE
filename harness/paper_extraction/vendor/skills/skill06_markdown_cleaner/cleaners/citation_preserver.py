import re
from collections import Counter


def extract_citations(text):
    bracketed = re.findall(r"\[(?:\d+(?:\s*[-,]\s*\d+)*)\]", text)
    author_year = re.findall(r"\([A-Z][A-Za-z'-]+(?:\s+et\s+al\.)?,\s*(?:19|20)\d{2}[a-z]?\)", text)
    # Markdown normalization may remove spaces adjacent to a line break
    # without changing the citation itself, e.g. "(Kerek et al., \n2023)"
    # -> "(Kerek et al.,\n2023)". Compare canonical whitespace so the
    # scientific-content gate catches citation loss or mutation, not an
    # equivalent formatting-only change.
    return Counter(re.sub(r"\s+", " ", value) for value in bracketed + author_year)
