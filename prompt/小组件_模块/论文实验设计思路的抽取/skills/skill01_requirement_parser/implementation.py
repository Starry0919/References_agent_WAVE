"""Backward-compatible import path for Skill01."""

try:
    from .skill import RequirementParser, execute
except ImportError:
    from skill import RequirementParser, execute

__all__ = ["RequirementParser", "execute"]
