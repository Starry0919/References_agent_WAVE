"""Sessions and JSONL persistence under runs/."""
from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO

from harness.config import PROJECT_ROOT, get_settings
from harness.events import Event, EventBus

logger = logging.getLogger(__name__)

DEFAULT_TITLE = "新会话"

# 落盘缓冲:每行先进内存 pending 缓冲,满足任一条件才真正写盘 ——
# ① 攒够 FLUSH_LINES 行;② 距上次 flush 超过 FLUSH_INTERVAL_S 秒
# (在每次 append 时检查时间戳,不加后台任务:流式期间 append 本来就
# 很频繁,时间阈值实际靠下一次 append 触发)。崩溃窗口上界因此约为
# FLUSH_INTERVAL_S 秒内的 delta 事件 —— 这是用可接受的丢失换取
# 每秒几十次 flush 系统调用的消除。
PENDING_FLUSH_LINES = 64
PENDING_FLUSH_INTERVAL_S = 0.5

# run 边界事件必须立即同步落盘:run_finished 是重放方判断"本次运行
# 已完整结束"的依据,崩溃时它之后的日志允许丢失,它本身不允许。
IMMEDIATE_FLUSH_EVENT_TYPES = frozenset({"run_finished"})


@dataclass
class Session:
    """One conversation: OpenAI-format messages plus the event timeline."""

    id: str
    title: str = DEFAULT_TITLE
    created_at: float = field(default_factory=time.time)
    status: str = "idle"  # "idle" | "running"
    messages: list[dict] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    bus: EventBus | None = None
    current_task: "asyncio.Task | None" = None
    _seq: int = 0

    def next_seq(self) -> int:
        """Return the next per-session monotonic sequence number (from 1)."""
        self._seq += 1
        return self._seq

    def emit(self, type: str, data: dict) -> Event:
        """Create an event with the next seq and publish it on the bus."""
        if self.bus is None:
            raise RuntimeError(f"session {self.id} has no event bus wired")
        event = Event(seq=self.next_seq(), type=type, ts=time.time(), data=data)
        self.bus.publish(event)
        return event


