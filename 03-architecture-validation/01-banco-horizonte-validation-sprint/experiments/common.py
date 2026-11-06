import json
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import uuid4
import httpx

PAYMENT = "http://localhost:8101"
FRAUD = "http://localhost:8102"
CORE = "http://localhost:8103"
TOKEN = "Bearer student-token"


def post(url, payload=None, headers=None, timeout=5.0):
    return httpx.post(url, json=payload or {}, headers=headers or {}, timeout=timeout)


def reset_all():
    post(f"{PAYMENT}/admin/reset")
    post(f"{FRAUD}/admin/reset")
    post(f"{CORE}/admin/reset")


def payment(key=None, correlation_id=None, risk="low", amount=100.0, bypass=False, token=TOKEN):
    key = key or f"K-{uuid4().hex}"
    headers = {
        "Authorization": token,
        "Idempotency-Key": key,
        "X-Correlation-ID": correlation_id or f"CORR-{uuid4().hex[:10]}",
    }
    if bypass:
        headers["X-Bypass-Fraud"] = "true"
    t0 = time.perf_counter()
    r = httpx.post(
        f"{PAYMENT}/payments",
        json={"customer_id": "C001", "amount": amount, "risk_level": risk},
        headers=headers,
        timeout=5.0,
    )
    latency_ms = (time.perf_counter() - t0) * 1000
    return r, latency_ms


def pct(values, p):
    if not values:
        return 0.0
    s = sorted(values)
    idx = max(0, min(len(s)-1, math.ceil(p * len(s)) - 1))
    return s[idx]


def run_load(rps, duration):
    total = int(rps * duration)
    start = time.perf_counter()
    latencies = []
    statuses = []

    def one(i):
        target = start + i / rps
        wait = target - time.perf_counter()
        if wait > 0:
            time.sleep(wait)
        r, latency = payment()
        return r.status_code, latency

    workers = min(200, max(10, int(rps * 2)))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(one, i) for i in range(total)]
        for f in as_completed(futures):
            status, latency = f.result()
            statuses.append(status)
            latencies.append(latency)

    elapsed = time.perf_counter() - start
    errors = sum(1 for s in statuses if s >= 400)
    return {
        "offered_rps": rps,
        "requests": total,
        "elapsed_s": round(elapsed, 2),
        "achieved_rps": round(total / elapsed, 2),
        "p50_ms": round(pct(latencies, .50), 2),
        "p95_ms": round(pct(latencies, .95), 2),
        "p99_ms": round(pct(latencies, .99), 2),
        "error_rate_pct": round(errors * 100 / total, 3),
        "status_counts": {str(s): statuses.count(s) for s in sorted(set(statuses))},
    }


def show(obj):
    print(json.dumps(obj, indent=2, sort_keys=True))
