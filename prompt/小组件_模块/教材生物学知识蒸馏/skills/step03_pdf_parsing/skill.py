"""Step03 - convert a PDF source to Markdown via MinerU (with a PyMuPDF
fallback), mirroring 论文实验设计抽取/skills/skill05_pdf_parser's role in
that pipeline. Sources that already arrive as pasted text/Markdown (no
`.pdf` path) pass straight through unchanged - this step never rewrites
text a caller already supplied.
"""
from __future__ import annotations

from pathlib import Path

from .parsers import MinerUParser, ParseFailure, ParserUnavailable, PyMuPdfParser, reconstruct_markdown_from_content_list

VERSION = "0.1.0"

DEFAULT_OUTPUT_ROOT = Path(__file__).resolve().parents[2] / "biological_knowledge_distillation" / "storage" / "pdf_parse_cache"


def _is_pdf_source(source_ref):
    path = source_ref.get("path")
    return bool(path) and Path(path).suffix.lower() == ".pdf"


def _page_count(content_list):
    pages = [entry.get("page_idx") for entry in content_list if isinstance(entry, dict) and entry.get("page_idx") is not None]
    return (max(pages) + 1) if pages else None


def execute(request, mineru_parser=None, fallback_parser=None, output_root=None, **kwargs):
    source_ref = request["source_ref"]
    source_id = request["validated_source"]["source_id"]

    if not _is_pdf_source(source_ref):
        return {
            "output": {
                "source_id": source_id, "used_pdf_parser": False, "parser_name": "not_applicable",
                "raw_markdown": source_ref.get("raw_text", "") or "", "content_list": [], "page_count": None,
            },
            "status": "succeeded", "errors": [],
            "provenance": {"step_version": VERSION, "source_ids": [source_id], "parser": "not_applicable", "parser_attempts": []},
        }

    pdf_path = Path(source_ref["path"])
    if not pdf_path.is_file():
        return {
            "output": None, "status": "retryable_failure",
            "errors": [{"code": "ACCESS_BLOCKED", "message": f"{source_id}: PDF path does not exist: {pdf_path}", "retryable": True, "source_id": source_id}],
            "provenance": {"step_version": VERSION, "source_ids": [source_id], "parser": None, "parser_attempts": []},
        }

    mineru = mineru_parser or MinerUParser()
    fallback = fallback_parser or PyMuPdfParser()
    run_root = Path(output_root or DEFAULT_OUTPUT_ROOT) / source_id
    attempts = []
    parse_result = None
    for parser in (mineru, fallback):
        try:
            parse_result = parser.parse(pdf_path, run_root / parser.name.lower())
            attempts.append({"parser": parser.name, "status": "succeeded"})
            break
        except (ParserUnavailable, ParseFailure, Exception) as exc:
            attempts.append({"parser": getattr(parser, "name", type(parser).__name__), "status": "failed", "error_type": type(exc).__name__, "message": str(exc)[:300]})

    if parse_result is None:
        return {
            "output": None, "status": "retryable_failure",
            "errors": [{
                "code": "PARSING_ERROR",
                "message": f"{source_id}: no PDF parser available/succeeded (attempts: {attempts}). Install MinerU at D:\\MinerU or `pip install pymupdf`, or supply raw_text directly.",
                "retryable": True, "source_id": source_id,
            }],
            "provenance": {"step_version": VERSION, "source_ids": [source_id], "parser": None, "parser_attempts": attempts},
        }

    if parse_result.content_list:
        raw_markdown = reconstruct_markdown_from_content_list(parse_result.content_list)
    else:
        raw_markdown = parse_result.markdown_path.read_text(encoding="utf-8", errors="replace")

    used_fallback = parse_result.parser != mineru.name
    warnings = []
    if used_fallback:
        warnings.append({
            "code": "OCR_UNCERTAIN",
            "message": f"{source_id}: MinerU unavailable/failed, used {parse_result.parser} fallback - no structural reconstruction (headings/figures/tables); expect STRUCTURE_LOSS from Step05.",
            "retryable": False, "source_id": source_id,
        })

    return {
        "output": {
            "source_id": source_id, "used_pdf_parser": True, "parser_name": parse_result.parser,
            "raw_markdown": raw_markdown, "content_list": parse_result.content_list,
            "page_count": _page_count(parse_result.content_list),
        },
        "status": "succeeded_with_warnings" if warnings else "succeeded", "errors": warnings,
        "provenance": {"step_version": VERSION, "source_ids": [source_id], "parser": parse_result.parser, "parser_attempts": attempts},
    }
