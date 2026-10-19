import { readFileSync } from "node:fs";
import assert from "node:assert/strict";

const source = readFileSync("contracts/delivery_court.py", "utf8");
for (const marker of [
  "class DeliveryCourt(gl.Contract)", "register_delivery_claim", "assess_delivery",
  "challenge_delivery_review", "resolve_delivery_challenge", "finalize_delivery_verdict",
  "get_claim", "get_review", "get_challenge", "get_verdict",
  "gl.vm.run_nondet_unsafe", "gl.nondet.web.render", "gl.nondet.exec_prompt",
  "snapshot_commitments", "baseline_evidence", "delivery_evidence", "counterevidence",
  "SNAPSHOT_LIMIT = 3200", "snapshot_binding_mismatch", "challenge_window_still_open", "hashlib.sha256",
]) assert.ok(source.includes(marker), `missing contract integrity marker: ${marker}`);
assert.ok(!source.includes("hash("), "non-cryptographic hash must not be used");
assert.match(source, /review\["baseline_hash"\] != claim\["baseline_hash"\]/);
console.log("DeliveryCourt contract integrity checks passed");
