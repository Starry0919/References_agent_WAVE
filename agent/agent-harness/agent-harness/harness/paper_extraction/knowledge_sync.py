"""Best-effort git sync for ``knowledge/ddr_database/`` across machines.

The DDR knowledge base is a directory of git-tracked JSON files (not a
database), so "sync across computers" just means committing+pushing after a
save and pulling before a read - both via the repo's own git remote. Every
git call here is best-effort: network/credential/conflict failures are
logged and swallowed, never raised, because a sync hiccup must not break
paper extraction or knowledge-base reads.
"""
from __future__ import annotations

import logging
import os
import subprocess
import threading
import time
from pathlib import Path

from harness.config import PROJECT_ROOT, get_settings

logger = logging.getLogger(__name__)

_GIT_TIMEOUT_S = 30
_PULL_MIN_INTERVAL_S = 10.0
_last_pull_ts = 0.0
_pull_lock = threading.Lock()


def _enabled() -> bool:
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    return get_settings().PAPER_EXTRACTION_GIT_SYNC


def _run_git(*args: str) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            ["git", *args], cwd=PROJECT_ROOT, capture_output=True, text=True,
            timeout=_GIT_TIMEOUT_S, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        logger.warning("knowledge_sync: git %s failed to run: %s", args[0], exc)
        return None


def _sync_after_save(paths: list[Path]) -> None:
    if not paths:
        return
    # Runs on a background daemon thread (see sync_after_save) - an
    # unexpected error here (not just a failing git subprocess, which
    # _run_git already turns into a None/non-zero return) must never
    # propagate as an unhandled exception on that thread.
    try:
        rel_paths = [str(p.relative_to(PROJECT_ROOT)) for p in paths]
        add = _run_git("add", "--", *rel_paths)
        if add is None or add.returncode != 0:
            logger.warning("knowledge_sync: git add failed: %s", add.stderr if add else "")
            return
        commit = _run_git("commit", "-m", f"knowledge: auto-sync {', '.join(rel_paths)}")
        if commit is None:
            return
        if commit.returncode != 0:
            # Most commonly "nothing to commit" (content identical to HEAD) -
            # not an error, just nothing new to push.
            if "nothing to commit" not in (commit.stdout + commit.stderr):
                logger.warning("knowledge_sync: git commit failed: %s", commit.stderr)
            return
        pull = _run_git("pull", "--rebase", "--autostash")
        if pull is None or pull.returncode != 0:
            logger.warning("knowledge_sync: git pull --rebase failed (commit kept locally, not pushed): %s", pull.stderr if pull else "")
            return
        push = _run_git("push")
        if push is None or push.returncode != 0:
            logger.warning("knowledge_sync: git push failed (commit kept locally): %s", push.stderr if push else "")
    except Exception:
        logger.warning("knowledge_sync: unexpected error during sync_after_save", exc_info=True)


def sync_after_save(paths: list[Path]) -> None:
    """Fire-and-forget commit+pull+push of the given DDR file(s).

    Runs in a background daemon thread so a slow/failing network call never
    adds latency to the request that just saved a DDR."""
    if not _enabled():
        return
    threading.Thread(target=_sync_after_save, args=(list(paths),), daemon=True).start()


def pull_latest() -> None:
    """Best-effort ``git pull --rebase`` before a knowledge-base read.

    Throttled to at most once per `_PULL_MIN_INTERVAL_S` seconds so a single
    page load (which can fan out into several list/fetch calls) doesn't
    trigger a git pull per call."""
    if not _enabled():
        return
    try:
        global _last_pull_ts
        with _pull_lock:
            now = time.monotonic()
            if now - _last_pull_ts < _PULL_MIN_INTERVAL_S:
                return
            _last_pull_ts = now
        pull = _run_git("pull", "--rebase", "--autostash")
        if pull is None or pull.returncode != 0:
            logger.warning("knowledge_sync: git pull --rebase failed: %s", pull.stderr if pull else "")
    except Exception:
        logger.warning("knowledge_sync: unexpected error during pull_latest", exc_info=True)
