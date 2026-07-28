from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .parser_interface import ParseFailure, ParseResult, ParserUnavailable


class MinerUParser:
    name = "MinerU"
    version = "3.4.4"

    def __init__(self, mineru_root=Path(r"D:\MinerU")):
        self.root = Path(mineru_root)
        self.executable = self.root / ".venv" / "Scripts" / "mineru.exe"

    def parse(self, pdf_path: Path, output_root: Path, mode="pipeline", timeout_seconds=1800):
        if not self.executable.is_file():
            raise ParserUnavailable(f"MinerU executable not found: {self.executable}")
        output_root.mkdir(parents=True, exist_ok=True)
        backend = "hybrid-engine" if mode == "hybrid" else "pipeline"
        command = [str(self.executable), "-p", str(pdf_path), "-o", str(output_root), "-b", backend]
        if mode == "hybrid":
            command.extend(["--effort", "medium"])
        env = os.environ.copy()
        env.update({
            "MINERU_MODEL_SOURCE": "local",
            "MODELSCOPE_CACHE": str(self.root / "models" / "modelscope"),
            "HF_HOME": str(self.root / "models" / "huggingface"),
            "TORCH_HOME": str(self.root / "models" / "torch"),
            "TEMP": str(self.root / "cache" / "temp"),
            "TMP": str(self.root / "cache" / "temp")
        })
        completed = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout_seconds, env=env, check=False
        )
        if completed.returncode != 0:
            raise ParseFailure(f"MinerU exit {completed.returncode}: {completed.stderr[-1000:]}")
        markdown_files = sorted(output_root.rglob(f"{pdf_path.stem}.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not markdown_files:
            markdown_files = sorted(output_root.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not markdown_files or not markdown_files[0].read_text(encoding="utf-8", errors="replace").strip():
            raise ParseFailure("MinerU produced no non-empty Markdown")
        markdown = markdown_files[0]
        content_candidates = list(markdown.parent.glob("*_content_list.json"))
        content_list = content_candidates[0] if content_candidates else None
        files = [p for p in markdown.parent.rglob("*") if p.is_file()]
        return ParseResult(
            parser=self.name, parser_version=self.version, mode=mode,
            markdown_path=markdown, content_list_path=content_list,
            output_files=files, command=command,
            stdout_tail=(completed.stdout + completed.stderr)[-2000:]
        )

