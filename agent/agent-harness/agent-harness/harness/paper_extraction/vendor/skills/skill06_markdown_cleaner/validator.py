import re
from collections import Counter

try:
    from .cleaners.citation_preserver import extract_citations
    from .cleaners.scientific_term_checker import protected_tokens
    from .json_builder import FIGURE, HEADING, TABLE
except ImportError:
    from cleaners.citation_preserver import extract_citations
    from cleaners.scientific_term_checker import protected_tokens
    from json_builder import FIGURE, HEADING, TABLE


def validate_cleaning(original, cleaned, document_json):
    original_protected = protected_tokens(original)
    cleaned_protected = protected_tokens(cleaned)
    original_citations = extract_citations(original)
    cleaned_citations = extract_citations(cleaned)
    original_headings = [m.group(2).strip() for line in original.splitlines() if (m := HEADING.match(line))]
    cleaned_headings = [m.group(2).strip() for line in cleaned.splitlines() if (m := HEADING.match(line))]
    markdown_figures = {re.sub(r"\s+", " ", m.group(1)).casefold() for m in FIGURE.finditer(cleaned)}
    markdown_tables = {m.group(1).casefold() for m in TABLE.finditer(cleaned)}
    json_figures = {v["figure_id"].casefold() for v in document_json["figures"]}
    json_tables = {v["table_id"].casefold() for v in document_json["tables"]}
    paragraph_consistency = all(v["text"] in cleaned for v in document_json["paragraphs"])
    section_consistency = all(v["content"] in cleaned for v in document_json["sections"])
    fallback_sections = [v for v in document_json["sections"] if v.get("is_fallback")]
    if cleaned_headings:
        section_count_consistency = (
            len(cleaned_headings) == len(document_json["sections"])
            and not fallback_sections
        )
    else:
        # A non-empty headingless document is represented by exactly one
        # conservative fallback section instead of silently losing its body.
        section_count_consistency = (
            bool(cleaned.strip())
            and len(document_json["sections"]) == 1
            and len(fallback_sections) == 1
        )
    no_new_words = _lexical_tokens(cleaned) - _lexical_tokens(original) == Counter()
    return [
        {"name": "sections_preserved", "passed": Counter(original_headings) == Counter(cleaned_headings)},
        {"name": "protected_scientific_values", "passed": original_protected == cleaned_protected},
        {"name": "citations_preserved", "passed": original_citations == cleaned_citations},
        {"name": "no_new_scientific_text", "passed": no_new_words},
        {"name": "markdown_json_section_count", "passed": section_count_consistency},
        {"name": "markdown_json_figure_count", "passed": markdown_figures == json_figures},
        {"name": "markdown_json_table_count", "passed": markdown_tables == json_tables},
        {"name": "markdown_json_text_consistency", "passed": paragraph_consistency and section_consistency}
    ]


def _lexical_tokens(text):
    text = re.sub(r"(?m)^\s*\|?\s*:?-{3,}.*$", "", text)
    return Counter(re.findall(r"[A-Za-z\u4e00-\u9fffΔμµ]+|\d+(?:\.\d+)?", text.casefold()))
