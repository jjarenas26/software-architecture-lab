import os
import httpx


class RemoteServiceError(Exception):
    pass


class FraudClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("FRAUD_SERVICE_URL", "http://localhost:8102")
        self.timeout = float(os.getenv("FRAUD_TIMEOUT_SECONDS", "0.4"))

    def decide(self, customer_id: str, amount: float, risk_level: str, correlation_id: str) -> str:
        try:
            r = httpx.post(
                f"{self.base_url}/decision",
                json={"customer_id": customer_id, "amount": amount, "risk_level": risk_level},
                headers={"X-Correlation-ID": correlation_id},
                timeout=self.timeout,
            )
        except httpx.RequestError as e:
            raise RemoteServiceError("fraud-service unavailable or timed out") from e
        if r.status_code >= 500:
            raise RemoteServiceError("fraud-service unavailable or timed out")
        r.raise_for_status()
        return r.json()["decision"]


class CoreClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("CORE_SERVICE_URL", "http://localhost:8103")
        self.timeout = float(os.getenv("CORE_TIMEOUT_SECONDS", "2.0"))

    def debit(self, idempotency_key: str, amount: float, correlation_id: str) -> str:
        try:
            r = httpx.post(
                f"{self.base_url}/debits",
                json={"idempotency_key": idempotency_key, "amount": amount},
                headers={"X-Correlation-ID": correlation_id},
                timeout=self.timeout,
            )
        except httpx.RequestError as e:
            raise RemoteServiceError("core-service unavailable or timed out") from e
        if r.status_code >= 500:
            raise RemoteServiceError("core-service unavailable or saturated")
        r.raise_for_status()
        return r.json()["debit_id"]
