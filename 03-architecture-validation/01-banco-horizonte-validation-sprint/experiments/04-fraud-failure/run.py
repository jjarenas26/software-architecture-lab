import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import CORE, FRAUD, payment, post, reset_all, show
reset_all(); post(f"{FRAUD}/admin/config", {"mode":"down"}); r,lat=payment(key="FRAUD-DOWN",risk="high"); debits=__import__('httpx').get(f"{CORE}/admin/debits").json(); show({"status":r.status_code,"latency_ms":round(lat,2),"body":r.json(),"core_debits":debits['count']}); assert r.status_code==503 and debits['count']==0
