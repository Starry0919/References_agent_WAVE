"""Loader for the shared, curated gene reference used by IdentityGate,
BiologicalRuleGate, and policies.py's risk classifier. See
`knowledge/biological_rules/essential_genes_reference.json`'s own
`_disclaimer` - this is illustrative, not a verified essentiality dataset.
Split out from gates.py so policies.py can use it too without gates.py and
policies.py importing each other.
"""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from harness.config import PROJECT_ROOT

ESSENTIAL_GENES_PATH = PROJECT_ROOT / "knowledge" / "biological_rules" / "essential_genes_reference.json"


@lru_cache(maxsize=1)
def load_gene_registry() -> dict[str, Any]:
    if not ESSENTIAL_GENES_PATH.is_file():
        return {"essential_genes": [], "known_genes": [], "foreign_genes": []}
    return json.loads(ESSENTIAL_GENES_PATH.read_text(encoding="utf-8"))


def essential_genes() -> set[str]:
    return set(load_gene_registry().get("essential_genes", []))


def known_genes() -> set[str]:
    return set(load_gene_registry().get("known_genes", []))


def foreign_genes() -> set[str]:
    return set(load_gene_registry().get("foreign_genes", []))
