try:
    from ..schema import normalize_doi, valid_doi_format
except ImportError:
    from schema import normalize_doi, valid_doi_format


def validate_doi(value):
    normalized = normalize_doi(value)
    return {"doi": normalized, "format_valid": valid_doi_format(normalized)}
