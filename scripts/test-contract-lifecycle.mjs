import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const source = readFileSync("contracts/quote_court.py", "utf8");
for (const id of ["qte_" + "a".repeat(20), "qdc_" + "b".repeat(20), "qch_" + "c".repeat(20), "qau_" + "d".repeat(20), "qex_" + "e".repeat(20)]) assert.match(id, /^(qte|qdc|qch|qau|qex)_[a-f0-9]{20}$/);
for (const marker of ["decision_not_challengeable", "challenge_window_closed", "challenge_window_still_open", "request_not_finalizable", "provider_not_authorized", "spend_cap_exceeded", "authorization_expired_or_consumed"]) assert.ok(source.includes(marker), `missing lifecycle guard ${marker}`);
assert.ok(source.includes('"content": content'), "rendered quote content must be persisted with each snapshot");
console.log("QuoteCourt lifecycle guard checks passed");
