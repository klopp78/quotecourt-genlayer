# QuoteCourt for GenLayer

QuoteCourt is a consensus procurement gate for AI agents and teams. It compares two source-bound provider quotes against a stored purchase policy and spend cap, then produces an on-chain authorization that a purchase executor must consume exactly once.

## Workflow

1. `register_quote_request` commits the purchase intent, selection policy, budget, provider quote URLs, and a real challenge window as canonical SHA-256 source snapshots.
2. `assess_provider_quotes` has validators independently re-render both provider sources and issue a `qdc_*` consensus decision tied to a `qte_*` request.
3. `challenge_quote_decision` and `resolve_quote_challenge` admit counterevidence during the stored window and preserve an auditable challenge record.
4. `finalize_purchase_authorization` creates a `qau_*` receipt only for the selected provider and capped amount.
5. `execute_authorized_purchase` rejects an expired, reused, mismatched-provider, or over-budget receipt and returns a one-time `qex_*` execution record.

Every consequential record uses canonical JSON and collision-resistant SHA-256 commitments. The app writes directly to the Studio contract, waits for consensus acceptance, extracts returned IDs, and reads records back on-chain.

## Run locally

```bash
npm ci
npm test
npm run dev
```

Deploy `contracts/quote_court.py` in GenLayer Studio, then enter that contract address in the app before registering a procurement request.
