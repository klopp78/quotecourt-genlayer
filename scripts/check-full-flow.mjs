import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("site-static/index.html", "utf8");
const client = readFileSync("site-static/main.ts", "utf8");
for (const marker of ["Register claim", "Assess delivery", "Challenge", "Resolve challenge", "Finalize verdict", "Read on-chain record"]) assert.ok(page.includes(marker), `missing visible workflow control: ${marker}`);
for (const method of ["register_delivery_claim", "assess_delivery", "challenge_delivery_review", "resolve_delivery_challenge", "finalize_delivery_verdict"]) assert.ok(client.includes(method), `missing GenLayer client call: ${method}`);
for (const readMethod of ["get_claim", "get_review", "get_challenge", "get_verdict"]) assert.ok(page.includes(readMethod), `missing readable contract method: ${readMethod}`);
assert.ok(client.includes("waitForTransactionReceipt"), "writes must wait for consensus acceptance");
console.log("DeliveryCourt frontend-contract flow checks passed");
