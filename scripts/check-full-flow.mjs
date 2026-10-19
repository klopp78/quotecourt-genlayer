import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const page = readFileSync("site-static/index.html", "utf8");
const client = readFileSync("site-static/main.ts", "utf8");
for (const marker of ["Register a procurement request", "Assess provider quotes", "Challenge and resolve", "Create one-use authorization", "Execute authorized purchase", "Read on-chain record"]) assert.ok(page.includes(marker), `missing visible workflow control: ${marker}`);
for (const method of ["register_quote_request", "assess_provider_quotes", "challenge_quote_decision", "resolve_quote_challenge", "finalize_purchase_authorization", "execute_authorized_purchase"]) assert.ok(client.includes(method), `missing GenLayer client call: ${method}`);
for (const readMethod of ["get_quote_request", "get_quote_decision", "get_quote_challenge", "get_purchase_authorization", "get_purchase_execution"]) assert.ok(page.includes(readMethod), `missing readable contract method: ${readMethod}`);
assert.ok(client.includes("waitForTransactionReceipt"), "writes must wait for consensus acceptance");
console.log("QuoteCourt frontend-contract flow checks passed");
