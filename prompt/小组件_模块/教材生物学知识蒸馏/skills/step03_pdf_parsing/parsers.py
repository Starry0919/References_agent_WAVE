"""PDF -> Markdown parsers for Step03, mirroring
论文实验设计抽取/skills/skill05_pdf_parser/parsers/ (MinerUParser +
PyMuPdfParser fallback, same ParseResult/ParserUnavailable/ParseFailure
contract) - proportionately scoped down to one file since this module
doesn't need that skill's separate figure/table/citation reconstruction
submodules: Step05 (document_parsing) already parses `#` headings,
`[[page:N]]` markers and figure/table caption lines out of Markdown, so
this module only needs to get PDF content into that shape, not re-implement
structure extraction a second time.

MinerU is invoked as a subprocess against a hard-coded out-of-repo install
(same constraint as the paper-extraction module's MinerUParser) - it is not
bundled and cannot be exercised in a sandboxed test environment. Every
change here should keep working when MinerU is entirely absent, falling
back to PyMuPDF and then to a clear, auditable failure rather than an
empty/successful-looking result.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ParserUnavailable(Exception):
    pass


class ParseFailure(Exception):
    pass


@dataclass
class ParseResult:
    parser: str
    parser_version: str
    mode: str
    markdown_path: Path
    content_list: list = field(default_factory=list)
    command: list = field(default_factory=list)


class MinerUParser:
    """Subprocess wrapper around a locally-installed MinerU CLI. Same
    hard-coded root as paper_experimental_design_extraction's MinerUParser -
    intentionally not portable; MinerU model weights are large and
    environment-specific, so pointing at a fixed local install is the same
    tradeoff the sibling module already made."""

    name = "MinerU"
    version = "3.4.4"

    def __init__(self, mineru_root=Path(r"D:\MinerU")):
        self.root = Path(mineru_root)
        self.executable = self.root / ".venv" / "Scripts" / "mineru.exe"

    def parse(self, pdf_path: Path, output_root: Path, mode: str = "pipeline", timeout_seconds: int = 1800) -> ParseResult:
        if not self.executable.is_file():
            raise ParserUnavailable(f"MinerU executable not found: {self.executable}")
        output_root.mkdir(parents=True, exist_ok=True)
        backend = "hybrid-engine" if mode == "hybrid" else "pipeline"
        command = [str(self.executable), "-p", str(pdf_path), "-o", str(output_root), "-b", backend]
        env = os.environ.copy()
        env.update({
            "MINERU_MODEL_SOURCE": "local",
            "MODELSCOPE_CACHE": str(self.root / "models" / "modelscope"),
            "HF_HOME": str(self.root / "models" / "huggingface"),
            "TORCH_HOME": str(self.root / "models" / "torch"),
            "TEMP": str(self.root / "cache" / "temp"),
            "TMP": str(self.root / "cache" / "temp"),
        })
        completed = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout_seconds, env=env, check=False,
        )
        if completed.returncode != 0:
            raise ParseFailure(f"MinerU exit {completed.returncode}: {completed.stderr[-1000:]}")
        markdown_files = sorted(output_root.rglob(f"{pdf_path.stem}.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not markdown_files:
            raise ParseFailure("MinerU produced no Markdown output")
        markdown_path = markdown_files[0]
        content_list_candidates = list(markdown_path.parent.glob("*_content_list.json"))
        content_list = []
        if content_list_candidates:
            try:
                content_list = json.loads(content_list_candidates[0].read_text(encoding="utf-8", errors="replace"))
            except (json.JSONDecodeError, OSError):
                content_list = []
        return ParseResult(parser=self.name, parser_version=self.version, mode=mode, markdown_path=markdown_path, content_list=content_list, command=command)


class PyMuPdfParser:
    """Plain per-page text fallback when MinerU is unavailable or fails.
    No structure recovery (no headings/figures/tables) - Step05 will fall
    back to treating the source as one flat section (STRUCTURE_LOSS
    warning), which is the honest degraded outcome, not a silently
    complete-looking one."""

    name = "PyMuPDF"
    version = "runtime"

    def parse(self, pdf_path: Path, output_root: Path, mode: str = "fallback", timeout_seconds: int = 300) -> ParseResult:
        try:
            import fitz
        except ImportError as exc:
            raise ParserUnavailable("PyMuPDF is not installed") from exc
        output_root.mkdir(parents=True, exist_ok=True)
        document = fitz.open(str(pdf_path))
        pages = []
        for index, page in enumerate(document):
            pages.append(f"[[page:{index + 1}]]\n\n{page.get_text('text')}")
        markdown_path = output_root / f"{pdf_path.stem}.md"
        markdown_path.write_text("\n\n".join(pages), encoding="utf-8")
        return ParseResult(parser=self.name, parser_version=getattr(fitz, "VersionBind", self.version), mode="fallback", markdown_path=markdown_path, content_list=[], command=["pymupdf", str(pdf_path)])


_HEADING_TYPE_MARKERS = {"title"}


def reconstruct_markdown_from_content_list(content_list: list[dict[str, Any]]) -> str:
    """Rebuild Markdown directly from MinerU's `*_content_list.json` instead
    of trusting MinerU's own `.md` heading detection, so the output matches
    exactly what Step05's parser already understands: `#`-headings,
    `[[page:N]]` page markers, and `Figure`/`Table` caption lines. Unknown
    `type` values degrade to plain paragraph text rather than being
    dropped, since content_list is deliberately treated as a v2-shaped,
    forward-compatible export.
    """
    lines: list[str] = []
    current_page = None
    for entry in content_list:
        if not isinstance(entry, dict):
            continue
        page_idx = entry.get("page_idx")
        if page_idx is not None and page_idx != current_page:
            current_page = page_idx
            lines.append(f"[[page:{int(page_idx) + 1}]]")
        entry_type = entry.get("type", "text")
        text_level = entry.get("text_level")
        if entry_type in _HEADING_TYPE_MARKERS or (entry_type == "text" and text_level):
            level = max(1, min(int(text_level or 1), 6))
            heading_text = (entry.get("text") or "").strip()
            if heading_text:
                lines.append(f"{'#' * level} {heading_text}")
        elif entry_type == "text":
            text = (entry.get("text") or "").strip()
            if text:
                lines.append(text)
        elif entry_type in {"image", "figure"}:
            caption = " ".join(entry.get("image_caption") or []) or Path(entry.get("img_path", "figure")).stem
            lines.append(f"Figure: {caption}".strip())
        elif entry_type == "table":
            caption = " ".join(entry.get("table_caption") or []) or "table"
            lines.append(f"Table: {caption}".strip())
            body = entry.get("table_body")
            if body:
                lines.append(body)
        lines.append("")
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"
