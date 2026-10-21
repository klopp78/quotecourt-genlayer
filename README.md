# QuoteCourt for GenLayer

QuoteCourt v2 is a consensus procurement gate for AI agents and teams. It compares independently reproduced provider quotes against a stored purchase policy and spend cap, then creates an executor-bound authorization. A submitted purchase proof is not treated as completed until a separate consensus verification writes the completed receipt.

## Workflow

1. `register_quote_request` commits the requester, authorized executor, currency, quantity, budget, quote URLs, full-content SHA-256 commitments, and challenge window.
2. `assess_provider_quotes` makes validators independently re-render all sources and rejects incomplete, changed, malformed, or uncommitted evidence.
3. `challenge_quote_decision` is requester-only and accepts evidence only from committed provider hosts. `resolve_quote_challenge` runs inside a validator-checked nondeterministic consensus block; `expire_quote_challenge` recovers a stalled dispute.
4. `finalize_purchase_authorization` creates a time-limited `qau_*` receipt for one executor, provider, amount, currency, and quantity.
5. `execute_authorized_purchase` only submits authenticated, positive-amount proof from that executor. `verify_purchase_completion` separately verifies that proof before changing status to `completed`.

Every consequential record uses canonical JSON and collision-resistant SHA-256 commitments. The app waits for finalized consensus, checks `FINISHED_WITH_RETURN`, and reads the exact record back from the selected Studio contract before showing success. Public HTTPS evidence is an explicitly disclosed trust boundary, not merchant identity verification.

## Run locally

```bash
npm ci
npm test
npm run dev
```

Deploy `contracts/quote_court_v2.py` in GenLayer Studio, then enter that exact contract address in the app before registering a procurement request. The current source-matched Studionet v2 deployment is [`0x72F669a824FC566146A83BF8d32E33eEa916CB6a`](https://explorer-studio.genlayer.com/address/0x72F669a824FC566146A83BF8d32E33eEa916CB6a). The public CI runs integrity, adversarial lifecycle, frontend-finality, static-build, and Pages-deployment checks.
