import io
import re

# 10.<4-9 digits>/<suffix> (the DOI Handbook's own syntax spec) - stops at
# whitespace/quotes/angle-brackets/closing-bracket so a DOI printed inline
# in running text (e.g. "Article https://doi.org/10.1038/s41467-...")
# doesn't swallow trailing prose.
_DOI_PATTERN = re.compile(r"10\.\d{4,9}/[^\s\"'<>\)\]]+", re.IGNORECASE)


def paper_identity(candidate):
    return {
        "paper_id": candidate.get("paper_id"),
        "title": candidate.get("title"),
        "doi": candidate.get("identifiers", {}).get("doi"),
        "authors": list(candidate.get("authors", [])),
        "journal": candidate.get("journal"),
        "year": candidate.get("year")
    }


def _clean_doi(raw):
    return raw.rstrip(".,;:")


def extract_doi_from_text(text):
    """First DOI-shaped token in `text`, or None. Pure regex, no PDF
    parsing - kept standalone so it's testable without a real PDF."""
    if not text:
        return None
    match = _DOI_PATTERN.search(text)
    return _clean_doi(match.group(0)) if match else None


def enrich_identity_from_pdf(identity, pdf_bytes):
    """Best-effort fill-in of a missing title/DOI straight from the PDF
    itself, via its own document metadata plus a DOI scan of page 1.

    Manual uploads never carry these (uploader/manual_upload_handler.py
    only ever supplies `path`+`paper_id`), and an auto-downloaded
    candidate's citation metadata can also arrive with a gap - this is the
    single choke point (`skill.py::_store`) both paths go through, so it
    applies uniformly to either source.

    Never overwrites an already-known field, and never raises: title is
    only ever taken from the PDF's own `/Title` metadata (authoritative
    when present) - unlike DOI, there's no reliable, low-risk way to guess
    a title from body text, so a missing metadata title is left as-is
    rather than fabricated from a heuristic guess.
    """
    if identity.get("title") and identity.get("doi"):
        return identity

    try:
        from pypdf import PdfReader
    except ImportError:
        return identity
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception:
        return identity

    enriched = dict(identity)

    if not enriched.get("title"):
        try:
            meta_title = reader.metadata.title if reader.metadata else None
        except Exception:
            meta_title = None
        if meta_title and meta_title.strip():
            enriched["title"] = meta_title.strip()

    if not enriched.get("doi"):
        try:
            subject = (reader.metadata.get("/Subject") if reader.metadata else None) or ""
        except Exception:
            subject = ""
        doi = extract_doi_from_text(subject)
        if not doi:
            try:
                first_page_text = reader.pages[0].extract_text() if reader.pages else ""
            except Exception:
                first_page_text = ""
            doi = extract_doi_from_text(first_page_text)
        if doi:
            enriched["doi"] = doi

    return enriched
