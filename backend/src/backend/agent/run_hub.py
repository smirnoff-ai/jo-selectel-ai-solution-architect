import asyncio
from collections.abc import AsyncIterator
from typing import Any


class RunChannel:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self._queues: list[asyncio.Queue[dict[str, Any] | None]] = []
        self.closed = False

    async def emit(self, event: dict[str, Any]) -> None:
        self.events.append(event)
        for queue in list(self._queues):
            await queue.put(event)

    def close(self) -> None:
        self.closed = True
        for queue in list(self._queues):
            queue.put_nowait(None)

    async def subscribe(self) -> AsyncIterator[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
        self._queues.append(queue)
        try:
            for event in list(self.events):
                yield event
            if self.closed:
                return
            while True:
                item = await queue.get()
                if item is None:
                    return
                yield item
        finally:
            self._queues.remove(queue)


class RunHub:
    def __init__(self) -> None:
        self._channels: dict[int, RunChannel] = {}

    def open(self, appeal_id: int) -> RunChannel:
        channel = RunChannel()
        self._channels[appeal_id] = channel
        return channel

    def get(self, appeal_id: int) -> RunChannel | None:
        return self._channels.get(appeal_id)
