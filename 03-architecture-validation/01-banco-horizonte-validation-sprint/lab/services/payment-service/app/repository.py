from threading import Lock
from app.domain import PaymentResult


class InMemoryPaymentRepository:
    def __init__(self) -> None:
        self._items: dict[str, PaymentResult] = {}
        self._lock = Lock()

    def get(self, key: str) -> PaymentResult | None:
        with self._lock:
            return self._items.get(key)

    def save(self, key: str, result: PaymentResult) -> None:
        with self._lock:
            self._items[key] = result

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
