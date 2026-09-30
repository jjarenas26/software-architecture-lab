from collections import defaultdict
from collections.abc import Callable
from typing import Any


EventHandler = Callable[[Any], None]


class InMemoryEventBus:
    """Minimal publish/subscribe bus used to expose the architectural pattern."""

    def __init__(self) -> None:
        self._handlers: dict[type, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: object) -> None:
        for handler in list(self._handlers[type(event)]):
            handler(event)

    def clear(self) -> None:
        self._handlers.clear()
