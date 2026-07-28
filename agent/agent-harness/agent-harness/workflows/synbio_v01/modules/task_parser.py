"""Module 0 - Task Understanding: natural language -> structured design request.

Per the V0.1 revision spec, E. coli K-12 is the only supported chassis: the
host is a fixed constant, injected here rather than parsed from the
request. The module extracts target product, substrate, engineering
objective, and constraints via lightweight bilingual (English/Chinese)
keyword matching - a stand-in for a future LLM-backed extractor. The
contract, `parse(request: str) -> dict`, is what that future extractor
must keep honoring.
"""
from __future__ import annotations

import re
from typing import Any

FIXED_HOST = "E. coli K-12"

# canonical name -> surface forms (English + Chinese) to match in free text.
_KNOWN_PRODUCTS: dict[str, list[str]] = {
    "tryptophan": ["tryptophan", "色氨酸"],
    "lysine": ["lysine", "赖氨酸"],
    "threonine": ["threonine", "苏氨酸"],
    "1,3-propanediol": ["1,3-propanediol", "1,3-丙二醇"],
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

_KNOWN_CONSTRAINTS: dict[str, list[str]] = {
    "minimal media": ["minimal media", "基本培养基", "基础培养基"],
    "aerobic conditions": ["aerobic", "有氧"],
    "anaerobic conditions": ["anaerobic", "厌氧"],
    "plasmid-free": ["plasmid-free", "无质粒", "不使用质粒"],
    "no antibiotic markers": ["no antibiotic", "无抗性标记", "无抗生素"],
}

_OBJECTIVE_PATTERNS = [
    (re.compile(r"improv|increase|enhance|boost|higher|提高|增加|提升|增强", re.I), "increase production"),
    (re.compile(r"reduce|decrease|lower|降低|减少|下降", re.I), "decrease production"),
    (re.compile(r"novel|new pathway|introduce|新通路|引入", re.I), "introduce novel pathway"),
]


def _find_keyword(text: str, vocab: dict[str, list[str]]) -> str:
    lowered = text.lower()
    for canonical, forms in vocab.items():
        for form in forms:
            if form.lower() in lowered:
                return canonical
    return ""


def _find_objective(text: str) -> str:
    for pattern, label in _OBJECTIVE_PATTERNS:
        if pattern.search(text):
            return label
    return "increase production"


def _find_constraints(text: str) -> list[str]:
    lowered = text.lower()
    found: list[str] = []
    for canonical, forms in _KNOWN_CONSTRAINTS.items():
        if any(form.lower() in lowered for form in forms):
            found.append(canonical)
    return found


def parse(request: str) -> dict[str, Any]:
    """Extract {host, product, substrate, objective, constraints} from free text.

    `host` is always the fixed chassis - never inferred from the request.
    """
    return {
        "host": FIXED_HOST,
        "product": _find_keyword(request, _KNOWN_PRODUCTS) or "unknown",
        "substrate": _find_keyword(request, _KNOWN_SUBSTRATES) or "glucose",
        "objective": _find_objective(request),
        "constraints": _find_constraints(request),
    }
