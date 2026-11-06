import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "services" / "payment-service"
sys.path.insert(0, str(ROOT))

from app.domain import PaymentCommand
from app.repository import InMemoryPaymentRepository
from app.service import PaymentService


class FakeFraud:
    def decide(self, customer_id, amount, risk_level, correlation_id):
        return "ALLOW"


class FakeCore:
    def __init__(self):
        self.calls = 0
    def debit(self, idempotency_key, amount, correlation_id):
        self.calls += 1
        return "D-1"


def test_normal_duplicate_is_idempotent():
    repo = InMemoryPaymentRepository()
    core = FakeCore()
    service = PaymentService(repo, FakeFraud(), core)
    cmd = PaymentCommand("C001", 100.0, "low")
    a = service.process(cmd, "K1", "C1")
    b = service.process(cmd, "K1", "C2")
    assert a.transaction_id == b.transaction_id
    assert core.calls == 1
