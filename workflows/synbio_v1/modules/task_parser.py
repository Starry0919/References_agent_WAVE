"""Module 0 - Task Understanding: natural language -> structured design request.

Output schema per the V1 spec (section 12, Module 0):
    {product, host, substrate, goal, engineering_type}

Unlike V0.1's task parser, V1 does not hard-inject the host - E. coli is
the target application's chassis family (spec section 1), but the specific
strain is still read from the request when present, falling back to the
common lab default (E. coli K-12) otherwise. Bilingual (English/Chinese)
keyword matching is a stand-in for a future LLM-backed extractor - see
workflows/synbio_v01/modules/task_parser.py for the same pattern.
"""
from __future__ import annotations

import re
from typing import Any

DEFAULT_HOST = "E. coli K-12"

_KNOWN_PRODUCTS: dict[str, list[str]] = {
    "L-tryptophan": ["l-tryptophan", "tryptophan", "色氨酸"],
    "1,4-butanediol": ["1,4-butanediol", "1,4-bdo", "bdo", "1,4-丁二醇"],
    "isoprene": ["isoprene", "异戊二烯"],
    "lysine": ["lysine", "赖氨酸"],
    "threonine": ["threonine", "苏氨酸"],
    "succinate": ["succinate", "琥珀酸"],
    "ethanol": ["ethanol", "乙醇"],
    "isobutanol": ["isobutanol", "异丁醇"],
    "citric acid": ["citric acid", "柠檬酸"],
}

_KNOWN_SUBSTRATES: dict[str, list[str]] = {
    "glucose": ["glucose", "葡萄糖"],
    "glycerol": ["glycerol", "甘油"],
    "xylose": ["xylose", "木糖"],
    "sucrose": ["sucrose", "蔗糖"],
    "acetate": ["acetate", "乙酸"],
}

_HOST_PATTERNS = [
    (re.compile(r"e\.?\s?coli\s*k-?12", re.I), "E. coli K-12"),
    (re.compile(r"e\.?\s?coli\s*bl21", re.I), "E. coli BL21"),
    (re.compile(r"e\.?\s?coli\s*w3110", re.I), "E. coli W3110"),
    (re.compile(r"e\.?\s?coli", re.I), "E. coli"),
]

_GOAL_PATTERNS = [
    (re.compile(r"improv|increase|enhance|boost|higher|提高|增加|提升|增强", re.I), "increase production"),
    (re.compile(r"reduce|decrease|lower|降低|减少|下降", re.I), "decrease production"),
    (re.compile(r"novel|new pathway|introduce|新通路|引入", re.I), "introduce novel pathway"),
]

_ENGINEERING_TYPE_PATTERNS = [
    (re.compile(r"new pathway|heterologous|de novo|从头|新通路|引入", re.I), "de novo pathway construction"),
]
_DEFAULT_ENGINEERING_TYPE = "rational metabolic engineering"


def _find_keyword(text: str, vocab: dict[str, list[str]]) -> str:
    lowered = text.lower()
    for canonical, forms in vocab.items():
        for form in forms:
            if form.lower() in lowered:
                return canonical
    return ""


def _find_host(text: str) -> str:
    for pattern, label in _HOST_PATTERNS:
        if pattern.search(text):
            return label
    return DEFAULT_HOST


def _find_goal(text: str) -> str:
    for pattern, label in _GOAL_PATTERNS:
        if pattern.search(text):
            return label
    return "increase production"


def _find_engineering_type(text: str) -> str:
    for pattern, label in _ENGINEERING_TYPE_PATTERNS:
        if pattern.search(text):
            return label
    return _DEFAULT_ENGINEERING_TYPE


def parse(request: str) -> dict[str, Any]:
    """Extract {product, host, substrate, goal, engineering_type} from free text."""
    return {
        "product": _find_keyword(request, _KNOWN_PRODUCTS) or "unknown",
        "host": _find_host(request),
        "substrate": _find_keyword(request, _KNOWN_SUBSTRATES) or "glucose",
        "goal": _find_goal(request),
        "engineering_type": _find_engineering_type(request),
    }
