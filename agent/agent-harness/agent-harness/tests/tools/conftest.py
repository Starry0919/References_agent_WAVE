"""Shared pytest fixtures for the tool-execution test suite.

Only injects the project root into `sys.path` (same pattern as
`tests/workflow/conftest.py`) so `harness.*` imports resolve no matter
which directory pytest is invoked from. No network or API keys needed:
these tests register their own throwaway tools.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
