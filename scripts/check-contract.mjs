import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
const source = readFileSync("contracts/quote_court_v2.py", "utf8");
for (const marker of ["class QuoteCourtV2(gl.Contract)", "authorized_executor", "execute_authorized_purchase", "verify_purchase_completion", "caller_not_authorized_executor", "invalid_purchase_amount", "proof_submitted", "completed", "gl.vm.run_nondet_unsafe", "resolve_quote_challenge", "counterevidence_host_not_committed", "resolution_deadline", "expire_quote_challenge", "content_length", "content_hash", "source_trust_model", "list_quote_request_ids_page", "hashlib.sha256"]) assert.ok(source.includes(marker), `missing v2 contract security marker: ${marker}`);
assert.ok(!source.includes("SNAPSHOT_LIMIT"), "v2 must not truncate provider evidence to a snapshot limit");
assert.ok(!source.includes("except Exception:\n        return 0"), "v2 must not silently normalize unavailable time");
console.log("QuoteCourt v2 contract integrity checks passed");
