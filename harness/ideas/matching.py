"""Idea relevance ranking - NOT idea-to-design auto-linking (`link_idea_to_design`
stays a human-confirmed action, per its own docstring: "honest hand-off
bookkeeping, not a prediction"). This only reorders a project's ideas so the
one most likely to matter surfaces first, cutting a manual search down to a
confirm-click.

Character-bigram overlap, not word tokenization: idea free text and diagnosis
hypothesis statements are equally often Chinese or English (`harness.i18n`
renders hypothesis statements in whichever locale was active at generation
time), and bigrams score both scripts uniformly without a word-segmentation
dependency. Same spirit as `harness.engineering_design.strategy_generator
._match_strategy_classes` - a transparent, inspectable heuristic, never a
hidden ML ranking.
"""
from __future__ import annotations

from harness.ideas.models import ProjectIdea


def _bigrams(text: str) -> set[str]:
    cleaned = "".join(ch for ch in text.lower() if not ch.isspace())
    if len(cleaned) < 2:
        return {cleaned} if cleaned else set()
    return {cleaned[i : i + 2] for i in range(len(cleaned) - 1)}


def relevance_score(idea: ProjectIdea, target_texts: list[str]) -> int:
    idea_grams = _bigrams(idea.free_text)
    if not idea_grams:
        return 0
    target_grams: set[str] = set()
    for text in target_texts:
        target_grams |= _bigrams(text)
    return len(idea_grams & target_grams)


def rank_ideas_by_relevance(ideas: list[ProjectIdea], target_texts: list[str]) -> list[ProjectIdea]:
    """Stable sort - ties keep `ideas`' incoming order (`list_ideas` already
    orders newest-first), so ranking only ever promotes a genuinely
    text-overlapping idea ahead of the default order, never reshuffles ties."""
    if not target_texts:
        return list(ideas)
    return sorted(ideas, key=lambda i: -relevance_score(i, target_texts))
