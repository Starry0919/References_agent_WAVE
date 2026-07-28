"""Event contract: the Event dataclass and the per-session EventBus."""
from __future__ import annotations

import asyncio
import contextlib
import logging
from dataclasses import dataclass
from typing import AsyncIterator, Callable

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """One agent-loop event; `seq` is per-session and monotonic from 1."""

    seq: int
    type: str
    ts: float
    data: dict

    def to_dict(self) -> dict:
        """Return the wire/persistence shape of this event."""
        return {"seq": self.seq, "type": self.type, "ts": self.ts, "data": self.data}


class EventBus:
    """One bus per session: records each event and fans it out to subscribers.

    The `sink` callback (wired by the SessionStore) appends the event to the
    session's event list and persists it before any fan-out.
    """

    def __init__(self, sink: Callable[[Event], None] | None = None) -> None:
        self._sink = sink
        self._queues: list[asyncio.Queue[Event | None]] = []

    def publish(self, event: Event) -> None:
        """Record the event, then fan out; a full/broken subscriber is dropped.

        A dropped subscriber receives a ``None`` sentinel so its consumer can
        close the connection and let the client reconnect/resync, instead of
        waiting forever on a queue that will never be fed again.
        """
        if self._sink is not None:
            try:
                self._sink(event)
            except Exception:
                # A persistence failure must never suppress the fan-out
                # (e.g. the terminal run_finished event) — log and continue.
                logger.exception("event sink failed for event type %s", event.type)
        for queue in list(self._queues):
            try:
                queue.put_nowait(event)
            except Exception:
                try:
                    self._queues.remove(queue)
                except ValueError:
                    pass
                try:  # make room, then signal the consumer it was dropped
                    queue.get_nowait()
                except Exception:
                    pass
                try:
                    queue.put_nowait(None)
                except Exception:
                    pass
                logger.warning("dropped a slow or broken event subscriber")

    @contextlib.asynccontextmanager
    async def subscribe(self) -> AsyncIterator["asyncio.Queue[Event | None]"]:
        """Async context manager yielding a queue of live events.

        A ``None`` item means the bus dropped this subscriber (overflow);
        the consumer should stop reading and close its connection.
        """
        queue: asyncio.Queue[Event | None] = asyncio.Queue(maxsize=1000)
        self._queues.append(queue)
        try:
            yield queue
        finally:
            try:
                self._queues.remove(queue)
            except ValueError:
                pass
