import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx
from common import PAYMENT, payment, reset_all, show
reset_all(); corr="CORR-CLASS11"; r,_=payment(key="TRACE-1", correlation_id=corr); trace=httpx.get(f"{PAYMENT}/admin/traces/{corr}").json(); show(trace); stages=[e['stage'] for e in trace['events']]; assert r.status_code==200 and 'fraud_decision' in stages and 'core_debit' in stages and 'local_commit' in stages
