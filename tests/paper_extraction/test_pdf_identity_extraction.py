"""skill04's title/DOI-from-PDF enrichment (artifact/metadata.py).

Manual uploads never carry a title/DOI (uploader/manual_upload_handler.py
only ever supplies `path`+`paper_id`) - this is what filled that gap in for
a real uploaded paper (s41467-023-41135-7.pdf) during a live end-to-end
run, where the resulting literature-evidence entry otherwise saved with an
"Untitled paper (...)" placeholder title.
"""
import io
import sys
from pathlib import Path

import pytest

_SKILLS_ROOT = Path(__file__).resolve().parents[2] / "harness" / "paper_extraction" / "vendor" / "skills"
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

from skill04_pdf_acquisition.artifact.metadata import enrich_identity_from_pdf, extract_doi_from_text  # noqa: E402

pypdf = pytest.importorskip("pypdf")


def _build_pdf_bytes(*, title=None, subject=None):
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=200, height=200)
    metadata = {}
    if title is not None:
        metadata["/Title"] = title
    if subject is not None:
        metadata["/Subject"] = subject
    if metadata:
        writer.add_metadata(metadata)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_extract_doi_from_text_finds_and_trims_doi():
    text = "Article https://doi.org/10.1038/s41467-023-41135-7 Using a synthetic machinery"
    assert extract_doi_from_text(text) == "10.1038/s41467-023-41135-7"


def test_extract_doi_from_text_trims_trailing_sentence_punctuation():
    text = "see doi:10.1234/abcd.5678."
    assert extract_doi_from_text(text) == "10.1234/abcd.5678"


def test_extract_doi_from_text_returns_none_when_absent():
    assert extract_doi_from_text("no identifiers in this text") is None
    assert extract_doi_from_text("") is None
    assert extract_doi_from_text(None) is None


def test_enrich_identity_from_pdf_fills_missing_title_and_doi():
    pdf_bytes = _build_pdf_bytes(
        title="A Sample Extracted Paper Title",
        subject="Nature Communications, doi:10.1038/s41467-023-41135-7",
    )
    identity = {"paper_id": "p1", "title": None, "doi": None, "authors": [], "journal": None, "year": None}

    enriched = enrich_identity_from_pdf(identity, pdf_bytes)

    assert enriched["title"] == "A Sample Extracted Paper Title"
    assert enriched["doi"] == "10.1038/s41467-023-41135-7"
    # Untouched fields carried through unchanged.
    assert enriched["paper_id"] == "p1"


def test_enrich_identity_from_pdf_never_overwrites_known_fields():
    pdf_bytes = _build_pdf_bytes(title="PDF Metadata Title", subject="doi:10.9999/other-doi")
    identity = {"paper_id": "p1", "title": "Already Known Title", "doi": "10.1111/already-known", "authors": [], "journal": None, "year": None}

    enriched = enrich_identity_from_pdf(identity, pdf_bytes)

    assert enriched["title"] == "Already Known Title"
    assert enriched["doi"] == "10.1111/already-known"


def test_enrich_identity_from_pdf_is_noop_when_pdf_is_unparseable():
    identity = {"paper_id": "p1", "title": None, "doi": None, "authors": [], "journal": None, "year": None}

    enriched = enrich_identity_from_pdf(identity, b"not a real pdf")

    assert enriched == identity


def test_enrich_identity_from_pdf_leaves_title_none_when_metadata_has_none():
    # No body-text guessing for title (fabrication risk) - only ever the
    # PDF's own /Title metadata; a PDF without one keeps title unset.
    pdf_bytes = _build_pdf_bytes(subject="doi:10.2222/no-title-here")
    identity = {"paper_id": "p1", "title": None, "doi": None, "authors": [], "journal": None, "year": None}

    enriched = enrich_identity_from_pdf(identity, pdf_bytes)

    assert enriched["title"] is None
    assert enriched["doi"] == "10.2222/no-title-here"
