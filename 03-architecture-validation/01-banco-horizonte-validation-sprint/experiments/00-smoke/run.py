import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import payment, reset_all, show
reset_all()
r, latency = payment(key="SMOKE-1")
show({"status": r.status_code, "latency_ms": round(latency,2), "body": r.json()})
assert r.status_code == 200