class SessionStore:
    """In-memory session registry with append-only JSONL persistence."""

    def __init__(self, runs_dir: Path | None = None) -> None:
        self.runs_dir = runs_dir or (PROJECT_ROOT / "runs")
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, Session] = {}
        self._files: dict[str, TextIO] = {}
        self._pending: dict[str, list[str]] = {}
        self._last_flush: dict[str, float] = {}
        self._load_existing()

    # -- persistence -------------------------------------------------------

    def _path_for(self, session_id: str) -> Path:
        return self.runs_dir / f"{session_id}.jsonl"

    def _append_line(self, session_id: str, obj: dict) -> None:
        """Append one JSONL line via a per-session buffered writer.

        Token deltas make this the hot path: the serialized line first
        lands in an in-memory pending buffer, and is flushed to disk only
        when ① the buffer reaches PENDING_FLUSH_LINES lines, ② more than
        PENDING_FLUSH_INTERVAL_S seconds elapsed since the last flush, or
        ③ the line carries a run-boundary event (run_finished), which is
        flushed immediately and synchronously so a crash can never lose
        the terminal record. 缓冲只影响落盘:WS 扇出仍由 EventBus 在 sink
        返回后立即进行,顺序(内存 list → 落盘排队 → 扇出)保持不变。
        """
        pending = self._pending.setdefault(session_id, [])
        pending.append(json.dumps(obj, ensure_ascii=False) + "\n")
        now = time.monotonic()
        event = obj.get("event") if obj.get("kind") == "event" else None
        is_run_boundary = (
            event is not None and event.get("type") in IMMEDIATE_FLUSH_EVENT_TYPES
        )
        if (
            is_run_boundary
            or len(pending) >= PENDING_FLUSH_LINES
            or now - self._last_flush.get(session_id, now) >= PENDING_FLUSH_INTERVAL_S
        ):
            self._flush_pending(session_id, now)

    def _flush_pending(self, session_id: str, now: float | None = None) -> None:
        """Write all buffered lines for one session to disk in one flush."""
        pending = self._pending.get(session_id)
        if now is None:
            now = time.monotonic()
        self._last_flush[session_id] = now
        if not pending:
            return
        fh = self._files.get(session_id)
        if fh is None or fh.closed:
            fh = self._path_for(session_id).open("a", encoding="utf-8")
            self._files[session_id] = fh
        fh.writelines(pending)
        fh.flush()
        pending.clear()

    def close_all(self) -> None:
        """Flush every pending buffer and close all open file handles.

        进程退出时由 server lifespan 调用一次。之后 store 仍可用
        (句柄会在下次 flush 时惰性重开),只是不再常驻持有句柄。
        """
        for session_id in set(self._pending) | set(self._files):
            try:
                self._flush_pending(session_id)
            except Exception:
                logger.exception("could not flush pending lines for session %s", session_id)
            fh = self._files.pop(session_id, None)
            if fh is not None:
                try:
                    fh.close()
                except Exception:  # pragma: no cover - best effort
                    logger.exception("could not close session file for %s", session_id)
        logger.info("closed all session files")

    def _write_meta(self, session: Session) -> None:
        self._append_line(
            session.id,
            {
                "kind": "meta",
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at,
            },
        )

    def _wire(self, session: Session) -> None:
        """Attach an EventBus whose sink records and persists each event."""

        def sink(event: Event, _session: Session = session) -> None:
            _session.events.append(event)
            self._append_line(_session.id, {"kind": "event", "event": event.to_dict()})

        session.bus = EventBus(sink=sink)

    def _load_existing(self) -> None:
        """Load all runs/*.jsonl back into memory, skipping corrupt lines."""
        for path in sorted(self.runs_dir.glob("*.jsonl")):
            try:
                session = self._load_file(path)
            except Exception as exc:
                logger.warning("could not load session file %s: %s", path.name, exc)
                continue
            self._sessions[session.id] = session
        if self._sessions:
            logger.info("loaded %d session(s) from %s", len(self._sessions), self.runs_dir)

    def _load_file(self, path: Path) -> Session:
        session = Session(id=path.stem)
        max_seq = 0
        with path.open("r", encoding="utf-8") as fh:
            for line_number, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    kind = obj.get("kind")
                    if kind == "meta":
                        session.id = str(obj.get("id", session.id))
                        session.title = str(obj.get("title", session.title))
                        session.created_at = float(obj.get("created_at", session.created_at))
                    elif kind == "message":
                        session.messages.append(dict(obj["message"]))
                    elif kind == "event":
                        raw = obj["event"]
                        event = Event(
                            seq=int(raw["seq"]),
                            type=str(raw["type"]),
                            ts=float(raw["ts"]),
                            data=dict(raw["data"]),
                        )
                        session.events.append(event)
                        max_seq = max(max_seq, event.seq)
                    else:
                        raise ValueError(f"unknown line kind: {kind!r}")
                except Exception as exc:
                    logger.warning(
                        "skipping corrupt line %d in %s: %s", line_number, path.name, exc
                    )
        session._seq = max_seq
        session.status = "idle"
        self._wire(session)
        self._repair_after_load(session)
        return session

    def _repair_after_load(self, session: Session) -> None:
        """Heal a session whose process died mid-run.

        A hard crash (SIGKILL, power loss) can leave (a) dangling assistant
        tool_calls, which the next LLM call would reject, and (b) an event
        log with no terminal run_finished, which would wedge replaying
        clients in the "running" state.
        """
        self.backfill_unanswered_tool_calls(session)
        open_run = False
        for event in session.events:
            if event.type == "run_started":
                open_run = True
            elif event.type == "run_finished":
                open_run = False
        if open_run:
            session.emit(
                "run_finished",
                {"status": "error", "error": "server stopped before this run finished"},
            )

    # -- public API --------------------------------------------------------

    def create(self) -> Session:
        """Create, wire, persist and return a new session."""
        session = Session(id=uuid.uuid4().hex[:12])
        self._wire(session)
        self._sessions[session.id] = session
        self._write_meta(session)
        self.append_message(
            session, {"role": "system", "content": get_settings().SYSTEM_PROMPT}
        )
        logger.info("created session %s", session.id)
        return session

    def get(self, session_id: str) -> Session | None:
        """Look up a session by id."""
        return self._sessions.get(session_id)

    def list(self) -> list[Session]:
        """All sessions, newest first."""
        return sorted(self._sessions.values(), key=lambda s: s.created_at, reverse=True)

    def delete(self, session_id: str) -> None:
        """Remove a session from memory and disk; refuses while running."""
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(session_id)
        if session.status == "running":
            raise RuntimeError("session is running")
        del self._sessions[session_id]
        # 文件马上要被删掉,未落盘的 pending 直接丢弃 —— 否则之后的
        # close_all() 会把已删除会话的行写回磁盘、把文件重建出来。
        self._pending.pop(session_id, None)
        self._last_flush.pop(session_id, None)
        fh = self._files.pop(session_id, None)
        if fh is not None:
            try:
                fh.close()
            except Exception:  # pragma: no cover - best effort
                pass
        self._path_for(session_id).unlink(missing_ok=True)
        logger.info("deleted session %s", session_id)

    def append_message(self, session: Session, message: dict) -> None:
        """Append a message to the session and persist it."""
        session.messages.append(message)
        self._append_line(session.id, {"kind": "message", "message": message})

    def backfill_unanswered_tool_calls(self, session: Session) -> None:
        """Protocol integrity: answer dangling tool_calls of the last assistant.

        If the last assistant message carries tool_calls whose ids lack a
        role=tool reply in the contiguous block that follows it, insert an
        ERROR tool message for each unanswered id immediately after the last
        existing reply — otherwise the next LLM call would be rejected.
        Idempotent; used after an interrupted run and when reloading files.
        """
        messages = session.messages
        last_assistant_index: int | None = None
        for index in range(len(messages) - 1, -1, -1):
            if messages[index].get("role") == "assistant":
                last_assistant_index = index
                break
        if last_assistant_index is None:
            return
        tool_calls = messages[last_assistant_index].get("tool_calls") or []
        if not tool_calls:
            return
        # Only tool messages directly following the assistant message count
        # as answers: the API requires exactly that ordering.
        insert_at = last_assistant_index + 1
        answered: set = set()
        while insert_at < len(messages) and messages[insert_at].get("role") == "tool":
            answered.add(messages[insert_at].get("tool_call_id"))
            insert_at += 1
        for tc in tool_calls:
            call_id = tc.get("id")
            if call_id in answered:
                continue
            repair = {
                "role": "tool",
                "tool_call_id": call_id,
                "content": "ERROR: run interrupted before this tool finished",
            }
            messages.insert(insert_at, repair)
            self._append_line(session.id, {"kind": "message", "message": repair})
            insert_at += 1

    def set_title(self, session: Session, title: str) -> None:
        """Update the title, persist a new meta line, emit session_meta."""
        session.title = title
        self._write_meta(session)
        session.emit("session_meta", {"title": title})

    def maybe_set_title(self, session: Session, user_content: str) -> None:
        """On the first user message, title = its first 40 chars (single line)."""
        user_count = sum(1 for m in session.messages if m.get("role") == "user")
        if user_count != 1:
            return
        single_line = " ".join(user_content.split())
        title = single_line[:40] or DEFAULT_TITLE
        self.set_title(session, title)
