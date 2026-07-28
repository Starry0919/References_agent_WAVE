"""Integration seam for the Biological Knowledge Distillation module.

The module (13-step pipeline: task contract -> source validation -> document
parsing -> extraction-scope selection -> concept/mechanism extraction ->
engineering-principle distillation -> decision-rule generation -> design-
pattern/validation-strategy/failure-pattern extraction -> evidence-binding
audit -> cross-source fusion -> paper-case linking -> quality governance ->
knowledge-graph/frontend adaptation) is vendored under `vendor/` as three
sibling packages (`biological_knowledge_distillation`, `skills`, `framework`) -
this exact layout is required because
`biological_knowledge_distillation/skills/registry.py` locates the real step
implementations via `Path(__file__).resolve().parents[2] / "skills"`, i.e. it
expects a sibling `skills/` directory two levels above itself. Do not flatten
or rename these three folders relative to each other. (Same constraint as
`harness/paper_extraction/__init__.py` - mirrored on purpose.)

`vendor/` itself is never imported as a package (no `__init__.py`); it is
added to `sys.path` so `biological_knowledge_distillation` resolves as a
top-level package, matching the internal relative imports used throughout the
vendored source.
"""
from __future__ import annotations

import sys
from pathlib import Path

_VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
if str(_VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(_VENDOR_DIR))
