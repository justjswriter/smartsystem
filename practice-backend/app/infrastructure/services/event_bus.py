import asyncio
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[dict[str, Any]]]] = {}

    def subscribe(self, topic: str) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._subscribers.setdefault(topic, []).append(queue)
        return queue

    def unsubscribe(self, topic: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
        subscribers = self._subscribers.get(topic, [])
        if queue in subscribers:
            subscribers.remove(queue)
        if not subscribers and topic in self._subscribers:
            self._subscribers.pop(topic, None)

    async def publish(self, topic: str, event: dict[str, Any]) -> None:
        for queue in self._subscribers.get(topic, []):
            await queue.put(event)


event_bus = EventBus()
