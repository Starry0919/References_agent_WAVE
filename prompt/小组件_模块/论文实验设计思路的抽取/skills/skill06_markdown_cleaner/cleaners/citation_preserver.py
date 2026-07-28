import re
from collections import Counter


def extract_citations(text):
    bracketed = re.findall(r"\[(?:\d+(?:\s*[-,]\s*\d+)*)\]", text)
    author_year = re.findall(r"\([A-Z][A-Za-z'-]+(?:\s+et\s+al\.)?,\s*(?:19|20)\d{2}[a-z]?\)", text)
    return Counter(bracketed + author_year)

