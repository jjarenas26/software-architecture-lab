.PHONY: up down smoke reset load-test stress-test latency-test fraud-down duplicate-payment-test crash-after-core-debit trace-payment security-test architecture-test modularity-metrics test

up:
	docker compose up -d --build

down:
	docker compose down -v

smoke:
	python3 experiments/00-smoke/run.py

reset:
	python3 experiments/reset.py

load-test:
	python3 experiments/01-load-test/run.py --rps 60 --duration 10

stress-test:
	python3 experiments/02-stress-test/run.py

latency-test:
	python3 experiments/03-latency-test/run.py

fraud-down:
	python3 experiments/04-fraud-failure/run.py

duplicate-payment-test:
	python3 experiments/05-idempotency/run.py

crash-after-core-debit:
	python3 experiments/06-crash-window/run.py

trace-payment:
	python3 experiments/07-observability/run.py

security-test:
	python3 experiments/08-security/run.py

architecture-test:
	python3 experiments/09-modularity/architecture_check.py

modularity-metrics:
	python3 experiments/09-modularity/metrics.py

test:
	pytest -q lab/tests
	python3 experiments/09-modularity/architecture_check.py
