from uuid import uuid4
from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.clients import CoreClient, FraudClient, RemoteServiceError
from app.domain import PaymentCommand
from app.repository import InMemoryPaymentRepository
from app.service import PaymentRejected, PaymentService

app = FastAPI(title="Banco Horizonte Payment Service", version="1.0")
repo = InMemoryPaymentRepository()
service = PaymentService(repo, FraudClient(), CoreClient())


class PaymentRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    amount: float = Field(gt=0)
    risk_level: str = Field(pattern="^(low|high)$")


class PaymentResponse(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    status: str
    core_debit_id: str
    correlation_id: str


def auth(authorization: str | None) -> None:
    if authorization != "Bearer student-token":
        raise HTTPException(status_code=401, detail="invalid or missing token")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "payment"}


@app.post("/payments", response_model=PaymentResponse)
def create_payment(
    request: PaymentRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID"),
    x_bypass_fraud: str | None = Header(default=None, alias="X-Bypass-Fraud"),
) -> PaymentResponse:
    auth(authorization)
    if x_bypass_fraud is not None:
        raise HTTPException(status_code=403, detail="fraud bypass is forbidden")
    correlation_id = x_correlation_id or f"CORR-{uuid4().hex[:10].upper()}"
    try:
        result = service.process(
            PaymentCommand(request.customer_id, request.amount, request.risk_level),
            idempotency_key,
            correlation_id,
        )
    except PaymentRejected as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except RemoteServiceError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return PaymentResponse(**result.__dict__, correlation_id=correlation_id)


@app.get("/admin/traces/{correlation_id}")
def get_trace(correlation_id: str) -> dict:
    return {"correlation_id": correlation_id, "events": service.trace(correlation_id)}


@app.post("/admin/config")
def set_config(payload: dict) -> dict:
    if "crash_after_core_debit" in payload:
        service.crash_after_core_debit = bool(payload["crash_after_core_debit"])
    return {"crash_after_core_debit": service.crash_after_core_debit}


@app.post("/admin/reset")
def reset() -> dict:
    repo.clear()
    service._traces.clear()
    service.crash_after_core_debit = False
    return {"status": "reset"}
