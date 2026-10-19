# DeliveryCourt for GenLayer

DeliveryCourt is a challengeable consensus court for disputed real-world service delivery. It lets a buyer, provider, or autonomous agent move from a fixed delivery promise to a final on-chain verdict.

## Workflow

1. `register_delivery_claim` commits a service reference, promise, deadline, buyer evidence, and provider evidence as bounded SHA-256 snapshots.
2. `assess_delivery` admits fresh delivery evidence and returns a `rev_*` consensus receipt.
3. `challenge_delivery_review` admits a `dch_*` counterevidence record only during the stored on-chain challenge window.
4. `resolve_delivery_challenge` and `finalize_delivery_verdict` use persisted snapshots, verify their binding, and return a final `dvr_*` receipt without refetching evidence.

Every consequential record stores canonical source URLs and collision-resistant snapshot commitments. The app writes directly to the Studio contract, waits for consensus acceptance, extracts returned IDs, and reads records back on-chain.

## Run locally

```bash
npm ci
npm test
npm run dev
```

Deploy `contracts/delivery_court.py` in GenLayer Studio, then enter that contract address in the app before creating a delivery claim. Current Studio deployment: `0xcA4F512aD1931658f5Dd839604873B205D9c1F9e`.
