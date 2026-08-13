"""Deterministic requirement parsing and retrieval-strategy generation.

This module intentionally performs no literature retrieval and makes no LLM
calls. Terms are emitted only when they occur in the user input or are expanded
from an explicitly matched alias.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

try:
    from .logger import JsonlSkillLogger
    from .schema import SKILL_ID, SKILL_VERSION, sha256_json
    from .validator import validate_input, validate_output
except ImportError:
    from logger import JsonlSkillLogger
    from schema import SKILL_ID, SKILL_VERSION, sha256_json
    from validator import validate_input, validate_output


STATUS_VALUES = {
    "succeeded",
    "succeeded_with_warnings",
    "needs_review",
    "retryable_failure",
    "terminal_failure",
    "cancelled",
}

_ORGANISM_ALIASES: Sequence[Tuple[re.Pattern[str], str, Sequence[str]]] = (
    (re.compile(r"大肠杆菌", re.I), "Escherichia coli", ("E. coli", "Escherichia coli", "大肠杆菌")),
    (re.compile(r"(?:e\.?\s*coli|escherichia\s+coli)\b|大肠杆菌", re.I), "Escherichia coli", ("E. coli", "Escherichia coli")),
    (re.compile(r"saccharomyces\s+cerevisiae\b|酿酒酵母", re.I), "Saccharomyces cerevisiae", ("S. cerevisiae", "Saccharomyces cerevisiae")),
    (re.compile(r"bacillus\s+subtilis\b|枯草芽孢杆菌", re.I), "Bacillus subtilis", ("B. subtilis", "Bacillus subtilis")),
    (re.compile(r"pseudomonas\s+putida\b|恶臭假单胞菌", re.I), "Pseudomonas putida", ("P. putida", "Pseudomonas putida")),
)

_STRAIN_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"(?:E\.?\s*coli\s*)?(K[-\s]?12|MG1655|BW25113|DH5α|BL21(?:\(DE3\))?|W3110)(?![A-Za-z0-9])", re.I),
    re.compile(r"(?:S\.?\s*cerevisiae\s*)?(BY4741|CEN\.PK(?:2-1C)?)(?![A-Za-z0-9])", re.I),
)

_PHENOTYPE_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"(?:提高|提升|增加|增强|改善|优化)[^，。；;,.]{0,36}(?:产量|产率|滴度|生产强度)"),
    re.compile(r"(?:提高|提升|增加|增强|改善|降低|减少|耐受|抗性)[^，。；;,.]{0,24}(?:产量|产率|生产强度|耐受性|抗性|生长|活性|表达|积累)"),
    re.compile(r"\b(?:increased?|improved?|enhanced?|reduced?)\s+[\w -]{1,40}(?:yield|titer|productivity|tolerance|growth|activity|expression)\b", re.I),
)

_OBJECTIVE_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"(?:提高|提升|增加|增强|改善|优化)[^，。；;,.]{1,60}(?:产量|产率|滴度|生产强度)"),
    re.compile(r"(?:通过|利用|采用|研究|寻找|检索|筛选|开发|构建)[^，。；;,.]{2,60}(?:提高|提升|增加|增强|改善|降低|减少|优化)[^，。；;,.]{0,36}"),
    re.compile(r"\b(?:engineer|engineering|optimi[sz]e|increase|improve|enhance|reduce)\b[\w\s,()-]{2,80}", re.I),
)

_METHOD_TERMS: Mapping[str, Sequence[str]] = {
    "代谢工程": ("metabolic engineering",),
    "基因编辑": ("gene editing", "CRISPR"),
    "CRISPR": ("CRISPR", "gene editing"),
    "适应性实验室进化": ("adaptive laboratory evolution", "ALE"),
    "合成生物学": ("synthetic biology",),
    "过表达": ("overexpression",),
    "敲除": ("knockout", "gene deletion"),
    "发酵": ("fermentation",),
}

_GENERIC_STOPWORDS = {
    "论文", "文献", "研究", "实验", "方法", "相关", "检索", "寻找", "分析",
    "paper", "papers", "study", "studies", "research", "method", "methods",
    "find", "search", "literature", "experimental",
}


def _unique(values: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        cleaned = value.strip()
        key = cleaned.casefold()
        if cleaned and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result


def _field(value: Any, confidence: float, status: Optional[str] = None) -> Dict[str, Any]:
    known = value is not None and value != [] and value != ""
    field_status = status or ("reported" if known else "unknown")
    return {
        "value": value if known else None if not isinstance(value, list) else [],
        "source": "user_input",
        "confidence": round(confidence if known else 1.0, 3),
        "status": field_status,
    }


def _first_match(patterns: Sequence[re.Pattern[str]], text: str) -> Optional[str]:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return re.sub(r"\s+", " ", match.group(0)).strip(" ，。；;,.")
    return None


def _extract_list_after_labels(text: str, labels: Sequence[str]) -> List[str]:
    label_group = "|".join(re.escape(label) for label in labels)
    match = re.search(
        rf"(?:{label_group})\s*[:：]\s*([^。；;\n]+)",
        text,
        re.I,
    )
    if not match:
        return []
    return _unique(re.split(r"[,，、]\s*|\s+(?:and|or)\s+", match.group(1)))


def _quote(term: str) -> str:
    escaped = term.replace('"', '\\"')
    return f'"{escaped}"' if re.search(r"[\s-]", term) else escaped


def _or_group(terms: Sequence[str]) -> str:
    values = _unique(terms)
    return "(" + " OR ".join(_quote(term) for term in values) + ")"


@dataclass(frozen=True)
class ParsedRequirement:
    research_intent: Dict[str, Any]
    field_metadata: Dict[str, Dict[str, Any]]
    retrieval_strategy: Dict[str, Any]
    review_reasons: List[str]
    warnings: List[Dict[str, str]]


class RequirementParser:
    """Parse a user request without inferring absent scientific parameters."""

    def __init__(
        self,
        logger: Optional[Callable[[Mapping[str, Any]], None]] = None,
        current_year: Optional[int] = None,
    ) -> None:
        self._logger = logger if logger is not None else JsonlSkillLogger()
        self._current_year = current_year or datetime.now(timezone.utc).year

    def execute(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        started = time.perf_counter()
        input_hash = sha256_json(request)
        try:
            error = validate_input(request)
            if error:
                result = self._error_result(error, input_hash)
            else:
                parsed = self._parse(str(request["user_request"]), request.get("constraints", {}))
                status = "needs_review" if parsed.review_reasons else (
                    "succeeded_with_warnings" if parsed.warnings else "succeeded"
                )
                output = {
                    "research_intent": parsed.research_intent,
                    "field_metadata": parsed.field_metadata,
                    "retrieval_strategy": parsed.retrieval_strategy,
                }
                checks = validate_output(output)
                if not all(check["passed"] for check in checks):
                    result = self._error_result(
                        {
                            "code": "EDX-VAL-002",
                            "category": "validation",
                            "message": "Skill01 output failed self-check.",
                            "retryable": False,
                            "severity": "blocking",
                            "context": {"failed_checks": [c["name"] for c in checks if not c["passed"]]},
                            "suggested_action": "Inspect parser output and contract.",
                        },
                        input_hash,
                    )
                else:
                    result = {
                        "status": status,
                        "output": output,
                        "artifacts": [],
                        "self_check": {"passed": True, "checks": checks, "score": 1.0},
                        "warnings": parsed.warnings,
                        "errors": [],
                        "metrics": {},
                        "provenance": {
                            "skill_id": SKILL_ID,
                            "skill_version": SKILL_VERSION,
                            "input_hash": input_hash,
                            "output_hash": sha256_json(output),
                            "method": "deterministic_rules",
                        },
                        "review_requests": [
                            {"reason": reason, "field_path": "research_intent"}
                            for reason in parsed.review_reasons
                        ],
                    }
        except Exception as exc:  # defensive boundary for the workflow runtime
            result = self._error_result(
                {
                    "code": "EDX-SYS-001",
                    "category": "system",
                    "message": "Unexpected Skill01 execution failure.",
                    "retryable": True,
                    "severity": "error",
                    "context": {"exception_type": type(exc).__name__},
                    "suggested_action": "Retry with the same input hash; inspect protected logs.",
                },
                input_hash,
            )

        result["metrics"]["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        self._emit_log(result, input_hash)
        return result

    def _parse(self, raw_text: str, constraints: Mapping[str, Any]) -> ParsedRequirement:
        text = re.sub(r"\s+", " ", raw_text).strip()
        organism = None
        organism_search_terms: List[str] = []
        for pattern, canonical, aliases in _ORGANISM_ALIASES:
            if pattern.search(text):
                organism = canonical
                organism_search_terms = list(aliases)
                break

        strain = _first_match(_STRAIN_PATTERNS, text)
        if strain:
            strain = re.sub(r"^(?:E\.?\s*coli|S\.?\s*cerevisiae)\s*", "", strain, flags=re.I)
            strain = "K-12" if re.fullmatch(r"K[\s-]?12", strain, re.I) else strain

        phenotype = _first_match(_PHENOTYPE_PATTERNS, text)
        objective = _first_match(_OBJECTIVE_PATTERNS, text)
        inclusion = _extract_list_after_labels(text, ("纳入", "包含", "inclusion", "include"))
        exclusion = _extract_list_after_labels(text, ("排除", "不包含", "exclusion", "exclude"))

        explicit_keywords = _extract_list_after_labels(text, ("关键词", "关键字", "keywords"))
        method_terms: List[str] = []
        method_expansions: List[str] = []
        for source_term, expansions in _METHOD_TERMS.items():
            if re.search(re.escape(source_term), text, re.I):
                method_terms.append(source_term)
                method_expansions.extend(expansions)

        alphanumeric_terms = re.findall(r"\b[A-Za-z][A-Za-z0-9αβ().-]{2,}\b", text)
        biochemical_targets = re.findall(
            r"(?<![A-Za-z0-9])(?:L-|D-)?[A-Za-z][A-Za-z0-9-]{2,}(?![A-Za-z0-9])",
            text,
            re.I,
        )
        biochemical_targets = [
            value for value in biochemical_targets
            if not strain or value.casefold() != strain.casefold()
        ]
        chinese_terms = re.findall(r"[\u4e00-\u9fff]{2,12}", text)
        candidate_keywords = explicit_keywords + method_terms + biochemical_targets + alphanumeric_terms
        candidate_keywords += [
            term for term in chinese_terms
            if term.casefold() not in _GENERIC_STOPWORDS
            and not any(stop in term for stop in ("论文", "文献", "检索", "寻找", "研究"))
            and not any(fragment in term for fragment in ("我用的是", "然后要", "菌种", "的产量"))
        ]
        keywords = _unique(candidate_keywords)[:20]

        time_range, time_status = self._extract_time_range(text)
        quality_terms = []
        if re.search(r"高影响力|高影响因子|high[- ]impact", text, re.I):
            quality_terms.append("high_impact")
        if re.search(r"高被引|引用量|highly cited|citation", text, re.I):
            quality_terms.append("citation_relevance")
        if re.search(r"实验验证|experimental validation|experimental evidence", text, re.I):
            quality_terms.append("experimental_evidence")

        engineering_objective = method_terms[0] if method_terms else objective

        research_intent = {
            "organism": organism,
            "strain": strain,
            "phenotype": phenotype,
            "engineering_objective": engineering_objective,
            "keywords": keywords,
            "inclusion_criteria": inclusion,
            "exclusion_criteria": exclusion,
        }
        field_metadata = {
            name: _field(value, 0.98 if name in {"organism", "strain"} else 0.9)
            for name, value in research_intent.items()
        }
        ambiguity = not organism and not objective and not phenotype
        for name in ("organism", "strain", "phenotype", "engineering_objective"):
            if ambiguity and field_metadata[name]["status"] == "unknown":
                field_metadata[name]["status"] = "needs_clarification"

        concept_groups = {
            "organism": _unique(organism_search_terms + ([strain] if strain else [])),
            "phenotype": _unique(biochemical_targets + ([phenotype] if phenotype and not biochemical_targets else [])),
            "engineering": _unique(method_terms + method_expansions),
            "keywords": keywords,
        }
        active_groups = [values for values in concept_groups.values() if values]
        boolean_query = " AND ".join(_or_group(values) for values in active_groups)
        queries = []
        if boolean_query:
            queries.append({"name": "broad", "query": boolean_query, "syntax": "boolean"})
            organism_group = concept_groups["organism"]
            target_group = concept_groups["phenotype"]
            if organism_group and target_group:
                queries.append({
                    "name": "organism_target",
                    "query": _or_group(organism_group) + " AND " + _or_group(target_group),
                    "syntax": "boolean",
                })
                queries.append({
                    "name": "production_focused",
                    "query": _or_group(organism_group) + " AND " + _or_group(target_group)
                    + " AND (production OR yield OR titer OR biosynthesis)",
                    "syntax": "boolean",
                })
            if inclusion:
                query = boolean_query + " AND " + _or_group(inclusion)
                if exclusion:
                    query += " NOT " + _or_group(exclusion)
                queries.append({"name": "criteria_aware", "query": query, "syntax": "boolean"})
        queries = queries[:4]

        recommended_sources = list(constraints.get(
            "sources", ["PubMed", "Crossref", "Europe PMC"]
        ))
        review_reasons = []
        if ambiguity:
            review_reasons.append("insufficient_scientific_scope")
        conflicts = sorted(set(map(str.casefold, inclusion)) & set(map(str.casefold, exclusion)))
        if conflicts:
            review_reasons.append("conflicting_inclusion_exclusion_criteria")

        warnings = []
        if not boolean_query:
            warnings.append({
                "code": "INSUFFICIENT_SEARCH_TERMS",
                "message": "No reliable executable search terms could be extracted.",
            })
        elif not organism:
            warnings.append({
                "code": "ORGANISM_UNKNOWN",
                "message": "Organism was not reported by the user and remains unknown.",
            })

        search_specification = {
            "research_objective": _field(objective, 0.9),
            "organism": _field(
                {"organism_name": organism, "taxonomy_level": "species"} if organism else None,
                0.98,
                "needs_clarification" if ambiguity and not organism else None,
            ),
            "strain": _field(
                strain,
                0.98,
                "needs_clarification" if ambiguity and not strain else None,
            ),
            "engineering_objective": _field(engineering_objective, 0.9),
            "target_phenotype": _field(phenotype, 0.9),
            "engineering_method": _field(method_terms, 0.95),
            "search_keywords": _field({
                "primary": _unique(organism_search_terms + ([strain] if strain else []) + ([phenotype] if phenotype else [])),
                "secondary": method_terms,
                "synonyms": _unique(method_expansions),
            }, 0.9),
            "inclusion_criteria": _field(inclusion, 0.95),
            "exclusion_criteria": _field(exclusion, 0.95),
            "time_range": _field(time_range, 0.98, time_status),
            "literature_quality_requirement": _field(quality_terms, 0.95),
        }

        return ParsedRequirement(
            research_intent=research_intent,
            field_metadata=field_metadata,
            retrieval_strategy={
                "concept_groups": concept_groups,
                "queries": queries,
                "recommended_sources": recommended_sources,
                "constraints": dict(constraints),
                "search_specification": search_specification,
            },
            review_reasons=review_reasons,
            warnings=warnings,
        )

    def _extract_time_range(self, text: str) -> Tuple[Dict[str, Any], str]:
        explicit = re.search(r"\b(19|20)\d{2}\s*[-–至到]\s*((?:19|20)\d{2})\b", text)
        if explicit:
            start = int(explicit.group(0)[:4])
            end = int(explicit.group(2))
            return {"mode": "explicit", "start_year": start, "end_year": end}, "reported"
        recent = re.search(r"(?:近|最近)\s*(\d{1,2})\s*年|last\s+(\d{1,2})\s+years?", text, re.I)
        if recent:
            years = int(recent.group(1) or recent.group(2))
            return {
                "mode": "relative",
                "start_year": self._current_year - years + 1,
                "end_year": self._current_year,
                "relative_years": years,
            }, "reported"
        return {"mode": "default_policy", "start_year": None, "end_year": None}, "unknown"

    @staticmethod
    def _error_result(error: Dict[str, Any], input_hash: str) -> Dict[str, Any]:
        return {
            "status": "retryable_failure" if error["retryable"] else "terminal_failure",
            "output": None,
            "artifacts": [],
            "self_check": {"passed": False, "checks": [], "score": 0.0},
            "warnings": [],
            "errors": [error],
            "metrics": {},
            "provenance": {
                "skill_id": SKILL_ID,
                "skill_version": SKILL_VERSION,
                "input_hash": input_hash,
                "output_hash": None,
                "method": "deterministic_rules",
            },
            "review_requests": [],
        }

    def _emit_log(self, result: Mapping[str, Any], input_hash: str) -> None:
        if self._logger is None:
            return
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "INFO" if result["status"] in {"succeeded", "succeeded_with_warnings"} else "WARNING",
            "event_name": "skill.completed",
            "skill_id": SKILL_ID,
            "skill_version": SKILL_VERSION,
            "input_hash": input_hash,
            "output_hash": result["provenance"]["output_hash"],
            "status": result["status"],
            "duration_ms": result["metrics"]["duration_ms"],
            "error_code": result["errors"][0]["code"] if result["errors"] else None,
            "model": None,
            "validation_result": result["self_check"],
            "errors": result["errors"],
            "confidence": result["self_check"]["score"],
        }
        try:
            self._logger(event)
        except Exception:
            # Observability must not change the scientific output or retry semantics.
            return


def execute(
    request: Mapping[str, Any],
    logger: Optional[Callable[[Mapping[str, Any]], None]] = None,
    current_year: Optional[int] = None,
) -> Dict[str, Any]:
    """Workflow-friendly functional entry point."""

    return RequirementParser(logger=logger, current_year=current_year).execute(request)
