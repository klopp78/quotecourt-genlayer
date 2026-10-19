import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
const source = readFileSync("contracts/quote_court.py", "utf8");
for (const marker of ["class QuoteCourt(gl.Contract)", "register_quote_request", "assess_provider_quotes", "challenge_quote_decision", "resolve_quote_challenge", "finalize_purchase_authorization", "execute_authorized_purchase", "get_quote_request", "get_quote_decision", "get_quote_challenge", "get_purchase_authorization", "get_purchase_execution", "gl.vm.run_nondet_unsafe", "gl.nondet.web.render", "gl.nondet.exec_prompt", "snapshot_commitments", "baseline_hash", "challenge_window_still_open", "hashlib.sha256"]) assert.ok(source.includes(marker), `missing contract integrity marker: ${marker}`);
assert.ok(!source.includes("hash("), "non-cryptographic hash must not be used");
assert.match(source, /authorization\["status"\] = "consumed"/);
console.log("QuoteCourt contract integrity checks passed");
