import time
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Fraud Simulator")
config = {"latency_ms": 20, "mode": "up"}


class FraudRequest(BaseModel):
    customer_id: str
    amount: float = Field(gt=0)
    risk_level: str = Field(pattern="^(low|high)$")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "fraud", "config": config}


@app.post("/decision")
def decision(request: FraudRequest, x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID")) -> dict:
    time.sleep(config["latency_ms"] / 1000)
    if config["mode"] == "down":
        raise HTTPException(status_code=503, detail="fraud provider unavailable")
    return {"decision": "ALLOW", "correlation_id": x_correlation_id}


@app.post("/admin/config")
def set_config(payload: dict) -> dict:
    if "latency_ms" in payload:
        config["latency_ms"] = max(0, int(payload["latency_ms"]))
    if "mode" in payload:
        if payload["mode"] not in {"up", "down"}:
            raise HTTPException(status_code=422, detail="mode must be up or down")
        config["mode"] = payload["mode"]
    return config


@app.post("/admin/reset")
def reset() -> dict:
    config.update({"latency_ms": 20, "mode": "up"})
    return config
