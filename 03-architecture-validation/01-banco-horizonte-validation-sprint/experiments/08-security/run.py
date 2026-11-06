import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx
from common import CORE, FRAUD, PAYMENT, payment, post, reset_all, show
reset_all()
base={"customer_id":"C001","amount":100,"risk_level":"high"}
missing=httpx.post(f"{PAYMENT}/payments",json=base,headers={"Idempotency-Key":"S1"})
bad=httpx.post(f"{PAYMENT}/payments",json=base,headers={"Idempotency-Key":"S2","Authorization":"Bearer wrong"})
bypass,_=payment(key="S3",risk="high",bypass=True)
post(f"{FRAUD}/admin/config", {"mode":"down"}); down,_=payment(key="S4",risk="high"); debits=httpx.get(f"{CORE}/admin/debits").json(); result={"missing_token":missing.status_code,"bad_token":bad.status_code,"bypass":bypass.status_code,"fraud_down":down.status_code,"core_debits":debits['count']}; show(result); assert result=={"missing_token":401,"bad_token":401,"bypass":403,"fraud_down":503,"core_debits":0}
