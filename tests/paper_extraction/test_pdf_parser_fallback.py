from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import fitz

import harness.paper_extraction

_SKILLS_ROOT = Path(harness.paper_extraction.__file__).resolve().parent / "vendor" / "skills"
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

from skill05_pdf_parser.parsers import ParserUnavailable
from skill05_pdf_parser.skill import PdfStructureParsingSkill


class _UnavailableMinerU:
    name = "MinerU"

    def parse(self, *args, **kwargs):
        raise ParserUnavailable("MinerU is not installed")


def _write_text_pdf(path: Path) -> None:
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Abstract\nA reproducible scientific PDF extraction test.\n"
        "Methods\nCells were cultured and measured with three replicates.",
    )
    document.save(path)
    document.close()


def test_manual_pdf_uses_pymupdf_when_mineru_is_unavailable(tmp_path):
    pdf_path = tmp_path / "uploaded-paper.pdf"
    _write_text_pdf(pdf_path)
    checksum = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    artifact = {
        "paper_identity": {"paper_id": "manual-upload"},
        "processing_status": "verified",
        "file_information": {"path": str(pdf_path)},
        "integrity": {"checksum_value": checksum},
    }

    result = PdfStructureParsingSkill(
        mineru_parser=_UnavailableMinerU(),
        output_root=tmp_path / "artifacts",
        logger=lambda event: None,
    ).execute({"paper_artifact": artifact})

    assert result["status"] in {"succeeded", "succeeded_with_warnings"}
    parsed = result["output"]["document_artifact"]
    assert parsed["document_metadata"]["parser"] == "PyMuPDF"
    assert "reproducible scientific PDF extraction test" in parsed["markdown_artifact"]["markdown_content"]
    assert [attempt["status"] for attempt in parsed["parse_attempts"]] == ["failed", "failed", "succeeded"]
