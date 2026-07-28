"""Integration seam for the Paper Experimental Design Extraction module.

The module (13-skill pipeline: requirement parsing -> literature retrieval ->
citation validation -> PDF acquisition/parsing -> markdown cleaning ->
experiment extraction -> evidence binding -> quality evaluation -> K12
transfer analysis -> engineering proposal -> QC/human review -> frontend
adaptation) is vendored under `vendor/` as three sibling packages
(`paper_experimental_design_extraction`, `skills`, `framework`) - this exact
layout is required because `paper_experimental_design_extraction/skills/
registry.py` locates the real skill implementations via
`Path(__file__).resolve().parents[2] / "skills"`, i.e. it expects a sibling
`skills/` directory two levels above itself. Do not flatten or rename these
three folders relative to each other.

`vendor/` itself is never imported as a package (no `__init__.py`); it is
added to `sys.path` so `paper_experimental_design_extraction` resolves as a
top-level package, matching the internal relative imports used throughout
the vendored source.
"""
from __future__ import annotations

import sys
from pathlib import Path

_VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
if str(_VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(_VENDOR_DIR))
