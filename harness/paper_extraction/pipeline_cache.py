"""Content-addressed caching for skill04/05/06 outputs, shared across every
project and run - the same paper's PDF only needs to be downloaded, parsed
and cleaned once, no matter which project, DOI, or search query it later
turns up under again.

`opus_extractor.py` already does this for skill07 (the one LLM-billed,
by-far-slowest step); this closes the same gap for the deterministic
parsing/cleaning steps upstream of it, which still cost real wall-clock
time (parsing alone commonly runs 30-90s per paper; skill05 in particular
sometimes calls out to MinerU) - reprocessing the same PDF from scratch
every time it recurs across projects was pure waste.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from . import _VENDOR_DIR

CACHE_ROOT = _VENDOR_DIR / "paper_experimental_design_extraction" / "storage" / "pipeline_cache"
_SKILLS_ROOT = _VENDOR_DIR / "skills"

# Results that still carry every downstream file they reference (see
# `_referenced_paths_exist`) are safe to reuse; anything else is treated as
# a cache miss so a manually-cleared artifact directory can never surface a
# result pointing at files that no longer exist.
_CACHEABLE_STATUSES = {"succeeded", "succeeded_with_warnings"}


def _write_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.stem, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _referenced_paths_exist(value: Any) -> bool:
    """Walks a result dict looking for any `*_path` string field (the
    vendored skills' own convention for markdown/JSON artifact locations,
    e.g. `markdown_path`, `clean_json_path`) and confirms it still points at
    a real file - a cached result is only reusable if everything it points
    to is still there."""
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str) and key.endswith("_path") and isinstance(item, str):
                if not Path(item).is_file():
                    return False
            if not _referenced_paths_exist(item):
                return False
    elif isinstance(value, list):
        for item in value:
            if not _referenced_paths_exist(item):
                return False
    return True


def _load_real_executor(skill_name: str) -> tuple[Callable[[dict[str, Any]], dict[str, Any]], str]:
    """Imports the real vendored skill the same way `SkillRegistry.execute`
    does (`skills/<name>/skill.py`'s module-level `execute`), rather than
    re-implementing any of its logic here, plus its own `SKILL_VERSION`
    constant so a cache key never drifts out of sync with the skill's
    actual version by being hand-copied into a second place."""
    if str(_SKILLS_ROOT) not in sys.path:
        sys.path.insert(0, str(_SKILLS_ROOT))
    execute = importlib.import_module(f"{skill_name}.skill").execute
    version = getattr(importlib.import_module(f"{skill_name}.schema"), "SKILL_VERSION", "0")
    return execute, version


def make_cached_executor(
    skill_name: str,
    key_fn: Callable[[dict[str, Any]], str],
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Wraps `skills/<skill_name>/skill.py`'s real `execute()` with a shared
    cache keyed by `key_fn(request)` + the skill's own `SKILL_VERSION`
    (bumping it on a real logic change invalidates stale entries
    automatically, same pattern as opus_extractor.py's skill07 cache). Only
    a successful (or warned-but-usable) result is ever cached; a failure is
    always re-attempted next time."""
    cache_dir = CACHE_ROOT / skill_name
    real_execute, skill_version = _load_real_executor(skill_name)

    def run(request: dict[str, Any]) -> dict[str, Any]:
        try:
            digest = hashlib.sha256(f"{key_fn(request)}\0{skill_version}".encode("utf-8")).hexdigest()
        except Exception:
            return real_execute(request)
        cache_path = cache_dir / f"{digest}.json"
        if cache_path.is_file():
            try:
                cached = json.loads(cache_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                cached = None
            if isinstance(cached, dict) and _referenced_paths_exist(cached):
                cached.setdefault("provenance", {})["cache"] = {
                    "hit": True, "path": str(cache_path), "key_type": "content_sha256+skill_version",
                }
                return cached
        result = real_execute(request)
        if result.get("status") in _CACHEABLE_STATUSES:
            try:
                _write_atomic(cache_path, result)
            except OSError:
                pass
        return result

    return run
