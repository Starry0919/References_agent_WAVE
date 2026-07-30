"""SessionStore 缓冲落盘与关停清理的回归测试(不依赖网络/API key)。

覆盖:
- 大量小事件 emit 后,经 run_finished 或 close_all,重放能读回全部事件;
- 行数/时间两个 flush 阈值各自生效,缓冲不丢事件;
- close_all 后文件句柄全部关闭。
"""
from __future__ import annotations

import json
from pathlib import Path

from harness import sessions as sessions_module
from harness.sessions import SessionStore


def _emit_deltas(session, count: int) -> None:
    for index in range(count):
        session.emit("assistant_delta", {"text": f"tok{index}"})


def _read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_many_small_events_replay_complete(store, runs_dir: Path) -> None:
    """流式 delta 洪峰:run_finished 后立即重放,事件一个不少。"""
    session = store.create()
    session.emit("run_started", {})
    _emit_deltas(session, 500)
    session.emit("run_finished", {"status": "ok"})

    replayed = SessionStore(runs_dir=runs_dir)
    try:
        loaded = replayed.get(session.id)
        assert loaded is not None
        assert len(loaded.events) == 502
        assert [event.seq for event in loaded.events] == list(range(1, 503))
        assert loaded.events[-1].type == "run_finished"
    finally:
        replayed.close_all()


def test_run_finished_flushes_immediately(store, runs_dir: Path, monkeypatch) -> None:
    """关掉行数/时间阈值后,只有 run 边界事件能触发落盘。"""
    monkeypatch.setattr(sessions_module, "PENDING_FLUSH_LINES", 10**9)
    monkeypatch.setattr(sessions_module, "PENDING_FLUSH_INTERVAL_S", 10**9)
    session = store.create()
    path = runs_dir / f"{session.id}.jsonl"

    session.emit("run_started", {})
    _emit_deltas(session, 50)
    # 阈值都被禁用且未到 run 边界:一行都不应落盘。
    assert not path.exists()

    session.emit("run_finished", {"status": "ok"})
    lines = _read_jsonl(path)
    events = [line for line in lines if line.get("kind") == "event"]
    assert len(events) == 52  # run_started + 50 deltas + run_finished
    assert events[-1]["event"]["type"] == "run_finished"


def test_close_all_flushes_pending(store, runs_dir: Path, monkeypatch) -> None:
    """run_finished 之后再来的 delta 只进缓冲;close_all 后重放完整。"""
    monkeypatch.setattr(sessions_module, "PENDING_FLUSH_LINES", 10**9)
    monkeypatch.setattr(sessions_module, "PENDING_FLUSH_INTERVAL_S", 10**9)
    session = store.create()
    session.emit("run_started", {})
    _emit_deltas(session, 30)
    session.emit("run_finished", {"status": "ok"})
    _emit_deltas(session, 5)  # 只进 pending 缓冲,尚未落盘

    store.close_all()

    replayed = SessionStore(runs_dir=runs_dir)
    try:
        loaded = replayed.get(session.id)
        assert loaded is not None
        assert [event.type for event in loaded.events] == [
            event.type for event in session.events
        ]
        assert len(loaded.events) == 1 + 30 + 1 + 5
    finally:
        replayed.close_all()


def test_line_threshold_triggers_flush(store, runs_dir: Path, monkeypatch) -> None:
    """pending 攒到行数阈值即落盘,不等时间窗口。"""
    monkeypatch.setattr(sessions_module, "PENDING_FLUSH_LINES", 4)
    monkeypatch.setattr(sessions_module, "PENDING_FLUSH_INTERVAL_S", 10**9)
    session = store.create()  # meta + system message = 2 行 pending
    session.emit("run_started", {})  # 3
    session.emit("assistant_delta", {"text": "a"})  # 4 -> flush

    lines = _read_jsonl(runs_dir / f"{session.id}.jsonl")
    assert len(lines) == 4


def test_time_threshold_triggers_flush(store, runs_dir: Path, monkeypatch) -> None:
    """距上次 flush 超过时间阈值即落盘(0 秒 = 每次 append 都落盘)。"""
    monkeypatch.setattr(sessions_module, "PENDING_FLUSH_LINES", 10**9)
    monkeypatch.setattr(sessions_module, "PENDING_FLUSH_INTERVAL_S", 0.0)
    session = store.create()  # 每次 append 立即 flush

    lines = _read_jsonl(runs_dir / f"{session.id}.jsonl")
    assert len(lines) == 2  # meta + system message


def test_close_all_closes_file_handles(store, runs_dir: Path) -> None:
    """close_all 关闭全部常驻句柄,store 自身清空句柄表。"""
    session = store.create()
    session.emit("run_finished", {"status": "ok"})  # 触发一次 flush,句柄常驻
    handle = store._files[session.id]
    assert not handle.closed

    store.close_all()

    assert handle.closed
    assert store._files == {}
