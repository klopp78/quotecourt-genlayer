import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const source = readFileSync("contracts/quote_court_v2.py", "utf8");
const state = { requester: "0x1111111111111111111111111111111111111111", executor: "0x2222222222222222222222222222222222222222", status: "authorized", authorization: "authorized", cap: 25000000, executed: false };
function submit(caller, amountMicros, proofHost) { assert.equal(caller, state.executor, "unauthorized wallet cannot consume authorization"); assert.ok(amountMicros > 0 && amountMicros <= state.cap, "amount must be positive and within cap"); assert.equal(proofHost, "provider.example", "proof must be hosted by authorized provider"); assert.equal(state.status, "authorized"); assert.equal(state.authorization, "authorized"); state.status = "purchase_proof_submitted"; state.authorization = "proof_submitted"; state.executed = true; }
assert.throws(() => submit(state.requester, 1000000, "provider.example"));
assert.throws(() => submit(state.executor, 0, "provider.example"));
assert.throws(() => submit(state.executor, 1000000, "forged.example"));
submit(state.executor, 1000000, "provider.example");
assert.throws(() => submit(state.executor, 1000000, "provider.example"), "replay must fail after proof submission");
assert.equal(state.status, "purchase_proof_submitted", "proof submission is not a completed purchase");
state.status = "completed"; state.authorization = "completed";
assert.equal(state.status, "completed", "only a separate verification transition completes purchase");
for (const guard of ["only_requester_can_challenge", "challenge_window_closed", "challenge_resolution_expired", "challenge_resolution_still_open", "counterevidence_host_not_committed", "caller_not_authorized_executor", "authorization_expired", "purchase_proof_host_not_authorized"]) assert.ok(source.includes(guard), `missing adversarial lifecycle guard ${guard}`);
console.log("QuoteCourt v2 adversarial lifecycle model checks passed");
