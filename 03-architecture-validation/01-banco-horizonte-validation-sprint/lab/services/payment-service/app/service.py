from collections import defaultdict
from threading import Lock
from time import perf_counter, time
from uuid import uuid4

from app.clients import CoreClient, FraudClient, RemoteServiceError
from app.domain import PaymentCommand, PaymentResult
from app.repository import InMemoryPaymentRepository


class PaymentRejected(Exception):
    pass


class PaymentService:
    def __init__(self, repository: InMemoryPaymentRepository, fraud: FraudClient, core: CoreClient) -> None:
        self.repository = repository
        self.fraud = fraud
        self.core = core
        self._locks: dict[str, Lock] = defaultdict(Lock)
        self._traces: dict[str, list[dict]] = defaultdict(list)
        self.crash_after_core_debit = False

    def _trace(self, correlation_id: str, stage: str, duration_ms: float | None = None, status: str = "ok") -> None:
        self._traces[correlation_id].append({
            "timestamp": time(),
            "stage": stage,
            "duration_ms": duration_ms,
            "status": status,
        })

    def trace(self, correlation_id: str) -> list[dict]:
        return list(self._traces.get(correlation_id, []))

    def process(self, command: PaymentCommand, idempotency_key: str, correlation_id: str) -> PaymentResult:
        lock = self._locks[idempotency_key]
        with lock:
            existing = self.repository.get(idempotency_key)
            if existing is not None:
                self._trace(correlation_id, "idempotency_hit")
                return existing

            self._trace(correlation_id, "payment_received")
            t0 = perf_counter()
            decision = self.fraud.decide(command.customer_id, command.amount, command.risk_level, correlation_id)
            self._trace(correlation_id, "fraud_decision", (perf_counter() - t0) * 1000, decision.lower())
            if decision != "ALLOW":
                raise PaymentRejected(f"fraud decision: {decision}")

            t1 = perf_counter()
            debit_id = self.core.debit(idempotency_key, command.amount, correlation_id)
            self._trace(correlation_id, "core_debit", (perf_counter() - t1) * 1000)

            if self.crash_after_core_debit:
                self.crash_after_core_debit = False
                self._trace(correlation_id, "injected_crash", status="failed")
                raise RuntimeError("injected crash after core debit before local commit")

            result = PaymentResult(
                transaction_id=f"TX-{uuid4().hex[:10].upper()}",
                customer_id=command.customer_id,
                amount=command.amount,
                status="COMPLETED",
                core_debit_id=debit_id,
            )
            self.repository.save(idempotency_key, result)
            self._trace(correlation_id, "local_commit")
            return result
