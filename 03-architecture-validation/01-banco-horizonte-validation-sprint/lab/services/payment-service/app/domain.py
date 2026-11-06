from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentCommand:
    customer_id: str
    amount: float
    risk_level: str


@dataclass(frozen=True)
class PaymentResult:
    transaction_id: str
    customer_id: str
    amount: float
    status: str
    core_debit_id: str
