import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx
from common import CORE, PAYMENT, payment, post, reset_all, show
reset_all(); key="CRASH-WINDOW"; post(f"{PAYMENT}/admin/config", {"crash_after_core_debit":True}); first,_=payment(key=key); second,_=payment(key=key); debits=httpx.get(f"{CORE}/admin/debits").json(); show({"first_status":first.status_code,"second_status":second.status_code,"core_debits_for_key":debits['by_key'].get(key,0),"interpretation":"risk reproduced if debit count is 2"}); assert first.status_code==500 and second.status_code==200 and debits['by_key'].get(key,0)==2
