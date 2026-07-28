from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


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
    content_list_path: Path | None = None
    output_files: List[Path] = field(default_factory=list)
    command: List[str] = field(default_factory=list)
    stdout_tail: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

