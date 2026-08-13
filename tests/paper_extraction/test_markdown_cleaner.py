from __future__ import annotations

import sys
from pathlib import Path

import harness.paper_extraction

_SKILLS_ROOT = Path(harness.paper_extraction.__file__).resolve().parent / "vendor" / "skills"
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

from skill06_markdown_cleaner.cleaners.citation_preserver import extract_citations


def test_author_year_citation_ignores_equivalent_line_break_spacing():
    original = "Prior work (Kerek et al., \n2023) supports this conclusion."
    normalized = "Prior work (Kerek et al.,\n2023) supports this conclusion."

    assert extract_citations(original) == extract_citations(normalized)
