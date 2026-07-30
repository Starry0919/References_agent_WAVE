"""Project-context relevance tagging for the local DDR corpus (老师 §Phase5:
"Knowledge Layer 是否根据 Current Project Context 筛选 Relevant DDR ... 而
不是静态展示数据库").

Deliberately a *tag*, not a hard filter: a DDR from an unrelated host/
product can still hold a transferable rule (老师 §四.5 "规则库把一类产物
的规则用到另一类问题上"), so hiding it outright would contradict the
design doc's own cross-product-transfer thesis. Callers sort
relevant-first and let the caller mark it, keeping "全量浏览" (browse
everything) and "项目过滤" (context-aware ranking) both true at once
instead of trading one off for the other.
"""
from __future__ import annotations

from typing import Any


def _norm(s: str | None) -> str:
    return (s or "").strip().lower()


def product_search_variants(project_product: str | None) -> list[str]:
    """`project_product` plus its LLM-translated English/Simplified-Chinese
    counterpart (`harness.translation.service.translate_batch`), so a
    project goal entered in either language still substring-matches a DDR
    corpus entry recorded in the other - this repo's curated DDRs record
    `target_product` in English (e.g. "L-tryptophan", "isoprene") regardless
    of what language a project's own goal was typed in. Translation is
    permanently cached per source string, so this only pays the LLM round
    trip once per distinct product string ever, not once per request; a
    provider failure falls back to the original text unchanged (same
    "honest fallback" contract `translate_batch` itself documents), so
    relevance tagging degrades to same-language matching, never breaks.
    """
    text = (project_product or "").strip()
    if not text:
        return []
    from harness.translation.service import translate_batch

    variants = {text, translate_batch([text], target_locale="en-US")[0], translate_batch([text], target_locale="zh-CN")[0]}
    return list(variants)


def ddr_relevance(
    raw_metadata: dict[str, Any],
    *,
    project_host: str | None,
    project_product: str | None,
    project_product_variants: list[str] | None = None,
) -> dict[str, Any]:
    """Returns `{"relevant": bool, "host_match": bool, "product_match": bool}`
    for one DDR record's `metadata` block against a project's host/product.
    `project_product_variants` (see `product_search_variants`) lets a caller
    precompute the zh/en translation once per request and reuse it across
    every DDR in the corpus, instead of this function re-translating per
    record; omitting it falls back to matching on `project_product` alone.
    """
    meta = raw_metadata.get("metadata", {}) if "metadata" in raw_metadata else raw_metadata
    ddr_organism = _norm(meta.get("organism"))
    ddr_host = _norm(meta.get("host"))
    ddr_product = _norm(meta.get("target_product"))

    host_match = False
    if project_host:
        ph = _norm(project_host)
        host_match = bool(ph) and (ph in ddr_organism or ddr_organism in ph or ph in ddr_host or ddr_host in ph)

    product_match = False
    if project_product and ddr_product:
        # `ddr_product in pp` is trivially True when `ddr_product` is ""
        # (Python: `"" in anything`) - a DDR whose metadata simply lacks
        # target_product (e.g. DDR-006/007/008) must not thereby match
        # every project's product, or "relevant" carries no signal at all
        # for those records - guarded above by requiring `ddr_product` too.
        for variant in (project_product_variants or [project_product]):
            pp = _norm(variant)
            if pp and (pp in ddr_product or ddr_product in pp):
                product_match = True
                break

    # Host alone does not drive `relevant`: this repo's whole corpus is
    # scoped to E. coli K-12 (design doc §一), so every DDR host-matches
    # every project - if host_match alone counted, "relevant" would be
    # true for the entire corpus and the tag would carry no signal.
    # Product overlap is the discriminating signal when a project product
    # is known; host match only stands in when there's nothing to compare
    # products against (either side missing the field).
    if project_product:
        relevant = product_match
    else:
        relevant = host_match

    return {"relevant": relevant, "host_match": host_match, "product_match": product_match}
