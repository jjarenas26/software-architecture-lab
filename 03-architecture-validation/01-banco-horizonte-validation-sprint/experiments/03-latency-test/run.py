import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import FRAUD, post, reset_all, run_load, show

for ms in [20, 200, 500, 900]:
    reset_all()
    post(f"{FRAUD}/admin/config", {"latency_ms": ms})
    print()
    print(f"FRAUD_LATENCY_MS={ms}")
    show(run_load(10, 3))
