# Experiments - command map

Run from the module root after `make up`.

| Command | Question |
|---|---|
| `make smoke` | Does the walking skeleton work end-to-end? |
| `make load-test` | Does scenario-equivalent peak load meet acceptance criteria? |
| `make stress-test` | Where does the system begin to degrade? |
| `make latency-test` | What happens as Fraud latency approaches/exceeds 400 ms? |
| `make fraud-down` | Does fail-closed prevent high-risk bypass? |
| `make duplicate-payment-test` | Do five retries create one debit? |
| `make crash-after-core-debit` | What happens if the remote side effect succeeds before local commit? |
| `make trace-payment` | Can one transaction be reconstructed by correlation ID? |
| `make security-test` | Do selected auth/fraud controls reject expected attacks? |
| `make architecture-test` | Has domain dependency direction been preserved? |
| `make modularity-metrics` | What do Ca/Ce/Instability reveal about structure? |

The expected result of an experiment may be FAIL. A failed acceptance criterion can be successful validation evidence.
