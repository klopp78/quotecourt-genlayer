import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const source = readFileSync("contracts/delivery_court.py", "utf8");
for (const id of ["dlv_" + "a".repeat(20), "rev_" + "b".repeat(20), "dch_" + "c".repeat(20), "dvr_" + "d".repeat(20)]) assert.match(id, /^(dlv|rev|dch|dvr)_[a-f0-9]{20}$/);
for (const marker of ["review_not_challengeable", "challenge_window_closed", "challenge_window_still_open", "claim_not_finalizable", "snapshot_binding_mismatch", "promised_delivery", "delivery_evidence"]) assert.ok(source.includes(marker), `missing lifecycle guard ${marker}`);
assert.ok(source.includes('"content": content'), "rendered evidence must be persisted with each snapshot");
console.log("DeliveryCourt lifecycle guard checks passed");
