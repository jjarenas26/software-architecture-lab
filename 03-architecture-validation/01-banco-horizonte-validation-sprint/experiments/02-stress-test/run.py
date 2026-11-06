import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import reset_all, run_load, show
for rps in [15,25,35,45,60,75]:
    reset_all(); result=run_load(rps,5); show(result)
