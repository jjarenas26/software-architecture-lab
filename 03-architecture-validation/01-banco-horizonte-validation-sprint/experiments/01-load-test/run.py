import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import reset_all, run_load, show
p=argparse.ArgumentParser(); p.add_argument('--rps',type=float,default=60); p.add_argument('--duration',type=float,default=10); p.add_argument('--strict',action='store_true'); a=p.parse_args()
reset_all(); result=run_load(a.rps,a.duration); show(result)
passed = result['p95_ms'] <= 1500 and result['p99_ms'] <= 3000 and result['error_rate_pct'] < 0.5
print('ACCEPTANCE:', 'PASS' if passed else 'FAIL')
if a.strict and not passed: raise SystemExit(2)
