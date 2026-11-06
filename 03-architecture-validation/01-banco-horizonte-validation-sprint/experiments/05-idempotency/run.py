import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from concurrent.futures import ThreadPoolExecutor
import httpx
from common import CORE, payment, reset_all, show
reset_all(); key="SAME-KEY"
with ThreadPoolExecutor(max_workers=5) as ex:
    rows=list(ex.map(lambda i: payment(key=key), range(5)))
ids=[r.json()['transaction_id'] for r,_ in rows if r.status_code==200]; debits=httpx.get(f"{CORE}/admin/debits").json(); show({"statuses":[r.status_code for r,_ in rows],"transaction_ids":ids,"unique_transaction_ids":len(set(ids)),"core_debits":debits['by_key'].get(key,0)}); assert len(set(ids))==1 and debits['by_key'].get(key,0)==1
