from collections import defaultdict, deque
from time import monotonic, sleep
from uuid import uuid4
from threading import Lock

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Legacy Core Simulator")
config = {"latency_ms": 20, "max_rps": 35, "idempotent": False}
recent = deque()
debits: list[dict] = []
lock = Lock()


class DebitRequest(BaseModel):
    idempotency_key: str
    amount: float = Field(gt=0)


def capacity_check() -> None:
    now = monotonic()
    with lock:
        while recent and now - recent[0] > 1.0:
            recent.popleft()
        if len(recent) >= config["max_rps"]:
            raise HTTPException(status_code=503, detail="legacy core saturated")
        recent.append(now)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "core", "config": config}


@app.post("/debits")
def debit(request: DebitRequest, x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID")) -> dict:
    capacity_check()
    sleep(config["latency_ms"] / 1000)
    with lock:
        if config["idempotent"]:
            for d in debits:
                if d["idempotency_key"] == request.idempotency_key:
                    return d
        record = {
            "debit_id": f"DB-{uuid4().hex[:10].upper()}",
            "idempotency_key": request.idempotency_key,
            "amount": request.amount,
            "correlation_id": x_correlation_id,
        }
        debits.append(record)
        return record


@app.get("/admin/debits")
def get_debits() -> dict:
    counts = defaultdict(int)
    for d in debits:
        counts[d["idempotency_key"]] += 1
    return {"count": len(debits), "by_key": dict(counts), "items": debits}


@app.post("/admin/config")
def set_config(payload: dict) -> dict:
    if "latency_ms" in payload:
        config["latency_ms"] = max(0, int(payload["latency_ms"]))
    if "max_rps" in payload:
        config["max_rps"] = max(1, int(payload["max_rps"]))
    if "idempotent" in payload:
        config["idempotent"] = bool(payload["idempotent"])
    return config


@app.post("/admin/reset")
def reset() -> dict:
    with lock:
        recent.clear()
        debits.clear()
    config.update({"latency_ms": 20, "max_rps": 35, "idempotent": False})
    return {"status": "reset", "config": config}
