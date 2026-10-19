import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";
import "./styles.css";

type Address = `0x${string}`;
type Prefix = "qte" | "qdc" | "qch" | "qau" | "qex";
const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const receiptField: Record<Prefix, string> = { qte: "request-id", qdc: "decision-id", qch: "challenge-id", qau: "authorization-id", qex: "execution-id" };
let wallet: Address | undefined;
const explorer = (kind: "address" | "tx", value: string) => `https://explorer-studio.genlayer.com/${kind}/${value}`;
const value = (id: string) => ($(id) as HTMLInputElement).value;
const setStatus = (message: string, phase = "READY") => { $("status").textContent = message; $("phase").textContent = phase; };
const output = (item: unknown) => { $("output").textContent = typeof item === "string" ? item : JSON.stringify(item, null, 2); };
function extract(item: unknown, prefix: Prefix): string | undefined { if (typeof item === "string") return item.match(new RegExp(`${prefix}_[a-f0-9]{20}`))?.[0]; if (!item || typeof item !== "object") return undefined; return Object.values(item as Record<string, unknown>).map((entry) => extract(entry, prefix)).find(Boolean); }
function put(id: string, item: string) { ($(id) as HTMLInputElement).value = item; }
function propagate(prefix: Prefix, item: string) { if (prefix === "qte") ["decision-request", "challenge-request", "authorize-request", "execute-request"].forEach((id) => put(id, item)); if (prefix === "qdc") put("challenge-decision", item); if (prefix === "qch") put("resolve-challenge", item); if (prefix === "qau") put("execute-authorization", item); put("record-id", item); }
async function connect() { const provider = window.ethereum; if (!provider) throw new Error("No browser wallet detected."); const accounts = await provider.request({ method: "eth_requestAccounts" }) as Address[]; if (!accounts[0]) throw new Error("No wallet account returned."); wallet = accounts[0]; $("connect").textContent = `${wallet.slice(0, 6)}...${wallet.slice(-4)}`; setStatus("Wallet connected. Forms write directly to the deployed Studio contract."); }
async function write(method: string, args: string[], prefix: Prefix) { if (!wallet) await connect(); const deployed = value("contract-address").trim() as Address; if (!/^0x[a-fA-F0-9]{40}$/.test(deployed)) throw new Error("Enter a valid deployed Studio contract address."); setStatus("Submitting consensus transaction...", "PENDING"); const client = createClient({ chain: studionet, account: wallet!, provider: window.ethereum }); const hash = await client.writeContract({ address: deployed, functionName: method, args, value: BigInt(0), leaderOnly: false }); $("tx").innerHTML = `<a target="_blank" rel="noreferrer" href="${explorer("tx", hash)}">${hash.slice(0, 10)}...</a>`; const receipt = await client.waitForTransactionReceipt({ hash, status: TransactionStatus.ACCEPTED, fullTransaction: true }); const id = extract(receipt, prefix); if (!id) throw new Error("Accepted transaction did not return the expected receipt ID."); $(receiptField[prefix]).textContent = id; propagate(prefix, id); setStatus(`${prefix}_ receipt accepted by consensus.`, "ACCEPTED"); output(receipt); }
const showError = (error: unknown) => setStatus(error instanceof Error ? error.message : String(error), "ERROR");
$("connect").addEventListener("click", () => connect().catch(showError));
$("contract-address").addEventListener("input", () => { const deployed = value("contract-address").trim(); $("short-address").textContent = `${deployed.slice(0, 6)}...${deployed.slice(-4)}`; $("explorer").setAttribute("href", explorer("address", deployed)); });
document.querySelectorAll<HTMLButtonElement>(".tab").forEach((tab) => tab.addEventListener("click", () => { document.querySelectorAll(".tab,.view").forEach((node) => node.classList.remove("active")); tab.classList.add("active"); $(tab.dataset.tab!).classList.add("active"); }));
$("request").addEventListener("submit", (event) => { event.preventDefault(); write("register_quote_request", [value("intent"), value("policy"), value("max-spend"), value("provider-a"), value("provider-b"), value("challenge-window")], "qte").catch(showError); });
$("decision").addEventListener("submit", (event) => { event.preventDefault(); write("assess_provider_quotes", [value("decision-request")], "qdc").catch(showError); });
$("challenge").addEventListener("submit", (event) => { event.preventDefault(); write("challenge_quote_decision", [value("challenge-request"), value("challenge-decision"), value("counterevidence")], "qch").catch(showError); });
$("resolve").addEventListener("click", () => write("resolve_quote_challenge", [value("challenge-request"), value("resolve-challenge")], "qch").catch(showError));
$("authorize").addEventListener("submit", (event) => { event.preventDefault(); write("finalize_purchase_authorization", [value("authorize-request"), value("authorization-window")], "qau").catch(showError); });
$("execute").addEventListener("submit", (event) => { event.preventDefault(); write("execute_authorized_purchase", [value("execute-request"), value("execute-authorization"), value("execute-provider"), value("execute-spend")], "qex").catch(showError); });
$("read").addEventListener("click", async () => { try { setStatus("Reading accepted chain state...", "READING"); const client = createClient({ chain: studionet }); const result = await client.readContract({ address: value("contract-address").trim() as Address, functionName: ($("record-type") as HTMLSelectElement).value, args: [value("record-id")], jsonSafeReturn: true, leaderOnly: true }); output(result); setStatus("Accepted record loaded.", "READ"); } catch (error) { showError(error); } });
