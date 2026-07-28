import json
from datetime import datetime, timezone
from pathlib import Path

from parsers.parser_interface import ParseResult
from schema import sha256_file

PDF_BYTES = b"%PDF-1.4\nscientific paper\n%%EOF\n"
MARKDOWN = """# Abstract

This study describes a sufficiently detailed scientific document for parser testing and reconstruction.

# Introduction

Prior work is cited here [1]. As shown in Fig. 1, production increased.

# Results

Figure 1: Production under the engineered condition.

Table 1: Experimental measurements

| Group | Yield |
|---|---:|
| Control | 1.0 |
| Engineered | 2.0 |

# Materials and Methods

## 2.1 Strain construction

The strain construction procedure is preserved without rewriting.

# Supplementary Methods

Supplementary conditions are recorded separately.

# References

[1] A. Author. Example reference. 2024.
"""

CONTENT_LIST = [
    {"type": "text", "text": "Abstract", "text_level": 1, "page_idx": 0},
    {"type": "image", "img_caption": ["Figure 1: Production under the engineered condition."], "bbox": [1, 2, 3, 4], "page_idx": 1},
    {"type": "table", "table_caption": ["Table 1: Experimental measurements"], "table_body": "<table></table>", "bbox": [1, 2, 3, 4], "page_idx": 1}
]


def fixed_clock():
    return datetime(2026, 7, 25, 8, 0, tzinfo=timezone.utc)


def make_artifact(directory: Path, checksum_override=None):
    pdf = directory / "original.pdf"
    pdf.write_bytes(PDF_BYTES)
    checksum = checksum_override or sha256_file(pdf)
    return {
        "paper_identity": {"paper_id": "paper:test", "title": "Scientific paper", "doi": "10.1000/test", "authors": [], "journal": None, "year": 2024},
        "file_information": {"file_name": "original.pdf", "path": str(pdf.resolve()), "size_bytes": len(PDF_BYTES), "mime_type": "application/pdf"},
        "integrity": {"checksum_algorithm": "sha256", "checksum_value": checksum},
        "processing_status": "verified",
        "artifact_ref": {"artifact_id": "artifact:test", "media_type": "application/pdf", "sha256": checksum, "version": "1", "source": "manual_upload", "uri": str(pdf.resolve())}
    }


class FakeMinerU:
    name = "MinerU"

    def __init__(self, markdown=MARKDOWN, content_list=CONTENT_LIST, fail_count=0):
        self.markdown = markdown
        self.content_list = content_list
        self.fail_count = fail_count
        self.calls = 0

    def parse(self, pdf_path, output_root, mode="pipeline", timeout_seconds=1800):
        self.calls += 1
        if self.calls <= self.fail_count:
            raise RuntimeError("simulated parser failure")
        output_root.mkdir(parents=True, exist_ok=True)
        md = output_root / f"{pdf_path.stem}.md"
        content = output_root / f"{pdf_path.stem}_content_list.json"
        md.write_text(self.markdown, encoding="utf-8")
        content.write_text(json.dumps(self.content_list, ensure_ascii=False), encoding="utf-8")
        return ParseResult(
            parser="MinerU", parser_version="3.4.4", mode=mode,
            markdown_path=md, content_list_path=content,
            output_files=[md, content], command=["mineru", "-b", mode]
        )


class NeverUsedFallback:
    name = "PyMuPDF"

    def parse(self, *args, **kwargs):
        raise AssertionError("fallback should not be used")

